import numpy
# import pylab
import scipy.signal
import sounddevice


SAMPLERATE = 44100
FFTSIZE = 32768
MAGTHRESH = 26    # dB
FREQTHRESH = 60   # Hz
SEARCHRANGE = 10  # must be smaller than FREQTHRESH
EPS = numpy.finfo(float).eps


class FreqDetector:
    # frequency resolution and OVERLAP size
    FRES = SAMPLERATE / FFTSIZE
    OVERLAP = SAMPLERATE // 10

    def __init__(self, queue):
        self.inbuffer = numpy.array([])
        self.fftbuffer = numpy.zeros(FFTSIZE)
        self.window = scipy.signal.get_window('blackman', FFTSIZE)
        self.queue = queue
        # self.screencap = True

    def add_samples(self, indata, num_samples):
        self.inbuffer = numpy.append(self.inbuffer, indata)
        while len(self.inbuffer) > self.OVERLAP:
            self.fftbuffer = numpy.append(self.fftbuffer[self.OVERLAP:], self.inbuffer[:self.OVERLAP])
            self.queue.put(self.find_note(self.fftbuffer, self.window))
            self.inbuffer = self.inbuffer[self.OVERLAP:]

    def find_note(self, fftbuffer, window):
        x = fftbuffer * window
        X = numpy.fft.fft(x)

        mag_spectrum = abs(X)[:len(X) // 2]
        mag_spectrum[mag_spectrum < EPS] = EPS
        mag_spectrum_db = 20 * numpy.log10(mag_spectrum)

        max_mag_index = mag_spectrum_db.argmax()
        if (mag_spectrum_db[max_mag_index] < MAGTHRESH) or (max_mag_index * self.FRES < FREQTHRESH):
            return None

        # some strings have stronger 1st harmonic freq component
        # search around half argmax for local maximum
        half_index = max_mag_index // 2
        search_index = mag_spectrum_db[half_index - SEARCHRANGE:half_index + SEARCHRANGE].argmax()
        half_max_candidate = half_index - SEARCHRANGE + search_index

        if (mag_spectrum_db[half_max_candidate] > MAGTHRESH) and (half_max_candidate * self.FRES > FREQTHRESH):
            freq = half_max_candidate * self.FRES
        else:
            freq = max_mag_index * self.FRES

        return freq

        # debug tool
        '''
        if 280 < freq < 300 and self.screencap:
            pylab.plot(mag_spectrum_db)
            pylab.axis([0, 300, 0, 100])
            pylab.savefig('f0.png')
            self.screencap = False
        '''

    def callback(self, indata, num_samples, time, status):
        if status:
            print(status)
        if num_samples:
            self.add_samples(indata, num_samples)

    def run(self):
        self.stream = sounddevice.InputStream(samplerate=SAMPLERATE, channels=1, dtype='float32', callback=self.callback)
        self.stream.start()
