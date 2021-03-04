
import threading
import time
 
def thread1():
    while True:
        threadLock_1.acquire()
        time.sleep(3)
        print(time.strftime('%H:%M:%S'),'hahaha')
        threadLock_1.release()
 
def thread2():
    while True:
        threadLock_2.acquire()
        time.sleep(1)
        print(time.strftime('%H:%M:%S'),'lalala')
        threadLock_2.release()
 
if __name__ == '__main__':
    threadLock_1 = threading.Lock() 
    threadLock_2 = threading.Lock()

    thread_thred1 = threading.Thread(target=thread1)
    thread_thred1.start()


    thread_thread2 = threading.Thread(target=thread2)
    thread_thread2.start()