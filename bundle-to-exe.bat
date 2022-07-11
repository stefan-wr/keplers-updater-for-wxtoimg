@echo off
call "python\scripts\env.bat"  %*
if not "%WINPYWORKDIR%"=="%WINPYWORKDIR1%" cd %WINPYWORKDIR1%

pyinstaller --clean bundle-to-exe.spec