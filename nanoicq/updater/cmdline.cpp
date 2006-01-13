#include "stdafx.h"
//
//  MODULE:   cmdline.cpp
//
//	AUTHOR: Carlos Antollini 
//
//  mailto: cantollini@hotmail.com
//
//	Date: 09/29/2001
//
//	Version 1.01
// 

#include <afxwin.h>
#include "cmdline.h"


CCommandLine::CCommandLine()
{
	m_strCommandLine = _T("");
	m_strAppName = _T("");
	m_strAppPath = _T("");
	string = NULL;
	ParseCommandLine();
}

CCommandLine::~CCommandLine()
{
	m_strCommandLine = _T("");
	m_strAppName = _T("");
	m_strAppPath = _T("");

	if(string != NULL)
		free(string);
}

BOOL CCommandLine::GetFirstParameter(CString& strFlag, CString& strParam)
{
	int nParam = 0;
	char seps[] = " ";
	BOOL bRet = FALSE;
	
	strFlag = _T("");
	strParam = _T("");

	string = (char*)malloc(m_strCommandLine.GetLength() * sizeof(char) + 1);
	memset(string, 0, m_strCommandLine.GetLength() * sizeof(char));

	strcpy(string, m_strCommandLine.GetBuffer(0));
	
	token = strtok(string, seps );
	while(token != NULL && nParam < 2)
	{

		CString strToken = (LPCTSTR)token;

		if(nParam > 0)
		{	if(strToken.Left(1).FindOneOf("/-") != -1)
			{
				strFlag = strToken.Mid(1);
				token = strtok(NULL, seps);
				strToken = (LPCTSTR)token;
			}

			strParam = strToken;
			bRet = TRUE;
		}

		token = strtok(NULL, seps);
		nParam++;	
	}

	return bRet;	
}

BOOL CCommandLine::GetNextParameter(CString& strFlag, CString& strParam)
{
	char seps[] = " ";
	strFlag = _T("");
	strParam = _T("");

	if(token != NULL)
	{
		CString strToken = (LPCTSTR)token;

		if(strToken.Left(1).FindOneOf("/-") != -1)
		{
			strFlag = strToken.Mid(1);
			token = strtok(NULL, seps);
			strToken = (LPCTSTR)token;
		}

		strParam = strToken;
		token = strtok( NULL, seps );
		return TRUE;
	}

	return FALSE;
}

void CCommandLine::ParseCommandLine()
{
	CString strParam;
	CString strFlag;
	int nParam = 0;
	char seps[] = " ";
	BOOL bRet = FALSE;
	
	strFlag = _T("");
	strParam = _T("");

	m_strCommandLine = ::GetCommandLine();
	m_strCommandLine.TrimLeft();
	m_strCommandLine.TrimRight();
	m_strAppName = AfxGetAppName(); 

	string = (char*)malloc(m_strCommandLine.GetLength() * sizeof(char) + 1);
	memset(string, 0, m_strCommandLine.GetLength() * sizeof(char));

	strcpy(string, m_strCommandLine.GetBuffer(0));
	
	token = strtok(string, seps );
	while(token != NULL)
	{
		bRet = TRUE;

		CString strToken = (LPCTSTR)token;

		if(nParam == 0)
		{
			m_strAppPath = strToken;
			m_strAppPath.TrimLeft(34);
			m_strAppPath.TrimRight();
			m_strAppPath.TrimRight(34);
		}
		else
		{	if(strToken.Left(1).FindOneOf("/-") != -1)
			{
				strFlag = strToken.Mid(1);
				token = strtok(NULL, seps);
				strToken = (LPCTSTR)token;
			}

			strParam = strToken;
		}

		token = strtok(NULL, seps);

		if(nParam > 0)
		{
			ParseParam(strFlag, TRUE, strtok == NULL);
			ParseParam(strParam, FALSE, strtok == NULL);
		}
		nParam++;	
	}
}

