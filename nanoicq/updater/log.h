
#ifndef log_h
#define log_h

#include <string>
#include <fstream>

#include "singleton.h"

using namespace std;

enum Level {
    DEFAULT
};

class Log : public CSingleton<Log> {
    string fileName_;
    ofstream log_;

public:
    Log(const string& fileName);
    Log();

    bool open(const string& fileName);

    ~Log();

    void write(const string& msg);
    void write(Level level, const string& msg);
    void write(const char* fmt, ...);

private:
    const string convertLevel(Level level);
    virtual std::string format(Level level, const std::string& msg);
};

extern Log* logger;

#define log logger->write

#endif // log_g
