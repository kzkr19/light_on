# ligt_on
照明をマストドンから操作するためのスクリプト．  

<a href="http://www.youtube.com/watch?feature=player_embedded&v=MZZINun98JE" target="_blank">
<img src="http://img.youtube.com/vi/MZZINun98JE/0.jpg" width="240" height="180" border="10" />
</a>

## 概要
Raspberry Pi ZeroからArduinoを通して照明を制御できるようにする．
マストドンに "cmd\n" から始まる文字列がトゥートされた場合，残りの文字をLispとして処理させ照明のON/OFFが制御できる．

## Arduinoのセットアップ

### 構成
RS304MDを用いる．

### 配線

|Arduino|RS304MD|
|:------|:------|
|5V|VCC|
|GND|GND|
|PIN_SERIAL_TX(2) | 信号線|

### プログラム
`./servo_control/`のArduinoコードを書き込めば良い．

### 参考リンク

[RS303MR/RS304MD 取扱説明書](http://www.futaba.co.jp/img/uploads/files/robot/download/RS303MR_RS304MD_115.pdf)  
[Arduinoでロボゼロのサーボを動かしてみよう！（10） : ROBOMIC（ブログ）](http://micono.cocolog-nifty.com/blog/2011/04/arduino10-5e6a.html)  
[Arduinoでロボゼロのサーボを動かしてみよう！（11）: ROBOMIC（ブログ）](http://micono.cocolog-nifty.com/blog/2011/04/arduino11-17d5.html)  

## Raspberry Piのセットアップ

### 構成
インターネットに接続可能なRaspberry Pi Zeroを用いる．

### ライブラリのインストール
Raspberry Pi Zeroにはpython3版のpyserialは入っていないらしいのでインストールする．

```
pip3 install Mastodon.py
pip3 install pyserial
```

### プログラム
`./python_script`の`main.py`を実行すれば良い．
select_port関数ではポートの先頭の物をArduinoだと決め打ちしているが，その保証はないので適宜変更する．

### 初回起動の手順
まずアプリケーションを新規登録する関係の処理があるので適当なアプリ名(e.g. ligt_on)を入力する．
次にメールアドレスとパスワードを入力してログインする．
初回以降はアクセストークンが保存されるのでこの処理は不要となる．


### 常駐化
crontabで自動起動するようにした．  
参考：[Raspberry Piでプログラムを自動起動する5種類の方法を比較・解説](http://hendigi.karaage.xyz/2016/11/auto-boot/)．


### Azure IoT Hubの利用
以下のチュートリアルに沿って手を動かす．

[Raspberry Pi からクラウドへ (Python) - Raspberry Pi の Azure IoT Hub への接続 | Microsoft Docs](https://docs.microsoft.com/ja-jp/azure/iot-hub/iot-hub-raspberry-pi-kit-python-get-started)

Raspberry Pi ZeroのようにRAMが1GB以下の場合は以下のサイトにあるようにswap領域を広げておかないとビルドが通らない．  
[Raspberry PiとMicrosoft Azureを連携してIoTを活用しよう (1/3)：CodeZine（コードジン）](https://codezine.jp/article/detail/10595)

あとは接続文字列を一重引用符で囲むことに注意すれば躓かないと思う．
僕はその後どうにも調理できなかったのでこれ以上かけない．

## つかいかた
### 照明のON/OFF
照明をつけるコード．
```Clojure
cmd
(def light True)
```

照明をけすコード．
```Clojure
cmd
(def light False)
```

照明がついていたら消す，消えていたらつけるコード．
```Clojure
cmd
(def light (not light))
```

### 関数定義とかもろもろ
時間のうち"分"が素数の場合に照明をつけるコード．

```Clojure
cmd
(do
    (def is-prime (fn (n)
        (if (<= n 1)
             False
            (not
                (contains? 
                    (map (fn (x) (mod n x)) (range 2 n))
                    0)))))
    (def light (is-prime (get-min))))
```

## その他

Lisp処理系で参考にしたもの．  
[（Pythonによる簡単なLispインタープリタ実装方法（四則演算編）） - Python, web, Algorithm 技術的なメモ](http://samurait.hatenablog.com/entry/lisp_interpreter_implementation_in_python)  
[(How to Write a (Lisp) Interpreter (in Python))](http://norvig.com/lispy.html)  

Mastodon.py公式ドキュメント．  
[Mastodon.py — Mastodon.py 1.2.2 documentation](http://mastodonpy.readthedocs.io/en/stable/)
