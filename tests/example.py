import time
from pathlib import Path

import sys,os

project_path = os.path.abspath(Path(__file__).resolve().parent.parent)
sys.path.append(project_path)


from Observer_Logger import ObserverLogger,FileHandler

fileLogger_LOG = os.path.join(project_path,'tests','mylogger.log')
ObserverLogger_LOG = os.path.join(project_path,'tests','Qloggerlog.log')

fileLogger = FileHandler(fileLogger_LOG,'TESTER:')


LogQ = ObserverLogger(fileLogger,ObserverLogger_LOG,'ObserverLog',batch_size=5)

LogQ.start()

c='a'
i=18
try:
    while 1:
        for j in range(1,i):
            LogQ.save(c*j)
        time.sleep(5)
        i=i+1
        c=chr(ord(c)+1)
        if i==25:break
except:
    print("exception found")
else:
    print("no exception found")    
finally:
    s=time.perf_counter()
    print('stoping gracefully')
    LogQ.stop_gracefully()
    # print('stoping.')
    # LogQ.stop()    
    print('Duration:',time.perf_counter()-s)