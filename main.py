"""
IoT Controlled Relay System - Main Entry Point
Raspberry Pi Pico W WiFi Relay Controller

Authors: M Armughan Ur Rahim, M Hamza Ummer, C Rahul Anand Rao
Description: Main application entry point for IoT relay control system

"""

from machine import Pin, reset
import network
import time
import gc
from wifi_manager import WiFiManager
from web_server import WebServer
from relay_controller import RelayController
from logger import Logger
from config import Config

class IoTRelaySystem:
    def __init__(self):
        """Initialize the IoT Relay System"""
        self.config = Config()
        self.logger = Logger(self.config.get('log_level', 'INFO'))
        self.wifi_manager = WiFiManager(self.config, self.logger)
        self.relay_controller = RelayController(self.config, self.logger)
        self.web_server = WebServer(self.config, self.logger, self.relay_controller)
        self.running = False
        
        # Status LED (built-in LED)
        self.status_led = Pin("LED", Pin.OUT)
        
        self.logger.info("IoT Relay System initialized")
    
    def start_system(self):
        """Start the complete IoT relay system"""
        try:
            self.logger.info("Starting IoT Relay System...")
            
            # Initialize hardware
            self.relay_controller.initialize()
            
            # Connect to WiFi
            if not self.wifi_manager.connect():
                self.logger.error("Failed to connect to WiFi")
                return False
            
            # Start web server
            self.web_server.start()
            
            # System ready
            self.running = True
            self.status_led.on()
            self.logger.info(f"System ready! Access at: http://{self.wifi_manager.get_ip()}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            return False
    
    def run(self):
        """Main system loop"""
        if not self.start_system():
            self.logger.error("System startup failed")
            return
        
        try:
            while self.running:
                # Handle web server requests
                self.web_server.handle_request()
                
                # Check WiFi connection
                if not self.wifi_manager.is_connected():
                    self.logger.warning("WiFi connection lost, attempting reconnection...")
                    self.status_led.off()
                    if self.wifi_manager.reconnect():
                        self.status_led.on()
                        self.logger.info("WiFi reconnected")
                
                # Memory cleanup
                if gc.mem_free() < 10000:  # If free memory < 10KB
                    gc.collect()
                
                time.sleep_ms(10)  # Small delay to prevent tight loop
                
        except KeyboardInterrupt:
            self.logger.info("System shutdown requested")
        except Exception as e:
            self.logger.error(f"System error: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful system shutdown"""
        self.logger.info("Shutting down IoT Relay System...")
        self.running = False
        self.status_led.off()
        self.web_server.stop()
        self.relay_controller.cleanup()
        self.logger.info("System shutdown complete")

# System entry point
def main():
    """Main entry point"""
    try:
        system = IoTRelaySystem()
        system.run()
    except Exception as e:
        print(f"Critical system error: {e}")
        time.sleep(5)
        reset()  # Reset system on critical error

if __name__ == "__main__":
    main()