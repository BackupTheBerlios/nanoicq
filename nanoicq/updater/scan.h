#ifndef scan_h
#define scan_h

#include <iostream>
#include <list>
#include <sstream>
#include <fstream>
#include <functional>

using namespace std;

typedef void (*dircb)(WIN32_FIND_DATA);

class Item {
    string fileName_;
    string md5_;
    FILETIME modTime_;

public:
    Item(const string& fileName, const string& md5, FILETIME modTime) :
        fileName_(fileName), md5_(md5), modTime_(modTime) {
    }

    bool operator==(const Item& item) {
        return fileName_.compare(item.fileName_) && md5_.compare(item.md5_) &&
            modTime_.dwLowDateTime == item.modTime_.dwLowDateTime &&
            modTime_.dwHighDateTime == item.modTime_.dwHighDateTime
            ;
    }

    friend ostream& operator<<(ostream& ofs, Item v) {
        ofs << v.fileName_.c_str()
            << " " 
            << v.modTime_.dwLowDateTime 
            << v.modTime_.dwHighDateTime 
            << " " 
            << v.md5_.c_str();
        return ofs;
    }

};


class Scanner {
    WIN32_FIND_DATA findData;

public:
    template <class T>
    void dump(const T& lst);

    bool traverse(string curdir, list<Item>& result, dircb pfun = 0);
};

#endif // scan_h

