#!/usr/bin/python3
# -*- coding: utf-8 -*-

from utils import speech_turns_to_speaker_turns, speaker_turns_to_speech_turns


def _set_interlocs(speech_turns, interlocutors):
    """Assigns speech turns to some interlocutor
    Args:
    speech_turns  (list): speech turns
    interlocutors (list): list of hypothesized interlocutors
    
    Returns:
    speech_turns  (list): speech turns
    """

    for i in range(len(speech_turns)):
        # keep manual annotation if available; otherwise, use hypothesized interlocutors
        if not 'interlocutors' in speech_turns[i]:
            speech_turns[i]['interlocutors'] = interlocutors

    return speech_turns


def _same_surrounding_speaker(i, speaker_turns):
    """Tests if i-th speaker turn is surrounded by speaker turns originating in the same speaker
    Args:
    i             (int): index of the speaker turn to test
    speaker_turns (list): list of speaker turns

    Returns:
    same_speaker  (bool)
    """

    same_speaker = (speaker_turns[i-1][-1]['speaker'] == speaker_turns[i+1][0]['speaker'])

    return same_speaker


def sequential(scene_speech_turns, inter_threshold=5.0):
    """For each speech turn, estimates the interlocutors from the surrounding speakers
    Args:
    scene_speech_turns     (dict):  speech turns, as distributed over every scene
    inter_threshold        (float): maximum silence duration between verbal interactions

    Returns:
    new_scene_speech_turns (list):  speech turns, as distributed over every scene, with interlocutors
    """

    new_scene_speech_turns = []
    
    # loop over speech_turns
    for scene_id, speech_turns in scene_speech_turns.items():

        # merge consecutive speech turns originating in the same speaker
        speaker_turns = speech_turns_to_speaker_turns(speech_turns)
        
        if len(speaker_turns) > 1:
            for i in range(len(speaker_turns)):
                curr_speaker = speaker_turns[i][0]['speaker']
                curr_start = speaker_turns[i][0]['start']
                curr_end = speaker_turns[i][-1]['end']
                
                # rule (2a): |spk_1 -> spk_2
                if i == 0:
                    next_speaker = speaker_turns[i+1][0]['speaker']
                    next_start = speaker_turns[i+1][0]['start']

                    if (next_start - curr_end) <= inter_threshold:
                        speaker_turns[i] = _set_interlocs(speaker_turns[i], [next_speaker])
                    else:
                        speaker_turns[i] = _set_interlocs(speaker_turns[i], [])
                        
                # rule (2b): spk_1 <- spk_2|
                elif i == (len(speaker_turns)-1):
                    prev_speaker = speaker_turns[i-1][-1]['speaker']
                    prev_end = speaker_turns[i-1][-1]['end']

                    if (curr_start - prev_end) <= inter_threshold:
                        speaker_turns[i] = _set_interlocs(speaker_turns[i], [prev_speaker])
                    else:
                        speaker_turns[i] = _set_interlocs(speaker_turns[i], [])
                        
                # rule (1): spk_1 <- spk_2 -> spk_1
                elif _same_surrounding_speaker(i, speaker_turns):
                    prev_speaker = speaker_turns[i-1][-1]['speaker']
                    prev_end = speaker_turns[i-1][-1]['end']
                    next_start = speaker_turns[i+1][0]['start']

                    if (curr_start - prev_end) <= inter_threshold or (next_start - curr_end) <= inter_threshold:
                        speaker_turns[i] = _set_interlocs(speaker_turns[i], [prev_speaker])
                    else:
                        speaker_turns[i] = _set_interlocs(speaker_turns[i], [])
                        
                else:
                    prev_speaker = speaker_turns[i-1][-1]['speaker']
                    prev_end = speaker_turns[i-1][-1]['end']
                    next_speaker = speaker_turns[i+1][0]['speaker']
                    next_start = speaker_turns[i+1][0]['start']

                    # tests if current speaker was already speaking before the previous one
                    inter_prev_occ = (i >= 2 and _same_surrounding_speaker(i-1, speaker_turns))

                    # tests if current speaker will be speaking after the next one
                    inter_next_occ = (i < (len(speaker_turns) - 2) and _same_surrounding_speaker(i+1, speaker_turns))

                    # rule (3a): (spk_2) - spk_1 <- spk_2 - spk_3
                    if inter_prev_occ and not inter_next_occ:
                        if (curr_start - prev_end) <= inter_threshold:
                            speaker_turns[i] = _set_interlocs(speaker_turns[i], [prev_speaker])
                        else:
                            speaker_turns[i] = _set_interlocs(speaker_turns[i], [])

                    # rule (3b): spk_1 - spk_2 -> spk_3 - (spk_2)
                    elif not inter_prev_occ and inter_next_occ:
                        if (next_start - curr_end) <= inter_threshold:
                            speaker_turns[i] = _set_interlocs(speaker_turns[i], [next_speaker])
                        else:
                            speaker_turns[i] = _set_interlocs(speaker_turns[i], [])

                    # rule (4): (spk) - spk_1 <- spk_2 -> spk_3 - (spk)
                    else:
                        lim = (prev_end + next_start) / 2
                        
                        for j in range(len(speaker_turns[i])) :
                            speech_turn_pos = (speaker_turns[i][j]['start'] + speaker_turns[i][j]['end']) / 2
                            if speech_turn_pos <= lim:
                                if (curr_start - prev_end) <= inter_threshold:
                                    speaker_turns[i][j]['interlocutors'] = [prev_speaker]
                                else:
                                    speaker_turns[i][j]['interlocutors'] = []
                            elif speech_turn_pos > lim:
                                if (next_start - curr_end) <= inter_threshold:
                                    speaker_turns[i][j]['interlocutors'] = [next_speaker]
                                else:
                                    speaker_turns[i][j]['interlocutors'] = []

        else:
            for j in range(len(speaker_turns[0])):
                speaker_turns[0][j]['interlocutors'] = []

        # flatten speaker turns into speech turns and append
        new_scene_speech_turns.append(speaker_turns_to_speech_turns(speaker_turns))
        
    return new_scene_speech_turns
