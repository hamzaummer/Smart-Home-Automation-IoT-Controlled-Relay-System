"""
IoT Controlled Relay System - Main Entry Point
Professional WiFi Relay Controller for Raspberry Pi Pico W

Author: M Hamza Ummer
Contributors: M Armughan Ur Rahim, C Rahul Anand Rao
Version: 2.0.0
License: MIT License

Description:
    Main application entry point for the IoT relay control system.
    Provides secure, web-based control of electrical appliances through
    a Raspberry Pi Pico W with comprehensive safety features and modern
    web interface.

Features:
    - Secure web-based control interface
    - Real-time status monitoring
    - Safety timers and protection mechanisms
    - RESTful API with authentication
    - Mobile-responsive design
    - Comprehensive logging and error handling

Hardware Requirements:
    - Raspberry Pi Pico W
    - Single Channel Relay Module
    - Electrical load to control

Usage:
    1. Configure WiFi credentials in config.json
    2. Set up hardware connections as per documentation
    3. Upload all files to Pico W
    4. Run this script to start the system
    5. Access web interface via device IP address

Safety Notice:
    This system controls electrical devices. Ensure proper electrical
    safety measures and qualified installation for AC loads.
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
                # Handle web server requests (non-blocking)
                self.web_server.handle_request()

                # Process request queue for better concurrency
                self.web_server.process_request_queue()

                # Check WiFi connection (non-blocking check)
                if not self.wifi_manager.is_connected():
                    self.logger.warning("WiFi connection lost, attempting reconnection...")
                    self.status_led.off()
                    # Non-blocking reconnection attempt
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