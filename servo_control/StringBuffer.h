#ifndef STRING_BUFFER_HEADER_FILE
#define STRING_BUFFER_HEADER_FILE

#include<inttypes.h>
#include<string.h>

class StringBuffer {
  public:
    // コンストラクタ
    StringBuffer(uint16_t buff_size) {
      buff_ = (char*)malloc(buff_size * sizeof(char));
      buff_size_ = buff_size;
      len_ = 0;
    }

    // デストラクタ
    ~StringBuffer() {
      free(buff_);
    }

    // dataをバッファに追加する関数
    // data: pushしたい文字
    void Push(char data) {
      if (IsOverflow()) {
        return;
      } else {
        buff_[len_] = data;
        len_++;
      }
    }

    // バッファに溜まってる文字列の長さを取得する関数
    uint16_t GetLength() const {
      return len_;
    }

    // バッファオーバーフローしたらtrue
    bool IsOverflow()const {
      // null文字を考慮
      return len_ == buff_size_ - 1;
    }

    // end_strで文字列が終わっていたらtrue
    bool EndsWith(const char *end_str) const {
      const uint16_t end_length = strlen(end_str);

      if ( len_ < end_length )return false;

      for (uint16_t i = 0 ; i < end_length ; i++ ) {
        if ( end_str[i] != buff_[i + len_ - end_length]) {
          return false;
        }
      }

      return true;
    }

    // バッファに入っている文字列をcopy_toにコピーする関数
    void Copy(char *copy_to) const {
      buff_[len_] = '\0';
      strcpy(copy_to,buff_);
    }

    // バッファをクリアする関数
    void Clear() {
      len_ = 0;
    }

  private:
  
    uint16_t len_;        // バッファに格納された文字列の長さ
    char *buff_;          // バッファ
    uint16_t buff_size_;  // バッファサイズ
};
#endif


