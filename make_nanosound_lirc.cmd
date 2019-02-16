7z.exe -ttar a dummy .\nanosound_lirc\* -so | 7z.exe -si -tgzip a nanosound_lirc.tar.gz
ren nanosound_lirc.tar.gz nanosound_lirc%date:~-4,4%%date:~-7,2%%date:~-10,2%.tar.gz
