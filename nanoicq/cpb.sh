#!/bin/sh

#
# $Id: cpb.sh,v 1.1 2006/08/28 10:04:21 lightdruid Exp $
#

V="0.1.2"

P=`pwd`
rm -Rf build-cpb
mkdir build-cpb
cp LICENSE README.* nanoicq HistoryDirection.py Plugin.py SingletonMixin.py antarctica.py buddy.py caps.py conversation.py events.py group.py history.py icq.py isocket.py logger.py message.py mm.py nanoicq.py proxy.py snacs.py utils.py build-cpb
cp -R plugins build-cpb
cp -R thirdparty build-cpb
mkdir -p build-cpb/sandbox/ui
cp sandbox/__init__.py build-cpb/sandbox
cd sandbox/ui
cp AboutDialog.py Captcha.py DynamicPanels.py FindUser.py Register.py StatusBar.py TrayIcon.py TrayIconWindows.py UserInfo.py __init__.py codes.py config.py encode_bitmaps.py errordialog.py gen-trayicon-stub.py guidebug.py iconset.py messagedialog.py misc.py persistence.py slider.py test.py tw.py userlistctrl.py version.py wxnanoicq.py ../../build-cpb/sandbox/ui
cp -R icons ../../build-cpb
cd $P
cp -R doc build-cpb

/usr/bin/find build-cpb -name CVS -print | xargs rm -rf

cat >build-cpb/nanoicq.config <<EOF
[icq]
default_charset = cp1251

incoming.bg = white
outgoing.bg = white

incoming.fg = blue
outgoing.fg = black

uin=203153632
password = q

host = login.icq.com:5190

# in seconds
keep.alive.interval = 57

[ui]
iconset = aox
show.offline = false
minimize.to.tray = true
show.window.in.taskbar = true
show.window.titlebar = true
show.window.statusbar = true
show.window.menu = true
raise.incoming.message = true
icon.blink.timeout = 1000
easy.move = true

#
EOF

[ -e nanoicq-${V} ] && rm -Rf nanoicq-${V}
mv build-cpb nanoicq-${V}
[ ! -e tmp ] && mkdir tmp
[ -e tmp/nanoicq-${V}.tar.gz ] && rm tmp/nanoicq-${V}.tar.gz
tar cvfz tmp/nanoicq-${V}.tar.gz nanoicq-${V}

echo "Done"

# ---
