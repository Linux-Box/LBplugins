#!/bin/sh
# Utils for LBPanel 
# GNU GPL2+

case $1 in
# Test updates for LBpanel and LBpanel Settings
init)
	sync ; echo 3 > /proc/sys/vm/drop_caches
	sysctl vm.dirty_background_ratio=1
	sysctl vm.min_free_kbytes=2192         
	sysctl vm.dirty_ratio=20
	sysctl vm.swappiness=10
	exit 0
	;;
testupdate)
	sync ; echo 3 > /proc/sys/vm/drop_caches
        opkg update
        opkg list-upgradable > /tmp/.list-upgradable
        for arg in `awk '/enigma2-plugin-extensions-lbpanel/{print $1}' /tmp/.list-upgradable` ; do
             opkg install $arg;
             echo "." > /tmp/.lbpanel.update
             echo "Installing $arg";
        done;
        rm -f /tmp/list-upgradable
                                                                
	exit 0
	;;

testsettings)
	sync ; echo 3 > /proc/sys/vm/drop_caches
	opkg update
	opkg list | grep '/enigma2-plugin-settings-sorys'  > /tmp/.list-upgradable
        for arg in `awk '/enigma2-plugin-settings-sorys/{print $1}' /tmp/.list-upgradable` ; do
                echo "Installing $arg";
                opkg install $arg;
                echo "." > /tmp/.lbsettings.update
        done;
        rm -f /tmp/.list-upgradable
                                                                
	exit 0
	;;
listcams)
	sync ; echo 3 > /proc/sys/vm/drop_caches
	opkg list | grep lbcam
	exit 0
	;;
update)
	sleep 5
	opkg update
	exit 0
	;;
appstore)
	sleep 2
	opkg install enigma2-plugin-extensions-extraappstore
	opkg update 
	;;
*)
	echo "Usage: lbutils.sh <util> [<option1>] [<option2>]" ;
	exit 1
	;;	
esac