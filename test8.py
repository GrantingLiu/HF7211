import threading
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys


class test():
    def __init__(self,index):
        self.index = index
        self.client_COM_timer = QTimer()    # 定时器
        if self.index == 1:
            self.sleeptime = 1000
        else:
            self.sleeptime = 200

    def update_data(self):
        self.thread_inquiry = threading.Thread(self.update_time())
        
        self.thread_inquiry.setDaemon(True)
        self.thread_inquiry.start()
        print("线程%d开启" % self.index)

    def update_time(self):
        if self.index == 1:
            threadLock_1.acquire()
            print(self.index)
            time.sleep(2)
            threadLock_1.release()
        else:
            threadLock_2.acquire()
            print(self.index)
            threadLock_2.release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    threadLock_1 = threading.Lock()    
    threadLock_2 = threading.Lock()    
    thread_all = [threadLock_1,threadLock_2]


    a = test(1)
    a.client_COM_timer.start(a.sleeptime)
    a.client_COM_timer.timeout.connect(a.update_data)

    
    b = test(2)
    b.client_COM_timer.start(b.sleeptime)
    b.client_COM_timer.timeout.connect(b.update_data)



    sys.exit(app.exec_())

