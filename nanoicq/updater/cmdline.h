//
//  MODULE:   cmdline.h
//
//	AUTHOR: Carlos Antollini 
//
//  mailto: cantollini@hotmail.com
//
//	Date: 09/29/2001
//
//	Version 1.01
// 


#include <afx.h>

class CCommandLine: public CCommandLineInfo
{
public:
	CCommandLine();
	~CCommandLine();

public:
	BOOL GetFirstParameter(CString& strFlag, CString& strParam);
	BOOL GetNextParameter(CString& strFlag, CString& strParam);
	void GetCommandLine(CString& strCommand) 
		{strCommand = m_strCommandLine;};
	void GetAppName(CString& strAppName)
		{strAppName = m_strAppName;};
	void GetAppPath(CString& strAppPath)
		{strAppPath = m_strAppPath;};

protected: 
	void ParseCommandLine();

protected:
	CString m_strCommandLine;
	CString m_strAppName;
	CString m_strAppPath;
	char *token;
	char* string;

};