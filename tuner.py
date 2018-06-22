import wx


class TunerGUI:
    def __init__(self, q):
        self.q = q
        self.app = wx.App()
        self.f = TunerFrame(None)
        self.app.MainLoop()

    # callback function for thread
    def queue_check(q):
        while True:
            i = q.get()
            print(i)


class TunerFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, size=(600, 300))
        self.Show()


# ERASE ME DEBUG TOOL
def check_queue(q):
    while True:
        i = q.get()
        if i == 'end_stream':
            break
        print(i)
        q.task_done()
