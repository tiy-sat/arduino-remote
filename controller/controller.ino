#include <ArduinoJson.h>
#include <stdlib.h>

const int ONBOARD_LED = 13;
const int LED1 = 2;
const int BUTTON1 = 3;
const int RGB_LED_RED = 9;
const int RGB_LED_GREEN = 10;
const int RGB_LED_BLUE = 11;

int button1LastState = HIGH;

struct Event {
  const char* type;
  const char* source;
  const char* name;
  String value;
};

struct Action {
  const char* type;
  const char* target;
  const char* name;
  const char* value;
};

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);

  Event evt_start = {"config", "arduino", "starting", String("")};
  sendEvent(evt_start);

#if defined (__AVR_ATmega328P__)
  String temp = String(getTemp(), 1);

  Event evt_temp = {"config", "arduino", "internal_temp_c", temp};
  sendEvent(evt_temp);
#endif

  Event evt_ver = {"config", "arduino", "arduino_version", String(ARDUINO)};
  sendEvent(evt_ver);

  pinMode(ONBOARD_LED, OUTPUT);
  pinMode(LED1, OUTPUT);
  pinMode(RGB_LED_RED, OUTPUT);
  pinMode(RGB_LED_GREEN, OUTPUT);
  pinMode(RGB_LED_BLUE, OUTPUT);
  pinMode(BUTTON1, INPUT);
}

void loop() {
  int button1State = digitalRead(BUTTON1);

  if (button1State == LOW && button1LastState == HIGH) {
    Event evt_button = {"button", "button1", "pressed", "True"};
    sendEvent(evt_button);
  }

  button1LastState = button1State;

  Action action;

  if (checkForAction(action)) {
    dispatchAction(action);
  }

//  sendEvent("heartbeat", "arduino", "alive", "");
}


void dispatchAction(Action& action) {
  if (String(action.type) == "led") {
    int target;
    if (String(action.target) == "onboard_led") {
      target = ONBOARD_LED;
    }
    else if (String(action.target) == "led1") {
      target = LED1;
    }
    else if (String(action.target) == "rgb_led") {
      if (String(action.name) == "red") {
        target = RGB_LED_RED;
      }
      else if (String(action.name) == "green") {
        target = RGB_LED_GREEN;
      }
      else if (String(action.name) == "blue") {
        target = RGB_LED_BLUE;
      }
    }
    if (String(action.value) == "on") {
      digitalWrite(target, HIGH);
    }
    else if (String(action.value) == "off") {
      digitalWrite(target, LOW);
    }
    else {
      int val;
      val = String(action.value).toInt();
      analogWrite(target, val);
    }
  }
}

void sendEvent(Event& evnt) {
  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& event = jsonBuffer.createObject();
  event["type"] = evnt.type;
  event["source"] = evnt.source;
  event["name"] = evnt.name;
  event["value"] = evnt.value;

  event.printTo(Serial);
  Serial.println("");
}

bool checkForAction(Action& action) {
  String input;

  while (Serial.available()) {
    char c = Serial.read();
    input += c;
    delay(2); // In case the buffer is filling
  }

  if (input.length() > 0) {
    StaticJsonBuffer<200> jsonBuffer;
    JsonObject& root = jsonBuffer.parseObject(input);
    action.type = root["type"];
    action.target = root["target"];
    action.name = root["name"];
    action.value = root["value"];

    return root.success(); // FIXME: handle parse errors better (or at all...)
  }

  return false;
}


// getTemp from http://playground.arduino.cc/Main/ShowInfo
float getTemp(void) {
  unsigned int wADC;
  float t;

  // The internal temperature has to be used
  // with the internal reference of 1.1V.
  // Channel 8 can not be selected with
  // the analogRead function yet.

  // This code is not valid for the Arduino Mega,
  // and the Arduino Mega 2560.

#ifdef THIS_MIGHT_BE_VALID_IN_THE_FUTURE
  analogReference (INTERNAL);
  delay(20);            // wait for voltages to become stable.
  wADC = analogRead(8); // Channel 8 is temperature sensor.
#else
  // Set the internal reference and mux.
  ADMUX = (_BV(REFS1) | _BV(REFS0) | _BV(MUX3));
  ADCSRA |= _BV(ADEN);  // enable the ADC

  delay(20);            // wait for voltages to become stable.

  ADCSRA |= _BV(ADSC);  // Start the ADC

  // Detect end-of-conversion
  while (bit_is_set(ADCSRA,ADSC));

  // Reading register "ADCW" takes care of how to read ADCL and ADCH.
#if defined (__AVR_ATmega32U4__)
  wADC = ADC;      // For Arduino Leonardo
#else
  wADC = ADCW;     // 'ADCW' is preferred over 'ADC'
#endif
#endif

  // The offset of 337.0 could be wrong. It is just an indication.
  t = (wADC - 337.0 ) / 1.22;

  return (t);
}
