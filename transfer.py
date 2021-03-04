
# 串口通信文件
import threading    # 线程

from PyQt5.QtCore import QUrl
from PyQt5 import QtCore, QtGui, QtWidgets,QtMultimedia
from PyQt5.QtCore import QTimer,pyqtSignal

import time,signal
import serial.tools.list_ports
import socket

from Ui_control import Ui_Control

threadLock_1 = threading.Lock()
threadLock_2 = threading.Lock()
threadLock_3 = threading.Lock()
threadLock_4 = threading.Lock()
threadLock_5 = threading.Lock()
threadLock_6 = threading.Lock()
threadLock_7 = threading.Lock()
threadLock_8 = threading.Lock()
threadLock_9 = threading.Lock()

threadLock = [threadLock_1,threadLock_2,threadLock_3,threadLock_4,threadLock_5,threadLock_6,threadLock_7,threadLock_8,
                threadLock_9]




class trans(Ui_Control):      # 通信类，每一个设备建立一个对象
    def __init__(self,IP,port,number):     # IP地址，端口号，序号

        self.IP = IP
        self.port = port
        self.number = number
        self.energy_value = 0
        self.threadLock = threading.Lock()

        self.volt_index =  [
        "aa 01 c3 cc 33 c3 3c","aa 02 c3 cc 33 c3 3c","aa 03 c3 cc 33 c3 3c","aa 04 c3 cc 33 c3 3c",
        "aa 05 c3 cc 33 c3 3c","aa 06 c3 cc 33 c3 3c","aa 07 c3 cc 33 c3 3c","aa 08 c3 cc 33 c3 3c",
        "aa 09 c3 cc 33 c3 3c","aa 0a c3 cc 33 c3 3c","aa 0b c3 cc 33 c3 3c","aa 0c c3 cc 33 c3 3c",
        "aa 0d c3 cc 33 c3 3c","aa 0e c3 cc 33 c3 3c"]    

        self.timer_stop = QTimer()      # 急停的计时器

        # 通信
        self.client_COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # 建立socket
        self.client_COM.settimeout(0.15)        # 发送和读取的超时
        try:
            self.client_COM.connect((self.IP,self.port))        # 连接目标设备
            print("连接%s成功" % self.IP)
        except:
            print("IP %s,第%d号设备连接失败" % (self.IP,self.number))
        # 轮询
        thread_inquiry = threading.Thread(target=self.update)
        thread_inquiry.setDaemon(True)
        thread_inquiry.start()

    def update(self):
        while True:
            if self.number == 17:      # 能量计
                # 能量计
                try:
                    self.client_COM.sendall('$SE\r\n'.encode('utf-8'))
                    print("已发送")
                except:
                    print("发送指令失败！")
                time.sleep(0.1)
                try :
                    rec_data = self.client_COM.recv(10240)
                    print("读取到能量数据",rec_data)
                    instruct = str(rec_data)
                    first_index = instruct.find("* ")
                    if first_index == -1 :
                        print("没有得到能量")
                        self.energy_value = "未查询到数据"
                    else:
                        str_energy_value = "%.2f" % (eval(instruct[(first_index+2):(len(instruct)-6)])*1000)
                        print("能量为",str_energy_value,"mJ")
                        self.energy_value = "能量值：%smJ" % str_energy_value
                        #self.label_energy.setText("能量值：%smJ" % self.energy_value)
                except:
                    print("未能读取到能量！可能连接中断")
                    self.client_COM.close()
                    try:
                        print("尝试重新连接.....")
                        self.client_COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client_COM.settimeout(0.15)
                        self.client_COM.connect((self.IP, self.port))
                        
                        print("重连成功！！！")
                        self.energy_value = "重连成功"
                    except:
                        self.label_energy.setText("连接中断，请检查设备连接")
                        self.energy_value = "连接中断，请检查设备连接"
                        print("连接中断，请检查设备连接")
                    return 0
            elif self.number == 18:
                print("继电器")
            # 电源
            else:
                self.threadLock.acquire()
                self.data_write(self.volt_index[self.number-1])
                time.sleep(0.1)
                try:
                    rec_data = self.client_COM.recv(10240)
                    #print(rec_data)
                    instruct = (rec_data.decode('iso-8859-1'))
                    #print("得到返回指令")
                    out_s = ''
                    for i in range(0, len(rec_data)):                         # 从0到数据长度个元素
                        out_s = out_s + '{:02X}'.format(rec_data[i]) + ' '    # 将data中的元素格式化转16进制，2位对齐，左补0，并拼接
                    response = out_s
                    print("第%d台返回:%s" % (self.number,response))
                    
                except:
                    #print("未能读取到第%d台返回！可能连接中断" % self.number)
                    self.client_COM.close()
                    try:
                        #print("尝试重新连接.....")
                        self.client_COM = socket.socket(socket.AF_INET)
                        self.client_COM.settimeout(0.15)
                        self.client_COM.connect((self.IP, self.port))
                    
                        print("第%d台重连成功！！！" % self.number)
                        self.energy_value = "重连成功"
                    except:
                        self.energy_value = "连接中断，请检查设备连接"
                        print("第%d台连接中断，请检查设备连接" % self.number)
                self.threadLock.release()
            time.sleep(1.5)

    def log_data(self,txt,str1):
        now = str(time.strftime("%Y-%m-%d %H:%M:%S  ",time.localtime(time.time())))     # 当下时间
        name = str(time.strftime("%Y_%m_%d",time.localtime(time.time())))       # 当下日期
        if txt == "user":           # 如果记录的是用户的操作
            file_name = "./log_user/" + name + ".txt"
        elif txt == "comm":         # 如果记录的是数据
            file_name = "./log_comm/" + name + ".txt"
        else:
            pass
        user_log = open(file_name,mode = 'a+')    # open打开文件file_name，如果没有此文件，则创建一个新的txt。a+在原有数据的基础上换行继续写入
        user_log.write(str(self.number)+"  "+ now + str1)        # 写入当下时间，和传递过来的信息
        user_log.close()

        
    def get_bytes(self,str):
        input_s = str
        if input_s != "":
            input_s = input_s.strip()
            send_list = []
            while input_s != '':
                try:
                    num = int(input_s[0:2], 16)
                except ValueError:
                    return None
                input_s = input_s[2:].strip()
                send_list.append(num)
            input_s = bytes(send_list)       
        return input_s


    def data_write(self,comm):      #发送指令
        input_s = comm
        if input_s != "":
            input_s = input_s.strip()
            send_list = []
            while input_s != '':
                try:
                    num = int(input_s[0:2], 16)
                except ValueError:
                    return 0
                input_s = input_s[2:].strip()
                send_list.append(num)
            input_s = bytes(send_list)
        else:
            return 0
        try:
            self.client_COM.sendall(input_s)   
            #print("已发送查询指令",input_s)
            return 1
        except:
            print("第%d台设备发送指令失败！" % self.number)
            return 0

