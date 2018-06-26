import wx
import queue


class TunerGUI:
    def __init__(self, queue):
        self.app = wx.App()
        self.frame = TunerFrame(queue, None)

    def run(self):
        self.app.MainLoop()

    # target for thread
    def queue_check(self):
        while True:
            try:
                self.frame.i = self.queue.get(False)
            except queue.Empty:
                pass

    def guess_note(self, i):
        pass


class TunerFrame(wx.Frame):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs, size=(600, 300))
        self.queue = queue
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(100)
        self.Show()

    def OnTimer(self, e):
        f = None
        while not self.queue.empty():
            f = self.queue.get()

        self.dc = wx.ClientDC(self)
        self.dc.Clear()
        if f is None:
            self.dc.DrawText('N/A', 30, 30)
        else:
            self.dc.DrawText(str(f), 30, 30)
