import threading
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys


class test():

    def __init__(self,numb,name):
        self.name = name
        self.number = numb
        print("\n","开启第%d台的轮询线程--------------------------------------------" % numb)
        self.thread_inquiry = threading.Thread(target=self.update(numb))
        self.thread_inquiry.setDaemon(True)
        self.thread_inquiry.start()

    def update(self,index):
        self.client_COM_timer = QTimer()    # 定时器
        if index == 1:
            sleeptime = 1000
        else:
            sleeptime = 200
        self.client_COM_timer.start(sleeptime)       # 每一秒触发一次
        self.client_COM_timer.timeout.connect(lambda:self.thread_comm(index))

    def thread_comm(self,index):
        thread_all[index-1].acquire()
        print(index,self.name) 
        if index == 1:
            time.sleep(2)
        thread_all[index-1].release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    threadLock_1 = threading.Lock()    
    threadLock_2 = threading.Lock()    
    thread_all = [threadLock_1,threadLock_2]
    a = test(1,"a")
    b = test(2,"b")
    sys.exit(app.exec_())
