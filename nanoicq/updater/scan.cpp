#include "stdafx.h"

#include <iostream>
#include <list>
#include <sstream>
#include <fstream>
#include <functional>

//#include <windows.h>
#include <afxwin.h>

#include "MD5Checksum.h"
#include "scan.h"
#include "singleton.h"
#include "log.h"

using namespace std;

template <typename T, typename S>
T stream_cast(S const& val) {
    stringstream stream;
    stream << val;
    T rc;
    stream >> rc;
    return rc;
}

#define ZZ cerr << __FILE__ << ":" << __LINE__ << endl;

//typedef struct _WIN32_FIND_DATA {
//  DWORD dwFileAttributes;
//  FILETIME ftCreationTime;
//  FILETIME ftLastAccessTime;
//  FILETIME ftLastWriteTime;
//  DWORD nFileSizeHigh;
//  DWORD nFileSizeLow;
//  DWORD dwReserved0;
//  DWORD dwReserved1;
//  TCHAR cFileName[MAX_PATH];
//  TCHAR cAlternateFileName[14];
//} WIN32_FIND_DATA, 
//*PWIN32_FIND_DATA, 
//*LPWIN32_FIND_DATA;


template <class T>
void Scanner::dump(const T& lst) {
    cout << "Directories:" << endl;
    for(T::const_iterator it = lst.begin(); it != lst.end(); it++) {
        cout << (*it).c_str() << endl;
    }
}

bool Scanner::traverse(string curdir, list<Item>& result, dircb pfun) {
    bool rc = true;
    const char* top = strdup(curdir.c_str());
    list<string> dirs;
    HANDLE hFind = 0;

    log("\nCur dir: %s", curdir.c_str());
    dirs.push_back(curdir);

    while(!dirs.empty()) {

        curdir = dirs.front();
        dirs.pop_front();
        curdir += "\\*";

        log("Going to %s", curdir.c_str());

        FindClose(hFind);
        hFind = FindFirstFile(curdir.c_str(), &findData);

        if (hFind == INVALID_HANDLE_VALUE) {
            DWORD errCode = GetLastError();

            if(errCode == ERROR_NO_MORE_FILES) {
                // exit gracefully
                log("No more files in current directory");
                continue;
            }

            log("Invalid File Handle. GetLastError reports %d", 
                errCode);
            break;
        }

        while(FindNextFile(hFind, &findData)) {
            if( (strcmp(findData.cFileName, ".") == 0) || ((strcmp(findData.cFileName, "..") == 0)) ) {
                log("[%s] Skipping . and ..", curdir.c_str());
                continue;
            }

            if(findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
                log("%s is directory", findData.cFileName);

                string tmp = curdir.substr(0, curdir.length() - 1);
                tmp += findData.cFileName;
                dirs.push_back(tmp);
            } else {
                if(findData.dwFileAttributes & FILE_ATTRIBUTE_READONLY) {
                    log("%s is read only", findData.cFileName);
                } else {
                    log("%s looks like file", findData.cFileName);

                    string fullFileName = curdir.substr(0, curdir.length() - 1);
                    fullFileName += findData.cFileName;
                    string md5 = CMD5Checksum::GetMD5(fullFileName.c_str());

                    result.push_back(Item(fullFileName, md5,
                        findData.ftLastWriteTime));

                    if(pfun) {
                        (*pfun)(findData, md5);
                    }

                    log(md5.c_str());
                }
            }
            
        }
    }

    dump(dirs);

    log("Scan is done\n");

    return rc;
}

#if 0
class Test {
public:
    static void cb(WIN32_FIND_DATA data) {
        printf("Called Test::cb for %s\n", data.cFileName);
    }
};

void cb(WIN32_FIND_DATA data) {
    printf("Called cb for %s\n", data.cFileName);
}
#endif

#if 0
int main(int argc, char** argv) {
    A a;

    list<Item> result;
    if(argc == 1)
        a.traverse(".", result, &Test::cb);
    else
        a.traverse(argv[1], result, &Test::cb);
#if 0
    list<Item> items;
    for(int ii = 0; ii < 10; ii++) {
        string f, m;
        f = stream_cast<string>(ii);
        m = stream_cast<string>(ii + 100);
        Item item(f, m);
        items.push_back(item);
    }
#endif

    for(list<Item>::const_iterator it = result.begin(); it != result.end(); it++) {
        cout << (Item)(*it) << endl;
    }

    return 0;
}
#endif
