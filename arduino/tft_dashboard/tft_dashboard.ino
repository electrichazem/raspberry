#include <MCUFRIEND_kbv.h>
#include <ArduinoJson.h>
#include <TouchScreen.h>

// ---------- Telemetry ----------
struct Telemetry {
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

void drawHeader(const char *pageTitle) {
    tft.fillRect(0, 0, 480, 60, highlight);
    tft.setTextColor(0x0000);
    tft.setTextSize(3);
    tft.setCursor(20, 18);
    tft.print(pageTitle);
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
    // Static variables to maintain state and simulate realistic variations
    static float airTemp = 22.0;
    static float humidity = 78.0;
    static float soilMoisture = 0.70;
    static float tds = 300.0;
    
    // Normal-like variations: small random steps with bounds
    // Air temp: average 22°C, vary by ±0.1°C per update
    airTemp += (random(-10, 11) / 100.0);  // -0.1 to +0.1
    if (airTemp < 21.5) airTemp = 21.5;
    if (airTemp > 22.5) airTemp = 22.5;
    
    // Humidity: average 78%, vary by ±0.5% per update
    humidity += (random(-5, 6) / 10.0);  // -0.5 to +0.5
    if (humidity < 76.0) humidity = 76.0;
    if (humidity > 80.0) humidity = 80.0;
    
    // Soil moisture: average 70%, vary by ±0.5% per update
    soilMoisture += (random(-5, 6) / 1000.0);  // -0.005 to +0.005
    if (soilMoisture < 0.68) soilMoisture = 0.68;
    if (soilMoisture > 0.72) soilMoisture = 0.72;
    
    // TDS: average 300 ppm, vary by ±5 ppm per update
    tds += random(-5, 6);
    if (tds < 290) tds = 290;
    if (tds > 310) tds = 310;
    
    // Calculate EC from TDS (EC mS/cm ≈ TDS ppm / 500)
    float ec = tds / 500.0;
    
    // CO2: fixed at 450 ppm
    float co2 = 450.0;
    
    // Water temp: fixed at 26°C
    float waterTemp = 26.0;
    
    // pH: fixed at 6.9
    float ph = 6.9;
    
    // Build JSON string
    String json = "{";
    json += "\"environment\":{";
    json += "\"air_temp_c\":" + String(airTemp, 1) + ",";
    json += "\"humidity\":" + String(humidity, 1) + ",";
    json += "\"co2_ppm\":" + String(co2, 0);
    json += "},";
    json += "\"reservoir\":{";
    json += "\"water_temp_c\":" + String(waterTemp, 1) + ",";
    json += "\"ph\":" + String(ph, 1) + ",";
    json += "\"ec\":" + String(ec, 2) + ",";
    json += "\"tds\":" + String(tds, 0);
    json += "},";
    json += "\"soil\":{";
    json += "\"moisture\":" + String(soilMoisture, 2);
    json += "}";
    json += "}";
    
    return json;
}

bool parseTelemetry(const String &payload, Telemetry &out) {
    StaticJsonDocument<512> doc;
    if (deserializeJson(doc, payload)) {
        return false;
    }

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
const uint8_t pageCount = 2;

void renderEnvPage(const Telemetry &data) {
    drawHeader("Environment");
    drawMetric(LEFT_X, ROW1_Y, "Air Temp", data.airTemp, "C", 0x07FF);
    drawMetric(RIGHT_X, ROW1_Y, "CO2", data.co2, "ppm", 0xF800, 0);
    drawMetric(LEFT_X, ROW2_Y, "Humidity", data.humidity, "%", 0x07E0);
    drawMetric(RIGHT_X, ROW2_Y, "Soil", data.soilMoisture * 100.0, "%", 0xFFE0);
}

void renderReservoirPage(const Telemetry &data) {
    drawHeader("Reservoir");
    drawMetric(LEFT_X, ROW1_Y, "Water Temp", data.waterTemp, "C", 0x07FF);
    drawMetric(RIGHT_X, ROW1_Y, "pH", data.ph, "", 0xFFE0, 2);
    drawMetric(LEFT_X, ROW2_Y, "EC", data.ec, "mS/cm", 0xFBE0, 2);
    drawMetric(RIGHT_X, ROW2_Y, "TDS", data.tds, "ppm", 0x07E0, 0);
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
    randomSeed(analogRead(0));  // Initialize random seed for realistic variations
    
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

   