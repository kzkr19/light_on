#include "StringBuffer.h"
#include "Servo.h"
#include "SoftwareSerial.h"
#include "RS304.h"


// 状態を格納する変数
typedef struct _State {
  bool servo_right;
  bool led_on;
} State;

// PCからの命令を読み取った結果を表す列挙型
enum Command {
  COMMAND_NONE,
  COMMAND_SERVO_LEFT,
  COMMAND_SERVO_RIGHT,
  COMMAND_LED_ON,
  COMMAND_LED_OFF,
};

const int PIN_SERIAL_RX = 3;
const int PIN_SERIAL_TX = 2;
const int PIN_LED = 13;
const int SERVO_ID = 1;
const int BUFFER_SIZE = 16;
const int ANGLE_LEFT = -500;
const int ANGLE_RIGHT = +500;

SoftwareSerial ser(PIN_SERIAL_RX, PIN_SERIAL_TX);
RS304 servo(&ser);

void setup() {
  Serial.begin(9600);
  ser.begin(115200);
  delay(500);

  pinMode(PIN_LED, OUTPUT);
  servo.SetTorque(SERVO_ID, true);
}

void loop() {
  // 状態を表す変数
  static State state = {true, false};

  // 命令の読み取り
  const Command cmd = ReadCommand();

  // 命令によって状態を変更
  ChangeState(cmd, state);

  // 状態に応じて出力
  Output(state);
}

// 状態を受け取り状態に応じてアクチュエータに出力する関数
void Output(const State state) {
  if ( state.servo_right ) {
    servo.SetAngle(SERVO_ID, ANGLE_RIGHT);
  } else {
    servo.SetAngle(SERVO_ID, ANGLE_LEFT);
  }

  if ( state.led_on ) {
    digitalWrite(PIN_LED, HIGH);
  } else {
    digitalWrite(PIN_LED, LOW);
  }
}

// 命令によって状態を変更する関数
void ChangeState(Command cmd, State &state) {
  if ( cmd == COMMAND_SERVO_RIGHT ) {
    state.servo_right = true;
  } else if (cmd == COMMAND_SERVO_LEFT) {
    state.servo_right = false;
  } else if (cmd == COMMAND_LED_ON) {
    state.led_on = true;
  } else if (cmd == COMMAND_LED_OFF) {
    state.led_on = false;
  }
}

// 1行Serialから読み取り，解析してCommand列挙体を返す関数
Command ReadCommand() {
  Command ret;
  char buff[BUFFER_SIZE];

  if ( not ReadLine(buff)) {
    ret = COMMAND_NONE;
  } else if ( strcmp(buff, "servo-right\r\n") == 0 ) {
    ret =  COMMAND_SERVO_RIGHT;
  } else if (strcmp(buff, "servo-left\r\n") == 0 ) {
    ret = COMMAND_SERVO_LEFT;
  } else if ( strcmp(buff, "led-on\r\n") == 0) {
    ret = COMMAND_LED_ON;
  } else if ( strcmp(buff, "led-off\r\n") == 0) {
    ret = COMMAND_LED_OFF;
  } else {
    ret = COMMAND_NONE;
  }

  return ret;
}

// Serialから1行だけ読み出す関数
// 読み出せたらtrueを返し，buffに文字列が格納される
bool ReadLine(char buff[]) {
  static StringBuffer str_buff(BUFFER_SIZE);

  while (Serial.available()) {
    const char c = Serial.read();

    str_buff.Push(c);

    if ( str_buff.EndsWith("\r\n")) {
      str_buff.Copy(buff);
      str_buff.Clear();
      return true;
    }

    if ( str_buff.IsOverflow() ) {
      str_buff.Clear();
    }
  }

  return false;
}

