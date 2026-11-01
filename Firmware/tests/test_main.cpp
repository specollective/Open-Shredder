#include <iostream>
#include <map>
#include <assert.h>
#include "mock_arduino.h"

// Include Sources directly for simple linking in single-file test
#include "../Arduino_Motor_Controller/DCDriver.cpp"
#include "../Arduino_Motor_Controller/StepperDriver.cpp"
#include "../Arduino_Motor_Controller/ShredderController.cpp"

// Define global mock variables
std::map<int, int> pinStates;
std::map<int, int> pinModes;
std::map<int, int> analogInputs;
unsigned long mock_millis = 0;
SerialMock Serial;

void test_dc_motor_jam_detection() {
    std::cout << "Running DC Motor Jam Detection Test..." << std::endl;

    // Setup
    mock_millis = 0;
    analogInputs.clear();
    pinStates.clear();

    DCDriver dc(3, 4, A0); // PWM=3, Dir=4, Current=A0
    ShredderController controller(&dc);

    ShredderConfig config;
    config.forwardSpeed = 100;
    config.reverseSpeed = 50;
    config.currentLimit = 500; // Limit at 500
    config.reverseDuration = 1000;
    config.useImpactMode = false;

    controller.setConfig(config);
    controller.start();

    // 1. Verify Normal Run
    controller.update();
    assert(controller.getState() == STATE_FORWARD);
    assert(pinStates[3] > 0); // PWM should be active

    // 1a. Verify Inrush Masking
    // We are at time 0. Jam check starts after 500ms.
    analogInputs[A0] = 600; // Spike!
    controller.update();
    assert(controller.getState() == STATE_FORWARD); // Should IGNORE spike

    // 2. Simulate Jam (After mask time)
    mock_millis += 600; // Advance past 500ms
    controller.update();
    assert(controller.getState() == STATE_JAM_DETECTED);
    assert(pinStates[3] == 0); // Should stop

    // 3. Verify Wait period
    mock_millis += 400; // Less than 500ms wait
    controller.update();
    assert(controller.getState() == STATE_JAM_DETECTED);

    mock_millis += 200; // Cross 500ms threshold
    controller.update();
    assert(controller.getState() == STATE_REVERSE_CLEARING);
    // Should be reversing
    // DC Driver implementation: Negative speed -> Dir PIN Low
    assert(pinStates[4] == LOW);

    // 4. Verify Return to Forward
    mock_millis += 1100; // Cross reverse duration
    controller.update();
    assert(controller.getState() == STATE_FORWARD);
    assert(pinStates[4] == HIGH);

    std::cout << "DC Jam Test Passed!" << std::endl;
}

void test_impact_mode() {
    std::cout << "Running Impact Mode Test..." << std::endl;

    mock_millis = 0;
    analogInputs.clear();
    pinStates.clear();

    DCDriver dc(3, 4, A0);
    ShredderController controller(&dc);

    ShredderConfig config;
    config.forwardSpeed = 100;
    config.reverseSpeed = 50;
    config.currentLimit = 500;
    config.useImpactMode = true; // Enable Impact
    config.impactBackoffDuration = 1000;

    controller.setConfig(config);
    controller.start();

    // Trigger Jam
    mock_millis += 600; // Past inrush
    analogInputs[A0] = 600;
    controller.update();
    assert(controller.getState() == STATE_JAM_DETECTED);

    // Wait out pause
    mock_millis += 600;
    controller.update();

    // Should enter IMPACT_PREP_BACKOFF instead of REVERSE_CLEARING
    assert(controller.getState() == STATE_IMPACT_PREP_BACKOFF);
    assert(pinStates[4] == LOW); // Reversing

    // Wait out backoff
    mock_millis += 1100;
    controller.update();

    // Should enter STRIKE
    assert(controller.getState() == STATE_IMPACT_STRIKE);
    assert(pinStates[4] == HIGH); // Forward
    assert(pinStates[3] == 255); // Full Speed (map 100 -> 255)

    std::cout << "Impact Mode Test Passed!" << std::endl;
}

int main() {
    test_dc_motor_jam_detection();
    test_impact_mode();
    std::cout << "All Tests Passed." << std::endl;
    return 0;
}
