import freq_detect
import queue
import threading
import tuner


def main():
    q = queue.Queue()
    fd = freq_detect.FreqDetector(q)

    freq_thread = threading.Thread(target=fd.init_stream)
    debug_thread = threading.Thread(target=tuner.check_queue, args=(q,))
    freq_thread.start()
    debug_thread.start()

    guitar_tuner = tuner.TunerGUI(q)


if __name__ == '__main__':
    main()
