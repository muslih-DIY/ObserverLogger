import threading
import time
from queue import Queue,Empty
from datetime import datetime
import traceback
from typing import  Protocol

class LogHandlerProtocol(Protocol):

    def connect(self):
        ...

    def close(self):
        ...

    def log(self,Data: list,**kwargs):
        ...

class FileHandler():
    
    def __init__(self,filename:str,Logger_name:str) -> None:
        
        self.filename = filename
        self.logger = Logger_name
        self.timef = datetime.now

    def connect(self):
        pass
    
    def log(self,Data:list,**kwargs):

        exception = kwargs.get('exception',False)    

        with open(self.filename,'a+') as f:
            f.write(f'\n{self.timef()}: {self.logger} :\n')
            f.write('\n'.join([str(r) for r in Data]))
            if exception:traceback.print_exc(file=f)

    def close(self):
        pass



class ObserverLogger(threading.Thread):
    
    
    def __init__(
            self,
            LogHandler:LogHandlerProtocol,
            filename:str,
            Logger_name:str,
            interval_sec:int=4,
            batch_size:int=20,
            daemon: bool=True,
            *args,
            **kwargs) -> None:

        self._DataQ:Queue = Queue()

        self._handler = LogHandler

        self.wait = interval_sec

        self.batch_size = batch_size
        
        self.ErrorHandler:FileHandler = FileHandler(
            filename=filename,
            Logger_name=Logger_name)

        super().__init__(*args, **kwargs,daemon=daemon) 

        self._stop_event = threading.Event()

    def run(self):
        while not self.stop_event_active():
            self.log()
            time.sleep(self.wait)

    def stop(self):
        self._stop_event.set()
        self._handler.close()
        self.join() 

    def stop_event_active(self):
        return self._stop_event.is_set()

    def stop_gracefully(self):
        """
        Expecting this method is called when no data is storing to Queue
        
        """
        length =  self._DataQ.qsize()
        print(length)
        self.batch_size = length+5
        self.wait = .1
        self._DataQ.join()
        self.stop() 

    def save(self,data):
        self._DataQ.put_nowait(data)

    def get_data(self,batch_size=None):

        items = []
        if not batch_size:
            batch_size = self.batch_size

        for count in range(0, batch_size):
            if count == batch_size:
                break
            try:
                items.append(self._DataQ.get_nowait())
                self._DataQ.task_done()
            except Empty:
                break
        return items   

    def log(self):        
        data = self.get_data()
        if not data:return
        try:
            self._handler.log(data)
        except:
            self.ErrorHandler.log(Data=data,exception=True)
        



