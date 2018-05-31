import numpy
import pylab
import scipy.signal
import sounddevice


SAMPLERATE = 44100
FFTSIZE = 32768
FRES = SAMPLERATE / FFTSIZE
OVERLAP = int(SAMPLERATE / 10)
MAG_THRESH = 70


class tuner:
    def __init__(self):
        self.main_array = numpy.zeros(FFTSIZE)
        self.samplerate = SAMPLERATE
        self.framecount = 0
        self.window = scipy.signal.get_window('blackman', FFTSIZE)
        self.screencap = True

    def add_samples(self, indata, frames):
        if frames > OVERLAP:
            for i in range(int(frames / OVERLAP)):
                self.main_array = numpy.append(self.main_array, indata[:OVERLAP])[OVERLAP:]
                indata = indata[OVERLAP:]
                self.find_note()
        frames = frames % OVERLAP
        if self.framecount + frames >= OVERLAP:
            cutoff_index = OVERLAP - self.framecount
            self.main_array = numpy.append(self.main_array, indata[:cutoff_index])[cutoff_index:]
            temp_array = indata[cutoff_index:]
            self.find_note()
            self.main_array = numpy.append(self.main_array, temp_array)[len(temp_array):]
            self.framecount = len(temp_array)
        else:
            self.main_array = numpy.append(self.main_array, indata)[frames:]
            self.framecount += frames

    def find_note(self):
        x = self.main_array * self.window
        X = numpy.fft.fft(x)
        mag_spectrum = abs(X)[:int(len(X) / 2)]
        freq = mag_spectrum.argmax() * FRES
        if (mag_spectrum.argmax() < MAG_THRESH):
            print('N/A')
        else:
            print(mag_spectrum.argmax(), freq)
        if 100 < freq < 120 and self.screencap:
            pylab.plot(mag_spectrum)
            pylab.axis([0, 300, 0, 100])
            pylab.savefig('f0.png')
            self.screencap = False


def callback(indata, frames, time, status):
    if status:
        print(status)
    if indata.any():
        GuitarTuner.add_samples(indata, frames)


sounddevice.default.samplerate = SAMPLERATE
GuitarTuner = tuner()

with sounddevice.InputStream(channels=1, dtype='float32', callback=callback):
    input()
