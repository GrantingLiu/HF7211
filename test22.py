import threading
import time 
from test11 import threadLock_1,test

def test2():
    threadLock_1.acquire()
    print("文件2开始锁死")
    time.sleep(10)
    threadLock_1.release()
    print("文件2结束")


if __name__ == '__main__':
    thread_updateUi = threading.Thread(target=test)     # 目标函数不能带括号，函数如果有参数要写arg=()
    #thread_updateUi.setDaemon(True)
    thread_updateUi.start()
    print("开启UI线程1")

    thread_updateUi = threading.Thread(target=test2)
    thread_updateUi.start()
    print("开启UI线程2")