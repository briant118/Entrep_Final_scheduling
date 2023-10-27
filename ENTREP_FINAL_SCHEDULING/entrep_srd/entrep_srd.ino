#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);

String storedUID = "12 7C DC 1B"; // Fixed UID
unsigned long lastScanTime = 0;   // Variable to store the time of the last scan
unsigned long delayDuration = 5000;  // Delay in milliseconds (5 seconds)

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
}

void loop() {
  unsigned long currentTime = millis();  // Get the current time

  // Check if enough time has passed since the last scan
  if (currentTime - lastScanTime >= delayDuration) {
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      Serial.print("NUID tag is: ");
      String ID = "";
      for (byte i = 0; i < rfid.uid.size; i++) {
        ID.concat(String(rfid.uid.uidByte[i] < 0x10 ? " 0" : " "));
        ID.concat(String(rfid.uid.uidByte[i], HEX));
      }
      ID.toUpperCase();

      if (ID.substring(1) == storedUID) {
        Serial.println("UID recognized");
        Serial.println(ID);

        // Send a message to the Python program
        Serial.println("Bryan Etoquilla");
        
        // Update the last scan time to the current time
        lastScanTime = currentTime;
        
        // Delay before scanning the next card
        delay(delayDuration);
      } else {
        // You can add your desired logic here for an unrecognized UID
        Serial.println("UID not recognized");
      }
    }
  }
}
