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
    """
    simple file logger handler

    exception = kwargs.get('exception',False)

    message = kwargs.get('message')

    f.write(f'\n{self.timef()}: {self.logger} : {message} \n')

    then data


    """
    def __init__(self,filename:str,logger_name:str) -> None:

        self.filename = filename
        self.logger = logger_name
        self.timef = datetime.now

    def connect(self):
        "No connect"

    def log(self,data:list,**kwargs):
        "Log the data to file"
        exception = kwargs.get('exception',False)
        header = kwargs.get('header',False)
        message = kwargs.get('message')
        with open(self.filename,'a+',encoding='utf-8') as f:
            if header:
                f.write(f'\n{self.timef()}: {self.logger} : {message} \n')
            f.write('\n'.join([str(r) for r in data]))
            if exception:
                traceback.print_exc(file=f)

    def close(self):
        "No need of close"



class ObserverLogger(threading.Thread):
    """
    Observer logger is producer
    and Handler will be the consumer
    """
    def __init__(self,
        LogHandler:LogHandlerProtocol,
        filename:str,
        logger_name:str,
        *args,
        interval_sec:int=4,
        batch_size:int=20,
        daemon: bool=True,
        **kwargs) -> None:
        """_summary_

        Args:
            LogHandler (LogHandlerProtocol): _description_
            filename (str): _description_
            Logger_name (str): _description_
            interval_sec (int, optional): _description_. Defaults to 4.
            batch_size (int, optional): _description_. Defaults to 20.
            daemon (bool, optional): _description_. Defaults to True.
        """

        self._data_queue:Queue = Queue()

        self._handler = LogHandler

        self.wait = interval_sec

        self.batch_size = batch_size

        self.error_handler:FileHandler = FileHandler(
            filename=filename,
            logger_name=logger_name)

        super().__init__(*args, **kwargs,daemon=daemon)

        self._stop_event = threading.Event()

    def run(self):
        "run the program till the stop event is active"
        while not self.stop_event_active():
            self.log()
            time.sleep(self.wait)

    def stop(self):
        "stop the logger"
        self._stop_event.set()
        self._handler.close()
        self.join()

    def stop_event_active(self):
        "stop the thread event"
        return self._stop_event.is_set()

    def stop_gracefully(self):
        """
        Expecting this method is called when no data is storing to Queue

        """
        length =  self._data_queue.qsize()

        self.batch_size = length+5
        self.wait = .1
        self._data_queue.join()
        self.stop()

    def save(self,data):
        "save data to queue"
        self._data_queue.put_nowait(data)

    def get_data(self,batch_size=None):
        "Get data from the queue"
        items = []
        if not batch_size:
            batch_size = self.batch_size

        for count in range(0, batch_size):
            if count == batch_size:
                break
            try:
                items.append(self._data_queue.get_nowait())
                self._data_queue.task_done()
            except Empty:
                break
        return items

    def log(self):
        "Internally call the handlers log funtion"
        data = self.get_data()
        if not data:
            return
        try:
            self._handler.log(data)
        except Exception as ess:
            self.error_handler.log(
                data=data,
                exception=True,
                header=True,
                message=str(ess))
        



