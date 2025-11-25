import glob
import time

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temperature():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    if lines[0].strip()[-3:] != 'YES':
        return None
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_c = float(lines[1][equals_pos+2:]) / 1000.0
        return temp_c
    return None

while True:
    temp = read_temperature()
    if temp is not None:
        print(f"Temperature: {temp:.2f}")
    else:
        print("Reading failed")
    time.sleep(1)

