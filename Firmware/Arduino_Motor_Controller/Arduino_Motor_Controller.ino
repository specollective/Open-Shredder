#include "DCDriver.h"
#include "StepperDriver.h"
#include "ShredderController.h"

// ================= USER CONFIGURATION =================

// Select Motor Type: 1 = DC, 2 = STEPPER
#define MOTOR_TYPE 1

// --- Pins for DC Motor ---
#define PIN_DC_PWM      3
#define PIN_DC_DIR      4
#define PIN_DC_CURRENT  A0

// --- Pins for Stepper Motor ---
#define PIN_STEP_PUL    3
#define PIN_STEP_DIR    4
#define PIN_STEP_ENA    5
#define PIN_STEP_ALARM  6

// --- Logic Settings ---
#define CURRENT_LIMIT   800   // 0-1023 ADC
#define USE_IMPACT_MODE true  // Enable Impact Hammer logic

// ======================================================

MotorInterface* driver = nullptr;
ShredderController* controller = nullptr;

void setup() {
    Serial.begin(115200);
    Serial.println("Shredder Controller Starting...");

    // Initialize Driver
    #if MOTOR_TYPE == 1
        driver = new DCDriver(PIN_DC_PWM, PIN_DC_DIR, PIN_DC_CURRENT);
        Serial.println("Mode: DC Motor");
    #elif MOTOR_TYPE == 2
        driver = new StepperDriver(PIN_STEP_PUL, PIN_STEP_DIR, PIN_STEP_ENA, PIN_STEP_ALARM);
        Serial.println("Mode: Stepper Motor");
    #endif

    driver->begin();

    // Initialize Controller
    controller = new ShredderController(driver);

    ShredderConfig config;
    config.forwardSpeed = 100; // 100%
    config.reverseSpeed = 60;
    config.currentLimit = CURRENT_LIMIT;
    config.runDuration = 0; // Infinite
    config.useImpactMode = USE_IMPACT_MODE;

    controller->setConfig(config);

    // Start Sequence
    controller->start();
    Serial.println("Controller Started.");
}

void loop() {
    // Main update loop
    if (controller) {
        controller->update();

        // Optional: Print Status periodically
        static unsigned long lastPrint = 0;
        if (millis() - lastPrint > 1000) {
            lastPrint = millis();
            Serial.print("State: ");
            Serial.print(controller->getState());
            Serial.print(" Load: ");
            Serial.println(driver->getLoad());
        }
    }
}
