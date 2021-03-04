import threading
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys


class test():
    def __init__(self,index):
        self.index = index
        self.client_COM_timer = QTimer() 
        self.client_COM_timer.timeout.connect(self.update_data)
        if self.index == 1:
            sleeptime = 1000
        else:
            sleeptime = 200
        self.client_COM_timer.start(sleeptime)


    def update_data(self):
        self.thread_inquiry = threading.Thread(target=self.update_time)
        self.thread_inquiry.setDaemon(True)
        self.thread_inquiry.start()


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
 
    b = test(2)
 
    sys.exit(app.exec_())


