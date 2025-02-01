import wx
import vlc
import os
import sys
import json
import threading
import win32gui
import win32con

class MediaPlayerApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.checker = wx.SingleInstanceChecker("MediaPlayerApp")

        if self.checker.IsAnotherRunning():
            self.bring_existing_instance_to_front()
            raise SystemExit(0)

        self.frame = MediaPlayer(None, title="Andhim Player")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        self.frame.initialize_playback()

    def bring_existing_instance_to_front(self):
        # Mencari window dengan nama "Andhim Player"
        def enum_window_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                results.append(hwnd)
        hwnd_list = []
        win32gui.EnumWindows(enum_window_callback, hwnd_list)
        for hwnd in hwnd_list:
            if win32gui.GetWindowText(hwnd) == "Andhim Player":
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                break

class MediaPlayer(wx.Frame):
    instance = None

    def __init__(self, parent, title="Andhim Player"):
        super(MediaPlayer, self).__init__(parent, title=title, size=(800, 750))
        self.stations = []
        self.mode = "standar"
        self.current_station = None  # Menyimpan URL stasiun yang sedang diputar
        self.playlist = []
        self.current_index = 0

        self.player = vlc.MediaPlayer()
        self.player.video_set_aspect_ratio("16:9")
        self.event_manager = self.player.event_manager()
        
        # Mendaftarkan callback untuk event MediaPlayerEndReached
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_song_finished)

        # Path untuk menyimpan file JSON di AppData\Roaming\Andhim Player
        self.app_data_path = os.path.join(os.getenv('APPDATA'), "AndhimPlayer")
        if not os.path.exists(self.app_data_path):
            os.makedirs(self.app_data_path)
        self.state_file_path = os.path.join(self.app_data_path, "last_playback_state.json")


        # load data straming dari file json
        self.app_data_dir = os.path.join(os.getenv("APPDATA"), "AndhimPlayer")
        self.project_dir = os.path.dirname(os.path.abspath(__file__))

        self.station_file_appdata = os.path.join(
            self.app_data_dir, "stations.json")
        self.station_file_project = os.path.join(
            self.project_dir, "stations.json")

        os.makedirs(self.app_data_dir, exist_ok=True)
        self.load_stations()

# panel utama 
        PanelUtama = wx.Panel(self)
        UkuranPanel = wx.BoxSizer(wx.VERTICAL)

        # panel untuk judul title 
        self.title_panel = wx.Panel(PanelUtama, size=(-1, 30))  # Perbaiki ukuran agar penuh
        self.title_panel.SetBackgroundColour(wx.Colour(0, 128, 255))  # Warna biru

        # Teks untuk judul
        self.title_label = wx.StaticText(self.title_panel, label="Andhim Player", style=wx.ALIGN_CENTER)
        self.title_label.SetForegroundColour(wx.WHITE)  # Warna putih

        # Font lebih menarik
        font = wx.Font(
            16,  # Ukuran font lebih besar
            wx.FONTFAMILY_SWISS,  # Gaya huruf modern (mirip Arial)
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD
        )
        self.title_label.SetFont(font)

        # Gunakan sizer untuk meletakkan teks di tengah panel
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(self.title_label, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

        # Terapkan sizer ke title_panel
        self.title_panel.SetSizer(title_sizer)

        # Fokus awal ke title
        self.title_label.SetFocus()

        # Buat panel untuk menu
        self.menu_panel = wx.Panel(PanelUtama)
        self.menu_panel.SetBackgroundColour(wx.BLACK)  
        # Buat sizer untuk menu_panel
        menu_sizer = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        # Tombol Menu di kiri
        self.menu_button = wx.Button(self.menu_panel, label="Menu")
        self.menu_button.SetBackgroundColour(wx.Colour(0, 128, 255))  # Warna tombol
        self.menu_button.SetForegroundColour(wx.WHITE)  # Warna teks tombol
        self.menu_button.Bind(wx.EVT_BUTTON, self.show_popup_menu)
        menu_sizer.Add(self.menu_button, flag=wx.ALIGN_LEFT)

        # Tombol Streaming di kanan
        self.radio_button = wx.Button(self.menu_panel, label="Streaming")
        self.radio_button.SetBackgroundColour(wx.Colour(34, 193, 195))  # Warna tombol
        self.radio_button.SetForegroundColour(wx.WHITE)  # Warna teks tombol
        self.radio_button.Bind(wx.EVT_BUTTON, self.show_stations)
        menu_sizer.Add(self.radio_button, flag=wx.ALIGN_RIGHT)

        # Atur sizer untuk menu_panel
        self.menu_panel.SetSizer(menu_sizer)

        # Panel untuk video
        self.video_panel = wx.Panel(PanelUtama, style=wx.SUNKEN_BORDER)
        self.video_panel.SetBackgroundColour(wx.BLACK)  
        # Tambahkan panel video ke dalam sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.video_panel, 1, flag=wx.EXPAND)
        PanelUtama.SetSizerAndFit(sizer)

        # Menetapkan hwnd untuk VLC player dan memperbarui layout panel
        self.player.set_hwnd(self.video_panel.GetHandle())

        # Panel untuk kontrol audio/video
        self.control_panel = wx.Panel(PanelUtama)
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        self.control_panel.SetBackgroundColour(wx.BLUE)

        # Tombol-tombol pengontrol media (Horizontal Layout)
        hbox_controls = wx.BoxSizer(wx.HORIZONTAL)

        self.play_button = wx.Button(self.control_panel, label="Putar")
        self.play_button.SetBackgroundColour(wx.BLACK)
        self.play_button.SetForegroundColour(wx.WHITE)
        self.play_button.Bind(wx.EVT_BUTTON, self.on_play)
        hbox_controls.Add(self.play_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.pause_button = wx.Button(self.control_panel, label="Jeda")
        self.pause_button.SetBackgroundColour(wx.BLACK)
        self.pause_button.SetForegroundColour(wx.WHITE)
        self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause)
        hbox_controls.Add(self.pause_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.stop_button = wx.Button(self.control_panel, label="Stop")
        self.stop_button.SetBackgroundColour(wx.BLACK)
        self.stop_button.SetForegroundColour(wx.WHITE)
        self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop)
        hbox_controls.Add(self.stop_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.prev_button = wx.Button(self.control_panel, label="Sebelumnya")
        self.prev_button.SetBackgroundColour(wx.BLACK)
        self.prev_button.SetForegroundColour(wx.WHITE)
        self.prev_button.Bind(wx.EVT_BUTTON, self.prev_station)
        hbox_controls.Add(self.prev_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.next_button = wx.Button(self.control_panel, label="Berikutnya")
        self.next_button.SetBackgroundColour(wx.BLACK)
        self.next_button.SetForegroundColour(wx.WHITE)
        self.next_button.Bind(wx.EVT_BUTTON, self.next_station)
        hbox_controls.Add(self.next_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        control_sizer.Add(hbox_controls, flag=wx.EXPAND | wx.ALL, border=5)

        # Checkbox Senyap
        self.mute_checkbox = wx.CheckBox(self.control_panel, label="Senyap")
        self.mute_checkbox.Bind(wx.EVT_CHECKBOX, self.on_mute)
        control_sizer.Add(self.mute_checkbox, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        # Tombol volume naik dan turun (Horizontal Layout)
        hbox_vol = wx.BoxSizer(wx.HORIZONTAL)

        self.volume_up_button = wx.Button(self.control_panel, label="Volume Naik")
        self.volume_up_button.SetBackgroundColour(wx.BLACK)
        self.volume_up_button.SetForegroundColour(wx.WHITE)
        self.volume_up_button.Bind(wx.EVT_BUTTON, self.on_volume_up)
        hbox_vol.Add(self.volume_up_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.volume_down_button = wx.Button(self.control_panel, label="Volume Turun")
        self.volume_down_button.SetBackgroundColour(wx.BLACK)
        self.volume_down_button.SetForegroundColour(wx.WHITE)
        self.volume_down_button.Bind(wx.EVT_BUTTON, self.on_volume_down)
        hbox_vol.Add(self.volume_down_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        control_sizer.Add(hbox_vol, flag=wx.EXPAND | wx.ALL, border=5)

        # Tombol layar penuh
        self.fullscreen_button = wx.Button(self.control_panel, label="Layar Penuh")
        self.fullscreen_button.SetBackgroundColour(wx.BLACK)
        self.fullscreen_button.SetForegroundColour(wx.WHITE)
        self.fullscreen_button.Bind(wx.EVT_BUTTON, self.toggle_fullscreen)
        control_sizer.Add(self.fullscreen_button, flag=wx.EXPAND | wx.ALL, border=5)

        # Terapkan sizer ke panel kontrol
        self.control_panel.SetSizer(control_sizer)


        # Panel untuk judul lagu dan slider
        self.info_panel = wx.Panel(PanelUtama)
        info_sizer = wx.BoxSizer(wx.VERTICAL)

        # Label untuk judul file
        self.title_label = wx.StaticText(self.info_panel, label="judul")
        info_sizer.Add(self.title_label, flag=wx.ALIGN_CENTER)

        # Slider
        self.slider = wx.Slider(self.info_panel, style=wx.SL_HORIZONTAL)
        self.slider.Bind(wx.EVT_SLIDER, self.on_slider)
        info_sizer.Add(self.slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Atur sizer ke dalam panel
        self.info_panel.SetSizer(info_sizer)
        #UkuranPanel.Add(self.info_panel, flag=wx.EXPAND | wx.ALL, border=5)




        # panel playlist 
        self.playlist_panel = wx.Panel(PanelUtama)
        self.playlist_panel.SetBackgroundColour(wx.BLACK)

        playlist_sizer = wx.BoxSizer(wx.VERTICAL)

        # Tambahkan ListBox ke dalam panel playlist
        self.playlist_box = wx.ListBox(self.playlist_panel, size=(300, 150), choices=[""])
        playlist_sizer.Add(self.playlist_box, flag=wx.EXPAND | wx.ALL, border=10)

        self.playlist_box.Bind(wx.EVT_CHAR_HOOK, self.on_playlist_key_down)
        self.playlist_box.Bind(wx.EVT_LISTBOX, self.on_playlist_item_selected)

        self.playlist = []
        self.current_index = -1

        # Atur sizer untuk panel playlist
        self.playlist_panel.SetSizer(playlist_sizer)


        
        # Memuat status pemutaran terakhir atau folder baru dari argumen
        if len(sys.argv) > 1:
            self.load_file_from_arg(sys.argv[1])  # Memuat folder dari argumen
        #else:
            #self.load_last_playback_state()  # Memuat status pemutaran terakhir


# mute dan full screen false
        self.is_muted = False
        self.is_fullscreen = False

        # Timer untuk memperbarui slider
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_slider, self.timer)
        self.timer.Start(1000)


        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

        PanelUtama.SetSizer(UkuranPanel)
        # Atur ukuran minimum agar video bisa ditampilkan
        #self.video_panel.SetMinSize((800, 600))

        #MediaPlayer.instance = self
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.load_last_playback_state()  # Memuat status pemutaran terakhir

        # Menambahkan panel-panel ke dalam sizer utama
        UkuranPanel.Add(self.title_panel, 0, wx.EXPAND | wx.TOP, 0)  # Tambahkan ke tata letak utama
        UkuranPanel.Add(self.video_panel, 1, wx.EXPAND | wx.ALL, 5)  
        UkuranPanel.Add(self.menu_panel, 0, wx.EXPAND | wx.TOP, 5)  
        UkuranPanel.Add(self.playlist_panel, 0, wx.EXPAND | wx.ALL, 5)  
        UkuranPanel.Add(self.info_panel, flag=wx.EXPAND | wx.ALL, border=5)
        UkuranPanel.Add(self.control_panel, 0, wx.EXPAND | wx.BOTTOM, 5)
        # Menambahkan sizer ke panel utama
        PanelUtama.SetSizer(UkuranPanel)

        self.Centre()
        self.Show()



    def initialize_playback(self):
        """Memuat status pemutaran terakhir atau folder baru dari argumen setelah inisialisasi frame."""
        if len(sys.argv) > 1:
            self.load_file_from_arg(sys.argv[1])  # Memuat folder dari argumen
        else:
            self.load_last_playback_state()  # Memuat status pemutaran terakhir


    def on_playlist_item_selected(self, event):
        selection = self.playlist_box.GetSelection()
        if selection != wx.NOT_FOUND:
            self.selected_index = selection  # Simpan indeks lagu yang dipilih

    def on_playlist_key_down(self, event):
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_RETURN and hasattr(self, 'selected_index'):
            self.current_index = self.selected_index
            self.mode = "standar"
            self.on_play()
            self.title_label.SetLabel(os.path.basename(
            self.playlist[self.current_index]))

        else:
            event.Skip()  # Pastikan tombol lain tetap berfungsi

    def update_playlist_display(self):
        # Menampilkan playlist di ListBox
        self.playlist_box.Set([os.path.basename(file) for file in self.playlist])

    # Fungsi on_size untuk menangani perubahan ukuran jendela
    def on_size(self, event):
        size = self.GetSize()
        self.player.set_xwindow(self.video_panel.GetHandle())
        video_height = size[1] - 150  # Sisakan ruang untuk panel lain
        self.video_panel.SetSize(self.GetClientSize())
        self.Layout()
        self.video_panel.Refresh()
        self.video_panel.Update()
        event.Skip()

    def toggle_fullscreen(self, event):
        self.is_fullscreen = not self.is_fullscreen
        self.ShowFullScreen(self.is_fullscreen)

    def load_stations(self):
        if os.path.exists(self.station_file_appdata):
            file_to_load = self.station_file_appdata
        elif os.path.exists(self.station_file_project):
            file_to_load = self.station_file_project
        else:
            self.stations = []
            return

        with open(file_to_load, "r") as f:
            self.stations = json.load(f)

    def save_stations(self):
        for path in [self.station_file_appdata, self.station_file_project]:
            with open(path, "w") as f:
                json.dump(self.stations, f, indent=4)

    def show_stations(self, event):
        self.stations_menu = wx.Menu()  # Simpan menu sebagai atribut

        for station in self.stations:
            menu_item = self.stations_menu.Append(wx.ID_ANY, station["name"])
            self.Bind(wx.EVT_MENU, self.on_station_selected, menu_item)

        self.PopupMenu(self.stations_menu)

    def on_station_selected(self, event):
        # Ambil ID item menu yang dipilih
        menu_id = event.GetId()

        # Ambil label item menu berdasarkan ID
        menu_item = self.stations_menu.FindItemById(menu_id)
        if not menu_item:
            return  # Hindari error jika item tidak ditemukan

        selected_station_name = menu_item.GetItemLabel()

        # Temukan stasiun berdasarkan nama
        selected_station = next(
            (s for s in self.stations if s["name"] == selected_station_name), None)
        if not selected_station:
            return  # Hindari error jika stasiun tidak ditemukan

        # Simpan URL stasiun dan ubah mode ke "radio"
        self.current_station_url = selected_station["url"]
        self.mode = "streaming"

        # Panggil fungsi play
        self.on_play(None)  # Pastikan sesuai dengan definisi fungsi

    def show_popup_menu(self, event):
        # Membuat objek menu
        menu = wx.Menu()

        # Menambahkan item ke menu
        open_file_item = menu.Append(wx.ID_ANY, "Open File")
        open_folder_item = menu.Append(wx.ID_ANY, "Open Folder")
        tambah_station_item = menu.Append(wx.ID_ANY, "Tambah Chanel Streaming")
        hapus_station_item = menu.Append(wx.ID_ANY, "Hapus Chanel Streaming")

        # Menyambungkan event handler untuk masing-masing item
        self.Bind(wx.EVT_MENU, self.on_open_file, open_file_item)
        self.Bind(wx.EVT_MENU, self.on_open_folder, open_folder_item)
        self.Bind(wx.EVT_MENU, self.add_station, tambah_station_item)
        self.Bind(wx.EVT_MENU, self.remove_station, hapus_station_item)

        # Menampilkan popup menu
        self.PopupMenu(menu)
        menu.Destroy()

    def load_file_from_arg(self, path):
        """Memuat file atau semua file dalam folder termasuk subfolder dari argumen saat aplikasi dibuka dengan 'Open With'."""
        # Cek apakah program dijalankan dengan argumen baru saat program dibuka kembali
        if not self.player.is_playing():
            self.playlist = []  # Kosongkan playlist jika program dibuka kembali dengan argumen baru
        
        if os.path.isfile(path):  # Jika path adalah file
            self.playlist.append(path)
            self.update_playlist_display()
            self.title_label.SetLabel(os.path.basename(path))

            # Set media hanya jika player dalam mode stop
            if not self.player.is_playing():
                self.player.set_media(vlc.Media(path))
                self.player.play()
        
        elif os.path.isdir(path):  # Jika path adalah folder
            new_files = []
            for root, _, files in os.walk(path):
                for f in files:
                    if f.endswith(('.mp4', '.avi', '.mkv', '.mp3', '.wav')):
                        new_files.append(os.path.join(root, f))
            
            self.playlist.extend(new_files)
            self.update_playlist_display()
            
            if new_files:
                self.title_label.SetLabel(os.path.basename(new_files[0]))

                # Set media hanya jika player dalam mode stop
                if not self.player.is_playing():
                    self.player.set_media(vlc.Media(new_files[0]))
                    self.player.play()
            else:
                wx.MessageBox("Folder tidak mengandung file media yang didukung.", "Peringatan", wx.OK | wx.ICON_WARNING)
        
        else:
            wx.MessageBox("Path yang diberikan tidak valid!", "Error", wx.OK | wx.ICON_ERROR)

    def add_station(self, event):
        # Dialog untuk nama stasiun
        dialog = wx.TextEntryDialog(
            self, "Masukkan Nama Chanel:", "Tambah Chanel")
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
        else:
            dialog.Destroy()
            return  # Jika dibatalkan, keluar dari fungsi
        dialog.Destroy()

        # Dialog untuk URL stasiun
        dialog = wx.TextEntryDialog(
            self, "Masukkan URL Chanel:", "Tambah Chanel")
        if dialog.ShowModal() == wx.ID_OK:
            url = dialog.GetValue()
        else:
            dialog.Destroy()
            return  # Jika dibatalkan, keluar dari fungsi
        dialog.Destroy()

        # Tambahkan ke daftar stasiun
        self.stations.append({"name": name, "url": url})

        # Simpan ke file JSON
        self.save_stations()

        # Beri konfirmasi
        wx.MessageBox(
            f"Chanel'{name}' berhasil ditambahkan!",
            "Info",
            wx.OK | wx.ICON_INFORMATION)

    def on_open_file(self, event):
        with wx.FileDialog(self, "Buka File", wildcard="Video files (*.mp4;*.avi;*.mkv)|*.mp4;*.avi;*.mkv;*.mp3;*.wav", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path = fileDialog.GetPath()
            self.playlist = [path]
            self.current_index = 0
            self.player.set_media(vlc.Media(path))
            self.player.set_hwnd(self.video_panel.GetHandle())
            self.mode = "standar"
            self.player.play()
            self.title_label.SetLabel(os.path.basename(path))

    def on_open_folder(self, event):
        """Membuka folder dan memasukkan semua file media dari subfolder ke dalam playlist."""
        with wx.DirDialog(self, "Buka Folder") as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return

            folder_path = dirDialog.GetPath()
            self.playlist = []

            # Gunakan os.walk() untuk menelusuri semua subfolder
            for root, _, files in os.walk(folder_path):
                for f in files:
                    if f.endswith(('.mp4', '.avi', '.mkv', '.mp3', '.wav')):
                        self.playlist.append(os.path.join(root, f))

            if self.playlist:
                self.current_index = 0
                self.player.set_media(
                    vlc.Media(self.playlist[self.current_index]))
                self.player.set_hwnd(self.video_panel.GetHandle())
                self.mode = "standar"
                self.update_playlist_display()
                self.playlist_box.SetFocus()
                self.player.play()
                self.title_label.SetLabel(os.path.basename(
                    self.playlist[self.current_index]))
            else:
                wx.MessageBox(
                    "Folder tidak mengandung file media yang didukung.",
                    "Peringatan",
                    wx.OK | wx.ICON_WARNING)

    def on_play(self, event=None):
        if self.mode == "streaming":
            # Putar radio
            media = vlc.Media(self.current_station_url)
            self.player.set_media(media)
            self.player.play()
        else:
            # Putar media lokal seperti biasa
            if self.current_index < 0 or self.current_index >= len(
                    self.playlist):
                return

            media = vlc.Media(self.playlist[self.current_index])
            self.player.set_media(media)
            # Sambungkan ke panel video
            self.player.set_xwindow(self.video_panel.GetHandle())
            self.player.play()

    def on_pause(self, event):
        self.player.pause()

    def on_stop(self, event):
        self.player.stop()

    def change_station(self, step):
        if not self.stations:
            wx.MessageBox(
                "Tidak ada Chanel Streamingyang tersedia!",
                "Error",
                wx.OK | wx.ICON_ERROR)
        return

    # Cari indeks stasiun yang sedang diputar
        current_index = next(
            (i for i, s in enumerate(
                self.stations) if s["url"] == self.current_station), -1)

    # Tentukan indeks stasiun berikutnya/sebelumnya
        new_index = (current_index + step) % len(self.stations)
        new_station = self.stations[new_index]

    # Setel URL stasiun baru
        self.current_station = new_station["url"]
        self.player.set_media(vlc.Media(self.current_station))
        self.player.play()

        wx.MessageBox(
            f"Memutar: {
                new_station['name']}",
            "Info",
            wx.OK | wx.ICON_INFORMATION)

    def next_station(self, event):
        if self.mode == "streaming" and self.current_station_url:
            # Temukan stasiun yang sedang diputar
            current_index = next(
                (i for i, s in enumerate(
                    self.stations) if s["url"] == self.current_station_url), -1)

            if current_index != -1:
                # Tentukan indeks stasiun berikutnya
                next_index = (current_index + 1) % len(self.stations)
                next_station = self.stations[next_index]

                # Simpan URL stasiun dan ubah mode ke "radio"
                self.current_station_url = next_station["url"]
                self.mode = "streaming"

                # Panggil fungsi play untuk memutar stasiun berikutnya
                self.on_play(None)

        elif self.mode == "standar" and self.playlist:
            # Mode standar, pindah ke lagu berikutnya
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.player.set_media(vlc.Media(self.playlist[self.current_index]))
            self.player.set_hwnd(self.video_panel.GetHandle())
            self.player.play()
            self.title_label.SetLabel(os.path.basename(
                self.playlist[self.current_index]))

    def prev_station(self, event):
        if self.mode == "streaming" and self.current_station_url:
            # Temukan stasiun yang sedang diputar
            current_index = next(
                (i for i, s in enumerate(
                    self.stations) if s["url"] == self.current_station_url), -1)

            if current_index != -1:
                # Tentukan indeks stasiun sebelumnya
                prev_index = (current_index - 1) % len(self.stations)
                prev_station = self.stations[prev_index]

                # Simpan URL stasiun dan ubah mode ke streaming
                self.current_station_url = prev_station["url"]
                self.mode = "streaming"

                # Panggil fungsi play untuk memutar stasiun sebelumnya
                self.on_play(None)

        elif self.mode == "standar" and self.playlist:
            # Mode standar, pindah ke lagu sebelumnya
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.player.set_media(vlc.Media(self.playlist[self.current_index]))
            self.player.set_hwnd(self.video_panel.GetHandle())
            self.player.play()
            self.title_label.SetLabel(os.path.basename(
                self.playlist[self.current_index]))

    def on_mute(self, event):
        self.is_muted = not self.is_muted
        self.player.audio_toggle_mute()

    def on_volume_up(self, event):
        volume = self.player.audio_get_volume()
        self.player.audio_set_volume(min(volume + 10, 100))

    def on_volume_down(self, event):
        volume = self.player.audio_get_volume()
        self.player.audio_set_volume(max(volume - 10, 0))

    def on_slider(self, event):
        position = self.slider.GetValue()
        self.player.set_position(position / 100.0)

    def update_slider(self, event):
        if self.player.is_playing():
            position = self.player.get_position() * 100
            self.slider.SetValue(int(position))

    def on_key_press(self, event):
        keycode = event.GetKeyCode()
        handled = False  # Untuk menandai apakah event telah ditangani

        if keycode == ord("K"):  # Play/Pause (Tombol K)
            if self.player.is_playing():
                self.on_pause(event)
            else:
                self.on_play(event)
            handled = True
        elif keycode == ord("S"):  # Stop
            self.on_stop(event)
            handled = True
        elif keycode == ord("N"):  # Next Track
            self.next_station(event)
            handled = True
        elif keycode == ord("B"):  # Previous Track
            self.prev_station(event)
            handled = True
        elif keycode == ord("M"):  # Mute
            self.on_mute(event)
            handled = True
        elif keycode == ord("="):  # Volume Up (Tombol =)
            self.on_volume_up(event)
            handled = True
        elif keycode == ord("-"):  # Volume Down (Tombol -)
            self.on_volume_down(event)
            handled = True
        elif keycode == ord("d"):  # fokus ke playlist
            self.playlist_box.SetFocus(event)
            handled = True

        elif keycode == ord("L"):  # Maju cepat (Tombol L)
            self.seek_forward(event)
            handled = True
        elif keycode == ord("J"):  # Mundur cepat (Tombol J)
            self.seek_backward(event)
            handled = True
        elif keycode == ord("F"):  # Fullscreen
            self.toggle_fullscreen(event)
            handled = True
        elif keycode == wx.WXK_ESCAPE:  # Keluar dari fullscreen atau aplikasi
            if self.is_fullscreen:
                self.toggle_fullscreen(event)
            else:
                self.on_close(event)
            handled = True

        if not handled:
            event.Skip()  # Hanya meneruskan event jika tidak ditangani
        else:
            event.Skip(False)

    def seek_forward(self, event):
        current_time = self.player.get_time()
        self.player.set_time(current_time + 5000)  # Maju 5 detik

    def seek_backward(self, event):
        current_time = self.player.get_time()
        self.player.set_time(max(0, current_time - 5000))  # Mundur 5 detik

    def remove_station(self, event):
        # Buat popup menu
        menu = wx.Menu()
        self.menu_items = {}  # Simpan mapping ID -> Nama Stasiun

        # Tambahkan setiap stasiun ke dalam menu
        for station in self.stations:
            menu_id = wx.NewIdRef()  # Buat ID unik
            menu_item = menu.Append(menu_id, station["name"])
            self.menu_items[menu_id] = station["name"]  # Simpan mapping
            self.Bind(wx.EVT_MENU, self.on_station_remove, menu_item)

        # Tampilkan popup menu
        self.PopupMenu(menu)
        menu.Destroy()

    def on_station_remove(self, event):
        # Ambil ID item menu yang dipilih
        menu_id = event.GetId()

        # Ambil nama stasiun dari mapping
        selected_station_name = self.menu_items.get(menu_id, None)

        if selected_station_name:
            # Temukan indeks stasiun berdasarkan nama
            selected_station_index = next((i for i, station in enumerate(
                self.stations) if station["name"] == selected_station_name), None)

            if selected_station_index is not None:
                # Tampilkan dialog konfirmasi
                confirm_dialog = wx.MessageDialog(
                    self,
                    f"Apakah Anda yakin ingin menghapus Chanel'{selected_station_name}'?",
                    "Konfirmasi Hapus",
                    wx.YES_NO | wx.ICON_WARNING)

                if confirm_dialog.ShowModal() == wx.ID_YES:
                    del self.stations[selected_station_index]
                    self.save_stations()  # Simpan perubahan setelah penghapusan
                    wx.MessageBox(
                        f"Chanel'{selected_station_name}' telah dihapus.",
                        "Info",
                        wx.OK | wx.ICON_INFORMATION)

                confirm_dialog.Destroy()

    def on_song_finished(self, event):
        # Jalankan next_station di thread terpisah untuk mencegah blocking
        threading.Thread(target=self.next_station, args=(None,)).start()

    def on_close(self, event):
        self.on_stop(None)
        self.player.release()
        self.timer.Stop()
        
        # Simpan status pemutaran terakhir ke dalam file JSON di AppData\Roaming\AndhimPlayer
        state = {
            "playlist": self.playlist,
            "current_index": self.current_index,
            "current_station_url": self.current_station_url,
            "mode": self.mode
        }
        
        with open(self.state_file_path, "w") as f:
            json.dump(state, f)
        
        self.Destroy()
        
    def load_last_playback_state(self):
        try:
            with open(self.state_file_path, "r") as f:
                state = json.load(f)
                self.playlist = state.get("playlist", [])
                self.current_index = state.get("current_index", 0)
                self.current_station_url = state.get("current_station_url", "")
                self.mode = state.get("mode", "standar")
                self.update_playlist_display()  # Memperbarui tampilan playlist
                
                if self.mode == "streaming":
                    pass
               #     self.on_play(None)
                elif self.playlist:
                    if self.current_index < len(self.playlist):  # Pengecekan tambahan
                        self.player.set_media(vlc.Media(self.playlist[self.current_index]))
                        #self.player.play()
                        self.title_label.SetLabel(os.path.basename(self.playlist[self.current_index]))
        except FileNotFoundError:
            # Jika file tidak ditemukan, mulai dengan status baru
            self.playlist = []
            self.current_index = 0
            self.current_station_url = ""
            self.mode = "standar"


if __name__ == "__main__":
    app = MediaPlayerApp()
    app.MainLoop()


