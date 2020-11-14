# 
# Evolutionary Music in python
# 
# CSE 848 semester project
# 
# Kevin McMahon
# 
# 
# 
# Using mingus, Lilypond, FluidSynth, midi2audio
# 

from mingus.containers import Track, Bar
from mingus.containers.instrument import MidiInstrument, Piano
import mingus.midi.midi_file_out as mfo
from midi2audio import FluidSynth
import mingus.extra.lilypond as lilypond
import mingus.extra.tablature as tab

# Determine what output to produce
midi_file = True
playback = True
sheet_music = True
tablature = False


# Create instrument
i = MidiInstrument("Jazz Bass")
i.instrument_nr = 34

# Create track
t = Track(i)

# For each measure/chord in a progression
# Create a bar, add notes to bar
for i in range(2):
    b = Bar()


    # range('C-0', 'B-8')
    # Use note_int_range(note) to see if random note can be added to melody
    # Check notes when reduced to list notation after GP operations
    b.place_notes("A-3", 4)
    b.place_notes("Bb-3", 4)
    b.place_notes("F#-3", 4)
    b.place_notes('G-3', 4)
    t.add_bar(b)


# 
# OUTPUT
# 

# Write to midi file
if midi_file:
    mfo.write_Track("new.mid", t, bpm=220, repeat=0, verbose=True)

# Play midi file
if playback:
    fs = FluidSynth('FluidR3_GM.sf2')
    fs.play_midi('new.mid')

# Generate sheet music
if sheet_music:
    bassline_pond = lilypond.from_Track(t)
    lilypond.to_png(bassline_pond, "best individual")

# Write to tab if in correct range
if tablature:
    print(tab.from_Track(t))