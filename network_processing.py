#!/usr/bin/python3
# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np


def build_interaction_network(scene_speech_turns):
    """Builds the dynamic network of speaker interaction time in each scene
    Args:
    scene_speech_turns (dict)         : speech turns with interlocutors, as distributed over scenes

    Returns:
    G                  (nx.MultiGraph): undirected, weighted multigraph of interaction time by scene
    """
    
    G = nx.MultiGraph()

    for i, speech_turns in enumerate(scene_speech_turns):

        for speech_turn in speech_turns:
            spk = speech_turn['speaker']
            duration = speech_turn['end'] - speech_turn['start']
                
            for interloc in speech_turn['interlocutors']:
                if not (spk == 'unknown' or interloc == 'unknown'): 
                    # initialize edge
                    if not G.has_edge(spk, interloc, key=i):
                        G.add_edge(spk, interloc, key=i, weight=0.0)

                    # update weight
                    prev_weight = G[spk][interloc][i]['weight']
                    G.add_edge(spk, interloc, key=i, weight=(prev_weight+duration))
                 
    return G


def _sigmoid(x, mu=0.01):
    """Evaluates the parameterized sigmoid function of x as 1 / (1 + exp(-mu * x))
    Args:
    x   (float): input number

    Returns:
    sig (float): sigmoid mapping
    """

    sig = 1 / (1 + np.exp(-mu * x))

    return round(sig, 4)


def narrative_smoothing(R, scene_mapping):
    """Interpolates the weight of every relation in each scene
    Args:
    R             (nx.MultiGraph): undirected, weighted multigraph of interaction time by scene
    scene_mapping (list):          episode id of each scene

    Returns:
    S             (nx.MultiGraph): undirected multigraph of interpolated interaction weight by scene
    """
    
    S = nx.MultiGraph()

    nodes = sorted(R.nodes)
    for i in range(len(nodes)):
        fSpk = nodes[i]
        for j in range(i+1, len(nodes)):
            sSpk = nodes[j]

            if R.has_edge(fSpk, sSpk):

                print('Processing: {} <-> {}'.format(fSpk, sSpk))
                
                edges = R[fSpk][sSpk]
                scene_indices = list(edges.keys())
                
                ###################################################
                # compute relation weight before first occurrence #
                ###################################################
                
                before_time = []
                for scene_idx in range(scene_indices[0]):
                    
                    # interaction time with other characters in current scene
                    fSpk_sep_time = np.sum([e[3] for e in R.edges(fSpk, data='weight', keys=True) if e[2] == scene_idx])
                    sSpk_sep_time = np.sum([e[3] for e in R.edges(sSpk, data='weight', keys=True) if e[2] == scene_idx])
                    before_time.append(fSpk_sep_time + sSpk_sep_time)

                before_time = np.array(before_time)

                # either character has interacted with others before the first occurrence of the relationship
                if np.any(before_time):
                    # first scene in which (at least) one of the two characters interacted with others
                    first_occ_idx = np.argmax(before_time > 0)
                    
                    # narrative anticipation on the next occurrence of the relation
                    cum_from_next = np.flip(np.cumsum(np.flip(before_time)))
                    narr_anticip = edges[scene_indices[0]]['weight'] - cum_from_next

                    # add edges
                    for scene_idx in range(first_occ_idx, scene_indices[0]):
                        S.add_edge(fSpk,
                                   sSpk,
                                   key=scene_idx,
                                   weight=_sigmoid(narr_anticip[scene_idx]),
                                   episode=scene_mapping[scene_idx])

                ###############################################################
                # compute relation weight between two consecutive occurrences #
                ###############################################################
                        
                for k in range(len(scene_indices)):

                    # index of last occurrence
                    last_idx = scene_indices[k]

                    # update graph
                    # last occurrence
                    S.add_edge(fSpk,
                               sSpk,
                               key=last_idx,
                               weight=_sigmoid(edges[last_idx]['weight']),
                               episode=scene_mapping[last_idx])

                    if k < len(scene_indices) - 1:
                        # index of next occurrence if any
                        next_idx = scene_indices[k+1]
                    
                        # interaction time with other characters in-between
                        sep_time = []
                    
                        for scene_idx in range(last_idx+1, next_idx):

                            # interaction time with other characters in current scene
                            fSpk_sep_time = np.sum([e[3] for e in R.edges(fSpk, data='weight', keys=True) if e[2] == scene_idx])
                            sSpk_sep_time = np.sum([e[3] for e in R.edges(sSpk, data='weight', keys=True) if e[2] == scene_idx])
                            sep_time.append(fSpk_sep_time + sSpk_sep_time)

                        cum_from_last = np.cumsum(sep_time)
                        cum_from_next = np.flip(np.cumsum(np.flip(sep_time)))

                        # narrative persistence of the last occurrence of the relation
                        narr_persist = edges[last_idx]['weight'] - cum_from_last

                        # narrative anticipation on the next occurrence of the relation
                        narr_anticip = edges[next_idx]['weight'] - cum_from_next

                        # weights of the relationship between the last and next occurrences
                        weights = np.max(np.array([narr_persist, narr_anticip]), axis=0)

                        # update graph
                        # between last and next occurrences
                        for i in np.arange(weights.shape[0]):
                            S.add_edge(fSpk,
                                       sSpk,
                                       key=last_idx+i+1,
                                       weight=_sigmoid(weights[i]),
                                       episode=scene_mapping[last_idx+i+1])

                        # next occurrence
                        S.add_edge(fSpk,
                                   sSpk,
                                   key=next_idx,
                                   weight=_sigmoid(edges[next_idx]['weight']),
                                   episode=scene_mapping[next_idx])

                #################################################
                # compute relation weight after last occurrence #
                #################################################

                after_time = []
                for scene_idx in range(scene_indices[-1] + 1, len(scene_mapping)):

                    # interaction time with other characters in current scene
                    fSpk_sep_time = np.sum([e[3] for e in R.edges(fSpk, data='weight', keys=True) if e[2] == scene_idx])
                    sSpk_sep_time = np.sum([e[3] for e in R.edges(sSpk, data='weight', keys=True) if e[2] == scene_idx])
                    after_time.append(fSpk_sep_time + sSpk_sep_time)

                after_time = np.array(after_time)

                # either character has interacted with others after the last occurrence of the relationship
                if np.any(after_time):
                    
                    # last scene in which (at least) one of the two characters interacted with others
                    last_occ_idx = after_time.shape[0] - np.argmax(np.flip(after_time) > 0) - 1

                    # narrative persistence of the last occurrence of the relation
                    cum_from_last = np.cumsum(after_time)
                    narr_persist = edges[scene_indices[-1]]['weight'] - cum_from_last

                    # add edges
                    for k in range(last_occ_idx + 1):
                        scene_idx = k + scene_indices[-1] + 1
                        S.add_edge(fSpk,
                                   sSpk,
                                   key=scene_idx,
                                   weight=_sigmoid(narr_persist[k]),
                                   episode=scene_mapping[scene_idx])

    return S


def export_to_graphml_format(G, path):
    """Writes out multigraph G to graphml format
    Args:
    H    (nx.MultiGraph): undirected multigraph of interpolated interaction weight by scene
    path (str)          : output file name

    Returns:
    None
    """

    nx.write_graphml(G, path)
    
