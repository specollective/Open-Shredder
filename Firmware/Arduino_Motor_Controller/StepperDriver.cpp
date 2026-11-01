#include "StepperDriver.h"

StepperDriver::StepperDriver(uint8_t pinStep, uint8_t pinDir, uint8_t pinEnable, uint8_t pinAlarm) {
    _pinStep = pinStep;
    _pinDir = pinDir;
    _pinEnable = pinEnable;
    _pinAlarm = pinAlarm;
    _currentSpeed = 0;
    _stepIntervalMicros = 0;
    _lastStepTime = 0;
    _stepState = false;
    _enabled = false;
}

void StepperDriver::begin() {
    pinMode(_pinStep, OUTPUT);
    pinMode(_pinDir, OUTPUT);
    pinMode(_pinEnable, OUTPUT);
    digitalWrite(_pinEnable, HIGH); // Disable by default (High Impedance)

    if (_pinAlarm != 255) {
        pinMode(_pinAlarm, INPUT_PULLUP);
    }
}

void StepperDriver::setSpeed(int speed_percent) {
    _currentSpeed = speed_percent;

    if (_currentSpeed == 0) {
        stop();
        return;
    }

    // Enable Driver
    if (!_enabled) {
        digitalWrite(_pinEnable, LOW); // Enable (Active Low common)
        _enabled = true;
    }

    // Set Direction
    if (_currentSpeed > 0) {
        digitalWrite(_pinDir, HIGH);
    } else {
        digitalWrite(_pinDir, LOW);
    }

    // Calculate Interval
    // Max Speed: Let's assume 100% = 2000 steps/sec (just an example base)
    // 2000 steps/sec -> 500us period -> 250us toggle
    // 1% = 20 steps/sec -> 50000us period
    // Simple Mapping: Map 1-100 to 10000us - 200us

    int absSpeed = abs(_currentSpeed);
    if (absSpeed > 100) absSpeed = 100;

    // Non-linear mapping is often better but linear for now
    // Interval = 10000 - (speed * 98) ?
    // Speed 1: 10000 - 98 = 9902us -> 100Hz
    // Speed 100: 10000 - 9800 = 200us -> 5kHz
    _stepIntervalMicros = map(absSpeed, 1, 100, 10000, 200);
}

void StepperDriver::stop() {
    _currentSpeed = 0;
    _enabled = false;
    digitalWrite(_pinEnable, HIGH); // Disable
}

void StepperDriver::update() {
    if (!_enabled || _currentSpeed == 0) return;

    unsigned long now = micros();
    if (now - _lastStepTime >= _stepIntervalMicros) {
        _lastStepTime = now;
        _stepState = !_stepState;
        digitalWrite(_pinStep, _stepState ? HIGH : LOW);
    }
}

int StepperDriver::getLoad() {
    // Steppers don't provide load unless via external sensor.
    // If we have an alarm, we return MAX_LOAD if alarmed.
    if (isFaulted()) return 1023; // Max simulated load
    return 0;
}

bool StepperDriver::isFaulted() {
    if (_pinAlarm != 255) {
        // Assume Active LOW alarm or Active HIGH depending on driver.
        // Often Open Collector -> Pullup -> LOW means Alarm.
        // But Leadshine is configurable. Let's assume LOW is Alarm.
        // Actually, let's assume HIGH is Alarm for generic safety?
        // Let's stick to standard input pullup: LOW = Active Alarm usually.
        return digitalRead(_pinAlarm) == LOW;
    }
    return false;
}
