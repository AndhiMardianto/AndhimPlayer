# Andhim Player

Andhim Player adalah aplikasi pemutar media sederhana untuk Windows yang dirancang untuk aksesibilitas bagi pengguna disabilitas, dengan dukungan pembaca layar.

## Deskripsi
Aplikasi pemutar media ini mendukung pemutaran media lokal serta jaringan TV dan radio streaming. Dirancang untuk memberikan pengalaman pengguna yang ramah bagi pengguna disabilitas dengan dukungan pembaca layar.

## Fitur
- Pemutaran media lokal (musik, video, dll.).
- Pemutaran radio dan TV streaming dari URL.
- **Pintasan tombol kontrol** yang memudahkan navigasi menggunakan keyboard:
  - **Play/Pause**: `Space`
  - **Stop**: `S`
  - **Next Track**: `Right Arrow`
  - **Previous Track**: `Left Arrow`
  - **Mute/Unmute**: `M`
  - **Volume Up**: `Up Arrow`
  - **Volume Down**: `Down Arrow`
  - **Open File**: `Ctrl + O`
  - **Open Folder**: `Ctrl + Shift + O`
  - **Exit**: `Ctrl + Q`
  
  Pintasan ini memberikan kontrol penuh terhadap pemutaran media hanya dengan keyboard, mendukung kenyamanan bagi pengguna dengan keterbatasan fisik.

## Instalasi
1. **Unduh VLC**:
   Untuk menjalankan aplikasi ini, Anda perlu mengunduh **VLC Media Player** versi Portable atau menginstalnya terlebih dahulu jika Anda belum memilikinya. Anda bisa mengunduh VLC di [sini](https://www.videolan.org/vlc/).
   
   Anda harus memastikan bahwa file `libvlc.dll` dan folder `plugins/` dari VLC ada di dalam folder proyek.

2. **Menyiapkan Aplikasi**:
   - Ekstrak folder VLC Portable atau gunakan instalasi VLC terpisah.
   - Salin file `libvlc.dll` dan folder `plugins/` ke dalam folder proyek ini.
   - Jalankan aplikasi dengan file eksekusi yang sesuai.

## Lisensi
Aplikasi ini dilisensikan di bawah **MIT License**.  
VLC Media Player (libvlc.dll) digunakan dalam proyek ini di bawah lisensi **LGPL v2.1**.

## Cara Menggunakan
- Buka aplikasi.
- Pilih file media atau folder untuk diputar.
- Gunakan pintasan keyboard yang disebutkan di atas untuk mengontrol pemutaran media.

## Kontribusi
Kontribusi sangat diterima! Jika Anda memiliki ide atau perbaikan untuk aplikasi ini, harap buka masalah atau ajukan pull request di repositori ini.

