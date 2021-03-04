import threading
import time 
import sys,functools
threadLock_1 = threading.Lock()

def test():
    threadLock_1.acquire()
    print("文件1开始锁死")
    time.sleep(10)
    threadLock_1.release()
    print("文件1结束")
    
