import freq_detect
import wx


class TunerGUI(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, size=(600, 300))
        self.InitGUI()

    def InitGUI(self):
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    guitar_tuner = TunerGUI(None, title='Guitar Tuner')
    fd = freq_detect.FreqDetector()
    fd.init_stream()
