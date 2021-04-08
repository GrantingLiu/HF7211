import threading        # 线程
import signal           # 信号槽
import sys              # 对解释器使用或维护的一些变量的访问
import serial           # 串口通信
import subprocess       # 启动新进程，用于CCD
import time             # 定时器
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QToolTip,QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore,QtGui, QtWidgets
from PyQt5.QtGui import *

from signalslot import slot                   # 信号槽文件
from transfer import trans                    # 通信文件
from Ui_control import Ui_control             # 主界面
from Ui_pw1dialog import Ui_Dialog            # 设置电压的弹出窗口
import image_rc

import win32api,win32gui,win32con
from ctypes import windll
import subprocess
import pywintypes
#from camera import *

import numpy



# 继承了GUI和信号槽，与通信对象分开
class soft(QMainWindow,Ui_control,slot):
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
        for i in range(0,14):
            #all_volt[i].threadLock.acquire()
            if i == 10:
                # 第10台无法读电压
                #myWin.volt11_set.setText(str(all_volt[i].voltage))
                pass
            else:
                myWin.pw_v[i].setText(str(all_volt[i].voltage))
                if all_volt[i].voltage != "loading":
                    print("设置第%d台设备电压为：%s" % (i+1,str(all_volt[i].voltage)))
            #all_volt[i].threadLock.release()
        myWin.label_energy.setText(str(energy.energy_value))
        time.sleep(1)

def updateUi_relay():
    while True:
        relay_1.threadLock.acquire()
        myWin.relay_state_1.setText(relay_1.relay_connect_state_1)
        for i in range(0,len(relay_1.relay_1_switch)-2):    # -2是因为最后两个是Q
            myWin.relay[i].setChecked(relay_1.relay_1_switch[i])
        relay_1.threadLock.release()
        relay_2.threadLock.acquire()
        myWin.relay_state_2.setText(relay_2.relay_connect_state_2)
        # 第2台继电器，B路的6台电源
        for i in range(0,len(relay_2.relay_2_switch)):
            myWin.relay[i+8].setChecked(relay_2.relay_2_switch[i])
        relay_2.threadLock.release()
        time.sleep(1)


# 继电器供电
def power_relay(num):
    relay_1.threadLock.acquire()
    relay_2.threadLock.acquire()
    print("点击了第%d个供电按钮" % (num+1))
    if num < 8 or num > 13:
        print("第1台继电器")
        num_index = 14
        #relay_1.relay_1_switch[num] = myWin.relay[num].isChecked()
    else:
        print("第2台继电器")
        num_index = 15
        #relay_2.relay_2_switch[num] = myWin.relay[num].isChecked()
    
    
    if myWin.relay[num].isChecked():
        does = "[开启]第%d台供电" % (num+1)
        send_order =  myWin.relay_on[num]
        set_button = True
    else:
        does = "[关闭]第%d台供电" % (num+1)
        send_order =  myWin.relay_off[num]
        set_button = False

    print("\n尝试%s\n"%(does))
    all_volt[num_index].log_data("user","尝试%s" % (does))
    state_1 = all_volt[num_index].data_write(send_order)
    time.sleep(0.1)
    state_2 = all_volt[num_index].data_write(send_order)
    state = state_1 + state_2
    if state == 0:  # 发送指令失败，按钮要变回原状
        now_state = bool(1-set_button)
        all_volt[num_index].log_data("user","%s失败\n" % (does))
        #print("\n未能%s\n" % (does))
    else:
        print("\n成功%s\n" % (does))
        all_volt[num_index].log_data("user","%s成功\n" % (does))
        now_state = set_button
    myWin.relay[num].setChecked(now_state)
    if num < 8:
        relay_1.relay_1_switch[num] = now_state
    elif num > 13:
        relay_1.relay_1_switch[num-6] = now_state
    else:
        relay_2.relay_2_switch[num-8] = now_state
    relay_1.threadLock.release()
    relay_2.threadLock.release()

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
        does = "[开启]第%d台预燃" % (num+1)
        send_order = pre_on_order
        set_button = True
    else:
        does = "[关闭]第%d台预燃" % (num+1)
        send_order = pre_off_order
        set_button = False
    print("\n尝试%s\n"%(does))
    all_volt[num].log_data("user","尝试%s\n" % (does))
    state_1 = all_volt[num].data_write(send_order)
    time.sleep(0.1)
    state_2 = all_volt[num].data_write(send_order)
    state = state_1 + state_2
    if state == 0:  # 发送指令失败，按钮要变回原状
        myWin.pre[button_num].setChecked(bool(1-set_button))
        all_volt[num].log_data("user","%s失败\n" % (does))
        print("\n未能%s\n" % (does))
    else:
        print("\n成功%s\n" % (does))
        all_volt[num].log_data("user","%s成功\n" % (does))
        myWin.on[num].setEnabled(set_button)
    all_volt[num].threadLock.release()

# 工作
def power_on(num):
    print("点击了第%d个工作按钮" % (num+1))
    all_volt[num].threadLock.acquire()
    if myWin.on[num].isChecked():  # 开
        does = "[开启]第%d台工作" % (num+1)
        send_order = myWin.on_onorder[num]
        set_button = True
    else:
        does = "[关闭]第%d台工作" % (num+1)
        send_order = myWin.on_offorder[num]
        set_button = False
    print("\n尝试%s\n"%(does))
    all_volt[num].log_data("user","尝试%s" % (does))
    state_1 = all_volt[num].data_write(send_order)
    time.sleep(0.1)
    state_2 = all_volt[num].data_write(send_order)
    state = state_1 + state_2
    if state == 0:  # 发送指令失败，按钮要变回原状
        myWin.on[num].setChecked(bool(1-set_button))
        all_volt[num].log_data("user","%s第%d台预燃失败\n" % (does,num+1))
        print("\n未能%s\n" % (does))
    else:
        print("\n成功%s\n" % (does))
        all_volt[num].log_data("user","%s成功\n" % (does))
    all_volt[num].threadLock.release()

# 修改电压
def change_power(num):
    all_volt[num].threadLock.acquire()
    does = "更改第%d台电压" % (num+1)
    volt_window = Ui_Dialog()
    if myWin.pw_v[num].text() == "loading":
        all_volt[num].log_data("user"," 点击第%d台电压为loading的设备按钮\n" % (num+1))
        print("第%d台未开机" % num)
    else:
        volt_window.spinBox.setValue(int(myWin.pw_v[num].text()))
        result = volt_window.exec_()
        set_value = volt_window.spinBox.value()
        all_volt[num].log_data("user"," 设置第%d台设备电流值为%dA\n" % (num+1,set_value))
        hex_value = '%04x' % set_value
        hex_addr = '%02x' % (num+1)
        send_value = "aa "+ hex_addr + "a1 "+ hex_value + " cc 33 c3 3c"
        save_value = "aa "+ hex_addr + "f6 cc 33 c3 3c"
        all_volt[num].voltage = str(set_value)
        all_volt[num].data_write(send_value)
        time.sleep(0.15)
        all_volt[num].data_write(send_value)
        myWin.pw_v[num].setText(str(set_value))   #修改按钮显示电压
        time.sleep(0.15)
        all_volt[num].data_write(save_value)
        time.sleep(0.15)
        all_volt[num].data_write(save_value)
    all_volt[num].threadLock.release()

# 第11台临时设置电压
def temp_volt():
    hex_value = '%04x' % myWin.volt11_set.value()
    send_value = "aa 0b a1" + hex_value + "cc 33 c3 3c"
    volt11.data_write(send_value)
    time.sleep(0.15)
    volt11.data_write(send_value)
    volt11.data_write("aa 0b f6 cc 33 c3 3c",2)


def alloff_def():
    thread_alloff = threading.Thread(target=alloff,args=(0,))
    thread_alloff.start()

def alloff(urgency):
    print("接受到的urgency：",urgency)
    if urgency == 0:     # 非急停，先关运行再关预燃
        #self.log_data("user","一键全关\n")
        for i in range(13,-1,-1):
            if myWin.on[i].isChecked():
                time.sleep(2)
                all_volt[i].threadLock.acquire()
                all_volt[i].data_write(myWin.on_offorder[i])
                myWin.on[i].setChecked(False)
                time.sleep(0.15)
                all_volt[i].data_write(myWin.on_offorder[i])
                all_volt[i].threadLock.release()
        

        if myWin.pre8.isChecked():
            time.sleep(2)
            volt8.threadLock.acquire()
            myWin.pre8.setChecked(False)
            myWin.on8.setEnabled(False)
            volt8.data_write("aa 08 10 cc 33 c3 3c")
            time.sleep(0.15)
            volt8.data_write("aa 08 10 cc 33 c3 3c")
            volt8.threadLock.release()
            

        if myWin.pre1.isChecked():
            time.sleep(2)
            volt9.threadLock.acquire()
            myWin.pre1.setChecked(False)
            myWin.on1.setEnabled(False)
            volt1.data_write("aa 01 10 cc 33 c3 3c")
            time.sleep(0.15)
            volt1.data_write("aa 01 10 cc 33 c3 3c")
            volt9.threadLock.release()
            

        for i in range(13,-1,-1):
            all_volt[i].threadLock.acquire()
            all_volt[i].data_write(myWin.on_offorder[i])
            myWin.on[i].setChecked(False)
            all_volt[i].threadLock.release()

        # B路六台电源
        print("检查B路")
        for i in range(13,7,-1):
            print("将关闭B路所有电源！！！" )
            if myWin.relay[i].isChecked():
                print("将关闭B路第%d台电源" % (i+1))
                time.sleep(3)
                all_volt[i].threadLock.acquire()
                relay_2.relay_2_switch[i-8] = False
                myWin.relay[i].setChecked(False)
                relay_2.data_write(myWin.relay_off[i])
                time.sleep(0.1)
                relay_2.data_write(myWin.relay_off[i])
                all_volt[i].threadLock.release()
            else:
                print("B路第%d台电源未开启！" % (i+1))
                pass


        print("检查A路")
        for i in range(7,-1,-1):
            if myWin.relay[i].isChecked():
                time.sleep(3)
                all_volt[i].threadLock.acquire()
                relay_1.relay_1_switch[i] = False
                myWin.relay[i].setChecked(False)
                relay_1.data_write(myWin.relay_off[i])
                time.sleep(0.1)
                relay_1.data_write(myWin.relay_off[i])
                all_volt[i].threadLock.release()
            else:
                print("A路第%d台电源未开启！" % (i+1))
                pass



                
'''
def CCD():
    # 枚举设备
    deviceList = enum_devices(device=0, device_way=False)
    # 判断不同类型设备
    identify_different_devices(deviceList)
    # 因为只用1个CCD，所以nConnectionNum选择第0号
    #nConnectionNum = input_num_camera(deviceList)
    nConnectionNum = 0
    # 创建相机实例并创建句柄(设置日志路径)
    cam, stDeviceList = creat_camera(deviceList, nConnectionNum, log=True, log_path="D:\\2021_new\\Python")
    # 打开设备
    open_device(cam)
    # 设置各种类型节点参数
    #set_Value(cam, param_type="bool_value", node_name="TriggerCacheEnable", node_value=1)
    # 获取各种类型节点参数
    #get_value = get_Value(cam , param_type = "int_value" , node_name = "PayloadSize")
    #print("get_value: ",get_value)
    # 开启取流并获取数据包大小
    #data_size = start_grab_and_get_data_size(cam)
    start_grab_and_get_data_size(cam)
    # 主动图像采集
    #access_get_image(cam, active_way="getImagebuffer", nPayloadSize=data_size)
    access_get_image( myWin.label_3.width(),myWin.label_3.height(),cam, active_way="getImagebuffer")
    # 关闭设备与销毁句柄
    close_and_destroy_device(cam)
'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    energy = trans("192.168.1.160",23,17)
    # 1到14台电源
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
    # 第11台特殊，读不到电压
    volt11 = trans("192.168.1.131",8811,11)
    volt12 = trans("192.168.1.132",8812,12)
    volt13 = trans("192.168.1.133",8813,13)
    volt14 = trans("192.168.1.134",8814,14)
    # 继电器
    relay_1 = trans("192.168.1.110", 8800,15)
    relay_2 = trans("192.168.1.136",8816,16)



    all_volt = [volt1,volt2,volt3,volt4,volt5,volt6,volt7,
                volt8,volt9,volt10,volt11,volt12,volt13,volt14,relay_1,relay_2,energy]


    myWin = soft()
    
    myWin.show()


    myWin.pre1.clicked.connect(lambda:power_pre(0))
    myWin.pre8.clicked.connect(lambda:power_pre(7))

    # relay 第1~8依次是A路种子源供电（第1台继电器第7位），A路六台电源供电（第1台继电器1到6位），B路种子源供电（第1台继电器第8位），
    # relay 第9~14是B路六台电源供电（第2台继电器1~6位）
    # relay 第15和16是A、B路的Q
    myWin.relay[0].clicked.connect(lambda:power_relay(0))
    myWin.relay[1].clicked.connect(lambda:power_relay(1))
    myWin.relay[2].clicked.connect(lambda:power_relay(2))
    myWin.relay[3].clicked.connect(lambda:power_relay(3))
    myWin.relay[4].clicked.connect(lambda:power_relay(4))
    myWin.relay[5].clicked.connect(lambda:power_relay(5))
    myWin.relay[6].clicked.connect(lambda:power_relay(6))
    myWin.relay[7].clicked.connect(lambda:power_relay(7))
    myWin.relay[8].clicked.connect(lambda:power_relay(8))
    myWin.relay[9].clicked.connect(lambda:power_relay(9))
    myWin.relay[10].clicked.connect(lambda:power_relay(10))
    myWin.relay[11].clicked.connect(lambda:power_relay(11))
    myWin.relay[12].clicked.connect(lambda:power_relay(12))
    myWin.relay[13].clicked.connect(lambda:power_relay(13))
    myWin.relay[14].clicked.connect(lambda:power_relay(14))
    myWin.relay[15].clicked.connect(lambda:power_relay(15))

    myWin.on[0].clicked.connect(lambda:power_on(0))
    myWin.on[1].clicked.connect(lambda:power_on(1))
    myWin.on[2].clicked.connect(lambda:power_on(2))
    myWin.on[3].clicked.connect(lambda:power_on(3))
    myWin.on[4].clicked.connect(lambda:power_on(4))
    myWin.on[5].clicked.connect(lambda:power_on(5))
    myWin.on[6].clicked.connect(lambda:power_on(6))
    myWin.on[7].clicked.connect(lambda:power_on(7))
    myWin.on[8].clicked.connect(lambda:power_on(8))
    myWin.on[9].clicked.connect(lambda:power_on(9))
    myWin.on[10].clicked.connect(lambda:power_on(10))
    myWin.on[11].clicked.connect(lambda:power_on(11))
    myWin.on[12].clicked.connect(lambda:power_on(12))
    myWin.on[13].clicked.connect(lambda:power_on(13))


    # 没有pw11_v_send
    myWin.pw_v[0].clicked.connect(lambda:change_power(0))
    myWin.pw_v[1].clicked.connect(lambda:change_power(1))
    myWin.pw_v[2].clicked.connect(lambda:change_power(2))
    myWin.pw_v[3].clicked.connect(lambda:change_power(3))
    myWin.pw_v[4].clicked.connect(lambda:change_power(4))
    myWin.pw_v[5].clicked.connect(lambda:change_power(5))
    myWin.pw_v[6].clicked.connect(lambda:change_power(6))
    myWin.pw_v[7].clicked.connect(lambda:change_power(7))
    myWin.pw_v[8].clicked.connect(lambda:change_power(8))
    myWin.pw_v[9].clicked.connect(lambda:change_power(9))
    #myWin.pw_v[10].clicked.connect(lambda:change_power(10))
    myWin.volt11_send.clicked.connect(temp_volt)
    myWin.pw_v[11].clicked.connect(lambda:change_power(11))
    myWin.pw_v[12].clicked.connect(lambda:change_power(12))
    myWin.pw_v[13].clicked.connect(lambda:change_power(13))

    myWin.off_all.clicked.connect(alloff_def)

    # 更新CCD
    #changePixmap = pyqtSignal(numpy.ndarray)
    #changePixmap.connect(setImage)

    thread_updateUi = threading.Thread(target=updateUi)     # 目标函数不能带括号，函数如果有参数要写arg=()
    thread_updateUi.setDaemon(True)
    thread_updateUi.start()
    print("开启更新电源UI线程")

    thread_updateUi = threading.Thread(target=updateUi_relay)     
    thread_updateUi.setDaemon(True)
    thread_updateUi.start()
    print("开启更新继电器UI线程")

    #thread_updateUi = threading.Thread(target=CCD)
    #thread_updateUi.setDaemon(True)
    #thread_updateUi.start()
    #print("开启更新CCD线程")

    sys.exit(app.exec_())




