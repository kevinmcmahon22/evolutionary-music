
from mingus.containers import Track, Bar, Note, Composition
from mingus.containers.instrument import MidiInstrument
from mingus.midi import fluidsynth as fs
import mingus.core.scales as scales
import mingus.midi.midi_file_out as mfo
import mingus.extra.lilypond as lilypond
import mingus.extra.tablature as tab
import random
import os



'''
Initialization
'''

# MIDI note values
MIN_NOTE = 24 # C0
MAX_NOTE = 47 # B1
INIT_NOTE = 36 # middle of playable range
INIT_RANGE = 5 # interval to allow initialized notes

def random_note():
    # return random.randint(MIN_NOTE, MAX_NOTE)
    # return INIT_NOTE
    return random.randint(INIT_NOTE-INIT_RANGE, INIT_NOTE+INIT_RANGE)


'''
Mutation
'''

# Mutations stpes to be used - half, whole, m3, M3, 4, 5
MUT_STEPS = [-1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -7, 7]

# prob of mutating any given note
P_MUT_NOTE = 0.05

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

            if note_index > 0 and note_index < changes.BASS_LEN - 1:
                next_note = bassline[note_index + 1]
                prev_note = bassline[note_index - 1]
                curr_note = bassline[note_index]

                # interval between next and current note is too large
                new_jump = abs(curr_note - next_note)
                if new_jump > 7 or new_jump == 6:
                    bassline[note_index] -= interval
                    continue
                    
                # interval between previous and current note is too large
                new_jump = abs(curr_note - prev_note)
                if new_jump > 7 or new_jump == 6:
                    bassline[note_index] -= interval
                    continue 
                    
                # new note identical to next or previous note
                if next_note == prev_note or next_note == curr_note:
                    bassline[note_index] -= interval
                    continue

                # new note doesn't create a rising/falling line, ignore with 1% probability
                # if (curr_note < prev_note and curr_note < next_note) or (curr_note > prev_note and curr_note > next_note):
                #     if random.random() < 0.01:
                #         bassline[note_index] -= interval
                #         continue
                            
            # Add in eighths and triplets when quarters down solid
            # Increment BASS_LEN if add/remove eighths

    return bassline


'''
Evaluation
'''

# Evaluation metrics
NON_REPEATED_NOTES = 1
NOTE_IN_CHORD = 3
NOTE_IN_SCALE = 4
NOTE_NOT_IN_SCALE = -5
LEADING_TONE = 2
FIRST_NOTE_ROOT = 6
WALKING_PATTERN = 5

def evaluate_bassline(bassline, changes):
    '''
    Basic bassline evaluation

    1. play root
    2. play any note of chord/scale
    3. play any note, new note
    4. leading tone: half, whole, fifth

    additions:
        reward if current note is in chord analogous to current scale
        reward if two adjacent notes are not repeating
        reward for musical line moving up/down, aka "walking" bassline
    '''
    
    fitness = 0
        
    for note_index in range(len(bassline)):
        
        current_note = bassline[note_index]
        next_note = bassline[0] if note_index >= changes.BASS_LEN - 1 else bassline[note_index + 1]
        prev_note = bassline[changes.BASS_LEN-1] if note_index <= 0 else bassline[note_index - 1]

        bar_num = note_index // 4
        beat_num = note_index % 4
        
        # 1st note: root
        if beat_num == 0:

            # reward if note is in chord
            chord = changes.BLUES_PROG_INT[bar_num]
            if current_note % 12 in chord:
                
                fitness += NOTE_IN_CHORD   
                
            # bonus if note is root of chord
            root = chord[0]
            if current_note % 12 == root:
                
                fitness += FIRST_NOTE_ROOT
        
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

        # Check if current note fits in current chord
        root = changes.BLUES_PROG_INT[bar_num][0]
        root_note = Note().from_int(root)
        scale = scales.Diatonic(root_note.name, (3, 7)).ascending()
        
        if Note().from_int(current_note).name in scale:
            
            fitness += NOTE_IN_SCALE

        else:

            fitness += NOTE_NOT_IN_SCALE
        
        # reward if two adjacent notes are different
        if current_note != prev_note:
            fitness += NON_REPEATED_NOTES
            
        if current_note != next_note:
            fitness += NON_REPEATED_NOTES
            
        if prev_note != next_note:
            fitness += NON_REPEATED_NOTES
        
        # reward for an upwards or downwards "walking" pattern
        if current_note > prev_note and current_note < next_note:
            fitness += WALKING_PATTERN
    
        if current_note < prev_note and current_note > next_note:
            fitness += WALKING_PATTERN
        
    return fitness,


'''
Output helper methods
'''

def generate_track(midi_list, instrument, notes_are_int = True, transpose = 0):
    '''
    midi_list should be list of tuple(int note_value, int_duration)
    works for single int and list of strings (note names)
    '''

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
    jazz_bass.instrument_nr = 38
    return jazz_bass

def Accompaniment():
    acc = MidiInstrument("Accompaniment")
    acc.instrument_nr = 38
    return acc
    

'''
Callable output methods
'''

# Variables for MIDI output
BPM = 220
soundfont = 'FluidR3_GM.sf2'

def generate_composition(bassline, changes, transpose=0):
    # Create data structures holding MIDI notes with duration
    notes_acc = []
    for chord in changes.BLUES_PROG:
        notes_acc.append((chord, 1))
        
    notes_bass = []
    for note in bassline:
        # change to a list of tups for representation if use eighths/triplets
        notes_bass.append((note, 4))
        
    # Generate midi tracks for piano and bass
    t_acc = generate_track(notes_acc, Accompaniment(), notes_are_int=False)
    t_bass = generate_track(notes_bass, JazzBass(), transpose=transpose)

    # Add tracks to a composition
    c = Composition()
    c.set_author('Kevin')
    c.set_title(f'{changes.SONG_TITLE} Evolved Bassline')
    c.add_track(t_bass)
    c.add_track(t_acc)

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

def create_midi_file(midi_filename, c):
    mfo.write_Composition(f'{midi_filename}.mid', c, bpm=BPM, repeat=0, verbose=True)

def create_wav_file(wav_filename, c):
    create_midi_file(wav_filename, c)
    os.system(f'fluidsynth -F {wav_filename}.wav {soundfont} {wav_filename}.mid')
    
# def print_tab(bassline):
#     # Write to ASCII tab if all notes are in guitar range
#     t_bass = generate_midi_track(bassline, Guitar(), 12)
#     print(tab.from_Track(t_bass))
