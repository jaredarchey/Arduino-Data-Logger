#define IR A0

void setup() {
  Serial.begin(115200);
}

void loop() { //Do nothing until python says
  transmission();
}

void transmission(void) {
  boolean init;
  if (Serial.available()) {
    char msg = Serial.read();
    if (msg == 's') {
      init = true;
    }
    else {
      init = false;
    }
    unsigned long int start_time = millis();
    while (init == true) {
      while (!Serial.available()) {}
      char cmd = Serial.read();
      if (cmd == '0') { //This is where data is sent
      //ALWAYS MAKE SURE TO END TRANSMISSION WITH PRINTLN
        Serial.print(analogRead(A0));
        Serial.print("|");
        Serial.println(millis() - start_time);
        /*Serial.print(millis() - start_time);
        Serial.print("|");
        Serial.print(analogRead(A0));
        Serial.print("|");
        Serial.print(millis() - start_time);
        Serial.print("|");
        Serial.println(analogRead(A0));*/
      }
      else if (cmd == '1') { //Break command is 1
        init = false;
      }
      else {init = false;} //Anything other than 0 or 1 also breaks
    }
  }
  else {/*If Serial not available*/}
}


