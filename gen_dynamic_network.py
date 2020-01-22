#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import json

import estimate_interactions
import network_processing

from utils import assign_speech_turns_to_scenes


def gen_dynamic_network(input_annot_fname, output_graph_fname):
    """Generates a dynamic network of interacting speakers within TV serials

    References:
    X. Bost, V. Labatut, S. Gueye, G. Linarès, Extraction and Analysis of Dynamic Conversational Networks from TV Series, Springer, Social Network Based Big Data Analysis and Applications, 2018
    X. Bost, V. Labatut, S. Gueye, G. Linarès, Narrative Smoothing: Dynamic Conversational Network for the Analysis of TV Series Plots, ASONAM/DyNo 2016
    
    Args:
    input_annot_fname  (str):           input annotation file
    output_graph_fname (str):           output graph file

    Returns:
    S                  (nx.MultiGraph): dynamic network of interacting speakers
    """

    all_speech_turns = [] # speech turns gathered by scenes
    scene_mapping = []    # mapping between scenes and episode ids
    
    # expand input paths
    input_annot_fname = os.path.expanduser(input_annot_fname)
    output_graph_fname = os.path.expanduser(output_graph_fname)

    # load annotations as dict
    annotations = json.load(open(input_annot_fname))

    # loop over episodes
    seasons = annotations['seasons']
    for i, season in enumerate(seasons):
        episodes = season['episodes']
        for j, episode in enumerate(episodes):
            
            scenes = episode['data']['scenes']
            speech_turns = episode['data']['speech_segments']
            episode_duration = episode['duration']
            episode_id = 'S{:02d}E{:02d}'.format(i+1, j+1)
            
            # assign speech turns to scenes
            scene_speech_turns = assign_speech_turns_to_scenes(scenes, speech_turns, episode_duration)
            
            # estimate the interlocutors from the sequence of speech turns
            scene_speech_turns = estimate_interactions.sequential(scene_speech_turns)
            
            # record episode id
            scene_mapping += [episode_id for k in range(len(scene_speech_turns))]

            # append speech turns
            all_speech_turns += scene_speech_turns
    
    # dynamic network of raw interaction time
    R = network_processing.build_interaction_network(all_speech_turns)

    # dynamic network of interpolated/smoothed interaction weight
    S = network_processing.narrative_smoothing(R, scene_mapping)
    
    network_processing.export_to_graphml_format(S, output_graph_fname)
                     
    return S


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_annot_fname',
                        type=str,
                        help='Annotation file name.',
                        required=True)

    parser.add_argument('--output_graph_fname',
                        type=str,
                        help='Output graph file name (.graphml extension expected).',
                        required=True)

    return parser.parse_args(argv)


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    gen_dynamic_network(args.input_annot_fname, args.output_graph_fname)
