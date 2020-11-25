
import mingus.core.progressions as progressions
import mingus.core.notes as notes

class Progression:
    '''
    Defines a progression object
    '''

    def __init__(self, filename):

        # Get chord progression in roman numeral notation from text file
        fp = open(filename, 'r')
        self.BLUES_12 = []
        for line in fp:
            self.BLUES_12.extend(line.split())
        
        self.BLUES_PROG = progressions.to_chords(self.BLUES_12)
        self.BLUES_PROG_INT = self.chords_as_int()
        self.BLUES_NUM_BARS = len(self.BLUES_12)
        self.BASS_LEN = self.BLUES_NUM_BARS * 4 # number of bars * 4 quarter notes

    def chords_as_int(self):
        return [[notes.note_to_int(note) for note in chord] for chord in self.BLUES_PROG]
