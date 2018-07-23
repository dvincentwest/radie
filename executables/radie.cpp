/* source code for a python application launcher
*
* This code is primarily intended for use in a suite of applications
* with an embedded python runtime available
*
* The code creates a launcher that will start
* a python application by injecting the proper command line arguments
* that would normally be expected by python.exe.  The command line
* arguments fed to this launcher then become the subsequent
*
* The pythonXX.dll is loaded dynamically at run time, rather than at load
* time.  This allows us to specify the location of the dll within the code
* allowing more flexibility when packaging a python appication with the
* python environment
*
*/

// requires _CRT_SECURE_NO_WARNINGS flag to compile deprecated path operations

// replace #include "stdafx.h"
#pragma once
#include <SDKDDKVer.h>  // #include "targetver.h"

#define WIN32_LEAN_AND_MEAN             // Exclude rarely-used stuff from Windows headers
// Windows Header Files:
#include <windows.h>

// C RunTime Header Files
#include <stdlib.h>
#include <malloc.h>
#include <memory.h>
#include <tchar.h>
// end include stdfax.h

#include "Windows.h"
#include "Shlwapi.h"
// #include "Python.h"  // don't need this as we are dynamically loading the library of choice
#include <string>
#include <sstream>
#include <iostream>

#pragma comment(lib, "Shlwapi.lib")
#pragma warning(disable:4996)  // # _CRT_SECURE_NO_DEPRECIATE

wchar_t SWITCH[] = L"-m";
wchar_t APP[] = L"radie.qt.viewer";

#ifdef ROOTRUN
wchar_t runtime_dir[] = L"";
#else
wchar_t runtime_dir[] = L"\\runtime";
#endif

wchar_t applications_dir[] = L"\\apps";
wchar_t python_dll[] = L"\\python36.dll";

// define the pythonXX.dll function call signature for the Py_Main function
typedef int(__stdcall *py_main_function)(int, wchar_t**);
typedef void(__stdcall *py_setpath_function)(const wchar_t *);

using namespace std;

#ifdef WINGUI
int APIENTRY wWinMain(
    _In_ HINSTANCE hInstance,
    _In_opt_ HINSTANCE hPrevInstance,
    _In_ LPWSTR    lpCmdLine,
    _In_ int       nCmdShow
) {
    int argc = __argc;
    wchar_t **argv = __wargv;
#else
int wmain(int argc, wchar_t **argv) {
#endif
    
    // determine the path of the executable so we know the absolute path
    // of the python runtime and application directories
    wchar_t executable_dir[MAX_PATH];
    if (GetModuleFileName(NULL, executable_dir, MAX_PATH) == 0)
        return 1;
    PathRemoveFileSpec(executable_dir);
    wstring executable_dir_string(executable_dir);

    // When the launcher is not run from within the same directory as the 
    // pythonXX.dll, we have to set the PYTHONHOME environment variable in
    // order to correctly use the right python environment
    wstring python_home(L"PYTHONHOME=" + executable_dir_string + runtime_dir);
    _wputenv(python_home.c_str());

    // by setting PYTHONPATH we overwrite any system settings, and we can also 
    // set a separate directory for our code that we want isolated from the runtime
    wstring python_path(L"PYTHONPATH=" + executable_dir_string + applications_dir);
    _wputenv(python_path.c_str());

    // put the python runtime at the front of the path
    wstringstream ss;
    ss << "PATH=" << executable_dir << runtime_dir << ";" << getenv("PATH");
    wstring path_string(ss.str());
    _wputenv(path_string.c_str());

    // dynamically load the python dll
    wstring python_dll_path(executable_dir_string + runtime_dir + python_dll);
    HINSTANCE hGetProcIDDLL = LoadLibrary(python_dll_path.c_str());
    py_main_function Py_Main = (py_main_function)GetProcAddress(hGetProcIDDLL, "Py_Main");
    py_setpath_function Py_SetPath = (py_setpath_function)GetProcAddress(hGetProcIDDLL, "Py_SetPath");
    

    // here we inject the python application launching commands into the arguments array
    int newargc;
    newargc = argc + 2;

    wchar_t **newargv = new wchar_t*[newargc];
    newargv[0] = argv[0];
    newargv[1] = SWITCH;
    newargv[2] = APP;

    for (int i = 1; i < argc; i++) {
        newargv[i + 2] = argv[i];
    }
    
    //just a little debug check
    //for (int i=0;i<newargc;i++) {wcout << newargv[i] << endl;}

    //now call Py_Main with our arguments
    return Py_Main(newargc, newargv);
    //Py_SetPath(python_home.c_str());
    //return Py_Main(argc, argv);

}
