import time
import board
import adafruit_dht

# Sensor data pin is connected to GPIO 4
sensor = adafruit_dht.DHT22(board.D4)
# Uncomment for DHT11
# sensor = adafruit_dht.DHT11(board.D4)

while True:
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity
        
        if temperature_c is not None and humidity is not None:
            print("Temp={0:0.1f}C, Temp={1:0.1f}F, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
        else:
            print("Sensor returned None values")
            
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print("RuntimeError:", error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        print("Other error:", error)
        sensor.exit()
        time.sleep(2.0)
        continue

    time.sleep(3.0)