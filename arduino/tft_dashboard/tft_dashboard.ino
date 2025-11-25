#include <MCUFRIEND_kbv.h>
#include <ArduinoJson.h>
#include <TouchScreen.h>

// ---------- Telemetry ----------
struct Telemetry {
    String timestamp;
    float airTemp;
    float humidity;
    float co2;
    float soilMoisture;
    float waterTemp;
    float ph;
    float ec;
    float tds;
};

// ---------- Display + UI ----------
MCUFRIEND_kbv tft;
uint16_t bgColor = 0x0020;
uint16_t cardColor = 0x0841;
uint16_t primaryText = 0xFFFF;
uint16_t accentText = 0xFBE0;
uint16_t highlight = 0xF9A0;
uint16_t dividerColor = 0x3186;

// ---------- Touch ----------
#define YP A3
#define XM A2
#define YM 9
#define XP 8
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);
const int16_t SCREEN_WIDTH = 480;
const int16_t SCREEN_HEIGHT = 320;
const int16_t BTN_WIDTH = 140;
const int16_t BTN_HEIGHT = 45;
const int16_t CONTENT_BOTTOM = SCREEN_HEIGHT - BTN_HEIGHT - 10;
const int16_t CARD_WIDTH = 210;
const int16_t CARD_HEIGHT = 90;
const int16_t CARD_GAP = 10;
const int16_t ROW1_Y = 70;
const int16_t ROW2_Y = ROW1_Y + CARD_HEIGHT + CARD_GAP;
const int16_t LEFT_X = 20;
const int16_t RIGHT_X = SCREEN_WIDTH - CARD_WIDTH - 20;

enum TouchAction { NONE, NEXT_PAGE, PREV_PAGE };

void drawTouchButtons() {
    int16_t btnTop = SCREEN_HEIGHT - BTN_HEIGHT;
    tft.fillRect(0, btnTop, SCREEN_WIDTH, BTN_HEIGHT, dividerColor);
    tft.drawRect(0, btnTop, SCREEN_WIDTH, BTN_HEIGHT, accentText);

    tft.drawRect(10, btnTop + 5, BTN_WIDTH, BTN_HEIGHT - 10, primaryText);
    tft.drawRect(SCREEN_WIDTH - BTN_WIDTH - 10, btnTop + 5, BTN_WIDTH, BTN_HEIGHT - 10, primaryText);

    tft.setTextSize(2);
    tft.setTextColor(primaryText);
    tft.setCursor(35, btnTop + 17);
    tft.print("PREV");
    tft.setCursor(SCREEN_WIDTH - BTN_WIDTH + 15, btnTop + 17);
    tft.print("NEXT");
}

TouchAction readTouchAction() {
    TSPoint p = ts.getPoint();
    pinMode(XM, OUTPUT);
    pinMode(YP, OUTPUT);
    if (p.z < 100 || p.z > 1000) {
        return NONE;
    }
    int16_t x = map(p.y, 150, 920, 0, SCREEN_WIDTH);
    int16_t y = map(p.x, 120, 900, SCREEN_HEIGHT, 0);
    int16_t btnTop = SCREEN_HEIGHT - BTN_HEIGHT;
    if (y < btnTop || y > SCREEN_HEIGHT) return NONE;
    if (x >= 10 && x <= 10 + BTN_WIDTH) return PREV_PAGE;
    if (x >= SCREEN_WIDTH - BTN_WIDTH - 10 && x <= SCREEN_WIDTH - 10) return NEXT_PAGE;
    return NONE;
}

void drawHeader(const String &timeStr, const char *pageTitle) {
    tft.fillRect(0, 0, 480, 60, highlight);
    tft.setTextColor(0x0000);
    tft.setTextSize(3);
    tft.setCursor(20, 18);
    tft.print(pageTitle);
    tft.setCursor(320, 18);
    tft.print(timeStr);
}

void drawCard(int16_t x, int16_t y, int16_t w, int16_t h) {
    tft.fillRoundRect(x, y, w, h, 12, cardColor);
    tft.drawRoundRect(x, y, w, h, 12, dividerColor);
}

void drawMetric(int16_t x, int16_t y, const char *label, float value, const char *unit, uint16_t color, uint8_t decimals = 1) {
    drawCard(x, y, CARD_WIDTH, CARD_HEIGHT);
    tft.setTextColor(accentText);
    tft.setTextSize(2);
    tft.setCursor(x + 14, y + 20);
    tft.print(label);

    tft.setTextColor(color);
    tft.setTextSize(4);
    tft.setCursor(x + 14, y + 60);
    if (isnan(value)) {
        tft.print("--");
    } else {
        tft.print(value, decimals);
    }
    tft.setTextSize(2);
    tft.setCursor(x + 140, y + 70);
    tft.print(unit);
}

void showError(const char *msg) {
    tft.fillScreen(0x0000);
    tft.setTextColor(0xF800);
    tft.setTextSize(3);
    tft.setCursor(20, 120);
    tft.print(msg);
}

String fetchBluetoothJson() {
    return R"({
        "timestamp":"12:34:56",
        "environment":{"air_temp_c":23.8,"humidity":58.2,"co2_ppm":1015},
        "reservoir":{"water_temp_c":19.4,"ph":6.1,"ec":1.8,"tds":820},
        "soil":{"moisture":0.41}
    })";
}

bool parseTelemetry(const String &payload, Telemetry &out) {
    StaticJsonDocument<512> doc;
    if (deserializeJson(doc, payload)) {
        return false;
    }

    out.timestamp = doc["timestamp"] | "--:--:--";
    out.airTemp = doc["environment"]["air_temp_c"] | NAN;
    out.humidity = doc["environment"]["humidity"] | NAN;
    out.co2 = doc["environment"]["co2_ppm"] | NAN;
    out.soilMoisture = doc["soil"]["moisture"] | NAN;
    out.waterTemp = doc["reservoir"]["water_temp_c"] | NAN;
    out.ph = doc["reservoir"]["ph"] | NAN;
    out.ec = doc["reservoir"]["ec"] | NAN;
    out.tds = doc["reservoir"]["tds"] | NAN;
    return true;
}

// ---------- Pages ----------
uint8_t currentPage = 0;
const uint8_t pageCount = 3;

void renderEnvPage(const Telemetry &data) {
    drawHeader(data.timestamp, "Environment");
    drawMetric(LEFT_X, ROW1_Y, "Air Temp", data.airTemp, "C", 0x07FF);
    drawMetric(RIGHT_X, ROW1_Y, "CO2", data.co2, "ppm", 0xF800, 0);
    drawMetric(LEFT_X, ROW2_Y, "Humidity", data.humidity, "%", 0x07E0);
    drawMetric(RIGHT_X, ROW2_Y, "Soil", data.soilMoisture * 100.0, "%", 0xFFE0);
}

void renderReservoirPage(const Telemetry &data) {
    drawHeader(data.timestamp, "Reservoir");
    drawMetric(LEFT_X, ROW1_Y, "Water Temp", data.waterTemp, "C", 0x07FF);
    drawMetric(RIGHT_X, ROW1_Y, "pH", data.ph, "", 0xFFE0, 2);
    drawMetric(LEFT_X, ROW2_Y, "EC", data.ec, "mS/cm", 0xFBE0, 2);
    drawMetric(RIGHT_X, ROW2_Y, "TDS", data.tds, "ppm", 0x07E0, 0);
}

void renderSystemPage(const Telemetry &data) {
    drawHeader(data.timestamp, "System");
    int16_t cardHeight = CONTENT_BOTTOM - 80;
    drawCard(20, 80, 440, cardHeight);
    tft.setTextColor(primaryText);
    tft.setTextSize(2);
    tft.setCursor(40, 120);
    tft.print("Extend this page with relays/pump info");
    tft.setCursor(40, 160);
    tft.print("Soil moisture: ");
    if (isnan(data.soilMoisture)) {
        tft.print("--");
    } else {
        tft.print(data.soilMoisture * 100.0, 1);
    }
    tft.print(" %");
    int16_t footerY = 80 + cardHeight - 40;
    if (footerY > CONTENT_BOTTOM - 30) {
        footerY = CONTENT_BOTTOM - 30;
    }
    tft.setCursor(40, footerY);
    tft.print("Add alarms, setpoints, etc.");
}

void renderCurrentPage(const Telemetry &data) {
    tft.fillScreen(bgColor);
    switch (currentPage) {
        case 0:
            renderEnvPage(data);
            break;
        case 1:
            renderReservoirPage(data);
            break;
        case 2:
            renderSystemPage(data);
            break;
    }
    drawTouchButtons();
}

bool refreshTelemetry(Telemetry &state) {
    Telemetry incoming;
    if (parseTelemetry(fetchBluetoothJson(), incoming)) {
        state = incoming;
        renderCurrentPage(state);
        return true;
    }
    showError("JSON parse failed");
    return false;
}

// ---------- Main ----------
Telemetry latest;

void setup() {
    uint16_t id = tft.readID();
    if (id == 0xD3D3) {
        id = 0x9486;
    }
    tft.begin(id);
    tft.setRotation(1);

    refreshTelemetry(latest);
}

void loop() {
    TouchAction action = readTouchAction();
    switch (action) {
        case NEXT_PAGE:
            currentPage = (currentPage + 1) % pageCount;
            renderCurrentPage(latest);
            break;
        case PREV_PAGE:
            currentPage = (currentPage + pageCount - 1) % pageCount;
            renderCurrentPage(latest);
            break;
        default:
            break;
    }
    static unsigned long lastRefresh = 0;
    unsigned long now = millis();
    if (now - lastRefresh >= 5000) {
        refreshTelemetry(latest);
        lastRefresh = now;
    }
}

   