#include <Servo.h>

Servo myServo;

void setup() {
  myServo.attach(9);   // attach to pin 9
  myServo.write(0);    // move to 0 degrees
}

void loop() {
  // nothing needed here
}
