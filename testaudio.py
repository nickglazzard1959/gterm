###################
# AudioFile CLASS #
#  For a "bell"!  #
###################

import pyaudio
import wave
import time

class AudioFile:
    """
    Play a WAV format audio file with PyAudio.
    For whatever reason, QSound does not work on Ubuntu Linux.
    This works, albeit with stupid messages (not easily silenced). Sound is still a mess. 
    Thanks to 'Mihail' of Nizhegorodskaya Oblast, Russia for this example code.
    """
    chunk = 1024
    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        print('frame length =',len(data))
        while len(data) > 0:
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """
        time.sleep(0.2)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
def make_noise(wavfile):
    """Make an arbitrary sound by playing a specified WAV file."""
    print('make_noise() BUT NOT.')
    #xsxsreturn
    a = AudioFile(wavfile)
    a.play()
    a.close()

if __name__ == "__main__":
    make_noise('kling.wav')
    make_noise('beep-3.wav')
    
    
