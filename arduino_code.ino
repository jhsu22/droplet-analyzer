#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <PWMServo.h>

// Create motor shield object
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

// Create stepper motor objects
Adafruit_StepperMotor *syringeStepper = AFMS.getStepper(200,1);
Adafruit_StepperMotor *frameStepper = AFMS.getStepper(200, 2);

// Define arduino pins
const int ledPin = 9;
const int potPin = A0;

// Creating variables
double syrHeight = 5.715;
double syrVol = 1;
double syrRatio = syrHeight / syrVol;
double leadPitch = 0.4;

double vol;                // desired droplet volume
double disp;               // required plunger displacement
double revolutions;        // required revolutions
double steps;              // required steps

int ledBrightness = 0;     // Global variable for current LED brightness

void setup() {

  Serial.begin(9600);
  while (!Serial);

  // Start motor shield
  AFMS.begin();

  // LED and potentiometer setup
  pinMode(LED, OUTPUT);
  pinMode(POT, INPUT);

  syringeStepper->setSpeed(15);  // stepper motor speed [rpm]
  frameStepper->setSpeed(15);

  // Start with LED off
  led(0);

  // Reserve memory for input string
  inputString.reserve(50);

}

void loop() {

  // Check if serial data is available
  while (Serial.available()) {

    // Read the next character
    char inputChar = Serial.read();

    // If character is not '\n', append it to the string
    if (inputChar != '\n') {

      inputString += inputChar;

    } else {

      processCommand(inputString);

      inputString = "";
    }
  }
}

// Comand processing function

void processCommand(String command) {

  // Remove and whitespace
  command.trim();

  // Convert command to uppercase
  command.toUpperCase();

  // Separate command from value
  int spaceIndex = command.indexOf(' ');

  String cmdKey;
  int cmdValue = -1;

  if (spaceIndex > 0) {
    cmdKey = command.substring(0, spaceIndex);
    String valueString = command.substring(spaceIndex + 1);

    cmdValue = valueString.toInt();
  } else {
    cmdKey = command;
  }

  // Route command to right function
  if (cmdKey == "LED") {
    led(cmdValue);
  } else if (cmdKey == "DISPENSE") {
    dispense(cmdValue);
  } else if (cmdKey == "MOVE") {
    move_frame(cmdValue);
  } else if (cmdKey == "STATUS") {
    Serial.println("System OK.");
  } else {
    Serial.print("Unknown command: ");
    Serial.println(cmdKey);
  }
}

// Control functions

void dispense(double vol) {
// Takes a desired droplet volume and dispenses it

  if vol > 0 {

    disp = syrHeight - (vol * syrRatio);

    revolutions = disp / leadPitch;

    steps = int(revolutions * 200);

    syringeMotor->step(steps, FORWARD, SINGLE);
    syringMotor->release();

  } else {

    Serial.println("Please enter a positive volume.");

  }

}

void move_frame(int steps) {
// Move the frame a certain amount up or down

  if (steps > 0) {
    frameMotor->step(steps, FORWARD, SINGLE);

    Serial.print("Moved the frame ");
    Serial.print(steps);
    Serial.println(" steps up.");
  } else {
    frameMotor->step(abs(steps), BACKWARD, SINGLE);

    Serial.print("Moved the frame ");
    Serial.print(steps);
    Serial.println(" steps down.");
  }

}

void led(int brightness) {
// Change LED brightness (override potentiometer)

  if (brightness >= 0) {
    // Constrain input to percent range
    currentBrightness = constrain(brightness, 0, 100);

    // Convert to PWM
    brightnessPWM = (currentBrightness / 100) * 255

    analogWrite(ledPin, brightnessPWM);
    Serial.print("LED Brightness set to: ");
    Serial.println(currentBrightness);
  } else {
    Serial.println("Please enter a positive brightness.");
  }
}