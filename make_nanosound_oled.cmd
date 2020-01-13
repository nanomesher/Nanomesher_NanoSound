dos2unix.exe .\nanosound_oled\*.py
dos2unix.exe .\nanosound_oled\*.conf
dos2unix.exe .\nanosound_oled\lircrc
7z.exe -ttar a dummy .\nanosound_oled\ -so | 7z.exe -si -tgzip a nanosound_oled3.tar.gz
ren nanosound_oled3.tar.gz nanosound_oled%date:~-4,4%%date:~-7,2%%date:~-10,2%.tar.gz
