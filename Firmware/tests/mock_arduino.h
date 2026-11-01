#ifndef MOCK_ARDUINO_H
#define MOCK_ARDUINO_H

#include <stdint.h>
#include <iostream>
#include <map>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <cmath>

// Mock Types
#define uint8_t unsigned char
#define LOW 0
#define HIGH 1
#define OUTPUT 1
#define INPUT 0
#define INPUT_PULLUP 2
#define A0 14 // A0 is typically digital pin 14 on Uno
#define A1 15
#define A2 16
#define A3 17
#define A4 18
#define A5 19

// Mock State
extern std::map<int, int> pinStates;
extern std::map<int, int> pinModes;
extern std::map<int, int> analogInputs;

// Functions
inline void pinMode(uint8_t pin, uint8_t mode) {
    pinModes[pin] = mode;
}

inline void digitalWrite(uint8_t pin, uint8_t val) {
    pinStates[pin] = val;
}

inline int digitalRead(uint8_t pin) {
    if (pinStates.find(pin) != pinStates.end()) {
        return pinStates[pin];
    }
    return LOW;
}

inline void analogWrite(uint8_t pin, int val) {
    pinStates[pin] = val; // Store PWM as state for testing
}

inline int analogRead(uint8_t pin) {
    if (analogInputs.find(pin) != analogInputs.end()) {
        return analogInputs[pin];
    }
    return 0;
}

inline long map(long x, long in_min, long in_max, long out_min, long out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// Remove custom abs to avoid conflict with std::abs.
// Arduino uses a macro usually, but we can just rely on std::abs or a macro if needed.
// If code uses abs(), it will pick up std::abs from <stdlib.h> or <cmath>
#ifndef abs
#define abs(x) ((x)>0?(x):-(x))
#endif

// Time mocking
extern unsigned long mock_millis;
inline unsigned long millis() {
    return mock_millis;
}

inline unsigned long micros() {
    return mock_millis * 1000;
}

inline void delay(unsigned long ms) {
    mock_millis += ms;
}

// Serial Mock
class SerialMock {
public:
    void begin(long speed) {}
    void println(const char* s) { std::cout << s << std::endl; }
    void println(int i) { std::cout << i << std::endl; }
    void print(const char* s) { std::cout << s; }
    void print(int i) { std::cout << i; }
};
extern SerialMock Serial;

#endif
