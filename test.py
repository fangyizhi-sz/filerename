import soundfile as sf
f = sf.SoundFile(r'G:\G\VPstage\个人\XuHaoJian\aa\11\Audio\250624-T013.WAV')
print(f)
print('samples = {}'.format(len(f)))
print('sample rate = {}'.format(f.samplerate))
print('seconds = {}'.format(len(f) / f.samplerate))

