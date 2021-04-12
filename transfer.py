
# 串口通信文件
import threading    # 线程

from PyQt5.QtCore import QUrl
from PyQt5 import QtCore, QtGui, QtWidgets,QtMultimedia
from PyQt5.QtCore import QTimer,pyqtSignal

import time,signal
import serial.tools.list_ports
import socket

from Ui_control import Ui_control
from Ui_seaddialog import Ui_seedDialog
from Ui_pw1dialog import Ui_Dialog

threadLock_1 = threading.Lock()
threadLock_2 = threading.Lock()
threadLock_3 = threading.Lock()
threadLock_4 = threading.Lock()
threadLock_5 = threading.Lock()
threadLock_6 = threading.Lock()
threadLock_7 = threading.Lock()
threadLock_8 = threading.Lock()
threadLock_9 = threading.Lock()
threadLock_10 = threading.Lock()
threadLock_11 = threading.Lock()
threadLock_12 = threading.Lock()
threadLock_13 = threading.Lock()
threadLock_14 = threading.Lock()
threadLock_15 = threading.Lock()
threadLock_16 = threading.Lock()
threadLock_17 = threading.Lock()

threadLock = [threadLock_1,threadLock_2,threadLock_3,threadLock_4,threadLock_5,threadLock_6,threadLock_7,threadLock_8,
                threadLock_9,threadLock_10,threadLock_11,threadLock_12,threadLock_13,threadLock_14,threadLock_15,threadLock_16,threadLock_17]



class trans(Ui_control):      # 通信类，每一个设备建立一个对象
    def __init__(self,IP,port,number):     # IP地址，端口号，序号
        self.IP = IP
        self.port = port
        self.number = number
        self.energy_value = 0
        self.voltage = "loading"
        self.threadLock = threadLock[self.number-1]

        self.volt_index =  [
        "aa 01 c3 cc 33 c3 3c","aa 02 c3 cc 33 c3 3c","aa 03 c3 cc 33 c3 3c","aa 04 c3 cc 33 c3 3c",
        "aa 05 c3 cc 33 c3 3c","aa 06 c3 cc 33 c3 3c","aa 07 c3 cc 33 c3 3c","aa 08 c3 cc 33 c3 3c",
        "aa 09 c3 cc 33 c3 3c","aa 0a c3 cc 33 c3 3c","aa 0b c3 cc 33 c3 3c","aa 0c c3 cc 33 c3 3c",
        "aa 0d c3 cc 33 c3 3c","aa 0e c3 cc 33 c3 3c"]    
        if self.number == 15:
            self.relay_connect_state_1 = "继电器1"
            self.relay_1_switch = [False,False,False,False,False,False,False,False,False,False]
        elif self.number == 16:
            self.relay_connect_state_2 = "继电器2"
            self.relay_2_switch = [False,False,False,False,False,False]
        else:
            pass
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
        

        if self.number == 15:       # 第一台继电器
            # 继电器先发送密码admin/r/n，返回ok（4F 4B）才能通信，若是返回4E 4F说明密码错误
            state_1 = self.data_write("61 64 6D 69 6E 0D 0A") 
            time.sleep(0.1)
            state_2 = self.data_write("61 64 6D 69 6E 0D 0A") 
            state = state_1 + state_2
            if state == 0:
                print("继电器1通信失败")
                self.relay_connect_state_1 = "请检查继电器1通信连接！"
                pass
            else:
                rec_data = self.data_read()
                if rec_data == "4F 4B":     # print("A路继电器可通信")
                    self.relay_connect_state_1 = "继电器1已连接 "
                else:
                    self.relay_connect_state_1 = "继电器1连接出错！ "


    def update(self):
        while True:
            if self.number == 15 or self.number == 16:
                time.sleep(3)
            else:
                time.sleep(1)
            self.threadLock.acquire()
            if self.number == 17:      # 能量计
                # 能量计
                try:
                    self.client_COM.sendall('$SE\r\n'.encode('utf-8'))
                    #print("能量计已发送")
                except:
                    #print("能量计发送指令失败！")
                    pass
                time.sleep(0.1)
                try :
                    rec_data = self.client_COM.recv(10240)
                    #print("读取到能量数据",rec_data)
                    instruct = str(rec_data)
                    first_index = instruct.find("* ")
                    if first_index == -1 :
                        #print("没有得到能量")
                        self.energy_value = "未查询到能量值数据"
                    else:
                        str_energy_value = "%.2f" % (eval(instruct[(first_index+2):(len(instruct)-6)])*1000)
                        #print("能量为",str_energy_value,"mJ")
                        self.energy_value = "能量值：%smJ" % str_energy_value
                        #self.label_energy.setText("能量值：%smJ" % self.energy_value)
                except:
                    #print("未能读取到能量！可能连接中断")
                    self.client_COM.close()
                    try:
                        #print("尝试重新连接.....")
                        self.client_COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client_COM.settimeout(0.15)
                        self.client_COM.connect((self.IP, self.port))
                        #print("重连成功！！！")
                        self.energy_value = "重连成功"
                    except:
                        #self.label_energy.setText("连接中断，请检查设备连接")
                        self.energy_value = "请检查能量计连接！"
                        #print("连接中断，请检查设备连接")
                    return 0
            elif self.number == 15:     # 第一台继电器，有登录密码
                # 10台设备，依次是A路种子源，A路6台电源，B路种子源，A路Q，B路Q
                try:
                    self.data_write("55 AA 00 02 00 0A 0C")
                    time.sleep(0.2)
                except:
                    self.re_connect()
                    self.threadLock.release()
                    continue
                response = self.data_read()
                #print("继电器1读取到：",response)
                self.get_ralay(response,1)

            elif self.number == 16:     # 第二台继电器
                try:
                    self.data_write("FE 01 00 00 00 08 29 C3")
                    time.sleep(0.2)
                    self.relay_connect_state_1 = "继电器2已连接 "
                except:
                    self.re_connect()
                    self.threadLock.release()
                    self.relay_connect_state_1 = "继电器2发送指令失败 "
                    continue
                response = self.data_read()
                self.get_ralay(response,2)
               
            # 电源
            elif self.number == 11:
                #print("第11台是无法读到电压的")
                pass
            else:
                try:
                    self.data_write(self.volt_index[self.number-1])
                    time.sleep(0.1)
                    self.data_write(self.volt_index[self.number-1])
                except:
                    self.re_connect()
                    self.search_volt(self.number,"000")
                    self.threadLock.release()
                    continue
                time.sleep(0.15)
                response = self.data_read()
                #print("读取电源返回指令：",response)
                self.search_volt(self.number,response)
            self.threadLock.release()
            


    def re_connect(self):
        self.client_COM.close()
        try:
            #print("尝试重新连接.....")
            self.client_COM = socket.socket(socket.AF_INET)
            self.client_COM.settimeout(0.15)
            self.client_COM.connect((self.IP, self.port))
            print("第%d台重连成功！！！" % self.number)
        except:
            #print("第%d台连接中断，请检查设备连接" % self.number)
            pass

    # 根据继电器返回指令，设置按钮
    def get_ralay(self,order,num):
        if order == "000":
            #print("控制器%s未开启" % num)
            if num == 1:
                self.relay_connect_state_1 = "请检查继电器1通信连接！ "
            elif num == 2:
                self.relay_connect_state_2 = "请检查继电器2通信连接！ "
        else:
            #print("控制器%d已开启，返回指令%s：" % (num,order))
            for i in range(0,len(order)):
                if order[i:i+8] == "FE 01 01":
                    self.relay_connect_state_2 = "继电器2通信正常。 "
                    relay_state = str(bin(int(order[i+9:i+11],16))[2:])  
                    # 返回指令的第四个字段代表状态，转为2进制，Bit0是第一个继电器状态
                    # [2:]是跳过开头两个，为了去掉0b
                    #print(relay_state)
                    if len(relay_state) < 9:
                        bin_relay_state = (8-len(relay_state))*"0" + relay_state
                    else:
                        bin_relay_state = relay_state
                    #print("%d路继电器状态返回指令" % num, bin_relay_state)
                    for j in range(0,len(bin_relay_state)):
                        state = bool(int(bin_relay_state[j]))
                        if j > 1:       # 第0和1位是继电器最后两位，暂时没用
                            #print("控制器%d第%d路继电器已开" % (num,8-j)) 
                            self.relay_2_switch[7-j] = state
                            #self.relay[15-j].setChecked(True)       # 继电器状态从低位到高位是从1到8路
                            
                    break
                # 继电器1
                elif order[i:i+17] == "AA 55 00 04 00 8A":
                    self.relay_connect_state_1 = "继电器1通信正常。 "
                    relay_state_1 = str(bin(int(order[i+18:i+20],16))[2:])
                    relay_state_2 = str(bin(int(order[i+21:i+23],16))[2:])
                    bin_relay_1_state_1 = (8-len(relay_state_1))*"0" + relay_state_1
                    bin_relay_1_state_2 = (8-len(relay_state_2))*"0" + relay_state_2

                    #print("%d路继电器1~8路：" % num, bin_relay_1_state_1,",9~16路：",bin_relay_1_state_2)
                    for j in range(0,len(bin_relay_1_state_1)):
                        state = bool(int(bin_relay_1_state_1[j]))
                        if bin_relay_1_state_1[j] == "1":
                            #print("控制器%d第%d路继电器已开" % (num,8-j))
                            pass
                        if j == 0:      # B种子源
                            self.relay_1_switch[7] = state
                            #self.relay8.setChecked(True)
                        elif j == 1:    # A种子源
                            self.relay_1_switch[0] = state
                            #self.relay1.setChecked(True)
                        elif j > 1:     # A路6台电源
                            self.relay_1_switch[8-j] = state
                            #self.relay[8-j].setChecked(True)
                    for j in range(0,len(bin_relay_1_state_2)):
                        state = bool(int(bin_relay_1_state_2[j]))
                        #print("控制器%d第%d路继电器已开" % (num,16-j))
                        if j == 7:      # AQ
                            self.relay_1_switch[8] = state
                            #self.relay_A_Q.setChecked(True) 
                        elif j == 6:    # BQ
                            self.relay_1_switch[9] = state
                            #self.relay_B_Q.setChecked(True) 
                    break

    # 根据电源查询电压的返回指令，设置按钮
    def search_volt(self,num,get_v):
        if get_v == "000":
            #print("第%d台未读到电压！" % num)
            self.voltage = "loading"
        else:
            for i in range(0,len(get_v)):      
                if get_v[i:i+2] == "BB" and get_v[i+6:i+20] == "C3 CC 33 C3 3C":
                    i += 21
                    if get_v[i:i+2] == "BB" and get_v[i+6:i+8] == "C3" and  get_v[i+21:i+32] == "CC 33 C3 3C":
                        addr_v = get_v[i+4]       # 地址位
                        high_volt = get_v[i+9:i+11]
                        low_volt = get_v[i+12:i+14]
                        hex_volt = high_volt+low_volt
                        real_v = str(int(hex_volt,16))
                        #print("得到第%c台电压值：" % addr_v,real_v)
                        self.voltage = real_v       # 更新电压值数组
                        i += 33
                    else:
                        print("得到电压返回指令，却未读到电压值！",get_v)
                        self.log_data("comm"," 获取异常指令为%s\n" % get_v)
                        i += 3
                        self.voltage = "loading"
                # 读到继电器的话
                else:
                    i += 3





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
            #print("第%d台设备发送指令失败！" % self.number)
            return 0

    def data_read(self):
        try :
            rec_data = self.client_COM.recv(10240)
            #print("此次接受",rec_data)
        except:
            #print("未读到")
            return "000"
        out_s = ''
        for i in range(0, len(rec_data)):                         # 从0到数据长度个元素
            out_s = out_s + '{:02X}'.format(rec_data[i]) + ' '    # 将data中的元素格式化转16进制，2位对齐，左补0，并拼接
        response = out_s
        #print("返回的16进制指令  response =",response)        
        #处理后得到的16进制返回指令
        return response


