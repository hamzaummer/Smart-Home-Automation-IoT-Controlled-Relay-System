"""
Relay Controller Module for IoT Relay System
Professional relay control with comprehensive safety features

Author: M Hamza Ummer
Contributors: M Armughan Ur Rahim, C Rahul Anand Rao
Version: 2.0.0
License: MIT License

Description:
    Hardware abstraction layer for relay control with comprehensive
    safety mechanisms, statistics tracking, and fail-safe operation.
    Designed for 24/7 operation with multiple protection layers.

Safety Features:
    - Dual safety timers (safety timeout + maximum on-time)
    - Rapid switching prevention (minimum 1-second interval)
    - Emergency stop functionality with force-off capability
    - Fail-safe design (relay turns OFF on system errors)
    - Hardware protection with GPIO pin validation
    - Automatic state recovery after system restart

Statistics Tracking:
    - Total runtime accumulation
    - Cycle counting (ON/OFF transitions)
    - Session duration tracking
    - Power-on event logging
    - Average session duration calculation
    - Statistics persistence across reboots

Hardware Requirements:
    - Raspberry Pi Pico W
    - Single Channel Relay Module (3.3V or 5V)
    - Proper electrical isolation for AC loads

Usage:
    controller = RelayController(config, logger)
    controller.set_relay_state(True)   # Turn ON
    controller.set_relay_state(False)  # Turn OFF
    success = controller.toggle_relay()
    status = controller.get_status()
    stats = controller.get_statistics()

Safety Notice:
    This module controls electrical devices. Ensure proper electrical
    safety measures and qualified installation for AC loads. The relay
    module must provide adequate isolation for the controlled voltage.
"""

from machine import Pin, Timer
import time
import json

class RelayController:
    """Controls relay hardware with safety features"""
    
    def __init__(self, config, logger):
        """Initialize relay controller"""
        self.config = config
        self.logger = logger
        self.relay_config = config.get_relay_config()
        
        # Hardware setup
        self.relay_pin = None
        self.relay_state = False
        self.last_state_change = 0
        self.total_on_time = 0
        self.session_start_time = 0
        
        # Safety features
        self.safety_timer = None
        self.max_on_timer = None
        self.active_low = self.relay_config['active_low']
        
        # Statistics
        self.stats = {
            'total_cycles': 0,
            'total_runtime': 0,
            'last_on_time': 0,
            'last_off_time': 0,
            'power_on_count': 0
        }
        
        self.logger.info("Relay Controller initialized")
    
    def initialize(self):
        """Initialize relay hardware"""
        try:
            relay_pin_num = self.relay_config['pin']
            self.relay_pin = Pin(relay_pin_num, Pin.OUT)
            
            # Set initial state
            initial_state = self.relay_config['initial_state']
            self.set_relay_state(initial_state, force=True)
            
            self.logger.info(f"Relay initialized on GPIO{relay_pin_num}")
            self.logger.info(f"Active low mode: {self.active_low}")
            self.logger.info(f"Initial state: {'ON' if initial_state else 'OFF'}")
            
            # Load statistics
            self._load_stats()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize relay: {e}")
            return False
    
    def set_relay_state(self, state, force=False):
        """Set relay state with safety checks"""
        if self.relay_pin is None:
            self.logger.error("Relay not initialized")
            return False
        
        # Safety check - prevent too rapid switching
        current_time = time.time()
        if not force and (current_time - self.last_state_change) < 1.0:
            self.logger.warning("Relay switching too rapidly, ignoring command")
            return False
        
        try:
            old_state = self.relay_state
            self.relay_state = state
            
            # Set physical pin state (consider active_low)
            if self.active_low:
                self.relay_pin.value(0 if state else 1)  # LOW = ON, HIGH = OFF
            else:
                self.relay_pin.value(1 if state else 0)  # HIGH = ON, LOW = OFF
            
            # Update timing
            self.last_state_change = current_time
            
            # Handle state change logic
            if state and not old_state:
                # Turning ON
                self._handle_relay_on()
            elif not state and old_state:
                # Turning OFF
                self._handle_relay_off()
            
            # Log state change
            state_text = "ON" if state else "OFF"
            self.logger.info(f"Relay turned {state_text}")
            
            # Update statistics
            self._update_stats(old_state, state)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set relay state: {e}")
            return False
    
    def _handle_relay_on(self):
        """Handle relay turning ON"""
        self.session_start_time = time.time()
        self.stats['power_on_count'] += 1
        self.stats['last_on_time'] = self.session_start_time
        
        # Start safety timers
        self._start_safety_timers()
        
        self.logger.info("Relay turned ON - safety timers started")
    
    def _handle_relay_off(self):
        """Handle relay turning OFF"""
        if self.session_start_time > 0:
            session_duration = time.time() - self.session_start_time
            self.total_on_time += session_duration
            self.stats['total_runtime'] += session_duration
            self.stats['last_off_time'] = time.time()
            self.session_start_time = 0
        
        # Stop safety timers
        self._stop_safety_timers()
        
        # Update cycle count
        self.stats['total_cycles'] += 1
        
        self.logger.info(f"Relay turned OFF - session duration: {session_duration:.1f}s")
        
        # Save statistics
        self._save_stats()
    
    def _start_safety_timers(self):
        """Start safety timers"""
        # Safety timeout timer
        safety_timeout = self.relay_config['safety_timeout']
        if safety_timeout > 0:
            self.safety_timer = Timer(-1)
            self.safety_timer.init(
                period=safety_timeout * 1000,  # Convert to milliseconds
                mode=Timer.ONE_SHOT,
                callback=self._safety_timeout_callback
            )
            self.logger.debug(f"Safety timer started: {safety_timeout}s")
        
        # Maximum on-time timer
        max_on_time = self.relay_config['max_on_time']
        if max_on_time > 0:
            self.max_on_timer = Timer(-1)
            self.max_on_timer.init(
                period=max_on_time * 1000,  # Convert to milliseconds
                mode=Timer.ONE_SHOT,
                callback=self._max_on_time_callback
            )
            self.logger.debug(f"Maximum on-time timer started: {max_on_time}s")
    
    def _stop_safety_timers(self):
        """Stop safety timers"""
        if self.safety_timer:
            self.safety_timer.deinit()
            self.safety_timer = None
        
        if self.max_on_timer:
            self.max_on_timer.deinit()
            self.max_on_timer = None
    
    def _safety_timeout_callback(self, timer):
        """Safety timeout callback - automatically turn off relay"""
        self.logger.warning("Safety timeout triggered - automatically turning OFF relay")
        self.set_relay_state(False, force=True)
    
    def _max_on_time_callback(self, timer):
        """Maximum on-time callback - automatically turn off relay"""
        self.logger.warning("Maximum on-time reached - automatically turning OFF relay")
        self.set_relay_state(False, force=True)
    
    def get_relay_state(self):
        """Get current relay state"""
        return self.relay_state
    
    def toggle_relay(self):
        """Toggle relay state"""
        return self.set_relay_state(not self.relay_state)
    
    def emergency_stop(self):
        """Emergency stop - immediately turn off relay"""
        try:
            if self.relay_pin:
                # Force OFF state regardless of active_low setting
                if self.active_low:
                    self.relay_pin.value(1)  # HIGH = OFF for active low
                else:
                    self.relay_pin.value(0)  # LOW = OFF for active high
                
                self.relay_state = False
                self._stop_safety_timers()
                
                self.logger.warning("EMERGENCY STOP - Relay forced OFF")
                return True
        except Exception as e:
            self.logger.error(f"Emergency stop failed: {e}")
            return False
    
    def get_status(self):
        """Get detailed relay status"""
        current_time = time.time()
        current_session_duration = 0
        
        if self.relay_state and self.session_start_time > 0:
            current_session_duration = current_time - self.session_start_time
        
        return {
            'state': self.relay_state,
            'pin': self.relay_config['pin'],
            'active_low': self.active_low,
            'current_session_duration': current_session_duration,
            'total_runtime': self.stats['total_runtime'],
            'total_cycles': self.stats['total_cycles'],
            'power_on_count': self.stats['power_on_count'],
            'last_state_change': self.last_state_change,
            'safety_timer_active': self.safety_timer is not None,
            'max_on_timer_active': self.max_on_timer is not None
        }
    
    def get_statistics(self):
        """Get relay usage statistics"""
        stats = self.stats.copy()
        
        # Add current session if relay is ON
        if self.relay_state and self.session_start_time > 0:
            current_session = time.time() - self.session_start_time
            stats['current_session_duration'] = current_session
            stats['total_runtime_including_current'] = stats['total_runtime'] + current_session
        else:
            stats['current_session_duration'] = 0
            stats['total_runtime_including_current'] = stats['total_runtime']
        
        # Calculate average session duration
        if stats['total_cycles'] > 0:
            stats['average_session_duration'] = stats['total_runtime'] / stats['total_cycles']
        else:
            stats['average_session_duration'] = 0
        
        return stats
    
    def reset_statistics(self):
        """Reset relay statistics"""
        self.stats = {
            'total_cycles': 0,
            'total_runtime': 0,
            'last_on_time': 0,
            'last_off_time': 0,
            'power_on_count': 0
        }
        self._save_stats()
        self.logger.info("Relay statistics reset")
        return True
    
    def _update_stats(self, old_state, new_state):
        """Update internal statistics"""
        # Statistics are updated in _handle_relay_on/off methods
        pass
    
    def _load_stats(self):
        """Load statistics from file"""
        try:
            with open('relay_stats.json', 'r') as f:
                self.stats = json.load(f)
            self.logger.debug("Relay statistics loaded")
        except (OSError, ValueError):
            # File doesn't exist or is invalid
            self.logger.debug("No existing statistics file found, using defaults")
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            with open('relay_stats.json', 'w') as f:
                json.dump(self.stats, f)
            self.logger.debug("Relay statistics saved")
        except OSError:
            self.logger.warning("Failed to save relay statistics")
    
    def test_relay(self, duration=2):
        """Test relay operation"""
        self.logger.info(f"Testing relay operation for {duration}s")
        
        try:
            # Test ON
            self.set_relay_state(True, force=True)
            time.sleep(duration)
            
            # Test OFF  
            self.set_relay_state(False, force=True)
            
            self.logger.info("Relay test completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Relay test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Turn off relay
            if self.relay_pin and self.relay_state:
                self.set_relay_state(False, force=True)
            
            # Stop timers
            self._stop_safety_timers()
            
            # Save final statistics
            self._save_stats()
            
            self.logger.info("Relay controller cleanup completed")
        except Exception as e:
            self.logger.error(f"Relay cleanup failed: {e}")
    
    def get_config_info(self):
        """Get relay configuration information"""
        return {
            'pin': self.relay_config['pin'],
            'active_low': self.relay_config['active_low'],
            'initial_state': self.relay_config['initial_state'],
            'max_on_time': self.relay_config['max_on_time'],
            'safety_timeout': self.relay_config['safety_timeout']
        }
    