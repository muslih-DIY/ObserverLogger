from logging import exception
import threading
import time
from queue import Queue,Empty
from datetime import datetime
import traceback
from typing import  List, Protocol

class LogHandler(Protocol):

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

    def connect():
        pass
    
    def log(self,Data:list,**kwargs):

        exception = kwargs.get('exception',False)    

        with open(self.filename,'a+') as f:
            f.write(f'\n{self.timef()}: {self.logger} :')
            f.write('\n'.join([str(r) for r in Data]))
            if exception:traceback.print_exc(file=f)

    def close():
        pass



class ObserverLogger(threading.Thread):
    
    _DataQ:Queue = None
    
    _handler:LogHandler=None
    
    def __init__(
            self,DataQ:Queue,
            LogHandler:LogHandler,
            filename:str,
            Logger_name:str,
            interval_sec:int=4,
            batch_size:int=20,
            daemon: bool=True,
            *args,
            **kwargs) -> None:

        self._DataQ = DataQ

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

    def stop_event_active(self):
        return self._stop_event.is_set()

    def stop_gracefully(self):
        """
        Expecting this method is called when no data is storing to Queue
        
        """        
        self._data_Q.join()
        self.stop()
        self.join()    

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
                items.append(self._data_Q.get_nowait())
                self._data_Q.task_done()
            except Empty:
                break
        return items   

    def log(self):        
        data = self.get_data()
        try:
            self._handler(data)
        except:
            FileHandler.log(data,exception=True)
        



