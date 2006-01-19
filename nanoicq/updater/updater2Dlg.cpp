// updater2Dlg.cpp : implementation file
//

#include "stdafx.h"
#include "updater2.h"
#include "updater2Dlg.h"
#include "PathDialog.h"
#include ".\updater2dlg.h"
#include "scan.h"
#include <afxisapi.h>

#include <list>

using namespace std;

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

CEdit* global_process = 0;
int global_lines = 1;

// CAboutDlg dialog used for App About

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	enum { IDD = IDD_ABOUTBOX };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

// Implementation
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
END_MESSAGE_MAP()


// Cupdater2Dlg dialog



Cupdater2Dlg::Cupdater2Dlg(CWnd* pParent /*=NULL*/)
	: CDialog(Cupdater2Dlg::IDD, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void Cupdater2Dlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_FOLDER, m_folder);
	DDX_Control(pDX, IDC_EDIT2, m_process);
}

BEGIN_MESSAGE_MAP(Cupdater2Dlg, CDialog)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	//}}AFX_MSG_MAP
	ON_BN_CLICKED(ID_TEST, OnBnClickedTest)
	ON_BN_CLICKED(ID_SCAN, OnBnClickedScan)
END_MESSAGE_MAP()


// Cupdater2Dlg message handlers

BOOL Cupdater2Dlg::OnInitDialog()
{
	const CString mREG_KEY = "Software\\LA2Updater";
	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon

	// TODO: Add extra initialization here
	if (!CRegistry::KeyExists(mREG_KEY)) {
		// empty
	}
	bool rc = m_registry.Open(mREG_KEY, HKEY_LOCAL_MACHINE);
	CString tmp = m_registry["Last directory"];
	if(tmp.GetLength() != 0)
		m_folder.SetWindowText(tmp);

	CHttpServer* cs = new CHttpServer();

	return TRUE;  // return TRUE  unless you set the focus to a control
}

void Cupdater2Dlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void Cupdater2Dlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

// The system calls this function to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR Cupdater2Dlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

void Cupdater2Dlg::updateProcessText(const CString& str)
{
	CString curText;
	m_process.GetWindowText(curText);
	curText += str;
	curText += "\r\n";
	m_process.SetWindowText(curText);
	m_process.LineScroll(global_lines++);
}

void Cupdater2Dlg::OnBnClickedTest()
{
	// TODO: Add your control notification handler code here
	CString caption = "Choose LA2 directory";
	CString title = "";
	CString path = ".";
	CPathDialog* pathDialog = new CPathDialog(caption, title, path);

	if(pathDialog->DoModal() == IDOK) {
		m_folder.SetWindowText(pathDialog->GetPathName());
		updateProcessText(pathDialog->GetPathName());
		m_registry["Last directory"] = pathDialog->GetPathName();
	}
}

void cb(WIN32_FIND_DATA data, const string& md5) {
    printf("Called cb for %s\n", data.cFileName);
	CString curText;
	global_process->GetWindowText(curText);
	curText += data.cFileName;
	curText += " ";
	curText += md5.c_str();
	curText += "\r\n";
	global_process->SetWindowText(curText);

	//int len = global_process->GetLength();
    //global_process->SetFocus();
    //global_process->SetSel(len,len);

	global_process->LineScroll(global_lines++);

	//global_process->UpdateData(FALSE);
	//global_process->UpdateWindow();
}

void Cupdater2Dlg::OnBnClickedScan()
{
	// TODO: Add your control notification handler code here
	global_process = &(this->m_process);
	updateProcessText("Scan started");
	CString buffer;
	m_folder.GetWindowText(buffer);
	doScan(buffer);
	updateProcessText("Scan stopped");
}

void Cupdater2Dlg::doScan(const CString& folder)
{
	list<Item> items;
	Scanner scanner;
	scanner.traverse(folder.GetString(), items, cb);

	ofstream ofs("updater.list", ios_base::out);
	if(!ofs.good())
		return;
	for(list<Item>::iterator it = items.begin(); it != items.end(); it++) {
		ofs << (*it) << endl;
	}
	ofs.close();
}
