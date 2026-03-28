@echo off
setlocal
cd /d "%~dp0"

echo Checking PyInstaller...
py -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
	py -m pip install pyinstaller || goto :error
)

for %%F in (
	fifa_db_switcher.py
	FIFA07_DB_Switcher.spec
	data\fifa.db
	data\fifa_patched.db
	assets\button_install.png
	assets\button_restore.png
	assets\button_browse.png
	assets\path_holder.png
	assets\app_icon.png
	assets\app_icon.ico
) do (
	if not exist "%%F" (
		echo [ERROR] Missing file: %%F
		goto :error
	)
)

echo Building EXE...
py -m PyInstaller --noconfirm --clean FIFA07_DB_Switcher.spec || goto :error

echo.
echo Build completed. EXE file: dist\FIFA07_DB_Switcher.exe
if /I "%~1"=="--pause" pause
exit /b 0

:error
echo.
echo Build failed.
if /I "%~1"=="--pause" pause
exit /b 1
