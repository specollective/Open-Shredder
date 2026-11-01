#ifndef STEPPER_DRIVER_H
#define STEPPER_DRIVER_H

#include "MotorInterface.h"

#ifdef ARDUINO
    #include <Arduino.h>
#else
    #include "../tests/mock_arduino.h"
#endif

class StepperDriver : public MotorInterface {
private:
    uint8_t _pinStep;
    uint8_t _pinDir;
    uint8_t _pinEnable; // Active LOW usually
    uint8_t _pinAlarm;  // Input from driver (e.g. Leadshine Alarm)

    long _stepIntervalMicros;
    unsigned long _lastStepTime;
    bool _stepState;
    int _currentSpeed;
    bool _enabled;

public:
    StepperDriver(uint8_t pinStep, uint8_t pinDir, uint8_t pinEnable, uint8_t pinAlarm = 255);

    void begin() override;
    void setSpeed(int speed_percent) override;
    void stop() override;
    void update() override; // Must be called frequently to generate pulses
    int getLoad() override;
    bool isFaulted() override;
};

#endif
