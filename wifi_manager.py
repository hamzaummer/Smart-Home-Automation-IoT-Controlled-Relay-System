"""
WiFi Manager Module for IoT Relay System
Robust WiFi connectivity with automatic reconnection

Author: M Hamza Ummer
Contributors: M Armughan Ur Rahim, C Rahul Anand Rao
Version: 2.0.0
License: MIT License

Description:
    Comprehensive WiFi management for Raspberry Pi Pico W with automatic
    reconnection, connection monitoring, and robust error handling.
    Designed for reliable 24/7 operation in IoT environments.

Features:
    - Automatic WiFi connection with retry logic
    - Connection monitoring and automatic reconnection
    - Configurable connection timeouts and retry attempts
    - Network status reporting and diagnostics
    - Non-blocking reconnection for service continuity
    - Comprehensive logging of network events

Network Requirements:
    - 2.4GHz WiFi network (Pico W limitation)
    - WPA2/WPA3 security (recommended)
    - Stable internet connection for remote access

Usage:
    wifi = WiFiManager(config, logger)
    if wifi.connect():
        print(f"Connected! IP: {wifi.get_ip_address()}")

    # In main loop
    if not wifi.is_connected():
        wifi.reconnect()

Configuration:
    Set WiFi credentials in config.json:
    {
        "wifi": {
            "ssid": "YourNetworkName",
            "password": "YourNetworkPassword",
            "timeout": 30,
            "max_attempts": 10,
            "reconnect_delay": 5
        }
    }
"""

import network
import time
from machine import Timer

class WiFiManager:
    """Manages WiFi connectivity for IoT Relay System"""
    
    def __init__(self, config, logger):
        """Initialize WiFi Manager"""
        self.config = config
        self.logger = logger
        self.wifi_config = config.get_wifi_config()
        
        # Initialize WiFi interface
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # Connection state
        self.connected = False
        self.ip_address = None
        self.connection_attempts = 0
        self.last_connection_attempt = 0
        
        # Reconnection timer
        self.reconnect_timer = None
        
        self.logger.info("WiFi Manager initialized")
    
    def connect(self):
        """Connect to WiFi network"""
        ssid = self.wifi_config['ssid']
        password = self.wifi_config['password']
        max_attempts = self.wifi_config['max_connect_attempts']
        
        if ssid == 'YOUR_WIFI_SSID':
            self.logger.error("WiFi SSID not configured. Please update config.json")
            return False
        
        self.logger.info(f"Connecting to WiFi network: {ssid}")
        
        # Connect to network
        self.wlan.connect(ssid, password)
        
        # Wait for connection
        connection_timeout = self.wifi_config['connection_timeout']
        start_time = time.time()
        
        while not self.wlan.isconnected() and (time.time() - start_time) < connection_timeout:
            time.sleep(1)
            self.logger.info("Waiting for WiFi connection...")
        
        if self.wlan.isconnected():
            self.connected = True
            self.ip_address = self.wlan.ifconfig()[0]
            self.connection_attempts = 0
            
            # Log connection details
            ifconfig = self.wlan.ifconfig()
           