import numpy
# import pylab
import scipy.signal
import sounddevice


SAMPLERATE = 44100
FFTSIZE = 32768
MAG_THRESH = 26
EPS = numpy.finfo(float).eps


class FreqDetector:
    # frequency resolution and OVERLAP size
    FRES = SAMPLERATE / FFTSIZE
    OVERLAP = int(SAMPLERATE / 10)

    def __init__(self, queue):
        self.fftbuffer = numpy.zeros(FFTSIZE)
        self.samplerate = SAMPLERATE
        self.framecount = 0
        self.window = scipy.signal.get_window('blackman', FFTSIZE)
        self.screencap = True
        self.queue = queue

    def add_samples(self, indata, frames):
        # stream yields enough frames for one or more fft calculations
        if frames > self.OVERLAP:
            for i in range(int(frames / self.OVERLAP)):
                self.fftbuffer = numpy.append(self.fftbuffer, indata[:self.OVERLAP])[self.OVERLAP:]
                indata = indata[self.OVERLAP:]
                self.queue.put(self.find_note(self.fftbuffer, self.window))
        frames = frames % self.OVERLAP

        # insufficient frames without leftover from last calculation
        if self.framecount + frames >= self.OVERLAP:
            cutoff_index = self.OVERLAP - self.framecount
            self.fftbuffer = numpy.append(self.fftbuffer, indata[:cutoff_index])[cutoff_index:]
            temp = indata[cutoff_index:]
            self.queue.put(self.find_note(self.fftbuffer, self.window))
            self.fftbuffer = numpy.append(self.fftbuffer, temp)[len(temp):]
            self.framecount = len(temp)
        # not enough frames even with leftover
        else:
            self.fftbuffer = numpy.append(self.fftbuffer, indata)[frames:]
            self.framecount += frames

    def find_note(self, fftbuffer, window):
        x = fftbuffer * window
        X = numpy.fft.fft(x)
        mag_spectrum = abs(X)[:int(len(X) / 2)]
        mag_spectrum[mag_spectrum < EPS] = EPS
        mag_spectrumDB = 20 * numpy.log10(mag_spectrum)

        if (mag_spectrumDB[mag_spectrumDB.argmax()] < MAG_THRESH):
            return None
        else:
            # check half argmax for f0
            half_index = int(mag_spectrumDB.argmax() / 2)
            if mag_spectrumDB[mag_spectrumDB[:half_index + 20].argmax()] > 24:
                freq = mag_spectrumDB[:half_index + 20].argmax() * self.FRES
            else:
                freq = mag_spectrumDB.argmax() * self.FRES

            # remove false f0 reports due to excessive noise
            if freq < (mag_spectrumDB.argmax() * self.FRES / 2) - 20:
                freq = mag_spectrumDB.argmax() * self.FRES

            return freq
            # debug tool
            '''
            if 280 < freq < 300 and self.screencap:
                pylab.plot(mag_spectrumDB)
                pylab.axis([0, 300, 0, 100])
                pylab.savefig('f0.png')
                self.screencap = False
            '''

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        if indata.any():
            self.add_samples(indata, frames)

    def run(self):
        self.stream = sounddevice.InputStream(channels=1, dtype='float32', callback=self.callback)
        self.stream.start()
