float sensorValue;

void setup()
{
  Serial.begin(9600);      // sets the serial port to 9600
}

void loop()
{
  sensorValue = analogRead(A5);       // read analog input pin 0
//  Serial.println(5*sensorValue/1024, DEC);  // prints the value read
  Serial.println(5*sensorValue/1023,DEC);
  delay(100);                        // wait 100ms for next reading
}

