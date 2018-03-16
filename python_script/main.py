from mastodon import Mastodon
import serial
from serial.tools import list_ports
import sys
import time
import re
from xml.sax.saxutils import unescape
import os

from use_mastodon import get_mastodon_instance, read_since_id, write_since_id, get_my_id
from lisp_processor import LispProcessor

def select_port():
    ports = list_ports.comports()
    n_port = len(ports)
    
    return serial.Serial(ports[0].device,9600)

    if n_port == 0:
        print("com port not found")
        sys.exit(0)
    elif n_port == 1:
        print("com port found: " + ports[0].device)
        n = 0
    else:
        # ポート選択
        print("%d com ports found" % n_port)
        for i,port in enumerate(ports):
            print("%5d : %s" % (i,port.device))
        
        print("intput number of device:")
        n = int(input())
    
    ser = serial.Serial(ports[n].device, 9600)
    
    return ser


def analyze_content(content,lisp):
    lines = re.split(r"\<[^>]*>",content)
    lines = lines[1:len(lines)-1]
    
    if lines[0] != "cmd":
        return True,None
    
    code = unescape("".join(lines[1:]))
    try:
        return True,lisp.execute(code)
    except:
        return False,sys.exc_info()[1].args[0]

def process_toot(toot,my_id,lisp,mastodon):
    if toot["account"]["id"] != my_id:
        return
    succ,result = analyze_content(toot["content"],lisp)
    
    print("content: %s" % (toot["content"]))
    
    if result is None:
        pass
    elif succ:
        result = "Success: %s" % str(result)
    else:
        result = "Failed: %s" % str(result)
    
    if not result is None:
        mastodon.status_post(
            result, 
            in_reply_to_id = toot["id"],
            visibility='unlisted'
        )
        print(result)

def output_arduino(lisp,ser):
    if isinstance(lisp.env["light"],bool):
        if lisp.env["light"]:
            ser.write(b"servo-right\r\n")
        else:
            ser.write(b"servo-left\r\n")
    
    if isinstance(lisp.env["led"],bool):
        if lisp.env["led"]:
            ser.write(b"led-on\r\n")
        else:
            ser.write(b"led-off\r\n")

def execute_every_min(old_exec_time,lisp,mastodon):
    tm = time.localtime()
    new_exec_time = tm.tm_hour * 100 + tm.tm_min
    
    if old_exec_time != new_exec_time:
        try:
            result = "every-min executed: %s" % str(lisp.execute("(every-min)"))
        except:
            result = "every-min failed: %s" % sys.exc_info()[1].args[0]
        
        mastodon.status_post(
            result, 
            visibility='unlisted'
        )
        
    return new_exec_time
    
def main():
    mastodon = get_mastodon_instance()
    ser = select_port()
    since_id = read_since_id()
    my_id = get_my_id(mastodon)
    lisp = LispProcessor()
    old_exec_time = -1
    
    lisp.execute("(def light True)")
    lisp.execute("(def led True)")
    lisp.execute("(def every-min (fn () (def every-min every-min)))")
    lisp.execute("""
(def contains? (fn (xs x)
    (if (empty? xs)
        False
        (if (= x (first xs))
            True
            (contains? (rest xs) x)))))
""")

    while True:
        # 新しいtoot一覧を取得
        toots = mastodon.timeline(
            timeline='home',
            since_id=since_id,
            max_id=None,
            limit=None)
        
        # since_idを更新
        if len(toots) != 0:
            since_id = toots[0]["id"]
            write_since_id(since_id)
        else:
            print("no new toot")
        
        # TLのtootから自分が発したトゥートを取り出し
        # 文字列を読み込んでいろいろやる
        for toot in toots[::-1]:
            process_toot(toot,my_id,lisp,mastodon)
        
        # 1分ごとにevery-min関数を実行させる
        # old_exec_time = execute_every_min(old_exec_time,lisp,mastodon)
        
        # Arduinoに出力
        output_arduino(lisp,ser)
        
        time.sleep(5)

def mylog(txt):
    with open("./log.txt","a") as f:
        f.write(txt + "\n")


if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__))) 
    mylog("executed: " + time.ctime())
    try:
        print("sleeping..")
        time.sleep(120)
        main()
    except:

        print(sys.exc_info())
        mylog("error:" + str(sys.exc_info()))

