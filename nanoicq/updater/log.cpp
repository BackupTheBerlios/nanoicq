
#include "stdafx.h"

#include <sstream>

#include "log.h"

Log::Log(const string& fileName) : fileName_(fileName) {
    log_.open(fileName_.c_str(), ios_base::out | ios_base::app);
    write("Log started");
}
Log::Log() {
}

bool Log::open(const string& fileName) {
    fileName_ = fileName;
    log_.open(fileName_.c_str(), ios_base::out | ios_base::app);
	return log_.is_open();
}

Log::~Log() {
    write("Log closed\n");
    log_.close();
}

void Log::write(const string& msg) {
    write(DEFAULT, msg);
}

void Log::write(Level level, const string& msg) {
    log_ << format(level, msg) << endl;
}

void Log::write(const char* fmt, ...) {
    va_list argptr;
    va_start(argptr, fmt);
    char buff[255];

    _vsnprintf(buff, sizeof(buff), fmt, argptr);
    log_ << format(DEFAULT, buff) << endl;

    va_end(argptr);
}

const string Log::convertLevel(Level level) {
    switch(level) {
    case DEFAULT:
        return "DEFAULT";
        break;
    }

    return "Unknown";
}

std::string Log::format(Level level, const std::string& msg)
{
    const int mx = 255;
    char time_[mx], date_[mx];

    GetTimeFormat(LOCALE_SYSTEM_DEFAULT, 0, NULL, "HH:mm:ss", time_, mx - 1);
    GetDateFormat(LOCALE_SYSTEM_DEFAULT, 0, NULL, "dd-MM-yyyy", date_,
        mx - 1);

    std::stringstream rc;
    std::string sLevel = convertLevel(level);

    rc << date_ << " " << time_ << " " << sLevel
        << " " << msg;
    return rc.str();
}

Log* logger = Log::Instance("somefile.log");

