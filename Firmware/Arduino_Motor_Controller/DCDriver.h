#ifndef DC_DRIVER_H
#define DC_DRIVER_H

#include "MotorInterface.h"

// Check if we are in Arduino environment, otherwise mock it or use standard types
#ifdef ARDUINO
    #include <Arduino.h>
#else
    #include "../tests/mock_arduino.h"
#endif

class DCDriver : public MotorInterface {
private:
    uint8_t _pinPWM;
    uint8_t _pinDir1;
    uint8_t _pinDir2; // Optional, set to -1 if using DIR/PWM mode
    uint8_t _pinCurrent;

    int _currentSpeed;

public:
    // Constructor for PWM + DIR (1 pin)
    DCDriver(uint8_t pinPWM, uint8_t pinDir, uint8_t pinCurrent);

    // Constructor for PWM + DIR1 + DIR2 (H-Bridge like L298N)
    // Note: If L298N is used with 1 PWM pin + 2 Control pins.
    // Or if using BTS7960, often it's R_EN, L_EN, R_PWM, L_PWM.
    // We will stick to a generic architecture:
    // Speed (PWM) + Direction (High/Low) is most common for high power drivers.

    void begin() override;
    void setSpeed(int speed_percent) override;
    void stop() override;
    void update() override; // DC motor PWM is handled by hardware, so this might be empty
    int getLoad() override;
    bool isFaulted() override;
};

#endif
