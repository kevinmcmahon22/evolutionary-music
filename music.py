# 
# Evolutionary Music in python
# 
# CSE 848 semester project
# 
# Kevin McMahon
# 
# 
# 
# Using mingus, Lilypond, FluidSynth
# 

from mingus.containers import Track, Bar, Note, Composition
from mingus.containers.instrument import MidiInstrument, Piano
from mingus.midi import fluidsynth as fs

import mingus.core.progressions as progressions
import mingus.core.notes as notes
import mingus.core.scales as scales
import mingus.midi.midi_file_out as mfo
import mingus.extra.lilypond as lilypond
import mingus.extra.tablature as tab

import os

# Determine what output to produce
midi_file = False
playback = True
wav = False
sheet_music = False
tablature = False

BPM = 200

soundfont = 'FluidR3_GM.sf2'



BLUES_12 = ['I', 'IV', 'I', 'I', 'IV', 'IV', 'I', 'VI', 'II', 'V', 'I', 'V']

BLUES_PROG = progressions.to_chords(BLUES_12)



def get_int_chords():
    '''
    Convert chord tones of progression to integer for ease of use in evaluation    
    '''
    new_prog = []
    for chord in BLUES_PROG:
        chord_int = []
        for note in chord:
            note_int = notes.note_to_int(note)
            chord_int.append(note_int)
        new_prog.append(chord_int)
    return new_prog

BLUES_PROG_INT = get_int_chords()


# Variables for evaluating fitness
# Rated from 1-5 on how important they are

NON_REPEATED_NOTES = 3

NOTE_IN_CHORD = 2

NOTE_IN_SCALE = 1

LEADING_TONE = 2

ROOT = 5


def evaluate_baseline(individual):
    
    fitness = 0
        
    for note_index in range(len(individual)):
        
        next_note = -1 if note_index >= len(individual) - 1 else individual[note_index + 1]
        prev_note = -1 if note_index <= 0 else individual[note_index - 1]
        
        bar_num = note_index // 4
        beat_num = note_index % 4
        
        current_note = individual[note_index]
        
        # 1st note: root
        if beat_num == 0:

            # reward if note is in chord
            chord = BLUES_PROG_INT[bar_num]
            if current_note % 12 in chord:
                
                fitness += NOTE_IN_CHORD   
                
            # bonus if note is root of chord
            root = chord[0]
            if current_note % 12 == root:
                
                fitness += ROOT
        
        # 2nd note: any note of chord/scale
        elif beat_num == 1:
            
            # reward if note is in chord
            chord = BLUES_PROG_INT[bar_num]
            if current_note % 12 in chord:
                
                fitness += NOTE_IN_CHORD
                
        
        # 3rd note: same as two, new note
        elif beat_num == 2:
            
            # reward if note is in chord
            chord = BLUES_PROG_INT[bar_num]
            if current_note % 12 in chord:
                
                fitness += NOTE_IN_CHORD
        
        # 4th note: leading tone to next root
        elif beat_num == 3:
            
            # check if interval to next note is half, whole, or fourth/dominant
            half = abs(current_note - next_note) == 1
            whole = abs(current_note - next_note) == 2
            dominant = abs(current_note - next_note) == 5
            
            if half or whole or dominant:
                
                fitness += LEADING_TONE
        
        # reward if two adjacent notes are different
        if prev_note > 0 and next_note > 0:
            if current_note != prev_note:
                fitness += NON_REPEATED_NOTES
            if current_note != next_note:
                fitness += NON_REPEATED_NOTES
            if prev_note != next_note:
                fitness += NON_REPEATED_NOTES
                
        
        # Check if current note fits in current chord
        root = BLUES_PROG_INT[bar_num][0]
        root_note = Note().from_int(root)
        scale = scales.Diatonic(root_note.name, (3, 7))
        
        # print(scale.ascending())
        
        if Note().from_int(current_note).name in scale.ascending():
            
            fitness += NOTE_IN_SCALE
        # get scale from 
        
        # # Reward if current note is between previous and next
        # if prev_note > 0 and next_note > 0:
        #     # up
        #     if current_note > prev_note and current_note < next_note:
        #         fitness += 10
        
        #     # down
        #     if current_note < prev_note and current_note > next_note:
        #         fitness += 10
        
    return fitness


def Jazz_Bass():
    jazz_bass = MidiInstrument("Jazz Bass")
    jazz_bass.instrument_nr = 34
    return jazz_bass

def generate_midi_track(bassline, instrument, transpose_halfsteps = 0):

    # Create MIDI track
    track = Track(instrument)
    
    # Fill track
    b = Bar()
    for note in bassline:
        # may change duration to second part of tuple for triplets/eighths
        b.place_notes(Note().from_int(note + transpose_halfsteps), 4)
        
        # Create new bar if previous bar full
        if b.is_full():
            track.add_bar(b)
            b = Bar()
    
    return track


def play_baseline(bassline):

    # Create MIDI track for chord progression    
    piano = Piano()
    t_prog = Track(piano)

    for chord in BLUES_PROG:
        b = Bar()
        b.place_notes(chord, 1)
        t_prog.add_bar(b)

    # create midi track for bassline

    t_bass = generate_midi_track(bassline, Jazz_Bass())

    # Create composition to hold tracks
    c = Composition()
    c.set_author('Kevin', 'email')
    c.set_title('Evolved bassline')

    c.add_track(t_bass)
    # c.add_track(t_prog)
    
    # play composition
    fs.init(soundfont)
    fs.play_Composition(c, None, BPM)
    
    
def generate_score(bassline, filename):
    # transpose an octave so bassline appears nicely on staff
    bass_track = generate_midi_track(bassline, Piano(), 24)
    bassline_pond = lilypond.from_Track(bass_track)
    lilypond.to_png(bassline_pond, filename)
    
    
    
def main():
    
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
    
    filename = 'new'
    midi_filename = filename + '.mid'
    
    # Write to midi file
    if midi_file:
        mfo.write_Track(midi_filename, t, bpm=BPM, repeat=0, verbose=True)
    
    # Play midi file
    if playback:
        fs.init(soundfont)
        fs.play_Track(t, 1, BPM)
    
    # Make wav file from .mid
    if wav:
        os.system(f'fluidsynth -F {filename}.wav {soundfont} {midi_filename}')
    
    # Generate sheet music
    if sheet_music:
        bassline_pond = lilypond.from_Track(t)
        lilypond.to_png(bassline_pond, filename)
    
    # Write to ASCII tab if notes in guitar range
    if tablature:
        print(tab.from_Track(t))