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
    OVERLAP = SAMPLERATE // 10

    def __init__(self, queue):
        self.inbuffer = numpy.array([])
        self.fftbuffer = numpy.zeros(FFTSIZE)
        self.samplerate = SAMPLERATE
        self.samplecount = 0
        self.window = scipy.signal.get_window('blackman', FFTSIZE)
        self.screencap = True
        self.queue = queue

    def add_samples(self, indata, num_samples):
        self.inbuffer = numpy.append(self.inbuffer, indata)
        while len(self.inbuffer) > self.OVERLAP:
            self.fftbuffer = numpy.append(self.fftbuffer, self.inbuffer[:self.OVERLAP])[self.OVERLAP:]
            self.queue.put(self.find_note(self.fftbuffer, self.window))
            self.inbuffer = self.inbuffer[self.OVERLAP:]

    # FIX ME: might be using argmax() too many times; check to see if that can be reduced
    def find_note(self, fftbuffer, window):
        x = fftbuffer * window
        X = numpy.fft.fft(x)

        mag_spectrum = abs(X)[:len(X) // 2]
        mag_spectrum[mag_spectrum < EPS] = EPS
        mag_spectrum_db = 20 * numpy.log10(mag_spectrum)

        if (mag_spectrum_db[mag_spectrum_db.argmax()] < MAG_THRESH):
            return None

        # check half argmax for f0
        half_index = mag_spectrum_db.argmax() // 2
        if mag_spectrum_db[mag_spectrum_db[:half_index + 20].argmax()] > 24:
            freq = mag_spectrum_db[:half_index + 20].argmax() * self.FRES

            # remove false f0 reports due to excessive noise
            if freq < (mag_spectrum_db.argmax() * self.FRES / 2) - 20:
                freq = mag_spectrum_db.argmax() * self.FRES
        else:
            freq = mag_spectrum_db.argmax() * self.FRES

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
        if indata.any():
            self.add_samples(indata, num_samples)

    def run(self):
        self.stream = sounddevice.InputStream(samplerate=SAMPLERATE, channels=1, dtype='float32', callback=self.callback)
        self.stream.start()
