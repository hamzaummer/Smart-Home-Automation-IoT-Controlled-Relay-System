"""
Configuration Management Module for IoT Relay System
Centralized configuration management with validation

Author: M Hamza Ummer
Contributors: M Armughan Ur Rahim, C Rahul Anand Rao
Version: 2.0.0
License: MIT License

Description:
    Centralized configuration management system for the IoT relay controller.
    Provides JSON-based configuration with validation, default values, and
    easy access to all system settings.

Features:
    - JSON-based configuration file (config.json)
    - Hierarchical configuration access with dot notation
    - Default value support for missing configuration keys
    - Configuration validation and error handling
    - Easy configuration updates and persistence

Configuration Structure:
    - wifi: Network connection settings
    - relay: Hardware control and safety settings
    - web_server: HTTP server and authentication settings
    - system: Device information and logging settings
    - security: Security feature configuration
    - api: API settings and rate limiting

Usage:
    config = Config()
    device_name = config.get('system.device_name', 'Default-Name')
    wifi_ssid = config.get('wifi.ssid')

    # Update configuration
    config.set('system.device_name', 'New-Name')
    config.save()

Configuration File:
    The system uses config.json for all settings. This file must be
    present in the root directory of the Pico W. See the included
    config.json for the complete configuration structure and examples.
"""

import json

class Config:
    """Configuration manager for IoT Relay System"""
    
    def __init__(self, config_file='config.json'):
        """Initialize configuration with default values"""
        self.config_file = config_file
        self.config_data = {
            # WiFi Configuration
            'wifi': {
                'ssid': 'YOUR_WIFI_SSID',
                'password': 'YOUR_WIFI_PASSWORD',
                'max_connect_attempts': 10,
                'reconnect_delay': 5,
                'connection_timeout': 30
            },
            
            # Relay Configuration  
            'relay': {
                'pin': 18,
                'active_low': True,  # True for LOW signal turns ON relay
                'initial_state': False,  # Start with relay OFF
                'max_on_time': 86400,  # Maximum continuous ON time (24 hours)
                'safety_timeout': 300  # 5 minutes safety timeout
            },
            
            # Web Server Configuration
            'web_server': {
                'port': 80,
                'max_connections': 5,
                'request_timeout': 10,
                'enable_auth': False,
                'auth_username': 'admin',
                'auth_password': 'password123'
            },
            
            # System Configuration
            'system': {
                'device_name': 'Pico-W-Relay',
                'log_level': 'INFO',
                'enable_watchdog': True,
                'status_led_pin': 'LED',
                'memory_threshold': 10000  # Minimum free memory in bytes
            },
            
            # Scheduling Configuration (future feature)
            'scheduler': {
                'enabled': False,
                'schedules': []
            },
            
            # API Configuration
            'api': {
                'enabled': True,
                'rate_limit': 60,  # requests per minute
                'enable_cors': True
            }
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file if it exists"""
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                self._merge_config(loaded_config)
        except (OSError, ValueError):
            # Config file doesn't exist or is invalid, use defaults
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            return True
        except OSError:
            return False
    
    def _merge_config(self, new_config):
        """Merge loaded config with defaults, preserving structure"""
        def merge_dict(default, new):
            for key, value in new.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dict(default[key], value)
                else:
                    default[key] = value
        
        merge_dict(self.config_data, new_config)
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation (e.g., 'wifi.ssid')"""
        keys = key_path.split('.')
        value = self.config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config_data
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_wifi_config(self):
        """Get WiFi configuration"""
        return self.config_data['wifi']
    
    def get_relay_config(self):
        """Get relay configuration"""
        return self.config_data['relay']
    
    def get_web_server_config(self):
        """Get web server configuration"""
        return self.config_data['web_server']
    
    def get_system_config(self):
        """Get system configuration"""
        return self.config_data['system']
    
    def update_wifi_credentials(self, ssid, password):
        """Update WiFi credentials"""
        self.config_data['wifi']['ssid'] = ssid
        self.config_data['wifi']['password'] = password
        return self.save_config()
    
    def is_valid_config(self):
        """Validate configuration"""
        wifi_config = self.get_wifi_config()
        
        # Check if WiFi credentials are set
        if wifi_config['ssid'] == 'YOUR_WIFI_SSID' or not wifi_config['ssid']:
            return False, "WiFi SSID not configured"
        
        if wifi_config['password'] == 'YOUR_WIFI_PASSWORD' or not wifi_config['password']:
            return False, "WiFi password not configured"
        
        # Check relay pin is valid
        relay_pin = self.get('relay.pin')
        if not isinstance(relay_pin, int) or relay_pin < 0:
            return False, "Invalid relay pin configuration"
        
        return True, "Configuration is valid"
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.__init__()
        return self.save_config()
    
    def export_config(self):
        """Export configuration as JSON string"""
        return json.dumps(self.config_data, indent=2)
    
    def import_config(self, json_string):
        """Import configuration from JSON string"""
        try:
            new_config = json.loads(json_string)
            self._merge_config(new_config)
            return self.save_config()
        except (ValueError, TypeError):
            return False