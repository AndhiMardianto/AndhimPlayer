untuk membuat file exe jalankan perintah di terminal dibawah ini 

pyinstaller --noconsole --add-data "lib;lib" --add-data "vlc.py;." --add-data "stations.json;." AndhimPlayer.py

maka akan menghasilkan file exe didalam folder disk 
kemudian jalankan file setup_script.iss

Pastikan anda telah menyertakan file komponen vlc didalam folder lib. 
baca  reademe.md didalam folder tersebut untuk informasi nya 