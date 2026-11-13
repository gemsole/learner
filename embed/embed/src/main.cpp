#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Arduino.h>
#include <Wire.h>

#include "config.h"
#include "expressions.h"

Adafruit_SSD1306 display(cfg::OLED_WIDTH, cfg::OLED_HEIGHT, &Wire,
                         cfg::OLED_RESET_PIN);

size_t currentIndex = 0;
uint32_t lastRotateMs = 0;

// 按键消抖状态
uint8_t buttonReading = !cfg::BUTTON_ACTIVE_LEVEL;
uint8_t buttonStable = !cfg::BUTTON_ACTIVE_LEVEL;
uint32_t buttonChangedMs = 0;

void showExpression(size_t index) {
  const Expression &item = EXPRESSIONS[index];

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  int16_t x1 = 0, y1 = 0;
  uint16_t w = 0, h = 0;

  display.setTextSize(cfg::FACE_TEXT_SIZE);
  display.getTextBounds(item.face, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((cfg::OLED_WIDTH - (int16_t)w) / 2 - x1,
                    cfg::FACE_CENTER_Y - (int16_t)h / 2 - y1);
  display.print(item.face);

  display.setTextSize(cfg::LABEL_TEXT_SIZE);
  display.getTextBounds(item.label, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((cfg::OLED_WIDTH - (int16_t)w) / 2 - x1,
                    cfg::LABEL_CENTER_Y - (int16_t)h / 2 - y1);
  display.print(item.label);

  display.display();
}

void drawProgressBar(uint32_t elapsedMs) {
  int16_t barWidth = 0;
  if (cfg::AUTO_ROTATE_INTERVAL_MS > 0) {
    int32_t filled = (int32_t)(elapsedMs * cfg::OLED_WIDTH /
                               cfg::AUTO_ROTATE_INTERVAL_MS);
    barWidth = (int16_t)constrain(filled, 0, (int32_t)cfg::OLED_WIDTH);
  }

  display.fillRect(0, cfg::PROGRESS_BAR_Y, cfg::OLED_WIDTH,
                   cfg::PROGRESS_BAR_HEIGHT, SSD1306_BLACK);
  display.fillRect(0, cfg::PROGRESS_BAR_Y, barWidth, cfg::PROGRESS_BAR_HEIGHT,
                   SSD1306_WHITE);
  display.display();
}

void switchToNext() {
  currentIndex = (currentIndex + 1) % EXPRESSION_COUNT;
  lastRotateMs = millis();
  showExpression(currentIndex);
  Serial.printf("[OLED] expression -> %zu %s\n", currentIndex,
                EXPRESSIONS[currentIndex].face);
}

// 返回 true 表示本次检测到一次有效按下
bool pollButton() {
  bool pressed = false;
  uint8_t reading = digitalRead(cfg::BUTTON_PIN);

  if (reading != buttonReading) {
    buttonChangedMs = millis();
    buttonReading = reading;
  }

  if ((millis() - buttonChangedMs) > cfg::BUTTON_DEBOUNCE_MS &&
      reading != buttonStable) {
    buttonStable = reading;
    if (buttonStable == cfg::BUTTON_ACTIVE_LEVEL) {
      pressed = true;
    }
  }
  return pressed;
}

void setup() {
  Serial.begin(cfg::SERIAL_BAUD);

  pinMode(cfg::BUTTON_PIN, INPUT_PULLUP);

  Wire.begin(cfg::OLED_SDA_PIN, cfg::OLED_SCL_PIN, cfg::I2C_CLOCK_HZ);

  if (!display.begin(SSD1306_SWITCHCAPVCC, cfg::OLED_I2C_ADDR)) {
    Serial.println("[OLED] SSD1306 init failed, check wiring/address");
    while (true) {
      delay(1000);
    }
  }

  display.clearDisplay();
  display.display();
  showExpression(currentIndex);
  lastRotateMs = millis();
}

void loop() {
  if (pollButton()) {
    switchToNext();
  }

  if (cfg::AUTO_ROTATE_INTERVAL_MS > 0) {
    uint32_t now = millis();
    if (now - lastRotateMs >= cfg::AUTO_ROTATE_INTERVAL_MS) {
      switchToNext();
    } else {
      drawProgressBar(now - lastRotateMs);
    }
  }

  delay(cfg::RENDER_INTERVAL_MS);
}
