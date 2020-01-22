#!/usr/bin/python3
# -*- coding: utf-8 -*-


def assign_speech_turns_to_scenes(scenes, speech_turns, duration):
    """Assigns every speech turn to the most overlapping scene
    Args:
    scenes             (list): scenes, defined by starting points
    speech_turns       (list): speech turns, defined by starting and ending points

    Returns:
    scene_speech_turns (dict): speech turns, as distributed over every scene
    """

    scene_speech_turns = {}
    
    # add (exclusive) scene ending points
    for i in range(len(scenes)-1):
        scenes[i]['end'] = scenes[i+1]['start']
    scenes[-1]['end'] = duration

    # assign each speech segment to a scene
    i = j = 0
    scene_speech_turns[0] = []
    
    while i < len(scenes) and j < len(speech_turns):
        scene_start = scenes[i]['start']
        scene_end = scenes[i]['end']
        seg_start = speech_turns[j]['start']
        seg_end = speech_turns[j]['end']

        if (scene_end - seg_start) > (seg_end - seg_start) / 2:
            scene_speech_turns[i].append(speech_turns[j])
            j += 1
        else:
            i += 1
            scene_speech_turns[i] = []

    # process possible extra scenes
    for idx in range(i+1, len(scenes)):
        scene_speech_turns[idx] = []
    
    return scene_speech_turns


def speech_turns_to_speaker_turns(speech_turns):
    """Merges speech turns into speaker turns
    Args:
    speech_turns  (list): list of speech turns

    Returns:
    speaker turns (list): list of list of speech turns, gathered by speaker
    """

    speaker_turns = []
    
    prev_speaker = ''
    prev_speaker_turn = []
    
    for speech_turn in speech_turns:
        curr_speaker = speech_turn['speaker']
        if not (prev_speaker == '' or curr_speaker == prev_speaker):
            speaker_turns.append(prev_speaker_turn)
            prev_speaker_turn = []
        prev_speaker_turn.append(speech_turn)
        prev_speaker = curr_speaker

    # last speaker turn
    speaker_turns.append(prev_speaker_turn)
        
    return speaker_turns


def speaker_turns_to_speech_turns(speaker_turns):
    """Flattens speaker turns into speech turns
    Args:
    speaker turns (list): list of list of speech turns, gathered by speaker

    Returns:
    speech_turns  (list): list of speech turns
    """

    speech_turns = []

    for speaker_speech_turns in speaker_turns:
        speech_turns += speaker_speech_turns

    return speech_turns
