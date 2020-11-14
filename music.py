#!/usr/bin/python

from mingus.containers import Track, Bar
from mingus.containers.instrument import MidiInstrument, Piano

# Output
import mingus.midi.midi_file_out as mfo
from midi2audio import FluidSynth
import mingus.extra.lilypond as lilypond
import mingus.extra.tablature as tab


midi_file = True
playback = True
sheet_music = True


i = MidiInstrument("Jazz Bass")
i.instrument_nr = 34
# i.clef = "bass"

# range('C-0', 'B-8')
# Use note_int_range(note) to see if random note can be added to melody
# Check notes when reduced to list notation after GP operations


t = Track(Piano())

# For each measure/chord in a progression

for i in range(2):
    b = Bar()

    b.place_notes("A-3", 4)
    b.place_notes("Bb-3", 4)
    b.place_notes("F#-3", 4)
    b.place_notes('G-3', 4)
    t.add_bar(b)

print(tab.from_Track(t))

# Write to midi file
if midi_file:
    mfo.write_Track("new.mid", t, bpm=220, repeat=0, verbose=True)

# Play midi file
if playback:
    fs = FluidSynth('FluidR3_GM.sf2')
    fs.play_midi('new.mid')

# fs.init("FluidR3_GM.sf2")
# fs.play_track(t, 1, 120)

# Generate sheet music
if sheet_music:
    bassline_pond = lilypond.from_Track(t)
    lilypond.to_png(bassline_pond, "best individual")