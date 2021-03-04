import sys
from PyQt5.QtCore import QTimer,pyqtSignal
import time 
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
from Ui_pw1dialog import Ui_Dialog
import threading
import transfer
from  Ui_control import Ui_Control

class slot():
    def signalslot(self):

        self.pre = [self.pre1,self.pre8]

        self.on=[self.on1,self.on2,self.on3,self.on4,self.on5,self.on6,self.on7,self.on8,
                    self.on9,self.on10,self.on11,self.on12,self.on13,self.on14]

        self.pw_v=[self.pw1_v_send,self.pw2_v_send,self.pw3_v_send,self.pw4_v_send,
                    self.pw5_v_send,self.pw6_v_send,self.pw7_v_send,self.pw8_v_send,
                    self.pw9_v_send,self.pw10_v_send,self.pw11_v_send,self.pw12_v_send,
                    self.pw13_v_send,self.pw14_v_send]

        self.relay = [self.relay1,self.relay2,self.relay3,self.relay4,self.relay5,self.relay6,self.relay7,
                      self.relay8,self.relay9,self.relay10,self.relay11,self.relay12,self.relay13,self.relay14]
        self.shutt = [self.shutter,self.shutter_2]

        
        self.on1.setEnabled(False)
        self.on8.setEnabled(False)
            
        self.pre_onorder = ["aa 01 12 cc 33 c3 3c","aa 02 12 cc 33 c3 3c","aa 03 12 cc 33 c3 3c","aa 04 12 cc 33 c3 3c",
                    "aa 05 12 cc 33 c3 3c","aa 06 12 cc 33 c3 3c","aa 07 12 cc 33 c3 3c","aa 08 12 cc 33 c3 3c",
                    
                    "aa 09 12 cc 33 c3 3c","aa 0a 12 cc 33 c3 3c","aa 0b 12 cc 33 c3 3c","aa 0c 12 cc 33 c3 3c",
                    "aa 0d 12 cc 33 c3 3c","aa 0e 12 cc 33 c3 3c"]

        self.pre_offorder = ["aa 01 10 cc 33 c3 3c","aa 02 10 cc 33 c3 3c","aa 03 10 cc 33 c3 3c","aa 04 10 cc 33 c3 3c",
                    "aa 05 10 cc 33 c3 3c","aa 06 10 cc 33 c3 3c","aa 07 10 cc 33 c3 3c","aa 08 10 cc 33 c3 3c",
                    
                    "aa 09 10 cc 33 c3 3c","aa 0a 10 cc 33 c3 3c","aa 0b 10 cc 33 c3 3c","aa 0c 10 cc 33 c3 3c",
                    "aa 0d 10 cc 33 c3 3c","aa 0e 10 cc 33 c3 3c"]

        self.on_onorder = ["aa 01 22 cc 33 c3 3c","aa 02 22 cc 33 c3 3c","aa 03 22 cc 33 c3 3c","aa 04 22 cc 33 c3 3c",
                "aa 05 22 cc 33 c3 3c","aa 06 22 cc 33 c3 3c","aa 07 22 cc 33 c3 3c","aa 08 22 cc 33 c3 3c",
                    
                    "aa 09 21 cc 33 c3 3c","aa 0a 21 cc 33 c3 3c","aa 0b 21 cc 33 c3 3c","aa 0c 21 cc 33 c3 3c",
                    "aa 0d 21 cc 33 c3 3c","aa 0e 21 cc 33 c3 3c"]

        self.on_offorder = ["aa 01 20 cc 33 c3 3c","aa 02 20 cc 33 c3 3c","aa 03 20 cc 33 c3 3c","aa 04 20 cc 33 c3 3c",
                    "aa 05 20 cc 33 c3 3c","aa 06 20 cc 33 c3 3c","aa 07 20 cc 33 c3 3c","aa 08 20 cc 33 c3 3c",
                    
                    "aa 09 20 cc 33 c3 3c","aa 0a 20 cc 33 c3 3c","aa 0b 20 cc 33 c3 3c","aa 0c 20 cc 33 c3 3c",
                    "aa 0d 20 cc 33 c3 3c","aa 0e 20 cc 33 c3 3c"]


        self.relay_on = ["0","1","2","3","4","5","6","7",
        
                "FE 05 00 00 98 35","FE 05 00 01 C9 F5","FE 05 00 02 39 F5","FE 05 00 03 68 35",
                "FE 05 00 04 D9 F4","FE 05 00 05 88 34","FE 05 00 06 78 34","FE 05 00 07 29 F4"]                

        self.relay_off = ["0","1","2","3","4","5","6","7",
        
                "FE 05 00 00 00 00 D9 C5","FE 05 00 01 00 00 88 05","FE 05 00 02 00 00 78 05","FE 05 00 03 00 00 29 C5",
                "FE 05 00 04 00 00 98 04","FE 05 00 05 00 00 C9 C4","FE 05 00 06 00 00 39 C4","FE 05 00 07 00 00 68 04"]


        self.shutter_onorder = ["FE 05 00 00 98 35","FE 05 00 01 C9 F5"]
        self.shutter_offorder = ["FE 05 00 00 00 00 D9 C5","FE 05 00 01 00 00 88 05"]
