"""
Basic Relay Control Example
Demonstrates simple relay on/off control without web server
"""

from machine import Pin
import time

# Initialize relay on GPIO18
relay = Pin(18, Pin.OUT)

print("Basic Relay Control Test")
print("Active Low Configuration: LOW=ON, HIGH=OFF")

# Turn relay ON (LOW signal for active-low relay)
print("Turning relay ON...")
relay.value(0)
time.sleep(2)

# Turn relay OFF (HIGH signal for active-low relay)  
print("Turning relay OFF...")
relay.value(1)
time.sleep(2)

# Toggle test
print("Toggle test - 5 cycles")
for i in range(5):
    print(f"Cycle {i+1}: ON")
    relay.value(0)  # ON
    time.sleep(1)
    
    print(f"Cycle {i+1}: OFF")
    relay.value(1)  # OFF
    time.sleep(1)

print("Basic relay test completed")
relay.value(1)  # Ensure relay is OFF