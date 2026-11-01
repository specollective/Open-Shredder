#include "DCDriver.h"

DCDriver::DCDriver(uint8_t pinPWM, uint8_t pinDir, uint8_t pinCurrent) {
    _pinPWM = pinPWM;
    _pinDir1 = pinDir;
    _pinCurrent = pinCurrent;
    _currentSpeed = 0;
}

void DCDriver::begin() {
    pinMode(_pinPWM, OUTPUT);
    pinMode(_pinDir1, OUTPUT);
    pinMode(_pinCurrent, INPUT);
    stop();
}

void DCDriver::setSpeed(int speed_percent) {
    _currentSpeed = speed_percent;

    // Clamp
    if (_currentSpeed > 100) _currentSpeed = 100;
    if (_currentSpeed < -100) _currentSpeed = -100;

    int pwmValue = map(abs(_currentSpeed), 0, 100, 0, 255);

    if (_currentSpeed > 0) {
        digitalWrite(_pinDir1, HIGH);
        analogWrite(_pinPWM, pwmValue);
    } else if (_currentSpeed < 0) {
        digitalWrite(_pinDir1, LOW);
        analogWrite(_pinPWM, pwmValue);
    } else {
        stop();
    }
}

void DCDriver::stop() {
    _currentSpeed = 0;
    analogWrite(_pinPWM, 0);
    // Depending on driver, we might want to disable ENABLE pin if we had one.
    // Here we just zero PWM.
}

void DCDriver::update() {
    // No continuous update needed for hardware PWM
}

int DCDriver::getLoad() {
    // Read analog value 0-1023
    return analogRead(_pinCurrent);
}

bool DCDriver::isFaulted() {
    // DC Drivers usually don't have a fault output unless sophisticated.
    // We rely on getLoad() in the controller.
    return false;
}
