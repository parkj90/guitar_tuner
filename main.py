import freq_detect
import queue
import tuner


def main():
    q = queue.Queue()

    fd = freq_detect.FreqDetector(q)
    fd.run()

    guitar_tuner = tuner.TunerGUI(q)
    guitar_tuner.run()


if __name__ == '__main__':
    main()
