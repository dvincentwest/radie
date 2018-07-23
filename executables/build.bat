:: This build script uses the MSVC command line tools to build Windows Executables
:: To launch the radie pyqt datastructures application

SET APPNAME=radie
SET DISTRO=C:\Coding\Python\Distributions\Python36_x64

:: Bare Python installs for development headers/libraries
:: set PY3_x86=C:\Coding\Python\PythonReleases\Python36_32\
:: set PY3_x64=C:\Coding\Python\PythonReleases\Python36_64\
set VCVARSALL="C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build\vcvarsall.bat"

:: Icon File
set LINK=%APPNAME%.res

:: use environment variables for INCLUDE LIB and LINK values
set UseEnv=true

:: Set environment variables for 64-bit and build
@echo off
if "%1"=="NOVS" (
    echo "skipping vcvarsall"
) else (
    set LIB=""
    set INCLUDE=""
    call %VCVARSALL% amd64
)
rc.exe %APPNAME%.rc
@echo on

:: LIB and INCLUDE are necessary for load-time loading of the Python DLL
:: if we are doing run-time loading, we don't need these
:: set LIB=%PY3_x64%libs;%LIB%
:: set INCLUDE=%PY3_x64%include;%INCLUDE%

:: Compiler Flags
::  - /EHsc -> Exception handling : If used with s (/EHsc), catches C++ exceptions only and tells the compiler to assume that functions declared as extern "C" never throw a C++ exception.
:: /DUNICODE /D_UNICODE -> Unicode preprocessor flags, in my case, fixes things like passing wchar_t pointers to functions expecting LPSTR, and other things as well.
:: /Fe -> Name of the exe file, used as /Fe%nameofexe%
cl /EHsc /DUNICODE /D_UNICODE /DWINGUI %APPNAME%.cpp /Fe%APPNAME%
cl /EHsc /DUNICODE /D_UNICODE %APPNAME%.cpp /Fe%APPNAME%-Console

:: SOME TEST CODE
:: XCOPY %APPNAME%.exe %DISTRO%\%APPNAME%.exe /Y
:: XCOPY %APPNAME%-Console.exe %DISTRO%\%APPNAME%-Console.exe /Y

:: Set environment variables for 32-bit and build
:: call VCVARSALL x86
