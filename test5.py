import threading
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys


class test():
    def usethread(self,num):
        self.mythread = threading.Timer(1,self.inquiry,(num,))
        self.mythread.start()
        print(time.strftime('%H:%M:%S'),"开启%d的线程" % num)
    def inquiry(self,num):
        thread_all[num-1].acquire()
        print(time.strftime('%H:%M:%S'),"锁住%d线程" % num)
        if num == 1:
            time.sleep(3)
        else:
            time.sleep(0.01)
        print(time.strftime('%H:%M:%S'),num)
        thread_all[num-1].release()
        self.mythread = threading.Timer(1,self.usethread,(num,))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    threadLock_1 = threading.Lock()    
    threadLock_2 = threading.Lock()    
    thread_all = [threadLock_1,threadLock_2]
    a = test()
    print(time.strftime('%H:%M:%S'),"建立a")
    b = test()
    print(time.strftime('%H:%M:%S'),"建立b")
    
    a.usethread(1)

    b.usethread(2)
    sys.exit(app.exec_())