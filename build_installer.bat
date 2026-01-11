@echo off
echo Instalando dependencias...
pip install -r requirements.txt

echo Creando ejecutable con PyInstaller...
pyinstaller --onefile --windowed --icon=logo.png --add-data="logo.png;." app.py

echo Creando instalador con Inno Setup...
echo Descarga Inno Setup desde: https://jrsoftware.org/isdl.php
echo Luego crea un script .iss para tu instalador

echo ¡Proceso completado!
pause