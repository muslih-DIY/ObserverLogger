import time
from Logger import ObserverLogger,FileHandler

fileLogger = FileHandler('mylogger.log','TESTER:')


LogQ = ObserverLogger(fileLogger,'Qloggerlog.log','LogQ',batch_size=5)

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