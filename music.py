
from mingus.containers import Track, Bar, Note, Composition
from mingus.containers.instrument import MidiInstrument, Piano, Guitar
from mingus.midi import fluidsynth as fs
import mingus.core.scales as scales
import mingus.midi.midi_file_out as mfo
import mingus.extra.lilypond as lilypond
import mingus.extra.tablature as tab
import random
import os


'''
Handle musical operations for GA
'''


# Vars for MIDI output
BPM = 200
soundfont = 'FluidR3_GM.sf2'

# Evaluation metrics
NON_REPEATED_NOTES = 4
NOTE_IN_CHORD = 3
NOTE_IN_SCALE = 1
LEADING_TONE = 2
ROOT = 5

# Mutations stpes to be used - half, whole, m3, M3, 4, 5
MUT_STEPS = [-1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -7, 7]

# prob of mutating any given note
P_MUT_NOTE = 0.05

# MIDI note values
MIN_NOTE = 24 # C0
MAX_NOTE = 47 # B1


'''
Initialization
'''

def random_note():
    return random.randint(MIN_NOTE, MAX_NOTE)


'''
Mutation
'''

# def stepwise(self, note_index, interval):
    
#     original_note = bassline[note_index]

#     bassline[note_index] += interval  
    
#     # if note is out of playable range, then keep original note
#     if bassline[note_index] < MIN_NOTE or bassline[note_index] > MAX_NOTE:
#         bassline[note_index] = original_note

# def quarter_to_triplets(bassline, note_index):
#     pass

# def quarter_to_eighths(bassline, note_index):
#     pass

def mutate_bassline(bassline, changes):

    for note_index in range(changes.BASS_LEN):
        if random.random() < P_MUT_NOTE:

            # Mutate note
            interval = random.choice(MUT_STEPS)
            bassline[note_index] += interval

            # 
            # MODIFIERS: reset note to original value if any of below conditions met
            # 

            # new note out of playable range
            if bassline[note_index] < MIN_NOTE or bassline[note_index] > MAX_NOTE:
                bassline[note_index] -= interval
                continue
            
            # interval between mutated and next/previous note that is larger than a fifth or a tritone
            if note_index > 0:
                new_jump = abs(bassline[note_index] - bassline[note_index - 1])
                if new_jump > 7 or new_jump == 6:
                    bassline[note_index] -= interval
                    continue
            if note_index < changes.BASS_LEN - 1:
                new_jump = abs(bassline[note_index] - bassline[note_index + 1])
                if new_jump > 7 or new_jump == 6:
                    bassline[note_index] -= interval
                    continue

            if note_index > 0 and note_index < changes.BASS_LEN - 1:            
                next_note = bassline[note_index + 1]
                prev_note = bassline[note_index - 1]
                curr_note = bassline[note_index]
                
                # new note doesn't create a rising/falling line, ignore with 1% probability
                if (curr_note < prev_note and curr_note < next_note) or (curr_note > prev_note and curr_note > next_note):
                    if random.random() < 0.01:
                        bassline[note_index] -= interval
                        continue
                    
                # new note identical to next or previous note
                if next_note == prev_note or next_note == curr_note:
                    bassline[note_index] -= interval
                    continue
                            
            # Add in eighths and triplets when quarters down solid
            # Increment BASS_LEN if add/remove eighths

    return bassline


'''
Evaluation
'''

def evaluate_bassline(bassline, changes):
    '''
    Basic bassline evaluation

    1. play root
    2. play any note of chord/scale
    3. play any note, new note
    4. leading tone: half, whole, fifth

    additions:
        check if each note is in chord represented by scale
        reward if two adjacent notes are not repeating

    potential:
        reward for moving up/down in linear patterns
    '''
    
    fitness = 0
        
    for note_index in range(len(bassline)):
        
        next_note = bassline[0] if note_index >= changes.BASS_LEN - 1 else bassline[note_index + 1]
        prev_note = bassline[changes.BASS_LEN-1] if note_index <= 0 else bassline[note_index - 1]
        
        bar_num = note_index // 4
        beat_num = note_index % 4
        
        current_note = bassline[note_index]
        
        # 1st note: root
        if beat_num == 0:

            # reward if note is in chord
            chord = changes.BLUES_PROG_INT[bar_num]
            if current_note % 12 in chord:
                
                fitness += NOTE_IN_CHORD   
                
            # bonus if note is root of chord
            root = chord[0]
            if current_note % 12 == root:
                
                fitness += ROOT
        
        # 2nd note: any note of chord/scale
        elif beat_num == 1:
            
            # reward if note is in chord
            chord = changes.BLUES_PROG_INT[bar_num]
            if current_note % 12 in chord:
                
                fitness += NOTE_IN_CHORD
                
        
        # 3rd note: same as two, new note
        elif beat_num == 2:
            
            # reward if note is in chord
            chord = changes.BLUES_PROG_INT[bar_num]
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
        if current_note != prev_note:
            fitness += NON_REPEATED_NOTES
            
        if current_note != next_note:
            fitness += NON_REPEATED_NOTES
            
        if prev_note != next_note:
            fitness += NON_REPEATED_NOTES
            
        
        # Check if current note fits in current chord
        root = changes.BLUES_PROG_INT[bar_num][0]
        root_note = Note().from_int(root)
        scale = scales.Diatonic(root_note.name, (3, 7)).ascending()
        
        if Note().from_int(current_note).name in scale:
            
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
        
    return fitness,


'''
Output helper methods
'''

def generate_track(midi_list, instrument, notes_are_int = True, transpose = 0):
    # midi_list should be list of tuple(int note_value, int_duration)
    # works for single int and list of strings (note names)

    # Create MIDI track
    track = Track(instrument)
    
    # Fill track with notes
    b = Bar()
    for tup in midi_list:
        note = tup[0]
        duration = tup[1]
        if notes_are_int:
            note = Note().from_int(tup[0]+transpose)
        b.place_notes(note, duration)
        if b.is_full():
            track.add_bar(b)
            b = Bar()
    return track

def JazzBass():
    jazz_bass = MidiInstrument("Jazz Bass")
    jazz_bass.instrument_nr = 34
    return jazz_bass


'''
Callable output methods
'''

def generate_composition(bassline, changes, transpose=0):
    # Create data structures holding MIDI notes with duration
    notes_piano = []
    for chord in changes.BLUES_PROG:
        notes_piano.append((chord, 1))
        
    notes_bass = []
    for note in bassline:
        # change to a list of tups for representation if use eighths/triplets
        notes_bass.append((note, 4))
        
    # Generate midi tracks for piano and bass
    t_piano = generate_track(notes_piano, Piano(), notes_are_int=False)
    t_bass = generate_track(notes_bass, JazzBass(), transpose=transpose)

    # Add tracks to a composition
    c = Composition()
    c.set_author('Kevin', 'email')
    c.set_title('Evolved bassline')
    c.add_track(t_bass)
    c.add_track(t_piano)
    
    return c

def play_composition(c):
    fs.init(soundfont)
    fs.play_Composition(c, None, BPM)

def generate_score(c, filename):
    bassline_pond = lilypond.from_Composition(c)
    lilypond.to_png(bassline_pond, filename)
    
'''
File creation
'''

def create_midi_file(midi_filename, c, BPM):
    mfo.write_Composition(midi_filename, c, bpm=BPM, repeat=0, verbose=True)

def create_wav_file(wav_filename, track, BPM):
    create_midi_file(wav_filename, track, BPM)
    os.system(f'fluidsynth -F {wav_filename}.wav {soundfont} {wav_filename}.mid')
    
# def print_tab(bassline):
#     # Write to ASCII tab if all notes are in guitar range
#     t_bass = generate_midi_track(bassline, Guitar(), 12)
#     print(tab.from_Track(t_bass))
