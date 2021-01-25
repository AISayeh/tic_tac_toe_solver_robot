#include <Servo.h>
#define size 5

Servo servo1, servo2, servo3, servo4;

int positions [15][4] = {
  {180, 135, 180, 60}, //initial position
  {141, 73, 170, 46}, //square 1
  {128, 75, 170, 45}, //square 2
  {114, 73, 170, 46},  //3
  {146, 90, 150, 33}, //4
  {128, 90, 150, 33}, //5
  {111, 90, 150, 38}, //6 
  {153, 120, 110, 40}, //7 
  {128, 120, 110, 38}, //8
  {104, 120, 110, 48}, //9
  {80, 100, 180, 60}, //10
  {0, 120, 105, 44}, //11
  {80, 40, 150, 60} //12
};

int current = -1;
bool selected = false;
int selected_ndx = 0;
int pos = 0, previous = 0;
boolean flag = false;
boolean isOnMove = false;
char command[size + 1];
int delay_ms = 600;
Servo servos[4];

void delayMovement(Servo* ser, int pos1, int pos2) {
    float i = pos1;
    float diff =  (pos2 - pos1) / 10.0;
    int c = 0;
    while (c < 11 && pos2 != int(i)) {
      i += diff;
      ser->write(int(i));
      delay(50);
      c++;
    }
}

void quickMove(int id) {
    servo1.write(positions[id][0]);
    servo2.write(positions[id][1]);
    servo3.write(positions[id][2]);
    servo4.write(positions[id][3]);
}

void moveToSquare(int id) {
  if (id == current) {
    return;
    }
    delayMovement(&servo3, servo3.read(),positions[id][2]);
    delay(delay_ms);
    delayMovement(&servo4, servo4.read(),positions[id][3]);
    delay(delay_ms);
    delayMovement(&servo2, servo2.read(),positions[id][1]);
    delay(delay_ms);
    delayMovement(&servo1, servo1.read(),positions[id][0]);
    delay(delay_ms);
    quickMove(id);
    current = id;
    Serial.write("Done\n");
}

void setup() {
  
  servo1.attach(3);
  servo2.attach(5);
  servo3.attach(6);
  servo4.attach(9);

  servos[0] = servo1;
  servos[1] = servo2;
  servos[2] = servo3;
  servos[3] = servo4;
  
  
  Serial.begin(9600);
  pinMode(2, OUTPUT);
}

void loop() {

  if (Serial.available() > 0) {
    String new_pos = Serial.readString();
    if (new_pos == "pick") {
      digitalWrite(2, HIGH);
      servo2.write(servo2.read() - 10);
      delay(delay_ms);
      servo2.write(servo2.read() + 10);
      return;
    } else if (new_pos == "drop") {
      digitalWrite(2, LOW);
      servo2.write(servo2.read() - 10);
      delay(delay_ms);
      servo2.write(servo2.read() + 10);
      return;
    }
        
    pos = new_pos.toInt();
    isOnMove = true;
    delay(delay_ms);
    moveToSquare(pos);   
  }
}
