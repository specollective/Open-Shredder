#include "ShredderController.h"

#ifdef ARDUINO
    #include <Arduino.h>
#else
    #include "../tests/mock_arduino.h"
#endif

ShredderController::ShredderController(MotorInterface* motor) {
    _motor = motor;
    _state = STATE_IDLE;
    _jamCount = 0;

    // Defaults
    _config.forwardSpeed = 100;
    _config.reverseSpeed = 50;
    _config.currentLimit = 800;
    _config.runDuration = 0;
    _config.reverseDuration = 2000;
    _config.useImpactMode = false;
    _config.impactBackoffDuration = 1000;
}

void ShredderController::setConfig(ShredderConfig config) {
    _config = config;
}

void ShredderController::start() {
    _state = STATE_FORWARD;
    _stateStartTime = millis();
    _runStartTime = millis();
    _motor->setSpeed(_config.forwardSpeed);
    _jamCount = 0;
}

void ShredderController::stop() {
    _state = STATE_IDLE;
    _motor->stop();
}

void ShredderController::update() {
    unsigned long now = millis();
    _motor->update(); // Tick the motor driver

    // State Machine
    switch (_state) {
        case STATE_IDLE:
            // Do nothing
            break;

        case STATE_FORWARD:
            // Check Timeout
            if (_config.runDuration > 0 && (now - _runStartTime > _config.runDuration)) {
                stop();
                return;
            }

            // Inrush Masking: Ignore current spikes during the first 500ms of entering STATE_FORWARD
            if (now - _stateStartTime > 500) {
                // Check Jam/Fault
                if (_motor->getLoad() > _config.currentLimit || _motor->isFaulted()) {
                    _state = STATE_JAM_DETECTED;
                    _stateStartTime = now;
                    _motor->stop();
                    _jamCount++;
                }
            }
            break;

        case STATE_JAM_DETECTED:
            // Pause briefly before reversing to protect electronics
            if (now - _stateStartTime > 500) {
                if (_config.useImpactMode) {
                    // Impact Strategy: Back up, then strike
                    _state = STATE_IMPACT_PREP_BACKOFF;
                    _motor->setSpeed(-_config.reverseSpeed);
                } else {
                    // Standard Strategy: Reverse, then Forward
                    _state = STATE_REVERSE_CLEARING;
                    _motor->setSpeed(-_config.reverseSpeed);
                }
                _stateStartTime = now;
            }
            break;

        case STATE_REVERSE_CLEARING:
            if (now - _stateStartTime > _config.reverseDuration) {
                _state = STATE_FORWARD;
                _motor->setSpeed(_config.forwardSpeed);
                _stateStartTime = now;
            }
            break;

        case STATE_IMPACT_PREP_BACKOFF:
            // Back up significantly
            if (now - _stateStartTime > _config.impactBackoffDuration) {
                _state = STATE_IMPACT_STRIKE;
                // Full speed forward for maximum inertia
                _motor->setSpeed(100);
                _stateStartTime = now;
            }
            break;

        case STATE_IMPACT_STRIKE:
            // We stay in this mode for a minimum time to ensure we hit the object
            // or we just switch back to FORWARD monitoring immediately?
            // Let's switch to FORWARD after a brief acceleration period
            if (now - _stateStartTime > 500) {
                _state = STATE_FORWARD;
                _motor->setSpeed(_config.forwardSpeed);
                _stateStartTime = now;
            }
            break;

        case STATE_PAUSED:
            // Placeholder
            break;
    }
}
