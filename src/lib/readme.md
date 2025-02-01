# Petunjuk Mengunduh dan Menyiapkan `libvlc.dll`

Agar aplikasi Andhim Player dapat berfungsi dengan baik, Anda perlu menyiapkan **VLC Media Player** dan memastikan **`libvlc.dll`** beserta folder plugin VLC tersedia di sistem Anda.

## Langkah-langkah:

1. **Unduh VLC**:
   - Kunjungi [halaman resmi VLC](https://www.videolan.org/vlc/) untuk mengunduh VLC Media Player. Anda dapat memilih versi yang sesuai dengan sistem operasi Anda.
   
2. **Lokasi `libvlc.dll` dan Folder Plugin**:
   - Jika Anda menggunakan **VLC Portable**, temukan `libvlc.dll` dan folder `plugins/` di dalam folder VLC yang telah Anda unduh.
   - Jika Anda menginstal VLC, `libvlc.dll` biasanya dapat ditemukan di:
     ```
     C:\Program Files\VideoLAN\VLC\libvlc.dll
     ```
   - Anda juga perlu menyalin folder `plugins/` yang ada di dalam direktori VLC tersebut.

3. **Salin ke Folder Proyek**:
   - Salin `libvlc.dll` dan folder `plugins/` dari instalasi VLC ke dalam folder `lib/` di dalam proyek ini.

4. **Verifikasi**:
   - Pastikan aplikasi dapat menemukan `libvlc.dll` dan file-file terkait untuk berjalan dengan benar.

Dengan mengikuti langkah-langkah di atas, Andhim Player akan dapat berjalan dengan lancar.
