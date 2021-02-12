@echo off
title Python-Installer
chcp 65001
echo [Python-Installer] Lade Python 3.9.1 herunter!
echo [Python-Installer] Bitte warten!
powershell -command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.9.1/python-3.9.1.exe', '%tmp%\python-3.9.1.exe');
echo [Python-Installer] Python wurde heruntergeladen! Folgen sie den Anweisungen im Installationsassistent!
echo [Python-Installer] Bitte klicken sie die Option "Add to PATH" an!
%tmp%\python-3.9.1.exe
echo [Python-Installer] Python wurde erfolgreich installiert!
echo [Python-Installer] Installiere benötigte Packete: bs4, requests
%localappdata%\Programs\Python\Python39\python.exe -m pip install bs4
%localappdata%\Programs\Python\Python39\python.exe -m pip install requests
pause