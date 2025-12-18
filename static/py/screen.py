import time
import queue
import ctypes
import threading
        
class ScreenWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.commands = queue.Queue()
        self.daemon = True
        self.running = True
    
    def run(self):                    
        print("> The screen is awais on!")

        while True:
            ctypes.windll.user32.keybd_event(0x7E, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x7E, 0, 0x0002, 0)
            time.sleep(290)

screen = ScreenWorker()
screen.start()