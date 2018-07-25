/* Minimal main program -- everything is loaded from the library. */

#define Py_LIMITED_API 1
#include "Python.h"

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

//#include "Windows.h"

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

    // here we inject the python application launching commands into the arguments array
    int newargc;
    newargc = argc + 1;
    wchar_t **newargv = new wchar_t*[newargc];

    // determine the path of the executable so we know the absolute path
    // of the python runtime and application directories
    wchar_t executable_name[MAX_PATH];
    if (GetModuleFileName(NULL, executable_name, MAX_PATH) == 0)
        return 1;

    newargv[0] = argv[0];
    newargv[1] = executable_name;
//    newargv[1] = argv[0];  // call executable as the python zipapp

    for (int i = 1; i < argc; i++) {
        newargv[i + 2] = argv[i];
    }

    //now call Py_Main with our arguments
    return Py_Main(newargc, newargv);
}