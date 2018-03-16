#ifndef RS304_HEADER_FILE
#define RS304_HEADER_FILE

#include "SoftwareSerial.h"
#define TO_BYTES(v) ((byte*)(&(v)))

enum ADDRESS {
  ADDRESS_CW_ANGLE_LIMIT_L  = 0x08,
  ADDRESS_CW_ANGLE_LIMIT_H  = 0x09,
  ADDRESS_CCW_ANGLE_LIMIT_L = 0x0a,
  ADDRESS_CCW_ANGLE_LIMIT_H = 0x0b,
  ADDRESS_GOAL_ANGLE_L      = 0x1e,
  ADDRESS_GOAL_ANGLE_H      = 0x1f,
  ADDRESS_GOAL_TIME_L       = 0x20,
  ADDRESS_GOAL_TIME_H       = 0x21,
  ADDRESS_TORQUE_ENABLE     = 0x24,
};

class RS304 {
  public:
    RS304(SoftwareSerial *ser) {
      ser_ = ser;
    }

    void SetAngle(byte id, int16_t angle) {
      SendData(id, 0, (byte)ADDRESS_GOAL_ANGLE_L, 2, 1, TO_BYTES(angle));
    }

    void SetTorque(byte id, bool enable) {
      SendData(id, 0, (byte)ADDRESS_TORQUE_ENABLE, 1, 1, TO_BYTES(enable));
    }

    void SendData(
      const byte id,  const byte flag,  const byte address,
      const byte len, const byte count, const byte *data) {

      byte checksum = id ^ flag ^ address ^ len ^ count;

      ser_->write(0xfa);
      ser_->write(0xaf);
      ser_->write(id);
      ser_->write(flag);
      ser_->write(address);
      ser_->write(len);
      ser_->write(count);

      for (int i = 0 ; i < len ; i++ ) {
        ser_->write(data[i]);
        checksum ^= data[i];
      }
      ser_->write(checksum);
    }

  private:
    SoftwareSerial *ser_;
};

#endif

