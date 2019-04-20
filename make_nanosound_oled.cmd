dos2unix.exe *.py

7z.exe -ttar a dummy .\nanosound_oled\ -so | 7z.exe -si -tgzip a nanosound_oled2.tar.gz
ren nanosound_oled2.tar.gz nanosound_oled%date:~-4,4%%date:~-7,2%%date:~-10,2%.tar.gz
