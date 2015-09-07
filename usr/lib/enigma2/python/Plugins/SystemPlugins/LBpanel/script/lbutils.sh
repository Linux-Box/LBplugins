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
	nohup /usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/script/lbutils.sh lbcron &
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
	sync ; echo 3 > /proc/sys/vm/drop_caches
	opkg update
	exit 0
	;;
appstore)
	sync ; echo 3 > /proc/sys/vm/drop_caches
	opkg install enigma2-plugin-extensions-extraappstore
	opkg update 
	;;
lbcron)
	x=$(ps -ef|grep -v grep|grep "lbutils.sh lbcron" |wc -l)
	echo $x 
	if [ "$x" -eq 3 ]; then
		echo "lbutils lbcron was already running"
		exit 2 
	fi
	while [ 1 ];do 
	  	for i in `ls /tmp/.runop*`; do
			chmod 777 $i
			$i
			rm -f $i*
 		 	touch $i."end"
	  	done
		sleep 1s
	done
	;;

*)
	echo "Usage: lbutils.sh <util> [<option1>] [<option2>]" ;
	exit 1
	;;	
esac