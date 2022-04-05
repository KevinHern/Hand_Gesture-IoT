# Libraries

# Pin and chip related
from machine import Pin, PWM

# Network related
import network, socket

# Others
import neopixel, time


# Connect to local Wi Fi
ssid = '---'
password = '---'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)


# Attempting connection
print("Attempting to connect to the Wi Fi...")
while station.isconnected() == False:
    pass
print('Connection successful')
print(station.ifconfig())


# Initializing constants
buzzer_duty_cycle = 100
num_neopixel_leds = 10


# Initializing Pins
buzzer_pwm = PWM(Pin(14))
buzzer_pwm.freq(0)
buzzer_pwm.duty(0)

neop = neopixel.NeoPixel(Pin(15), num_neopixel_leds)


# Create Server
print("Initializing Server...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating Socket
s.bind(('', 15000))  # Setting up port to listen to
s.listen(2)         # Only accept at a maximum of N connections

print("Awaiting Connections...")
while True:
    conn, address = s.accept()
    #print('Got a connection from %s' % str(address))

    # Reading request
    request = conn.recv(1024)
    request = int.from_bytes(request, "big")

    # Parsing request
    mode = request & 0xFF000000

    # RGB: Mode = 1
    if (mode >> 24) == 0x01:
        # Extracting RGB values
        red = (request & 0x00FF0000) >> 16
        green = (request & 0x0000FF00) >> 8
        blue = request & 0x000000FF

        # Chaging Neopixel Colors
        for led in range(0, num_neopixel_leds):
            neop[led]=(red,green,blue)

        # Writing to Neopixel Module
        neop.write()

    elif (mode >> 24) == 0x02:
        frequency = request & 0x00000FFF
        buzzer_pwm.freq(frequency)
        if frequency == 0:
            buzzer_pwm.duty(0)
        else:
            buzzer_pwm.duty(buzzer_duty_cycle)

    conn.close()

#pwm = PWM(Pin(14))
# duty de 0-1000
# cambiar la frecuencia freq de 0-1000
#pwm.freq(800)
#pwm.duty(750)
