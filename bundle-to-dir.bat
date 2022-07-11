@echo off
call "python\scripts\env_for_icons.bat"  %*
if not "%WINPYWORKDIR%"=="%WINPYWORKDIR1%" cd %WINPYWORKDIR1%

pyinstaller --clean bundle-to-dir.spec