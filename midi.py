#!/usr/bin/env python

# MIDIUtil


from midiutil import MIDIFile

# Pitches based on equal temperment scale

channel  = 13    # instrument
track    = 0    # streams of notes for an instrument
time     = 0    # In beats
duration = 1    # In beats
tempo    = 100   # In BPM
volume   = 100  # 0-127, as per the MIDI standard

midi = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
midi.addTempo(track, time, tempo)
midi.addTempo(track, 2, 120)

# C0 = 24, base chord patterns off of that

# list of tuples
notes = []

# swing eigths
for i in range(8):
    note = (track, channel, 30+i, time+i, 0.667, volume)
    notes.append(note)
    note = (track, channel, 30+i+5, time+i+0.667, 0.333, volume)
    notes.append(note)


for note in notes:
    midi.addNote(note[0], note[1], note[2], note[3], note[4], note[5])

# Minor 7th
# midi.addNote(0, 1, 35, 1, 4, volume)
# midi.addNote(0, 1, 38, 2, 3, volume)
# midi.addNote(0, 1, 42, 3, 2, volume)
# midi.addNote(0, 1, 45, 4, 1, volume)



with open("bass.mid", "wb") as output_file:
    midi.writeFile(output_file)