/*  ESP32-C3 (Super Mini или DevKit) + OLED 0.96" I2C (SSD1306) — приём текста по Bluetooth.
 *
 *  Дешёвый вариант: плата ESP32-C3 + отдельный OLED-дисплей, соединённые четырьмя
 *  шлейфами «мама-мама» — без паяльника.
 *
 *  Подключение (4 провода):
 *      OLED VCC  →  ESP32-C3  3V3
 *      OLED GND  →  ESP32-C3  GND
 *      OLED SDA  →  ESP32-C3  GPIO8
 *      OLED SCL  →  ESP32-C3  GPIO9
 *  У ESP32-C3 на этих пинах аппаратный I2C. Если экран не завёлся — поменяй местами
 *  SDA и SCL, у разных плат они переставлены.
 *
 *  В Arduino IDE:
 *    1. Платы: esp32 by Espressif; выбрать «ESP32C3 Dev Module».
 *    2. Библиотеки: Adafruit SSD1306, Adafruit GFX Library, NimBLE-Arduino.
 *    3. В Adafruit_SSD1306.h раскомментировать "#define SSD1306_NO_SPLASH" (по желанию).
 *
 *  ВНИМАНИЕ: код написан под это железо, но на живом модуле ещё не проверялся —
 *  проверю и поправлю, когда плата приедет и её подключат по USB.
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <NimBLEDevice.h>

#define SERVICE_UUID   "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"   // Nordic UART Service
#define CHAR_RX_UUID   "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"   // сюда пишем текст
#define CHAR_TX_UUID   "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"   // сюда отвечаем

#define SDA_PIN 8
#define SCL_PIN 9
#define SCREEN_W 128
#define SCREEN_H 64

Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);
NimBLECharacteristic *txChar = nullptr;

const char *DEVICE_NAME = "Hermes-Display";
const int LINE_H = 10;
const int MAX_LINES = 6;
String lines[MAX_LINES];
int lineCount = 0;
bool connected = false;

void redraw() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print(connected ? "BT: connect" : "BT: wait");
  display.drawFastHLine(0, 9, SCREEN_W, SSD1306_WHITE);
  int y = 12;
  for (int i = 0; i < lineCount; i++) {
    display.setCursor(0, y);
    display.print(lines[i]);
    y += LINE_H;
  }
  display.display();
}

void pushLine(const String &s) {
  if (lineCount >= MAX_LINES) {
    for (int i = 1; i < MAX_LINES; i++) lines[i - 1] = lines[i];
    lineCount = MAX_LINES - 1;
  }
  lines[lineCount++] = s;
  redraw();
}

// шрифт 1 — 6 пикселей на символ, влезает 21 символ в строку
void showText(const String &text) {
  if (text.length() == 0) return;
  if (lineCount >= MAX_LINES) { lineCount = 0; for (int i = 0; i < MAX_LINES; i++) lines[i] = ""; }
  String cur = "";
  for (unsigned int i = 0; i < text.length(); i++) {
    char c = text[i];
    if (c == '\n') { pushLine(cur); cur = ""; continue; }
    cur += c;
    if (cur.length() >= 21) { pushLine(cur); cur = ""; }
  }
  if (cur.length()) pushLine(cur);
}

class RxCallback : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic *c) override {
    std::string value = c->getValue();
    if (value.length() == 0) return;
    String text = String(value.c_str());
    showText(text);
    Serial.print("получено: ");
    Serial.println(text);
    if (txChar) { txChar->setValue(("ok: " + text).c_str()); txChar->notify(); }
  }
};

class ServerCallback : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer *s) override { connected = true; redraw(); }
  void onDisconnect(NimBLEServer *s) override {
    connected = false;
    redraw();
    NimBLEDevice::startAdvertising();
  }
};

void setup() {
  Serial.begin(115200);

  Wire.begin(SDA_PIN, SCL_PIN);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {   // адрес 0x3C, иногда 0x3D
    Serial.println("OLED не найден: проверь адрес (0x3C/0x3D) и провода SDA/SCL");
  }
  display.clearDisplay();
  display.display();

  NimBLEDevice::init(DEVICE_NAME);
  NimBLEServer *server = NimBLEDevice::createServer();
  server->setCallbacks(new ServerCallback());

  NimBLEService *service = server->createService(SERVICE_UUID);
  NimBLECharacteristic *rxChar = service->createCharacteristic(
      CHAR_RX_UUID, NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR);
  rxChar->setCallbacks(new RxCallback());
  txChar = service->createCharacteristic(CHAR_TX_UUID, NIMBLE_PROPERTY::NOTIFY);
  service->start();

  NimBLEAdvertising *adv = NimBLEDevice::getAdvertising();
  adv->addServiceUUID(SERVICE_UUID);
  adv->setName(DEVICE_NAME);
  adv->start();

  pushLine("Hermes-Display");
  pushLine("ждём Bluetooth");
}

void loop() {
  delay(50);
}
