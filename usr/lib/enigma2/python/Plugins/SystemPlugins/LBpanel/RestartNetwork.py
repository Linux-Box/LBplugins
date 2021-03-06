from Components.Network import iNetwork
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.Label import Label
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext, os

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("lbpanel")
gettext.bindtextdomain("lbpanel", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "SystemPlugins/LBpanel/locale/"))

def _(txt):
        t = gettext.dgettext("lbpanel", txt)
        if t == txt:
                t = gettext.gettext(txt)
        return t

class RestartNetwork(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        skin = """
            <screen name="RestartNetwork" position="center,center" size="600,100" title="LBpanel - Restart Network Adapter">
            <widget name="label" position="10,30" size="500,50" halign="center" font="Regular;20" transparent="1" foregroundColor="white" />
            </screen> """
        self.skin = skin
        self["label"] = Label(_("Please wait while your network is restarting..."))
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.restartLan)

    def setWindowTitle(self):
        self.setTitle(_("LBpanel - Restart Network Adapter"))

    def restartLan(self):
        iNetwork.restartNetwork(self.restartLanDataAvail)
  
    def restartLanDataAvail(self, data):
        if data is True:
            iNetwork.getInterfaces(self.getInterfacesDataAvail)

    def getInterfacesDataAvail(self, data):
        self.close()