/**
 * ESP32-C3 Smart Shelf Light Beacon Firmware
 * Track 3 — Amber Box Tracker
 * Features:
 *   - Non-blocking FreeRTOS long-polling task for commands:
 *     GET /api/devices/{DEVICE_ID}/commands?wait=20&battery=..&rssi=..
 *   - Non-blocking NeoPixel animations (Blink Blue, Blink Red, Ack Solid Green, Off)
 *   - Passive buzzer chirp alert every 3s during active blinking
 *   - Automatic Wi-Fi reconnection state machine
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include "config.h"

// NeoPixel strip instance
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// Animation states
enum LightState {
  STATE_OFF,
  STATE_BLINK_BLUE,
  STATE_BLINK_RED,
  STATE_ACK_GREEN
};

volatile LightState currentState = STATE_OFF;
volatile unsigned long stateExpiresAt = 0;
volatile unsigned long lastBlinkToggle = 0;
volatile bool blinkLedOn = false;
volatile unsigned long lastBuzzerChirp = 0;

// Command queue synchronisation
portMUX_TYPE stateMux = portMUX_INITIALIZER_UNLOCKED;

void setLightState(LightState state, unsigned long durationMs) {
  portENTER_CRITICAL(&stateMux);
  currentState = state;
  stateExpiresAt = (durationMs > 0) ? (millis() + durationMs) : 0;
  blinkLedOn = true;
  lastBlinkToggle = millis();
  portEXIT_CRITICAL(&stateMux);
}

// Wi-Fi setup & reconnection
void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.printf("[WiFi] Connecting to %s...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] Connected! IP: %s | RSSI: %d dBm\n",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("\n[WiFi] Connection timeout, will retry in background.");
  }
}

// FreeRTOS Task: Long-polling HTTP Worker
void commandPollTask(void *pvParameters) {
  HTTPClient http;

  for (;;) {
    if (WiFi.status() != WL_CONNECTED) {
      connectWiFi();
      vTaskDelay(pdMS_TO_TICKS(3000));
      continue;
    }

    int rssi = WiFi.RSSI();
    float fakeBattery = 3.95f; // Measured via ADC in hardware revision

    char url[256];
    snprintf(url, sizeof(url), "%s/api/devices/%s/commands?wait=%d&battery=%.2f&rssi=%d",
             SERVER_HOST, DEVICE_ID, LONG_POLL_WAIT_SEC, fakeBattery, rssi);

    http.begin(url);
    http.setTimeout(HTTP_CLIENT_TIMEOUT_MS);

    int httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.printf("[HTTP 200] Commands received: %s\n", payload.c_str());

      JsonDocument doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error && doc["commands"].is<JsonArray>()) {
        for (JsonObject cmd : doc["commands"].as<JsonArray>()) {
          const char *action = cmd["cmd"] | "off";
          const char *color = cmd["color"] | "blue";
          int seconds = cmd["seconds"] | 30;
          unsigned long durMs = (unsigned long)seconds * 1000UL;

          if (strcmp(action, "blink") == 0) {
            Serial.printf(">> Action: BLINK BLUE for %d s\n", seconds);
            setLightState(STATE_BLINK_BLUE, durMs);
          } else if (strcmp(action, "blink_red") == 0) {
            Serial.printf(">> Action: BLINK RED for %d s\n", seconds);
            setLightState(STATE_BLINK_RED, durMs);
          } else if (strcmp(action, "ack") == 0) {
            Serial.printf(">> Action: ACK SOLID GREEN for 2 s\n");
            setLightState(STATE_ACK_GREEN, 2000);
          } else if (strcmp(action, "off") == 0) {
            Serial.printf(">> Action: OFF\n");
            setLightState(STATE_OFF, 0);
          }
        }
      }
    } else {
      if (httpCode > 0) {
        Serial.printf("[HTTP] Code: %d\n", httpCode);
      } else {
        Serial.printf("[HTTP] Connection failed: %s\n", http.errorToString(httpCode).c_str());
      }
      vTaskDelay(pdMS_TO_TICKS(2000));
    }

    http.end();
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}

void renderPixels() {
  unsigned long now = millis();

  // Check state expiration
  if (stateExpiresAt > 0 && now >= stateExpiresAt) {
    currentState = STATE_OFF;
    stateExpiresAt = 0;
  }

  switch (currentState) {
    case STATE_OFF:
      strip.clear();
      strip.show();
      break;

    case STATE_BLINK_BLUE: {
      // 250 ms toggle
      if (now - lastBlinkToggle >= 250) {
        blinkLedOn = !blinkLedOn;
        lastBlinkToggle = now;
      }
      uint32_t color = blinkLedOn ? strip.Color(0, 80, 255) : 0;
      for (int i = 0; i < LED_COUNT; i++) strip.setPixelColor(i, color);
      strip.show();

      // Buzzer chirp every 3s
      if (now - lastBuzzerChirp >= 3000) {
        tone(BUZZER_PIN, BUZZER_FREQUENCY_HZ, 80);
        lastBuzzerChirp = now;
      }
      break;
    }

    case STATE_BLINK_RED: {
      // Fast 130 ms toggle for wrong shelf alert
      if (now - lastBlinkToggle >= 130) {
        blinkLedOn = !blinkLedOn;
        lastBlinkToggle = now;
      }
      uint32_t color = blinkLedOn ? strip.Color(255, 0, 0) : 0;
      for (int i = 0; i < LED_COUNT; i++) strip.setPixelColor(i, color);
      strip.show();

      // Faster buzzer chirp for wrong shelf
      if (now - lastBuzzerChirp >= 1500) {
        tone(BUZZER_PIN, BUZZER_FREQUENCY_HZ, 120);
        lastBuzzerChirp = now;
      }
      break;
    }

    case STATE_ACK_GREEN: {
      // Solid green
      uint32_t color = strip.Color(0, 255, 60);
      for (int i = 0; i < LED_COUNT; i++) strip.setPixelColor(i, color);
      strip.show();
      break;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n============================================");
  Serial.printf("ESP32-C3 Shelf-Light Beacon: %s\n", DEVICE_ID);
  Serial.println("============================================");

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  strip.begin();
  strip.setBrightness(180);
  strip.clear();
  strip.show();

  // Startup chirp
  tone(BUZZER_PIN, 2000, 100);

  // FreeRTOS long-polling task on Core 0
  xTaskCreate(
    commandPollTask,
    "PollTask",
    8192,
    NULL,
    1,
    NULL
  );
}

void loop() {
  renderPixels();
  delay(10);
}
