#!/usr/bin/env python

# Copyright (C) 2011 by Eka A. Kurniawan
# eka.a.kurniawan(ta)gmail(tod)com
#
# This program is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import sys, serial, glob
from PyQt4.QtGui import QApplication, QMainWindow, QTextCursor
from PyQt4.QtCore import QObject, SIGNAL, SLOT, QTimer
from mainWindow import Ui_MainWindow

baudRates = ['9600',
             '38400',
             '115200',
             '1200000',]

class CMainWindow(QMainWindow):
   def __init__(self, *args):
      apply(QMainWindow.__init__, (self, ) + args)
      self.ui = Ui_MainWindow()
      self.setupUi()
      self.ser = None
      self.logTimer = None
      self.printInfo("Ready...")

   def setupUi(self):
      self.ui.setupUi(self)
      self.ui.baudRateComboBox.addItems(baudRates)
      self.refreshPorts()
      QObject.connect(self.ui.exitPushButton, SIGNAL("clicked()"), self, SLOT("close()"))
      QObject.connect(self.ui.refreshPortsPushButton, SIGNAL("clicked()"), self.refreshPorts)
      QObject.connect(self.ui.connectPushButton, SIGNAL("clicked()"), self.connect)
      QObject.connect(self.ui.disconnectPushButton, SIGNAL("clicked()"), self.disconnect)
      QObject.connect(self.ui.cmdLineEdit, SIGNAL("returnPressed()"), self.processCmd)

   def getUSBPorts(self):
      return glob.glob("/dev/ttyUSB*")

   def getSPPorts(self):
      return glob.glob("/dev/ttyS*")
   
   def getSelectedPort(self):
      return self.ui.portsComboBox.currentText()
   
   def getSelectedBaudRate(self):
      return self.ui.baudRateComboBox.currentText()

   def refreshPorts(self):
      self.ui.portsComboBox.clear()
      self.ui.portsComboBox.addItems(sorted(self.getUSBPorts()))
      self.ui.portsComboBox.addItems(sorted(self.getSPPorts()))

   def connect(self):
      self.disconnect()
      try:
         self.printInfo("Connecting to %s with %s baud rate." % \
                        (self.getSelectedPort(), self.getSelectedBaudRate()))
         self.ser = serial.Serial(str(self.getSelectedPort()), \
                                  int(self.getSelectedBaudRate()))
         self.startPooling()
         self.printInfo("Connected successfully.")
      except:
         self.ser = None
         self.printError("Failed to connect!")

   def disconnect(self):
      self.stopPooling()
      if self.ser == None: return
      try:
         if self.ser.isOpen:
            self.ser.close()
            self.printInfo("Disconnected successfully.")
      except:
         self.printError("Failed to disconnect!")
      self.ser = None

   def printInfo(self, text):
      self.ui.logPlainTextEdit.appendPlainText(text)
   
   def printError(self, text):
      self.ui.logPlainTextEdit.appendPlainText(text)
   
   def printCmd(self, text):
      self.ui.logPlainTextEdit.appendPlainText("> " + text + "\n\n")

   def updateLog(self, text):
         self.ui.logPlainTextEdit.moveCursor(QTextCursor.End)
         self.ui.logPlainTextEdit.insertPlainText(text)
         self.ui.logPlainTextEdit.moveCursor(QTextCursor.End)

   def startPooling(self):
      self.stopPooling()
      self.logTimer = QTimer()
      QObject.connect(self.logTimer, SIGNAL("timeout()"), self.checkBuffer)
      self.logTimer.start(10)
      
   def stopPooling(self):
      if self.logTimer == None: return
      self.logTimer.stop()

   def checkBuffer(self):
      inWaiting = self.ser.inWaiting()
      if inWaiting:
         self.updateLog(self.ser.read(inWaiting))

   def processCmd(self):
      cmd = self.ui.cmdLineEdit.text()
      self.printCmd(cmd)
      self.ser.write(str(cmd))
      self.ui.cmdLineEdit.clear()

   def closeEvent(self, event):
      self.disconnect()

   
if __name__ == "__main__":
   app = QApplication(sys.argv)
   mainWindow = CMainWindow()
   mainWindow.show()
   sys.exit(app.exec_())

