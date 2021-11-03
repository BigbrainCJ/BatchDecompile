import subprocess
import time
import os
import sys
import _thread
import threading


currentThreadNum = 0
mutex = threading.Lock()



def shell(cmd, ifPrint):   
    result = ''
    if ifPrint == False:    
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            if line:
                tmp = line.decode('utf-8') + '\n'
                result += tmp
        if p.returncode != 0:
            print('Shell failed' + result)
        return result
    else:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT , universal_newlines=True)
        for line in iter(p.stdout.readline,""):
            sys.stdout.write('\\'+line[:-1])
            print("")
            sys.stdout.flush()
        return result

    
  

def thread_run(cmd, ifPrint):
    print("new thread!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    global currentThreadNum
    global mutex

    mutex.acquire()
    currentThreadNum += 1
    mutex.release()
    shell(cmd,ifPrint);
    
    mutex.acquire()
    currentThreadNum -= 1
    mutex.release()


if __name__ == '__main__':
    
    JebHomePath = "C:\\Home\\Jeb\\"
    pkgName_list = []
    path_list = []

    res = shell('adb -s 5ef0314a shell "pm list packages -f"',False)
    if res:
        for line in res.splitlines():
            maohao_index = line.find(":")
            lastxie_index = line.rfind("/", 0, len(line))
            equel_index = line.rfind("=", 0, len(line))

            orgPath = line[maohao_index + 1 : equel_index]
            pkgName = line[equel_index + 1 : len(line)] #等号后面的
            path = line[maohao_index + 1 : lastxie_index + 1] #路径，lastxie_index前面
            pkgName_list.append(pkgName)
            path_list.append(path)

            #创建文件夹
            if not os.path.exists("./" + path):
                os.makedirs("./" + path)
            
            #搬运文件
            cmd ="adb -s 5ef0314a pull" + " " + orgPath + " " + "./" + orgPath
            print(cmd)
            res2 = shell(cmd,False)

            #解压及反编译  多线程
            cmd = JebHomePath + "jeb_wincon.bat -c --srv2 --script=" + JebHomePath + "scripts\\samples\\DecompileFile.py -- " + "./" + orgPath + " " + "./" + path
            shell(cmd, True)
          
