// ---------------------------------------------- //
// Arduino code for droplet dispenser system      //
// Two steppers wired to an Adafruit motor shield //
// LED wired to digital pin 9                     //
// Potentiometer wired to analog pin A0           //
// ---------------------------------------------- //

#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <PWMServo.h>

// Create motor shield object
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

// Create stepper motor objects
Adafruit_StepperMotor *syringeStepper = AFMS.getStepper(200, 1);
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

String inputString = "";   // A String to hold incoming data
bool manualLedControl = false; // Flag to override potentiometer

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Start motor shield
  AFMS.begin();

  // LED and potentiometer setup
  pinMode(ledPin, OUTPUT);
  pinMode(potPin, INPUT);

  syringeStepper->setSpeed(15);  // stepper motor speed [rpm]
  frameStepper->setSpeed(15);

  // Start with LED off, but in automatic (potentiometer) mode
  analogWrite(ledPin, 0);

  // Reserve memory for input string
  inputString.reserve(50);
}

void loop() {
  // Check if serial data is available
  while (Serial.available()) {
    char inputChar = Serial.read();
    if (inputChar != '\n') {
      inputString += inputChar;
    } else {
      processCommand(inputString);
      inputString = "";
    }
  }

  // If not in manual mode, control LED with potentiometer
  if (!manualLedControl) {
    int potValue = analogRead(potPin);
    int brightnessPWM = map(potValue, 0, 1023, 0, 255);
    analogWrite(ledPin, brightnessPWM);
  }
}

// Command processing function
void processCommand(String command) {
  command.trim();
  command.toUpperCase();

  int spaceIndex = command.indexOf(' ');
  String cmdKey;
  String valueString = "";

  if (spaceIndex > 0) {
    cmdKey = command.substring(0, spaceIndex);
    valueString = command.substring(spaceIndex + 1);
  } else {
    cmdKey = command;
  }

  // Route command to right function
  if (cmdKey == "LED") {
    if (valueString != "") {
      led(valueString.toInt());
    } else {
      // If "LED" is sent without a value, switch back to potentiometer control
      manualLedControl = false;
      Serial.println("LED control switched to potentiometer.");
    }
  } else if (cmdKey == "DISPENSE") {
    dispense(valueString.toFloat());
  } else if (cmdKey == "MOVE") {
    move_frame(valueString.toInt());
  } else if (cmdKey == "STATUS") {
    Serial.println("System OK.");
  } else {
    Serial.print("Unknown command: ");
    Serial.println(cmdKey);
  }
}

// Control functions
void dispense(double vol) {
  if (vol > 0) {
    disp = syrHeight - (vol * syrRatio);
    revolutions = disp / leadPitch;
    steps = int(revolutions * 200);

    syringeStepper->step(steps, FORWARD, SINGLE);
    syringeStepper->release();
  } else {
    Serial.println("Please enter a positive volume.");
  }
}

void move_frame(int steps) {
  if (steps > 0) {
    frameStepper->step(steps, FORWARD, SINGLE);
    Serial.print("Moved the frame ");
    Serial.print(steps);
    Serial.println(" steps up.");
  } else {
    frameStepper->step(abs(steps), BACKWARD, SINGLE);
    Serial.print("Moved the frame ");
    Serial.print(abs(steps));
    Serial.println(" steps down.");
  }
}

void led(int brightnessPercent) {
  // Switch to manual control
  manualLedControl = true;

  if (brightnessPercent >= 0 && brightnessPercent <= 100) {
    int brightnessPWM = map(brightnessPercent, 0, 100, 0, 255);
    analogWrite(ledPin, brightnessPWM);
    Serial.print("LED Brightness set to: ");
    Serial.print(brightnessPercent);
    Serial.println("%");
  } else {
    Serial.println("Please enter a brightness between 0 and 100.");
  }
}
