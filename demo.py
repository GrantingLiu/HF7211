import threading        # 线程
import signal           # 信号槽
import sys              # 对解释器使用或维护的一些变量的访问
import serial           # 串口通信
import subprocess       # 启动新进程，用于CCD
import time             # 定时器

# 接口等
import win32api,win32gui,win32con
from ctypes import windll              
import subprocess
import pywintypes


# GUI界面所需组件
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QToolTip,QMessageBox
from PyQt5.QtCore import QTimer,pyqtSignal
from PyQt5 import QtCore

from signalslot import slot                   # 信号槽文件，存放指令和按钮列表
from transfer import trans                    # 通信文件，定义通信类
from Ui_control import Ui_control             # 主界面GUI文件
from Ui_pw1dialog import Ui_Dialog            # 设置电压的弹出窗口的GUI文件
import image_rc                               # 在Qt配置的图片资源打包调用





# 继承了GUI和信号槽的类，作为主窗口
class soft(QMainWindow,Ui_control,slot):
    pop_signal = pyqtSignal(str)
    def __init__(self):
        super(soft,self).__init__()
        self.number = 0     # 初始化
        self.machine_name = "soft"
        trans.log_data(self,"user"," 开启软件-----------------------------")
        trans.log_data(self,"comm"," 开启软件-----------------------------")
        time.sleep(0.5)
        self.setupUi(self)               # 主界面
        self.signalslot()                # 信号槽
        self.timer_stop = QTimer(self)   # 急停计时器



# 更新GUI
def updateUi():
    print("更新UI界面")
    while True:                 # 无限循环
        for i in range(0,14):   # 共14台设备
            all_volt[i].threadLock.acquire()    # 线程锁  
            if i == 10:         # 第10台无法读电压，设备本身问题
                pass
            else:
                # 电压数组中记录的是loading，且继电器记录状态为false时说明电源已关闭，更新按钮为loading
                if myWin.relay[i].isChecked() == False:
                    do_what = False     # 继电器该路供电是关的
                    myWin.pw_v[i].setText("loading")        # 则设置电压loading
                    trans.log_data(myWin,"update_volt","更新%s电压值为loading" % (all_volt[i].machine_name))
                else:
                    do_what = True      # 若继电器该电源供电已开，说明电源已开启但没读到电压
                if do_what and all_volt[i].voltage != "loading":    # 电源已开且轮询电压结果不是loading时
                    myWin.pw_v[i].setText(str(all_volt[i].voltage)) # 按钮显示电压值
                    print("设置第%d台设备电压为：%s" % (i+1,str(all_volt[i].voltage)))
                    trans.log_data(myWin,"update_volt","更新%s电压值为%s" % (all_volt[i].machine_name,str(all_volt[i].voltage)))
                else:
                    pass
            all_volt[i].threadLock.release()    # 释放线程锁
        myWin.label_energy.setText(str(energy.energy_value))        # 更新能量计
        time.sleep(1)     # 两次更新之间间隔1s以上

# 更新继电器
def updateUi_relay():
    while True:
        # 继电器1
        relay_1.threadLock.acquire()        # 线程锁
        myWin.relay_state_1.setText(relay_1.relay_connect_state_1)      # 更新继电器连接状态（界面下方的文本框）
        
        for i in range(0,len(relay_1.relay_1_switch)-2):                # -2是因为继电器最后两个位还没有接
            myWin.relay[i].setChecked(relay_1.relay_1_switch[i])        # 更新开关按钮状态
            trans.log_data(myWin,"update_relay","更新%s状态:%s" % (str(myWin.relay[i].objectName()),str(relay_1.relay_1_switch[i])))
        relay_1.threadLock.release()        # 释放锁
        # 继电器2与上面相同
        relay_2.threadLock.acquire()
        myWin.relay_state_2.setText(relay_2.relay_connect_state_2)      
        # 第2台继电器，B路的6台电源
        for i in range(0,len(relay_2.relay_2_switch)):
            myWin.relay[i+8].setChecked(relay_2.relay_2_switch[i])
            trans.log_data(myWin,"update_relay","更新%s状态:%s" % (str(myWin.relay[i+8].objectName()),str(relay_2.relay_2_switch[i])))
        relay_2.threadLock.release()
        time.sleep(1)

# 继电器供电
def power_relay(num):
    relay_1.threadLock.acquire()    # 继电器1线程锁
    relay_2.threadLock.acquire()    # 继电器2线程锁
    print("-----------------点击了第%d个供电按钮" % (num+1))
    if num < 8 or num > 13:         # A路7台电源和B路种子源，以及两路的Q（未装）
        print("第1台继电器")
        num_index = 14              # 所有继电器位all_volt列表中的序号
    else:
        print("第2台继电器")
        num_index = 15

    if myWin.relay[num].isChecked():        # 若点击后按钮处于开启状态
        does = "[开启]第%d台供电" % (num+1) 
        send_order = myWin.relay_on[num]    # 选择对应开启指令
        set_button = True                   # 记录当前设置的状态
    else:
        does = "[关闭]第%d台供电" % (num+1)  # 对应的，若点击后按钮处于关闭状态
        send_order =  myWin.relay_off[num]  # 选择对应关闭指令
        set_button = False                  # 记录当前设置的状态

    print("\n尝试%s\n"%(does))
    all_volt[num_index].log_data("user","尝试%s" % (does))
    state_1 = all_volt[num_index].data_write(send_order)        # 发送指令
    time.sleep(0.1)
    state_2 = all_volt[num_index].data_write(send_order)        # 二次发送
    state = state_1 + state_2                                   # 两次发送至少有一次成功则不为0
    if state == 0:                          # 说明发送指令失败，按钮要变回原状
        now_state = bool(1-set_button)      # 原状就是前面设置的状态取反
        all_volt[num_index].log_data("user","%s失败" % (does))
        print("\n未能%s-----------------\n" % (does))
    else:
        print("\n成功%s-----------------\n" % (does))        # 发送指令成功
        all_volt[num_index].log_data("user","%s成功" % (does))
        now_state = set_button              # 按钮状态为前面设置的状态
    myWin.relay[num].setChecked(now_state)  # 设置按钮状态
    # 更新继电器状态列表
    if num < 8:     # A路继电器                                     
        relay_1.relay_1_switch[num] = now_state
    elif num > 13:  # B路继电器
        relay_1.relay_1_switch[num-6] = now_state
    else:
        relay_2.relay_2_switch[num-8] = now_state
    # 释放锁
    relay_1.threadLock.release()    # 继电器1线程锁
    relay_2.threadLock.release()    # 继电器2线程锁


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
    all_volt[num].threadLock.acquire()     # 锁住线程，避免和轮询冲突
    # 根据按钮当前状态设定临时参数
    if myWin.pre[button_num].isChecked():  # 选种状态为开
        does = "[开启]第%d台预燃" % (num+1) # 记录操作
        send_order = pre_on_order
        set_button = True
    else:
        does = "[关闭]第%d台预燃" % (num+1)
        send_order = pre_off_order
        set_button = False
    # 尝试发送，根据data_write的return值判断是否发送成功
    print("\n尝试%s\n"%(does))              
    all_volt[num].log_data("user","尝试%s" % (does))
    state_1 = all_volt[num].data_write(send_order)      #发送指令
    time.sleep(0.1)
    state_2 = all_volt[num].data_write(send_order)      # 二次发送
    state = state_1 + state_2                           
    if state == 0:                                      # 说明两次发送指令都失败（电脑和路由设备之间的通信中断）
        myWin.pre[button_num].setChecked(bool(1-set_button))        # 则按钮要变回原状
        all_volt[num].log_data("user","%s失败" % (does))
        print("\n未能%s\n" % (does))
    else:
        print("\n成功%s\n" % (does))
        all_volt[num].log_data("user","%s成功" % (does))
        
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
        all_volt[num].log_data("user","%s失败" % (does))
        print("\n未能%s\n" % (does))
        
    else:
        print("\n成功%s\n" % (does))
        all_volt[num].log_data("user","%s成功" % (does))
    all_volt[num].threadLock.release()

# 修改电压
def change_power(num):
    all_volt[num].threadLock.acquire()
    does = "更改第%d台电压" % (num+1)
    volt_window = Ui_Dialog()
    if myWin.pw_v[num].text() == "loading" :
        all_volt[num].log_data("user"," 点击第%d台电压为loading的设备按钮" % (num+1))
        print("第%d台未开机" % num)
    else:
        volt_window.spinBox.setValue(int(myWin.pw_v[num].text()))
        result = volt_window.exec_()
        set_value = volt_window.spinBox.value()
        all_volt[num].log_data("user"," 设置第%d台设备电流值为%dA" % (num+1,set_value))
        hex_value = '%04x' % set_value
        hex_addr = '%02x' % (num+1)
        send_value = "aa "+ hex_addr + "a1 "+ hex_value + " cc 33 c3 3c"
        save_value = "aa "+ hex_addr + "f6 cc 33 c3 3c"
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
    volt11.data_write("aa 0b f6 cc 33 c3 3c")


# shutter全关全开工作
def pause(num):
    if num == 1:
        trans.log_data(myWin,"user","全开工作")
    elif num == 2:
        trans.log_data(myWin,"user","全关工作")
    for i in range(1,14):
        if i == 7:
            continue
        if num == 1:    #1是全开工作
            send_order = myWin.on_onorder[i]
            does = "[开启]第%d台工作" % (i+1)
            set_button = True                   # 按钮状态
        elif num == 2:  #2是全关工作
            send_order = myWin.on_offorder[i]
            does = "[关闭]第%d台工作" % (i+1)
            set_button = False

        all_volt[i].threadLock.acquire()    # 线程锁
        state_1 = all_volt[i].data_write(send_order)
        time.sleep(0.1)
        state_2 = all_volt[i].data_write(send_order)
        state = state_1 + state_2
        if state != 0:  # 发送指令成功，按钮变化
            myWin.on[i].setChecked(set_button)
            all_volt[i].log_data("user"," 运行总控 %s成功" % (does))
            
        elif state == 0:
            all_volt[i].log_data("user"," 运行总控 %s失败！！！" % (does))
            str_text = " 运行总控 %s失败！！！" % (does)
            
            state_3 = all_volt[i].data_write(send_order)
            if state_3 != 0:
                myWin.on[i].setChecked(set_button)
                all_volt[i].log_data("user"," 运行总控二次尝试 %s成功" % (does))
                
                
            elif state_3 == 0:
                all_volt[i].log_data("user"," 运行总控二次尝试 %s失败！！！" % (does))

            
        all_volt[i].threadLock.release()

def stop_judge():
    myWin.stop_emer.clicked.disconnect(stop_judge)      # 解除原有信号槽。因为都要用到clicked
    myWin.times = 1  
    myWin.timer_stop.singleShot(700,lambda:count_stop_judge(myWin.times))   # 定时器触发信号，0.7s后变成触发信号槽
    myWin.stop_emer.clicked.connect(inclease_times)
    # self.timer_stop.timeout.connect(lambda:self.count_stop_judge(self.times))      # 计时结束后查看点击次数

def inclease_times():
    myWin.times += 1
    if myWin.times == 2:
        alloff(1)

def count_stop_judge(all_times):
    print("0.7秒内点击急停次数：",all_times,"\n")
    myWin.stop_emer.clicked.disconnect(inclease_times)
    myWin.stop_emer.clicked.connect(stop_judge)


def alloff_def():
    thread_alloff = threading.Thread(target=alloff,args=(0,))
    thread_alloff.start()

def allon_def():
    thread_allon = threading.Thread(target=allon)
    thread_allon.start()

def allon():
    print("准备一键全开")     
    myWin.on_all.setText("全开中……")
    trans.log_data(myWin,"user","一键全开")
    for num in range(0,14):     # 共14台
        relay_1.threadLock.acquire()        # 锁住两个继电器
        relay_2.threadLock.acquire()
        if myWin.relay[num].isChecked() == False:       # 若现在没开
            if num < 8 or num > 13:                     # 区分当前开启的是哪一个继电器
                print("[全开中……] 第1台继电器")
                num_index = 14
            else:
                print("[全开中……] 第2台继电器")
                num_index = 15
            send_order = myWin.relay_on[num]
            print("\n[全开中……]尝试开启第%d台设备\n"%(num+1))
            all_volt[num_index].log_data("user","\n[全开中……]尝试开启第%d台设备\n"%(num+1))
            state_1 = all_volt[num_index].data_write(send_order) 
            time.sleep(0.1)
            state_2 = all_volt[num_index].data_write(send_order) 
            state = state_1 + state_2 
            if state == 0:                          # 说明发送指令失败，按钮要变回原状
                now_state = bool(0)      
                all_volt[num_index].log_data("user","[一键全开]第%d台失败" % (num+1))
                print("[一键全开]第%d台失败" % (num))
            else:
                print("[一键全开]第%d台成功" % (num))        # 发送指令成功
                all_volt[num_index].log_data("user","[一键全开]第%d台成功" % (num+1))
                now_state = bool(1)              # 按钮状态为前面设置的状态
            myWin.relay[num].setChecked(now_state)  # 设置按钮状态
            if num < 8:     # A路继电器                                     
                relay_1.relay_1_switch[num] = now_state
            elif num > 13:  # B路继电器
                relay_1.relay_1_switch[num-6] = now_state
            else:
                relay_2.relay_2_switch[num-8] = now_state
            time.sleep(1.5)
        else:       # 若已经供电，则无需操作
            pass
        relay_1.threadLock.release()
        relay_2.threadLock.release()
    myWin.on_all.setText("一键全开")


def alloff(urgency):
    print("接受到的urgency：",urgency)
    if urgency == 0:     # 非急停，先关运行再关预燃
        myWin.off_all.setText("全关中……")
        trans.log_data(myWin,"user","一键全关")
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

        # 再次全关
        for i in range(13,7,-1):
            all_volt[i].threadLock.acquire()
            relay_2.relay_2_switch[i-8] = False
            myWin.relay[i].setChecked(False)
            relay_2.data_write(myWin.relay_off[i])
            all_volt[i].threadLock.release()
        for i in range(7,-1,-1):
            all_volt[i].threadLock.acquire()
            relay_1.relay_1_switch[i] = False
            myWin.relay[i].setChecked(False)
            relay_1.data_write(myWin.relay_off[i])
            all_volt[i].threadLock.release()
        myWin.off_all.setText("一键全关")

    elif urgency == 1:
        trans.log_data(myWin,"user","急停")
        print("开始发送急停")
        # B路六台电源
        print("检查B路")
        for i in range(13,7,-1):
            #print("急停关闭B路电源！！！" )
            if myWin.relay[i].isChecked():
                time.sleep(0.05)
                print("急停关闭B路第%d台电源" % (i+1))
                all_volt[i].threadLock.acquire()
                relay_2.relay_2_switch[i-8] = False
                myWin.relay[i].setChecked(False)
                relay_2.data_write(myWin.relay_off[i])
                all_volt[i].threadLock.release()
            else:
                #print("B路第%d台电源未开启！" % (i+1))
                pass
        print("检查A路")
        for i in range(7,-1,-1):
            if myWin.relay[i].isChecked():
                time.sleep(0.05)
                print("急停关闭A路第%d台电源" % (i+1))
                all_volt[i].threadLock.acquire()
                relay_1.relay_1_switch[i] = False
                myWin.relay[i].setChecked(False)
                relay_1.data_write(myWin.relay_off[i])
                all_volt[i].threadLock.release()
            else:
                #print("A路第%d台电源未开启！" % (i+1))
                pass
        print("急停二次关闭B路电源！！！" )
        for i in range(13,7,-1):
            time.sleep(0.1)
            all_volt[i].threadLock.acquire()
            relay_2.data_write(myWin.relay_off[i])
            all_volt[i].threadLock.release()
        print("急停二次关闭A路电源！！！" )
        for i in range(7,-1,-1):
            time.sleep(0.1)
            all_volt[i].threadLock.acquire()
            relay_1.data_write(myWin.relay_off[i])
            all_volt[i].threadLock.release()

if __name__ == '__main__':
    # 管理图形用户界面应用程序的控制流和主要设置
    app = QApplication(sys.argv)
    # trans类，通信对象，每台设备定义一个。
    energy = trans("192.168.1.160",23,17,"energy")
    # 1到14台电源对象，各自独立IP通信
    volt1 = trans("192.168.1.121",8801,1,"volt_1")
    volt2 = trans("192.168.1.122",8802,2,"volt_2")
    volt3 = trans("192.168.1.123",8803,3,"volt_3")
    volt4 = trans("192.168.1.124",8804,4,"volt_4")
    volt5 = trans("192.168.1.125",8805,5,"volt_5")
    volt6 = trans("192.168.1.126",8806,6,"volt_6")
    volt7 = trans("192.168.1.127",8807,7,"volt_7")
    volt8 = trans("192.168.1.128",8808,8,"volt_8")
    volt9 = trans("192.168.1.129",8809,9,"volt_9")
    volt10 = trans("192.168.1.130",8810,10,"volt_10")
    volt11 = trans("192.168.1.131",8811,11,"volt_11")    # 第11台故障，读不到电压
    volt12 = trans("192.168.1.132",8812,12,"volt_12")
    volt13 = trans("192.168.1.133",8813,13,"volt_13")
    volt14 = trans("192.168.1.134",8814,14,"volt_14")
    # 继电器
    relay_1 = trans("192.168.1.110", 8800,15,"relay_1")
    relay_2 = trans("192.168.1.136", 8816,16,"relay_2")
    
    all_volt = [volt1,volt2,volt3,volt4,volt5,volt6,volt7,
                volt8,volt9,volt10,volt11,volt12,volt13,volt14,relay_1,relay_2,energy]

    myWin = soft()  # 包含GUI和指令的主对象
    
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
    myWin.on_all.clicked.connect(allon_def)


    myWin.shutter.clicked.connect(lambda:pause(1))
    myWin.shutter_2.clicked.connect(lambda:pause(2))

    myWin.stop_emer.clicked.connect(stop_judge)  # 



    thread_updateUi = threading.Thread(target=updateUi)     # 目标函数不能带括号，函数如果有参数要写arg=()
    thread_updateUi.setDaemon(True)
    thread_updateUi.start()
    print("开启更新电源UI线程")
    
    thread_updateUi = threading.Thread(target=updateUi_relay)     # 目标函数不能带括号，函数如果有参数要写arg=()
    thread_updateUi.setDaemon(True)
    thread_updateUi.start()
    print("开启更新继电器UI线程")
    
    # 运行主循环
    sys.exit(app.exec_())




