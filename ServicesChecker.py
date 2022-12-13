import socket
import codecs
from time import sleep
from os import system as cmd
import psutil
try:
    import requests
except:
    cmd("python -m pip install requests")
    import requests

class mcstatus:
    def __init__(self,hostname,port = 25565,timeout = 0.6):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout
    def status(self):
        # 初始化
        mcsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname(self.hostname)
        try:
            # 尝试连接
            mcsocket.settimeout(self.timeout)
            mcsocket.connect((ip,self.port))
            mcsocket.send(bytearray([0xFE, 0x01]))
            data_raw = mcsocket.recv(1024)
            mcsocket.close()
            # 使用 cp437 编码方式解码
            data = data_raw.decode('cp437').split('\x00\x00\x00')
            info = {}
            info['version'] = data[2].replace("\x00","")
            info['online'] = data[4].replace("\x00","")
            info['maxp'] = data[5].replace("\x00","")
            info['motd'] = codecs.utf_16_be_decode(data_raw[1:])[0].split('\x00')[3]
            return info
        except socket.error:
            # 无法连接到服务器
            return False

def getPID(taskname):
    pl = psutil.pids()
    for pid in pl:
        if(psutil.Process(pid).name == taskname):
            return pid
    return False

def taskkill():
    cmd("taskkill -im java.exe -f")

def start():
    cmd("start ServerMain.exe")

srv = mcstatus('mc.hjfunny.site')   
#srv = mcstatus('s4.i7xl.cn',10116)
errorlevel = 0
maxerrorlevel = 5
while(1):
    cmd("cls")
    print(srv.hostname + ":" + str(srv.port), end = '')
    srvstat = srv.status()
    if(srvstat == False):
        errorlevel += 1
        print()
        print("无法连接到服务器，错误次数：" + str(errorlevel))
        if(errorlevel >= maxerrorlevel):
            print("已超过最大允许错误次数，开启诊断模式")
            print("获取远端控制信息……")
            inforeq = requests.get("https://codezhangborui.eu.org/static/javawatchdog.info")
            if(inforeq.text != 'normal'):
                print("解析远端控制信息……")
                if(inforeq.text == 'taskkill'):
                    print("远端请求结束进程")
                    taskkill()
                if(inforeq.text == 'start'):
                    print("远端请求启动服务器")
                    start()
                if(inforeq.text == 'noaction'):
                    print("远端请求不做任何动作")
            else:
                print("远端未提供任何信息，执行本地策略")
                print("检查 Java 是否在运行…… ", end = '')
                if(getPID('java.exe') == False):
                    print("否")
                    print("尝试启动服务器…… ")
                    start()
                    sleep(180)
                    if(srv.status() == False):
                            print("失败")
                            print("-----")
                            print("本地策略无法完成")
                    else:
                            print("成功")
                            print("-----")
                            print("诊断结束：服务器未启动")
                else:
                    print("是")
                    print("再次检查服务器是否开放…… ", end = '')
                    if(srv.status() == False):
                        print("否")
                        print("尝试直接结束进程…… ", end = '')
                        taskkill()
                        sleep(180)
                        if(srv.status() == False):
                            print("失败")
                            print("-----")
                            print("本地策略无法完成")
                        else:
                            print("成功")
                            print("-----")
                            print("诊断结束：服务器停止响应玩家请求")
                    else:
                        print("是")
                        print("-----")
                        print("诊断结束：服务器可能临时崩溃或正在启动")
                
    else:
        errorlevel = 0
        print("          " + srvstat['version'] + " | " + str(srvstat['online']) + "/" + str(srvstat['maxp']))
        print(srvstat['motd'])
    sleep(60)
