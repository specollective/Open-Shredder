#ifndef MOTOR_INTERFACE_H
#define MOTOR_INTERFACE_H

#include <stdint.h>

class MotorInterface {
public:
    virtual ~MotorInterface() {}

    // Initialize pins
    virtual void begin() = 0;

    // Set speed (-100 to 100).
    // Positive = Forward, Negative = Reverse, 0 = Stop
    virtual void setSpeed(int speed_percent) = 0;

    // Immediate stop
    virtual void stop() = 0;

    // Update loop (called frequently for non-blocking operations)
    virtual void update() = 0;

    // Return current load (0-100% or raw ADC value, dependent on implementation)
    // Used for jam detection.
    virtual int getLoad() = 0;

    // Check if external hardware signals a jam/fault
    virtual bool isFaulted() = 0;
};

#endif
