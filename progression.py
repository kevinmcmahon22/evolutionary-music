
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

        # First line of text file will always be song name
        self.SONG_TITLE = fp.readline().strip()

        # Read in chords from file
        for line in fp:
            if line[0] != '#':
                self.BLUES_12.extend(line.split())

        # Format input for use by GA
        self.BLUES_PROG = progressions.to_chords(self.BLUES_12)
        self.BLUES_PROG_INT = self.chords_as_int()
        self.BLUES_NUM_BARS = len(self.BLUES_12)
        self.BASS_LEN = self.BLUES_NUM_BARS * 4 # number of bars * 4 quarter notes

    def chords_as_int(self):
        return [[notes.note_to_int(note) for note in chord] for chord in self.BLUES_PROG]

    def print_progression(self):
        print(self.BLUES_PROG)
