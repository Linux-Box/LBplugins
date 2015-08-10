#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import os
import sys

try:
        oimg="http://appstore.linux-box.es/preview/%s_all.ipk.png" % sys.argv[1]
        dimg="/tmp/%s" % sys.argv[2]
        swait="/tmp/.lbwait%s" % sys.argv[2]
        print "Descargando %s a %s" % (oimg, dimg)
        urllib.urlretrieve (oimg, dimg)
        print "Borrando %s" % swait
        os.remove(swait)
except:
        swait="/tmp/.lbwait%s" % sys.argv[2]
        os.remove(swait)
        os.remove(dimg)
        print "Error download image - %s" % oimg  
