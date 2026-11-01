#ifndef SHREDDER_CONTROLLER_H
#define SHREDDER_CONTROLLER_H

#include "MotorInterface.h"

// Define States
enum ShredderState {
    STATE_IDLE,
    STATE_FORWARD,
    STATE_JAM_DETECTED,
    STATE_REVERSE_CLEARING,
    STATE_IMPACT_PREP_BACKOFF,
    STATE_IMPACT_STRIKE,
    STATE_PAUSED
};

struct ShredderConfig {
    int forwardSpeed;         // 0-100
    int reverseSpeed;         // 0-100
    int currentLimit;         // 0-1023 ADC value
    unsigned long runDuration; // ms, 0 = infinite
    unsigned long reverseDuration; // ms (time to back up during normal clear)
    bool useImpactMode;       // Use "Back up + Strike" strategy
    unsigned long impactBackoffDuration; // ms
};

class ShredderController {
private:
    MotorInterface* _motor;
    ShredderConfig _config;
    ShredderState _state;

    unsigned long _stateStartTime;
    unsigned long _runStartTime;
    int _jamCount;

public:
    ShredderController(MotorInterface* motor);

    void setConfig(ShredderConfig config);
    void start();
    void stop();
    void update(); // Main Loop Logic

    ShredderState getState() { return _state; }
};

#endif
