:: This build script uses the MSVC command line tools to build Windows Executables
:: To launch the radie pyqt application

:: creates Console and GUI executables for:
:: - Embedded distribution (load python.dll after .exe loads)
:: - Standard Launcher for Python environment on the path (load python.dll at .exe load time)

@echo off

SET APPNAME=radie
set ZIPAPP=radie_qt_viewer

:: Bare Python installs for development headers/libraries
set PY3_x64=C:\Miniconda3\

set VCVARSALL="C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build\vcvarsall.bat"
if not exist %VCVARSALL% (
    set VCVARSALL="C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
)

:: Icon File
set LINK=%APPNAME%.res

:: use environment variables for INCLUDE LIB and LINK values
set UseEnv=true

:: Set environment variables for 64-bit and build
if "%1"=="NOVS" (
    echo "skipping vcvarsall"
) else (
    set LIB=""
    set INCLUDE=""
    call %VCVARSALL% amd64
)
rc.exe %APPNAME%.rc

:: set environment variables for python libraries
set LIB=%PY3_x64%libs;%LIB%
set INCLUDE=%PY3_x64%include;%INCLUDE%

call python -m zipapp %ZIPAPP% -o %ZIPAPP%.pyz

:: Compiler Flags
::  /EHsc -> Exception handling : If used with s (/EHsc), catches C++ exceptions only and tells the compiler to assume that functions declared as extern "C" never throw a C++ exception.
::  /DUNICODE /D_UNICODE -> Unicode preprocessor flags, in my case, fixes things like passing wchar_t pointers to functions expecting LPSTR, and other things as well.
::  /Fe -> Name of the exe file, used as /Fe%nameofexe%

echo Compiling embedded launchers
cl /EHsc /DUNICODE /D_UNICODE /DWINGUI embedded_runtime_launcher.cpp /Feout
COPY /B /Y out.exe+%ZIPAPP%.pyz %APPNAME%-embedded.exe

cl /EHsc /DUNICODE /D_UNICODE embedded_runtime_launcher.cpp /Feout
COPY /B /Y out.exe+%ZIPAPP%.pyz %APPNAME%-embedded-Console.exe

echo Compiling standard launchers
cl /EHsc /DUNICODE /D_UNICODE /DWINGUI standard_launcher.cpp /Feout
COPY /B /Y out.exe+%ZIPAPP%.pyz %APPNAME%.exe

cl /EHsc /DUNICODE /D_UNICODE standard_launcher.cpp /Feout
COPY /B /Y out.exe+%ZIPAPP%.pyz %APPNAME%-Console.exe

del out.exe
del *.obj

@echo on
