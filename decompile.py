import subprocess
import time
import os
import sys
import _thread
import threading
import sqlite3

currentThreadNum = 0
mutex = threading.Lock()
JebHomePath = "C:\\Home\\Jeb\\"
device_num = "R5CN7012X5A"
conn = None
cur = None

def db_init():
    if cur == None:
        print("Cur is None")
        exit()
    sql_text = '''CREATE TABLE record(FuckIndex NUMBER,PkgName TEXT,OrgPath TEXT,IsDecomplied TEXT);'''
    cur.execute(sql_text)
    conn.commit()

def db_insert(fuckIndex, pkgName, orgPath, isDecomplied):
    if cur == None:
        print("Cur is None")
        exit() 
    sql_text = "INSERT INTO record VALUES('" + str(fuckIndex) + "', '" + pkgName + "', '" + orgPath + "', '" + isDecomplied + "')"
    cur.execute(sql_text)
    conn.commit()

def db_query():
    if cur == None:
        print("Cur is None")
        exit()

def db_update(fuckIndex):
    if cur == None:
        print("Cur is None")
        exit()
    sql_text = "Update record SET IsDecomplied='true' WHERE FUckIndex=" + str(fuckIndex);
    cur.execute(sql_text)
    conn.commit()

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
            print('Shell failed: ' + result)
            return -1
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


def pull_apk():
    db_init()
    res = shell('adb -s ' + device_num + ' shell "pm list packages -f"',False)
    if res:
        index = 0
        for line in res.splitlines():
            maohao_index = line.find(":")
            equel_index = line.rfind("=")

            orgPath = line[maohao_index + 1 : equel_index] #冒号后面等号前面
            pkgName = line[equel_index + 1 : len(line)] #等号后面的
            path = orgPath[0 : orgPath.rfind('/') + 1] #路径，lastxie_index前面
            if ("com.samsung" in pkgName) | ("com.sec" in pkgName): 
                #创建文件夹
                if not os.path.exists("./" + path):
                    os.makedirs("./" + path)
                #搬运文件
                cmd ="adb -s " + device_num + " pull" + " " + orgPath + " " + "./" + orgPath
                print(cmd)
                if shell(cmd,False) != -1:
                    db_insert(index, pkgName,  orgPath, "false")
                    index += 1


if __name__ == '__main__':
    conn = sqlite3.connect('record.db')
    cur = conn.cursor()      
    #pull_apk()
    
    cur.execute("SELECT max(rowid) from record")
    db_num = cur.fetchone()[0]
    print("Has " + str(db_num) + " records")
    index = -1
    while index < db_num:
        index += 1
        sql_text = "SELECT * FROM record WHERE FuckIndex==" + str(index)
        cur.execute(sql_text)
        res = cur.fetchone()
    
        #根据结果获取包路径     
        isDecomplied = res[3]
        if 'true' in isDecomplied:
            continue
        orgPath = res[2] 
        path = orgPath.replace(".apk", "_decomplie")
        os.makedirs("./" + path)

        db_update(index)
        cmd = JebHomePath + "jeb_wincon.bat -c --srv2 --script=" + JebHomePath + "scripts\\samples\\DecompileFile.py -- " + "./" + orgPath + " " + "./" + path + '/'
        shell(cmd, True)      
        



    cur.close()
    conn.close()
