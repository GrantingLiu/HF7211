import sys
from PyQt5.QtCore import QTimer,pyqtSignal
import time 
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
from Ui_pw1dialog import Ui_Dialog
import threading
import transfer
from  Ui_control import Ui_control

class slot():
    def signalslot(self):
        # 预燃按钮
        self.pre = [self.pre1,self.pre8]
        # 工作按钮
        self.on=[self.on1,self.on2,self.on3,self.on4,self.on5,self.on6,self.on7,self.on8,
                    self.on9,self.on10,self.on11,self.on12,self.on13,self.on14]

        # 电压按钮。注意第11台电源没有定义对象，其他程序要避开self.pw_v[10]
        self.pw_v=[self.pw1_v_send,self.pw2_v_send,self.pw3_v_send,self.pw4_v_send,
                    self.pw5_v_send,self.pw6_v_send,self.pw7_v_send,self.pw8_v_send,
                    self.pw9_v_send,self.pw10_v_send,1,self.pw12_v_send,
                    self.pw13_v_send,self.pw14_v_send]

        # 继电器按钮
        self.relay = [self.relay1,self.relay2,self.relay3,self.relay4,self.relay5,self.relay6,self.relay7,
                      self.relay8,self.relay9,self.relay10,self.relay11,self.relay12,self.relay13,self.relay14,
                      self.relay_A_Q,self.relay_B_Q]

        # shutter按钮
        self.shutt = [self.shutter,self.shutter_2]

        # 电压状态文本框
        self.volt_state = [self.VoltState_1,self.VoltState_2,self.VoltState_3,self.VoltState_4,self.VoltState_5,self.VoltState_6,self.VoltState_7,
                            self.VoltState_8,self.VoltState_9,self.VoltState_10,self.VoltState_11,self.VoltState_12,self.VoltState_13,self.VoltState_14]

        # 种子源的工作按钮初始化关闭
        self.on1.setEnabled(False)
        self.on8.setEnabled(False)
            
        # 开预燃指令。目前只用到1和8
        self.pre_onorder = ["aa 01 12 cc 33 c3 3c","aa 02 12 cc 33 c3 3c","aa 03 12 cc 33 c3 3c","aa 04 12 cc 33 c3 3c",
                    "aa 05 12 cc 33 c3 3c","aa 06 12 cc 33 c3 3c","aa 07 12 cc 33 c3 3c","aa 08 12 cc 33 c3 3c",
                    
                    "aa 09 12 cc 33 c3 3c","aa 0a 12 cc 33 c3 3c","aa 0b 12 cc 33 c3 3c","aa 0c 12 cc 33 c3 3c",
                    "aa 0d 12 cc 33 c3 3c","aa 0e 12 cc 33 c3 3c"]

        # 关预燃指令
        self.pre_offorder = ["aa 01 10 cc 33 c3 3c","aa 02 10 cc 33 c3 3c","aa 03 10 cc 33 c3 3c","aa 04 10 cc 33 c3 3c",
                    "aa 05 10 cc 33 c3 3c","aa 06 10 cc 33 c3 3c","aa 07 10 cc 33 c3 3c","aa 08 10 cc 33 c3 3c",
                    
                    "aa 09 10 cc 33 c3 3c","aa 0a 10 cc 33 c3 3c","aa 0b 10 cc 33 c3 3c","aa 0c 10 cc 33 c3 3c",
                    "aa 0d 10 cc 33 c3 3c","aa 0e 10 cc 33 c3 3c"]

        # 开工作指令
        self.on_onorder = ["aa 01 22 cc 33 c3 3c","aa 02 22 cc 33 c3 3c","aa 03 22 cc 33 c3 3c","aa 04 22 cc 33 c3 3c",
                "aa 05 22 cc 33 c3 3c","aa 06 22 cc 33 c3 3c","aa 07 22 cc 33 c3 3c","aa 08 22 cc 33 c3 3c",
                    
                    "aa 09 21 cc 33 c3 3c","aa 0a 21 cc 33 c3 3c","aa 0b 21 cc 33 c3 3c","aa 0c 21 cc 33 c3 3c",
                    "aa 0d 21 cc 33 c3 3c","aa 0e 21 cc 33 c3 3c"]

        # 关工作指令
        self.on_offorder = ["aa 01 20 cc 33 c3 3c","aa 02 20 cc 33 c3 3c","aa 03 20 cc 33 c3 3c","aa 04 20 cc 33 c3 3c",
                    "aa 05 20 cc 33 c3 3c","aa 06 20 cc 33 c3 3c","aa 07 20 cc 33 c3 3c","aa 08 20 cc 33 c3 3c",
                    
                    "aa 09 20 cc 33 c3 3c","aa 0a 20 cc 33 c3 3c","aa 0b 20 cc 33 c3 3c","aa 0c 20 cc 33 c3 3c",
                    "aa 0d 20 cc 33 c3 3c","aa 0e 20 cc 33 c3 3c"]

        # 前8个指令依次是：A路种子源供电（继电器第7位），A路六台电源供电（继电器1到6位），B路种子源供电（继电器第8位）
        # # 后8个指令依次是：B路6台电源供电（继电器1~6位），A路Q，B路Q
        self.relay_on = [
        "55 AA 00 03 00 02 07 0C","55 AA 00 03 00 02 01 06","55 AA 00 03 00 02 02 07","55 AA 00 03 00 02 03 08",
        "55 AA 00 03 00 02 04 09","55 AA 00 03 00 02 05 0A","55 AA 00 03 00 02 06 0B","55 AA 00 03 00 02 08 0D",

        "FE 05 00 00 FF 00 98 35","FE 05 00 01 FF 00 C9 F5","FE 05 00 02 FF 00 39 F5","FE 05 00 03 FF 00 68 35",
        "FE 05 00 04 FF 00 D9 F4","FE 05 00 05 FF 00 88 34",
        "55 AA 00 03 00 02 09 0E","55 AA 00 03 00 02 0A 0F"]                

        self.relay_off = [
        "55 AA 00 03 00 01 07 0B","55 AA 00 03 00 01 01 05","55 AA 00 03 00 01 02 06","55 AA 00 03 00 01 03 07",
        "55 AA 00 03 00 01 04 08","55 AA 00 03 00 01 05 09","55 AA 00 03 00 01 06 0A","55 AA 00 03 00 01 08 0C",
    
        "FE 05 00 00 00 00 D9 C5","FE 05 00 01 00 00 88 05","FE 05 00 02 00 00 78 05","FE 05 00 03 00 00 29 C5",
        "FE 05 00 04 00 00 98 04","FE 05 00 05 00 00 C9 C4",
        "55 AA 00 03 00 01 09 0D","55 AA 00 03 00 01 0A 0E"]

        # 开关shutter
        self.shutter_onorder = ["FE 05 00 00 98 35","FE 05 00 01 C9 F5"]
        self.shutter_offorder = ["FE 05 00 00 00 00 D9 C5","FE 05 00 01 00 00 88 05"]
