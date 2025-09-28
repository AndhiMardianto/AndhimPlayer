import wx
from gui.main import MainFrame  # Impor MainFrame dari dalam gui

class AndhimPlayer(wx.App):
    def OnInit(self):
        self.frame = MainFrame()  # Jangan berikan argumen tambahan jika tidak diperlukan
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = AndhimPlayer()
    app.MainLoop()
