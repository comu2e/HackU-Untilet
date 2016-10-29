
float val = 0;

void setup() {
    pinMode(3,OUTPUT);
    pinMode(4,OUTPUT);
    Serial.begin(115200);
}

void loop() {
    for (int i = 0; i <= 3; i++){
        delay(242);
        digitalWrite(4,HIGH);
        delay(8);
        digitalWrite(4,LOW); 
    }     
    delay(245);
    digitalWrite(3,HIGH);
    delay(3);
    val = analogRead(A5);
    delay(2);
    digitalWrite(3,LOW);
    digitalWrite(4,HIGH);
    delay(8);
    digitalWrite(4,LOW); 
    val = 1023 - val;
    val = val * 5;
    Serial.println(val);
    // 3msec loop
    delay(3000);
}
