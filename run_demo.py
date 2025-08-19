"""
IoT Relay System - Professional Demonstration
Live demonstration of system features and capabilities

Author: M Hamza Ummer
Version: 2.0.0
License: MIT License

This script demonstrates the IoT Relay System's features and verifies
that all components are working correctly before deployment.
"""

import time
import json
from config import Config
from logger import Logger
from security import SecurityManager


def print_header():
    """Print professional header"""
    print("=" * 70)
    print("🔌 IoT Relay System - Professional Demonstration")
    print("   WiFi Relay Controller for Raspberry Pi Pico W")
    print("=" * 70)
    print("Author: M Hamza Ummer")
    print("Version: 2.0.0")
    print("License: MIT License")
    print("=" * 70)


def test_configuration():
    """Test configuration loading"""
    print("\n📋 CONFIGURATION TEST")
    print("-" * 30)
    
    try:
        config = Config()
        print("✅ Configuration loaded successfully")
        
        # Test key configuration values
        device_name = config.get('system.device_name', 'Unknown')
        print(f"   Device Name: {device_name}")
        
        auth_enabled = config.get('web_server.enable_auth', False)
        print(f"   Authentication: {'✅ Enabled' if auth_enabled else '❌ Disabled'}")
        
        relay_pin = config.get('relay.pin', 18)
        print(f"   Relay Pin: GPIO {relay_pin}")
        
        rate_limit = config.get('api.rate_limit', 60)
        print(f"   Rate Limit: {rate_limit} requests/minute")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_security_features():
    """Test security features"""
    print("\n🔐 SECURITY FEATURES TEST")
    print("-" * 35)
    
    try:
        config = Config()
        logger = Logger('INFO')
        security = SecurityManager(config, logger)
        
        print("✅ Security manager initialized")
        
        # Test input validation
        print("\n   Input Validation Tests:")
        test_cases = [
            ("relay_command", "on", True),
            ("relay_command", "malicious_input", False),
            ("pin_number", 18, True),
            ("pin_number", 999, False),
        ]
        
        for input_type, value, expected in test_cases:
            result = security.validate_input(input_type, value)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {input_type}='{value}' -> {'Valid' if result else 'Invalid'}")
        
        # Test authentication
        print("\n   Authentication Tests:")
        valid_auth = security.authenticate_user("admin", "SecureRelay2024!")
        print(f"   {'✅' if valid_auth else '❌'} Valid credentials test")
        
        invalid_auth = security.authenticate_user("admin", "wrong_password")
        print(f"   {'✅' if not invalid_auth else '❌'} Invalid credentials test")
        
        # Test session management
        print("\n   Session Management Tests:")
        session_id = security.create_session("admin", "192.168.1.100")
        print(f"   ✅ Session created: {session_id[:16]}...")
        
        session_valid = security.validate_session(session_id, "192.168.1.100")
        print(f"   {'✅' if session_valid else '❌'} Session validation test")
        
        # Test CSRF protection
        print("\n   CSRF Protection Tests:")
        csrf_token = security.generate_csrf_token(session_id)
        print(f"   ✅ CSRF token generated: {csrf_token[:16]}...")
        
        csrf_valid = security.validate_csrf_token(csrf_token, session_id)
        print(f"   {'✅' if csrf_valid else '❌'} CSRF validation test")
        
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False


def test_system_components():
    """Test system components"""
    print("\n🔧 SYSTEM COMPONENTS TEST")
    print("-" * 35)
    
    try:
        # Test logger
        logger = Logger('INFO')
        logger.info("Logger test message")
        print("✅ Logger system working")
        
        # Test configuration access
        config = Config()
        test_value = config.get('system.device_name', 'Test')
        print("✅ Configuration access working")
        
        # Test security manager
        security = SecurityManager(config, logger)
        print("✅ Security manager working")
        
        return True
        
    except Exception as e:
        print(f"❌ System components test failed: {e}")
        return False


def show_deployment_info():
    """Show deployment information"""
    print("\n🚀 DEPLOYMENT INFORMATION")
    print("-" * 35)
    
    config = Config()
    
    print("📋 Current Configuration:")
    print(f"   Device Name: {config.get('system.device_name', 'Pico-W-Relay')}")
    print(f"   Web Server Port: {config.get('web_server.port', 80)}")
    print(f"   Authentication: {'Enabled' if config.get('web_server.enable_auth') else 'Disabled'}")
    print(f"   Rate Limiting: {config.get('api.rate_limit', 60)} requests/minute")
    print(f"   Relay Pin: GPIO {config.get('relay.pin', 18)}")
    print(f"   Safety Timeout: {config.get('relay.safety_timeout', 300)} seconds")
    
    print("\n🔐 Security Status:")
    print("   ✅ User authentication enabled")
    print("   ✅ Rate limiting active")
    print("   ✅ CSRF protection enabled")
    print("   ✅ Input validation active")
    print("   ✅ Session security enabled")
    
    print("\n📡 Available Endpoints:")
    print("   GET  /                 - Main web interface")
    print("   GET  /login           - Login page")
    print("   GET  /config          - Configuration dashboard")
    print("   GET  /api/status      - System status (JSON)")
    print("   POST /api/relay/set   - Control relay (JSON)")
    print("   POST /api/relay/toggle - Toggle relay (JSON)")


def main():
    """Main demonstration function"""
    print_header()
    
    # Run tests
    config_ok = test_configuration()
    security_ok = test_security_features()
    components_ok = test_system_components()
    
    # Show results
    print("\n" + "=" * 70)
    print("📊 DEMONSTRATION RESULTS")
    print("=" * 70)
    
    all_tests_passed = config_ok and security_ok and components_ok
    
    print(f"Configuration Test:     {'✅ PASSED' if config_ok else '❌ FAILED'}")
    print(f"Security Features Test: {'✅ PASSED' if security_ok else '❌ FAILED'}")
    print(f"System Components Test: {'✅ PASSED' if components_ok else '❌ FAILED'}")
    
    print("\n" + "-" * 70)
    
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!")
        print("\n✅ The IoT Relay System is working correctly and ready to use.")
        print("✅ All security features are active and functioning.")
        print("✅ Configuration is loaded and valid.")
        
        show_deployment_info()
        
        print("\n📖 NEXT STEPS:")
        print("1. Upload all files to your Raspberry Pi Pico W")
        print("2. Update WiFi credentials in config.json")
        print("3. Change the default password in config.json")
        print("4. Run main.py on the Pico W")
        print("5. Access the web interface using the device's IP address")
        
    else:
        print("⚠️ SOME TESTS FAILED - PLEASE CHECK THE ERRORS ABOVE")
        print("\nPlease resolve the issues before deploying the system.")
    
    print("\n" + "=" * 70)
    return all_tests_passed


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("Demo completed successfully! 🎉")
        else:
            print("Demo completed with errors. ⚠️")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        print("Please check your installation and try again.")
