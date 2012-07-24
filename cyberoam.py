from PyQt4 import QtGui, QtCore
from xml.dom.minidom import parseString
import urllib, sys, time, base64, threading

class CyberoamLogin(threading.Thread):
    
    def  __init__(self,client,address,user):
        
        threading.Thread.__init__ ( self )
        self.logoutSignal=0
        self.timeout=180
        self.address=address
        self.user=user
        self.client=client
        
    def logout(self):
        
        self.logoutSignal=1
        
    def run(self):
        
        count=0
        while self.logoutSignal==0:
            count+=1
            if count==self.timeout:
                count=0
                try:
                    myfile = urllib.urlopen(self.address + "/live?mode=192&username=" + self.user + "&a=" + (str)((int)(time.time() * 1000)))
                except IOError:
                    print "Error connecting"
                    sys.exit(1)
                data = myfile.read()
                myfile.close()
                dom = parseString(data)
                xmlTag = dom.getElementsByTagName('ack')[0].toxml()
                message = xmlTag.replace('<ack>', '').replace('</ack>', '')
                if message!='ack':
                    self.client.updateStatus("Error Logging In")
                    return
            time.sleep(1)

class Cyberoam(QtGui.QWidget):
    
    def __init__(self):
        
        super(Cyberoam, self).__init__()
        self.initializeSettings()
        self.createwindow()
        self.placeContents()
        self.attachSignals()
        self.initializeSystemTray()
        self.autologin()
        
    def initializeSettings(self):
        self.loggedIn=0
        self.actionMessages=['Login','Logout']
        
        self.userSettings={'url':'https://172.16.1.1:8090','askonexit':'1','autologin':'0','lastuser':'null','lastpassword':'null','rememberme':'1'}
        self.savedSettings=QtCore.QSettings("cyberoam-client","cyberoam")
        for key in self.userSettings.iterkeys():
            if(self.savedSettings.contains(key)):
                self.userSettings[key]=str(self.savedSettings.value(key).toString())
            else:
                self.savedSettings.setValue(key,self.userSettings[key])
        if self.userSettings['lastuser']!="null":
            self.user=self.userSettings['lastuser']
        else:
            self.user=""
        if self.userSettings['lastpassword']!="null":
            self.password=base64.b64decode(self.userSettings['lastpassword'])
        else:
            self.password=""
                
    def createwindow(self):
        
        self.setFixedSize(300, 240)
        self.setWindowTitle("Cyberoam Client")
        self.setWindowIcon(QtGui.QIcon("cyberoam.png"))
        
        #center window
        qr=self.frameGeometry()
        center=QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(center)
        self.move(qr.topLeft())
        
    def placeContents(self):
        
        self.userLabel=QtGui.QLabel("Username")
        self.passwordLabel=QtGui.QLabel("Password")
        
        self.userField=QtGui.QLineEdit()
        self.passwordField=QtGui.QLineEdit()
        self.passwordField.setEchoMode(QtGui.QLineEdit.Password)
        
        self.rememberField=QtGui.QCheckBox("Remember Me")
        
        self.actionButton=QtGui.QPushButton(self.actionMessages[self.loggedIn])
        self.exitButton=QtGui.QPushButton("Exit")
        self.settingsButton=QtGui.QPushButton("Settings")
        
        self.statusLabel=QtGui.QTextEdit()
        self.statusLabel.setText("Not Logged In")
        self.statusLabel.setReadOnly(True)
        
        layout = QtGui.QGridLayout()
        layout.setSpacing(10)
        
        layout.addWidget(self.userLabel,1,0)
        layout.addWidget(self.passwordLabel,2,0)
        layout.addWidget(self.userField,1,1)
        layout.addWidget(self.passwordField,2,1)
        layout.addWidget(self.rememberField,3,0)
        layout.addWidget(self.actionButton,4,0)
        layout.addWidget(self.settingsButton,4,1)
        layout.addWidget(self.exitButton,5,1)
        layout.addWidget(self.statusLabel,6,0,1,2)
                
        self.setLayout(layout)
        
        self.userField.setText(self.user)
        self.passwordField.setText(self.password)
        if self.userSettings['rememberme']=='1':
            self.rememberField.setChecked(True)
        
    def attachSignals(self):
        
        self.actionButton.clicked.connect(self.handleActionButton)
        self.settingsButton.clicked.connect(self.showSettingsWindow)
        self.exitButton.clicked.connect(self.exitApp)
        
    def initializeSystemTray(self):
        
        tray=QtGui.QSystemTrayIcon(QtGui.QIcon("cyberoam.png"),self)
        menu=QtGui.QMenu(self)
        exitAction = menu.addAction("Exit")
        exitAction.activated.connect(self.exitApp)
        tray.setContextMenu(menu)
        
        tray.activated.connect(self.handleTrayAction)
        tray.show()
        
    def autologin(self):
        
        if self.userSettings['autologin']=='1' and self.userSettings['lastuser']!="null" and self.userSettings['lastpassword']!="null":
            self.login()
        else:
            self.updateStatus("Could not auto login. Username or password not saved")
        
    def handleTrayAction(self): 
        
        if self.isHidden():
            self.show()
        else:
            self.hide()
               
    def handleActionButton(self):
        
        if self.loggedIn==0:            
            if self.userField.text()=="" or self.passwordField.text()=="":
                self.updateStatus("Username or Password Missing!")
                return          
            self.user=str(self.userField.text())
            self.password=str(self.passwordField.text())
            val={}
            if self.rememberField.isChecked():
                val['lastuser']=self.user
                val['rememberme']='1'
                val['lastpassword']=base64.b64encode(self.password)
            else:
                val['lastuser']=self.user
                val['rememberme']='0'
                val['lastpassword']="null"
            self.saveSettings(val)
            self.login()
        elif self.loggedIn==1:
            self.logout()
    
    def showSettingsWindow(self):
        
        self.settingsWindow=QtGui.QDialog(self)
        self.settingsWindow.setFixedSize(250,150)
        self.settingsWindow.setWindowTitle("Settings")
        
        urlLabel=QtGui.QLabel("Url")
        askOnExitLabel=QtGui.QLabel("Ask On Exit")
        autoLoginLabel=QtGui.QLabel("Auto Login")
        
        self.urlField=QtGui.QLineEdit()
        
        self.askOnExitField=QtGui.QCheckBox()
        self.autoLoginField=QtGui.QCheckBox()
        
        okButton=QtGui.QPushButton("OK")
        okButton.clicked.connect(self.handleSaveSettings)
        cancelButton=QtGui.QPushButton("Cancel")
        cancelButton.clicked.connect(self.settingsWindow.close)
        
        layout=QtGui.QGridLayout()
        
        layout.addWidget(urlLabel,1,0)
        layout.addWidget(self.urlField,1,1)
        layout.addWidget(askOnExitLabel,2,0)
        layout.addWidget(self.askOnExitField,2,1)
        layout.addWidget(autoLoginLabel,3,0)
        layout.addWidget(self.autoLoginField,3,1)
        layout.addWidget(okButton,4,0)
        layout.addWidget(cancelButton,4,1)
        
        self.settingsWindow.setLayout(layout)
        
        self.settingsWindow.show()
        
        self.urlField.setText(self.userSettings['url'])
        if self.userSettings['askonexit']=='1':
            self.askOnExitField.setChecked(True)
        if self.userSettings['autologin']=='1':
            self.autoLoginField.setChecked(True)
        
    def saveSettings(self,val):
        
        for key in val.iterkeys():
            self.userSettings[key]=str(val[key])
            self.savedSettings.setValue(key,str(val[key]))
        self.savedSettings.sync()
    
    def handleSaveSettings(self):
        
        val={}
        val['url']=self.urlField.text()
        if self.askOnExitField.isChecked():
            val['askonexit']='1'
        else:
            val['askonexit']='0'
        if self.autoLoginField.isChecked():
            val['autologin']='1'
        else:
            val['autologin']='0'
        self.saveSettings(val)
        self.settingsWindow.close()
        
    def updateStatus(self,message):
        
        self.statusLabel.setText(message)
    
    def login(self):
        
        cyberoamAddress=self.userSettings['url'].strip(" /")
        username=self.user
        password=self.password
        
        try:
            myfile = urllib.urlopen(cyberoamAddress + "/login.xml", "mode=191&username=" + username + "&password=" + password + "&a=" + (str)((int)(time.time() * 1000)))
        except IOError:
            self.updateStatus("Error Connecting")
            return
        data = myfile.read()
        myfile.close()
        dom = parseString(data)
        xmlTag = dom.getElementsByTagName('message')[0].toxml()
        message = xmlTag.replace('<message>', '').replace('</message>', '').replace('<message/>', '')
        xmlTag = dom.getElementsByTagName('status')[0].toxml()
        status = xmlTag.replace('<status>', '').replace('</status>', '')
        
        if status.lower()=='live':
            self.updateStatus(message)
            self.loggedIn=1
            self.userField.setEnabled(False)
            self.passwordField.setEnabled(False)
            self.rememberField.setEnabled(False)
            self.actionButton.setText(self.actionMessages[self.loggedIn])
            self.passwordField.setText("abcdefghijklmnopqrstuvwxyz")
            self.loginThread=CyberoamLogin(self,cyberoamAddress,username)
            self.loginThread.start()
        else:
            self.updateStatus("Error: "+message)
            return
    
    def logout(self):
        
        if self.loggedIn==1:
            
            self.loginThread.logout()
            self.loginThread.join()
            
            cyberoamAddress=self.userSettings['url']
            username=self.user
            
            try:
                myfile = urllib.urlopen(cyberoamAddress + "/logout.xml", "mode=193&username=" + username + "&a=" + (str)((int)(time.time() * 1000)))
            except IOError:
                self.updateStatus("Error Connecting")
                return
            data = myfile.read()
            myfile.close()
            dom = parseString(data)
            xmlTag = dom.getElementsByTagName('message')[0].toxml()
            message = xmlTag.replace('<message>', '').replace('</message>', '').replace('<message/>', '')
            if message=="":
                message="Logout request did not complete successfully. Probably you are already logged out."
            self.updateStatus(message)
            
            if self.userSettings['lastpassword']!='null':
                self.passwordField.setText(self.password)
            else:
                self.passwordField.setText("")
            self.loggedIn=0
            self.userField.setEnabled(True)
            self.passwordField.setEnabled(True)
            self.rememberField.setEnabled(True)
            self.actionButton.setText(self.actionMessages[self.loggedIn])
    
    def closeEvent(self,event):
        
        self.hide()
        event.ignore()
    
    def exitApp(self):
        
        if self.userSettings['askonexit']=='1':
            reply=QtGui.QMessageBox.question(self,"Exit Cyberoam","Are you sure you want to quit?",QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply!=QtGui.QMessageBox.Yes:
                return
        self.logout()
        QtCore.QCoreApplication.instance().quit()

def main():
    
    app=QtGui.QApplication(sys.argv)
    client=Cyberoam()
    client.show()
    sys.exit(app.exec_())
    
if __name__=="__main__":
    main()