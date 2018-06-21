import numpy
import pylab
import scipy.signal
import sounddevice


SAMPLERATE = 44100
FFTSIZE = 32768
MAG_THRESH = 70


class FreqDetector:
    # frequency resolution and overlap size
    fres = SAMPLERATE / FFTSIZE
    overlap = int(SAMPLERATE / 10)

    def __init__(self):
        self.fftbuffer = numpy.zeros(FFTSIZE)
        self.samplerate = SAMPLERATE
        self.framecount = 0
        self.window = scipy.signal.get_window('blackman', FFTSIZE)
        self.screencap = True

    def add_samples(self, indata, frames):
        if frames > self.overlap:
            for i in range(int(frames / self.overlap)):
                self.fftbuffer = numpy.append(self.fftbuffer, indata[:self.overlap])[self.overlap:]
                indata = indata[self.overlap:]
                self.find_note()
        frames = frames % self.overlap
        if self.framecount + frames >= self.overlap:
            cutoff_index = self.overlap - self.framecount
            self.fftbuffer = numpy.append(self.fftbuffer, indata[:cutoff_index])[cutoff_index:]
            temp = indata[cutoff_index:]
            self.find_note()
            self.fftbuffer = numpy.append(self.fftbuffer, temp)[len(temp):]
            self.framecount = len(temp)
        else:
            self.fftbuffer = numpy.append(self.fftbuffer, indata)[frames:]
            self.framecount += frames

    def find_note(self):
        x = self.fftbuffer * self.window
        X = numpy.fft.fft(x)
        mag_spectrum = abs(X)[:int(len(X) / 2)]
        freq = mag_spectrum.argmax() * self.fres
        if (mag_spectrum[mag_spectrum.argmax()] < MAG_THRESH):
            print('N/A')
        else:
            print(mag_spectrum.argmax(), freq)
        if 100 < freq < 120 and self.screencap:
            pylab.plot(mag_spectrum)
            pylab.axis([0, 300, 0, 100])
            pylab.savefig('f0.png')
            self.screencap = False

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        if indata.any():
            self.add_samples(indata, frames)

    def init_stream(self):
        with sounddevice.InputStream(channels=1, dtype='float32', callback=self.callback):
            input()


if __name__ == '__main__':
    sounddevice.default.samplerate = SAMPLERATE
    fd = FreqDetector()
    fd.init_stream()
