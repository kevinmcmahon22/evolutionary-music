from midi2audio import FluidSynth

# use a custom sound font
fs = FluidSynth('FluidR3_GM.sf2')

fs.play_midi('bass.mid')

# using the default sound font in 44100 Hz sample rate
# fs.midi_to_audio('major-scale.mid', 'output.wav')

# FLAC, a lossless codec, is supported as well (and recommended to be used)
# fs.midi_to_audio('input.mid', 'output.flac')