/*  TTGO T-Display (ESP32 + цветной ST7789 135x240) — приём текста по Bluetooth.
 *
 *  Что делает: включает Bluetooth-сервис «UART», ждёт подключения и показывает
 *  на экране всё, что ему пришлют. Текст переносится по строкам, старые уезжают
 *  вверх. Сверху — состояние связи.
 *
 *  Что нужно в Arduino IDE:
 *    1. Платы: esp32 by Espressif (Boards Manager → "esp32").
 *    2. Библиотеки: TFT_eSPI, NimBLE-Arduino.
 *    3. В библиотеке TFT_eSPI открыть User_Setup_Select.h и раскомментировать строку
 *       #include <User_Setups/Setup25_TTGO_T_Display.h>
 *       (все остальные #include <User_Setup.h> — закомментировать).
 *    4. Плата: "TTGO LoRa32-OLED" или "ESP32 Dev Module", скорость 921600.
 *
 *  ВНИМАНИЕ: код написан под это железо, но на живом модуле ещё не проверялся —
 *  проверю и поправлю, когда плата приедет и её подключат по USB.
 */

#include <TFT_eSPI.h>
#include <NimBLEDevice.h>

#define SERVICE_UUID   "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"   // Nordic UART Service
#define CHAR_RX_UUID   "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"   // сюда пишем текст
#define CHAR_TX_UUID   "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"   // сюда отвечаем

TFT_eSPI tft = TFT_eSPI();
NimBLECharacteristic *txChar = nullptr;

const char *DEVICE_NAME = "Hermes-Display";
const int LINE_H = 18;          // высота строки при шрифте 2
const int MAX_LINES = 8;        // сколько строк держим на экране
String lines[MAX_LINES];
int lineCount = 0;
bool connected = false;
String lastMessage = "";

void redraw() {
  tft.fillScreen(TFT_BLACK);
  tft.setTextSize(1);
  tft.setTextColor(connected ? TFT_GREEN : TFT_DARKGREY, TFT_BLACK);
  tft.setCursor(4, 4);
  tft.print(connected ? "BT: connect" : "BT: wait");
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(2);
  int y = 24;
  for (int i = 0; i < lineCount; i++) {
    tft.setCursor(4, y);
    tft.print(lines[i]);
    y += LINE_H;
  }
  tft.setTextSize(1);
  tft.setTextColor(TFT_DARKGREY, TFT_BLACK);
  tft.setCursor(4, tft.height() - 12);
  tft.print(DEVICE_NAME);
}

void pushLine(const String &s) {
  // сдвигаем вверх, если строк стало больше, чем влезает
  if (lineCount >= MAX_LINES) {
    for (int i = 1; i < MAX_LINES; i++) lines[i - 1] = lines[i];
    lineCount = MAX_LINES - 1;
  }
  lines[lineCount++] = s;
  redraw();
}

// раскладываем пришедший текст по строкам: по 21 символ (шрифт 2 на экране 240 px)
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
    lastMessage = text;
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
    NimBLEDevice::startAdvertising();   // снова ждём подключения
  }
};

void setup() {
  Serial.begin(115200);

  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);

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
