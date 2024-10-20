#include "saapi.h"

#include <tchar.h>

#include <fstream>
#include <locale>
#include <sstream>
#include <string>
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

HANDLE hPipe;

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)

{
  switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
      break;
  }
  return TRUE;
}

void InitPipe() { hPipe = CreateFile(_T("\\\\.\\pipe\\d4lf"), GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL); }

std::string ToNarrow(const wchar_t *s, char dfault = '?', const std::locale &loc = std::locale::classic()) {
  std::ostringstream stm;

  while (*s != L'\0') {
    stm << std::use_facet<std::ctype<wchar_t>>(loc).narrow(*s++, dfault);
  }
  stm << std::endl;
  return stm.str();
}

extern "C" bool SA_SayW(const wchar_t *str) {
  DWORD bytesWritten = 0;
  auto stest = ToNarrow(str);
  auto flg = WriteFile(hPipe, stest.c_str(), stest.length(), &bytesWritten, NULL);
  if (flg == FALSE) InitPipe();
  return true;
}

extern "C" bool SA_BrlShowTextW(const wchar_t *str) { return true; }

extern "C" bool SA_StopAudio() { return true; }

extern "C" bool SA_IsRunning() { return true; }
