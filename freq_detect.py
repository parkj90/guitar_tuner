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

    def __init__(self, q):
        self.fftbuffer = numpy.zeros(FFTSIZE)
        self.samplerate = SAMPLERATE
        self.framecount = 0
        self.window = scipy.signal.get_window('blackman', FFTSIZE)
        self.screencap = True
        self.q = q

    def add_samples(self, indata, frames):
        # stream yields enough frames for one or more fft calculations
        if frames > self.overlap:
            for i in range(int(frames / self.overlap)):
                self.fftbuffer = numpy.append(self.fftbuffer, indata[:self.overlap])[self.overlap:]
                indata = indata[self.overlap:]
                self.find_note()
        frames = frames % self.overlap

        # insufficient frames without leftover from last calculation
        if self.framecount + frames >= self.overlap:
            cutoff_index = self.overlap - self.framecount
            self.fftbuffer = numpy.append(self.fftbuffer, indata[:cutoff_index])[cutoff_index:]
            temp = indata[cutoff_index:]
            self.find_note()
            self.fftbuffer = numpy.append(self.fftbuffer, temp)[len(temp):]
            self.framecount = len(temp)
        # not enough frames even with leftover
        else:
            self.fftbuffer = numpy.append(self.fftbuffer, indata)[frames:]
            self.framecount += frames

    # FIX ME!! change to make function not need to access external variables (i/o... return something)
    def find_note(self):
        x = self.fftbuffer * self.window
        X = numpy.fft.fft(x)
        mag_spectrum = abs(X)[:int(len(X) / 2)]
        freq = mag_spectrum.argmax() * self.fres

        # FIX ME!!! use log dB scale for cutoff (better yet, look at a graph of the log dB scale)
        # also, in final version, pass queue to the instance
        if (mag_spectrum[mag_spectrum.argmax()] < MAG_THRESH):
            # print('N/A')
            self.q.put('N/A')
        else:
            # print(mag_spectrum.argmax(), freq)
            self.q.put((mag_spectrum.argmax(), freq))
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
            # FIX ME!!! this is just a debugging tool
            self.q.put('end_stream')


if __name__ == '__main__':
    sounddevice.default.samplerate = SAMPLERATE
    fd = FreqDetector()
    fd.init_stream()
