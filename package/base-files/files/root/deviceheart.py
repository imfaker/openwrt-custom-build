from encodings.utf_8 import encode
from enum import Enum
from http.client import HTTPException
from threading import Thread
import time
import platform
from urllib.error import HTTPError
import requests

import logging
import logging.handlers
# from hashlib import sha256
import hmac, base64

# key = signmsg = deviceId + timeStamp
# sign = get_sha256(signmsg,b'MjpK6DOfyAMnJOWUZXvAaNqipOL2eZiUBRDkRBmB5CMaUY1yznKrNaLBVqhkaDRJ')
def get_sha256(data, key):
 
    # key = key.encode('utf-8')       # sha256加密的key
    message = data.encode('utf-8')  # 待sha256加密的内容\
    # sign1 = base64.b64encode(hmac.new(key, message, digestmod=sha256).digest()).decode()
    sign = base64.b64encode(hmac.new(key, message, digestmod="sha256").digest())
    sign = str(sign, 'utf-8')

    return sign

logger = logging.getLogger('manager')
# 输出到控制台, 级别为DEBUG
console = logging.StreamHandler()  
console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console.setLevel(logging.DEBUG)
logger.addHandler(console)

# 输出到文件, 级别为INFO, 文件按大小切分
filelog = logging.handlers.RotatingFileHandler('log.txt', maxBytes=1024*1024, backupCount=5,encoding='utf-8')
filelog.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.setLevel(logging.DEBUG)
logger.addHandler(filelog)


# 按时间切分
# logging.handlers.TimedRotatingFileHandler(filename="all.log", when='S', interval=1, backupCount=3,encoding='utf-8')

loopTime = 60
delay_minutes=40
host='http://notify.cloudtu.cn/api/notify'
thread_list=[]


localIdFilePath = './identity.txt'

import uuid

version = "1"
deviceType = "deviceType1"
deviceId = ""
firmwareVersion = "1"
mainboard = ""
macAddress = ""


class RequestMethod(Enum):
    activate = "activate"
    connect = "connect"



def getSystemInfo():
    global mainboard
    # ('64bit', '')
    # uname =  uname_result(system='Linux', node='OpenWrt', release='5.10.88', version='#0 SMP Fri Dec 31 08:05:40 2021', machine='x86_64')
    # Linux
    # x86_64
    #

    # logger.info('architecture = %s',platform.architecture())
    # logger.info('uname = %s',platform.uname())
    mainboard = platform.system() + platform.machine() + platform.processor()


def get_mac_address():
    global macAddress
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]

    displayMac = ":".join([mac[e:e+2] for e in range(0,11,2)])
    logger.info('displayMac:%s',displayMac)
    macAddress = displayMac
    return displayMac


# 
def readLocalIdentityId():
    try:
        with open(localIdFilePath,'r+', encoding="utf-8") as f:
            read_data = f.read()
            return  read_data
  
    except FileNotFoundError:
        return None
    except Exception as e: 
        return None

def writeLocalIdentityId(id):
    try:
        with open(localIdFilePath,'w', encoding="utf-8") as f:
            data = id
            f.write(data)
            
    except FileNotFoundError:
        return 
    except Exception as e:  
        return 

def generateAndActiveMachineDeviceId():
    id = uuid.uuid1().hex
    return id

 
    
def getMachineId():
    id =  readLocalIdentityId()
    if id == None or id == "" :
        logger.info('device-id is none ,begin generate') 
        id = generateAndActiveMachineDeviceId()
        writeLocalIdentityId(id)
        return id
    else:
        return  id
    
def sendNetworkRequest(method,deviceId):
    timeStamp = str(int(round(time.time() * 1000))) 
    signmsg = deviceId + timeStamp
    sign = get_sha256(signmsg,b'MjpK6DOfyAMnJOWUZXvAaNqipOL2eZiUBRDkRBmB5CMaUY1yznKrNaLBVqhkaDRJ')
    
    json = {'version': version,"device_id":deviceId,"device_type":deviceType,"mac_address":macAddress,"firmware_version":firmwareVersion,"mainboard":mainboard,"timestamp":timeStamp,"method": method.value,"signature":sign}
    header = {"Content-Type":"application/json"}
    r = requests.request(method='post', url=host,json=json,headers=header,timeout=10)
    r.raise_for_status()
    return
        
  


getSystemInfo()
get_mac_address()
deviceId = getMachineId()
while True:
    try:
        sendNetworkRequest(RequestMethod.connect,deviceId=deviceId)
    except Exception as e:
        pass
    finally:
        time.sleep(loopTime)
            
  
#13位毫秒 字符串  
# millis = int(round(time.time() * 1000))
# print millis


# if __name__=='__main__':
#     run_manage()