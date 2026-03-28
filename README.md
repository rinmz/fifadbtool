# FIFA 07 DB Switcher

Desktop utility for switching FIFA 07 database files.

## Features

- Applies the patch by copying `data/fifa_patched.db` to the game target `data/cmn/fifa.db`.
- Restores original state by copying `data/fifa.db` back to `data/cmn/fifa.db`.
- Shows clearer runtime errors (permissions, missing files, invalid game folder).

## Requirements

- Windows
- Python 3.12+ (only needed for source execution or local build)

## Project Structure

- `fifa_db_switcher.py`: Main application source
- `FIFA07_DB_Switcher.spec`: PyInstaller build specification
- `build_exe.bat`: Build script
- `assets/`: UI images and icons
- `data/`: source database files used by the app

## Run From Source

```bat
py fifa_db_switcher.py
```

## Build EXE

```bat
build_exe.bat
```

To keep the terminal open after completion:

```bat
build_exe.bat --pause
```

Output binary:

- `dist/FIFA07_DB_Switcher.exe`

## Release Note

If the target game folder is under Program Files, run the app as administrator when write permission is denied.