import threading        # 线程
import signal           # 信号槽
import sys              # 对解释器使用或维护的一些变量的访问
import serial           # 串口通信
import subprocess       # 启动新进程，用于CCD
import time             # 定时器
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QToolTip,QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore

from signalslot import slot                   # 信号槽文件
from transfer import trans                    # 通信文件
from Ui_control import Ui_Control
from Ui_pw1dialog import Ui_Dialog


import win32api,win32gui,win32con
from ctypes import windll
import subprocess
import pywintypes

# 继承了GUI和信号槽，与通信对象分开
class soft(QMainWindow,Ui_Control,slot):
    pop_signal = pyqtSignal(str)
    def __init__(self): 
        super(soft,self).__init__()
        self.number = "exe"
        trans.log_data(self,"user"," 开启软件-----------------------------\n")
        trans.log_data(self,"comm"," 开启软件-----------------------------\n")

        
        
        time.sleep(0.5)
        self.setupUi(self)    
            
        #self.init()                     # 参数初始化、开串口、设置轮询
        self.signalslot()               # 信号槽



# 更新GUI
def updateUi():
    print("更新UI界面")
    while True:
        #myWin.label_energy.setText(str(energy.energy_value))
        
        #print("更新UI界面成功")
        time.sleep(0.5)

# 预燃
def power_pre(num):
    time.sleep(0.01)
    print("点击了第%d个预燃按钮" % (num+1))
    if num == 0:    # A路种子源
        pre_on_order = "aa 01 12 cc 33 c3 3c"
        pre_off_order = "aa 01 10 cc 33 c3 3c"
        button_num = 0
    elif num == 7:  # B路种子源
        pre_on_order = "aa 08 12 cc 33 c3 3c"
        pre_off_order = "aa 08 10 cc 33 c3 3c"
        button_num = 1
        
    # 锁住线程，避免和轮询撞
    all_volt[num].threadLock.acquire()
    if myWin.pre[button_num].isChecked():  # 开
        does = "[开启]"
        send_order = pre_on_order
        set_button = True
    else:
        does = "[关闭]"
        send_order = pre_off_order
        set_button = False

    print("\n尝试%s第%d个预燃\n"%(does,num+1))
    all_volt[num].log_data("user","尝试%s第%d台预燃\n" % (does,num+1))
    state = all_volt[num].data_write(send_order)
    time.sleep(0.1)
    state = all_volt[num].data_write(send_order)
    if state == 0:  # 发送指令失败，按钮要变回原状
        myWin.pre[button_num].setChecked(bool(1-set_button))
        all_volt[num].log_data("user","%s第%d台预燃失败\n" % (does,num+1))
        print("\n未能%s第%d台预燃\n" % (does,num+1))
    else:
        print("\n成功%s第%d台预燃\n" % (does,num+1))
        all_volt[num].log_data("user","%s第%d台预燃成功\n" % (does,num+1))
        myWin.on[num].setEnabled(set_button)
    
    all_volt[num].threadLock.release()

    '''if myWin.pre[num].isChecked():  # 开
        print("开第%d台预燃"%(num+1))
        all_volt[num].log_data("user","尝试开启第%d台预燃\n" % (num+1))
        state = all_volt[num].data_write(pre_on_order)
        time.sleep(0.1)
        state = all_volt[num].data_write(pre_on_order)
        if state == 0:
            myWin.pre[num].setChecked(False)
            all_volt[num].log_data("user","开启第%d台预燃失败\n" % (num+1))
        else:
            print("成功开启第%d台预燃" % (num+1))
            all_volt[num].log_data("user","开启第%d台预燃成功\n" % (num+1))
            myWin.on[num].setEnabled(True)
    else:   # 关
        print("关第%d台预燃" %(num+1))
        all_volt[num].log_data("user","尝试关闭第%d台预燃\n" % (num+1))
        state = all_volt[num].data_write(myWin.pre_offorder[num])
        time.sleep(0.1)
        state = all_volt[num].data_write(myWin.pre_offorder[num])
        if state == 0:
            myWin.pre[num].setChecked(True)
            all_volt[num].log_data("user","关闭第%d台预燃失败\n" % (num+1))
        else:
            print("成功关闭第%d台预燃" % (num+1))
            myWin.on[num].setEnabled(False)
            all_volt[num].log_data("user","关闭第%d台预燃成功\n" % (num+1))'''



        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #energy = trans("192.168.1.160",23,17)
    volt1 = trans("192.168.1.121",8801,1)
    volt2 = trans("192.168.1.122",8802,2)
    volt3 = trans("192.168.1.123",8803,3)
    volt4 = trans("192.168.1.124",8804,4)
    volt5 = trans("192.168.1.125",8805,5)
    volt6 = trans("192.168.1.126",8806,6)
    volt7 = trans("192.168.1.127",8807,7)
    volt8 = trans("192.168.1.128",8808,8)
    volt9 = trans("192.168.1.129",8809,9)
    volt10 = trans("192.168.1.130",8810,10)
    volt11 = trans("192.168.1.131",8811,11)
    volt12 = trans("192.168.1.132",8812,12)
    volt13 = trans("192.168.1.133",8813,13)
    volt14 = trans("192.168.1.134",8814,14)




    all_volt = [volt1,volt2,volt3,volt4,volt5,volt6,volt7,
                volt8,volt9,volt10,volt11,volt12,volt13,volt14]



    #volt2 = trans("192.168.1.122",8802,2)
    # 建立多个通信对象，再在这修改界面

    myWin = soft()
    
    myWin.show()

    thread_updateUi = threading.Thread(target=updateUi)     # 目标函数不能带括号，函数如果有参数要写arg=()
    thread_updateUi.setDaemon(True)
    thread_updateUi.start()
    print("开启UI线程")

    myWin.pre1.clicked.connect(lambda:power_pre(0))

    myWin.pre8.clicked.connect(lambda:power_pre(7))




    sys.exit(app.exec_())    




