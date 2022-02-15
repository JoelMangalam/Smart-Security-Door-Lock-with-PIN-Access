#include <Servo.h>
Servo myservo;  // create servo object to control a servo

String command1 = "DOOR";
String unlocked = "UNLOCKED";
int pos = 0;    // variable to store the servo position

void setup() {
  // put your setup code here, to run once:
    myservo.attach(9);  // attaches the servo on pin 5 to the servo object
    Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
   if (Serial.available() > 0){  // Check if there is data available to read from the Serial port.  
    if (Serial.readStringUntil("/r") == command1){  // Check if the message matches the command. 

  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  Serial.println(unlocked);
//  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
//    myservo.write(pos);              // tell servo to go to position in variable 'pos'
//    delay(15);                       // waits 15ms for the servo to reach the position
    }
  }
}
