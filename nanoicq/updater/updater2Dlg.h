// updater2Dlg.h : header file
//

#pragma once
#include "afxwin.h"


// Cupdater2Dlg dialog
class Cupdater2Dlg : public CDialog
{
// Construction
public:
	Cupdater2Dlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	enum { IDD = IDD_UPDATER2_DIALOG };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	void updateProcessText(const CString& str);


// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnBnClickedTest();
	CEdit m_folder;
	CEdit m_process;
	afx_msg void OnBnClickedScan();
	void doScan(const CString& folder);
};
