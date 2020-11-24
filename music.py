# 
# Evolutionary Music in Python
# 
# CSE 848 semester project
# 
# Kevin McMahon
# 
# define Bassline class that handles all musical operations in GA
# 
# Using mingus, Lilypond, FluidSynth
# 

from mingus.containers import Track, Bar, Note, Composition
from mingus.containers.instrument import MidiInstrument, Piano, Guitar
from mingus.midi import fluidsynth as fs

import mingus.core.progressions as progressions
import mingus.core.notes as notes
import mingus.core.scales as scales
import mingus.midi.midi_file_out as mfo
import mingus.extra.lilypond as lilypond
import mingus.extra.tablature as tab

import os



# range('C-0', 'B-8')
# Use note_int_range(note) to see if random note can be added to melody


class Bassline:
    
    
    BPM = 200
    soundfont = 'FluidR3_GM.sf2'
    
    # Evaluation metrics
    NON_REPEATED_NOTES = 4
    NOTE_IN_CHORD = 3
    NOTE_IN_SCALE = 1
    LEADING_TONE = 2
    ROOT = 5
    
    
    def __init__(self, prog):
        
        self.BLUES_12 = ['I', 'IV', 'I', 'I', 'IV', 'IV', 'I', 'VI', 'II', 'V', 'I', 'V']
        self.BLUES_PROG = progressions.to_chords(self.BLUES_12)
        self.BLUES_PROG_INT = self.get_int_chords()
        
        
    def get_int_chords(self):
        '''
        Convert chord tones of progression to integer for ease of use in evaluation    
        '''
        new_prog = []
        for chord in self.BLUES_PROG:
            chord_int = []
            for note in chord:
                note_int = notes.note_to_int(note)
                chord_int.append(note_int)
            new_prog.append(chord_int)
        return new_prog


    def evaluate_baseline(self, individual):
        
        fitness = 0
            
        for note_index in range(len(individual)):
            
            next_note = individual[0] if note_index >= len(individual) - 1 else individual[note_index + 1]
            prev_note = individual[len(individual)-1] if note_index <= 0 else individual[note_index - 1]
            
            bar_num = note_index // 4
            beat_num = note_index % 4
            
            current_note = individual[note_index]
            
            # 1st note: root
            if beat_num == 0:
    
                # reward if note is in chord
                chord = self.BLUES_PROG_INT[bar_num]
                if current_note % 12 in chord:
                    
                    fitness += self.NOTE_IN_CHORD   
                    
                # bonus if note is root of chord
                root = chord[0]
                if current_note % 12 == root:
                    
                    fitness += self.ROOT
            
            # 2nd note: any note of chord/scale
            elif beat_num == 1:
                
                # reward if note is in chord
                chord = self.BLUES_PROG_INT[bar_num]
                if current_note % 12 in chord:
                    
                    fitness += self.NOTE_IN_CHORD
                    
            
            # 3rd note: same as two, new note
            elif beat_num == 2:
                
                # reward if note is in chord
                chord = self.BLUES_PROG_INT[bar_num]
                if current_note % 12 in chord:
                    
                    fitness += self.NOTE_IN_CHORD
            
            # 4th note: leading tone to next root
            elif beat_num == 3:
                
                # check if interval to next note is half, whole, or fourth/dominant
                half = abs(current_note - next_note) == 1
                whole = abs(current_note - next_note) == 2
                dominant = abs(current_note - next_note) == 5
                
                if half or whole or dominant:
                    
                    fitness += self.LEADING_TONE
            
            # reward if two adjacent notes are different
            if current_note != prev_note:
                fitness += self.NON_REPEATED_NOTES
                
            if current_note != next_note:
                fitness += self.NON_REPEATED_NOTES
                
            if prev_note != next_note:
                fitness += self.NON_REPEATED_NOTES
                
            
            # Check if current note fits in current chord
            root = self.BLUES_PROG_INT[bar_num][0]
            root_note = Note().from_int(root)
            scale = scales.Diatonic(root_note.name, (3, 7)).ascending()
            
            if Note().from_int(current_note).name in scale:
                
                fitness += self.NOTE_IN_SCALE
                
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
    
    
    def JazzBass():
        jazz_bass = MidiInstrument("Jazz Bass")
        jazz_bass.instrument_nr = 34
        return jazz_bass
    
    
    def generate_midi_track(midi_list, instrument, transpose_halfsteps = 0):
    
        # Create MIDI track
        track = Track(instrument)
        
        # Fill track with notes
        b = Bar()
        for tup in midi_list:
            b.place_notes(Note().from_int(tup[0] + transpose_halfsteps), tup[1])
            if b.is_full():
                track.add_bar(b)
                b = Bar()
        
        return track
    
    
    def create_midi_file(midi_filename, track, BPM):
        # Don't include .mid in filename
        mfo.write_Track(midi_filename, track, bpm=BPM, repeat=0, verbose=True)
        
        
    def create_wav_file(self, wav_filename, track, BPM):
        # Create MIDI AND wav file with given filename
        # Don't include .wav in filename
        self.create_midi_file(wav_filename, track, BPM)
        os.system(f'fluidsynth -F {wav_filename}.wav {self.soundfont} {wav_filename}.mid')
    
    
    def play_baseline(self, bassline):
    
        # Create data structures holding MIDI notes with duration
        notes_piano = []
        for chord in self.BLUES_PROG:
            notes_piano.append((chord, 1))
            
        notes_bass = []
        for note in bassline:
            notes_bass.append((note, 4))
            
        # Generate midi tracks for piano and bass
        t_piano = self.generate_midi_track(notes_piano, Piano())
        t_bass = self.generate_midi_track(notes_bass, self.JazzBass())
    
        # Add tracks to a composition
        c = Composition()
        c.set_author('Kevin', 'email')
        c.set_title('Evolved bassline')
        c.add_track(t_bass)
        c.add_track(t_piano)
        
        # Create MIDI file of composition
        midi_filename = 'goat.mid'
        self.create_midi_file(midi_filename, c, self.BPM)
        
        # play composition
        fs.init(self.soundfont)
        fs.play_Composition(c, None, self.BPM)
        
        
    def generate_score(self, bassline, filename):
        # transpose 2 octaves so bassline appears nicely on staff
        bass_track = self.generate_midi_track(bassline, Piano(), 24)
        bassline_pond = lilypond.from_Track(bass_track)
        lilypond.to_png(bassline_pond, filename)
        
        
    def print_tab(self, bassline):
        # Write to ASCII tab if all notes are in guitar range
        t_bass = self.generate_midi_track(bassline, Guitar(), 12)
        print(tab.from_Track(t_bass))
