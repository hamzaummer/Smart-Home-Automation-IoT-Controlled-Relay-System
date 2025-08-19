# 🔌 IoT Controlled Relay System

**Professional WiFi Relay Controller for Raspberry Pi Pico W**

A production-ready IoT relay control system featuring enterprise-grade security, modern web interface, and comprehensive safety mechanisms. Control electrical appliances remotely with confidence through a secure, user-friendly web interface.

**Author:** M Hamza Ummer
**Contributors:** M Armughan Ur Rahim, C Rahul Anand Rao
**Version:** 2.0.0
**License:** MIT License

## 📁 Project Structure

```
pico-w-iot-relay-controller/
├── main.py              # Main application entry point
├── config.py            # Configuration management
├── config.json          # System configuration file
├── web_server.py        # HTTP server and web interface
├── relay_controller.py  # Hardware control and safety
├── wifi_manager.py      # WiFi connectivity management
├── security.py          # Security features and authentication
├── logger.py            # Logging system
├── run_demo.py          # System demonstration script
├── requirements.txt     # System requirements and dependencies
├── README.md            # This documentation
├── LICENSE              # MIT License
├── WINDOWS_SETUP.md     # Windows-specific setup guide
├── .gitignore           # Git ignore rules
└── docs/                # Additional documentation
    ├── CHANGELOG.md     # Version history
    └── CONTRIBUTING.md  # Contribution guidelines
```

## ✨ Key Features

### 🔐 **Enterprise Security**
- **User Authentication** - Secure login with session management
- **Rate Limiting** - Protection against DoS attacks (60 requests/minute)
- **CSRF Protection** - Cross-Site Request Forgery prevention
- **Input Validation** - Comprehensive validation of all user inputs
- **Session Security** - IP-based validation with automatic expiry

### 🌐 **Modern Web Interface**
- **Responsive Design** - Mobile-friendly interface with real-time updates
- **Live Status Updates** - Automatic updates every 2 seconds
- **Professional UI** - Clean design with visual feedback
- **System Monitoring** - Real-time connection and system health
- **Configuration Dashboard** - Easy-to-use settings interface

### 🛡️ **Safety & Reliability**
- **Dual Safety Timers** - 5-minute safety timeout + 24-hour maximum on-time
- **Emergency Stop** - Force-off capability for safety
- **Fail-Safe Design** - Automatic OFF state on system errors
- **Hardware Protection** - GPIO validation and switching prevention
- **Statistics Tracking** - Usage monitoring and persistence

### 🚀 **Professional Features**
- **RESTful API** - Complete API for third-party integration
- **Memory Management** - Optimized for 24/7 operation
- **Network Recovery** - Automatic WiFi reconnection
- **JSON Configuration** - Easy setup and customization

## 🛠️ Hardware Requirements :

### Essential Components
- Raspberry Pi Pico W (1x) – WiFi-enabled microcontroller  
- Single Channel Relay Module (1x) – 5V/3.3V with optocoupler isolation  
- Breadboard (1x) – For prototyping connections  
- Jumper Wires (8–10x) – Male-to-male connecting wires  
- Micro USB Cable (1x) – For programming and power  
- AC Load (1x) – Bulb, fan, or other appliance to control  

### Optional Components
- Status LEDs for visual feedback  
- Push button for manual override  
- Enclosure for permanent installation

## 🔌 Circuit Connections (Tabular Format)

| Relay Module Pin  | Raspberry Pi Pico W Pin | Description                         |
|-------------------|-------------------------|-------------------------------------|
| VCC               | 3.3V or VBUS            | Power supply (3.3V or 5V)           |
| GND               | GND                     | Ground connection                   |
| IN (Trigger)      | GP18                    | Control signal                      |
| NO (Normally Open)| AC Load Hot Wire        | Switched output                     |
| COM (Common)      | AC Load Neutral         | Common terminal                     |
| NC (Normally Closed)| Not Connected         | Not used                            |

## 🚀 Quick Start Guide

### 📋 **Step 1: Hardware Setup**

1. **Flash MicroPython Firmware**
   - Download the latest MicroPython firmware for Raspberry Pi Pico W
   - Hold the BOOTSEL button while connecting USB to your computer
   - Copy the .uf2 firmware file to the RPI-RP2 drive that appears
   - The Pico W will reboot automatically with MicroPython installed

2. **Wire the Relay Module**
   ```
   Relay Module    →    Pico W Pin
   VCC            →    3.3V (Pin 36) or VBUS (Pin 40)
   GND            →    GND (Pin 38)
   IN (Signal)    →    GP18 (Pin 24)
   ```

   ⚠️ **SAFETY WARNING:** For AC loads, ensure proper electrical safety measures and qualified installation.

### 🔧 **Step 2: Software Installation**

1. **Install Thonny IDE** (Recommended)
   - Download from [thonny.org](https://thonny.org)
   - Install and connect to your Pico W via USB

2. **Download Project Files**
   - Clone or download this repository
   - You'll need these files on your Pico W:
     - `main.py` - Main application
     - `config.py` - Configuration management
     - `wifi_manager.py` - WiFi connectivity
     - `web_server.py` - Web interface and API
     - `relay_controller.py` - Hardware control
     - `logger.py` - Logging system
     - `security.py` - Security features
     - `config.json` - System configuration

3. **Upload Files to Pico W**
   - Using Thonny: Copy all files to the Pico W's root directory
   - Using other IDEs: Transfer files via your preferred method

### 🔐 **Step 3: Configuration**

1. **⚠️ CRITICAL: Change Default Password**

   Edit `config.json` and update the password:
   ```json
   {
     "web_server": {
       "auth_password": "YourSecurePassword123!"
     }
   }
   ```

2. **Configure WiFi**

   Update your network credentials in `config.json`:
   ```json
   {
     "wifi": {
       "ssid": "YourWiFiNetwork",
       "password": "YourWiFiPassword"
     }
   }
   ```

3. **Customize Device Name** (Optional)
   ```json
   {
     "system": {
       "device_name": "Living-Room-Relay"
     }
   }
   ```

### Step 2: Configure WiFi Credentials

Edit config.py and update your WiFi credentials:

'wifi': {
    'ssid': 'YOUR_ACTUAL_WIFI_SSID',
    'password': 'YOUR_ACTUAL_WIFI_PASSWORD',
    # ... other settings
}

### Step 3: Upload Code Files
Upload all Python files to your Raspberry Pi Pico W:
- `main.py` - Main application entry point  
- `config.py` - Configuration management  
- `wifi_manager.py` - WiFi connectivity handling  
- `web_server.py` - HTTP server and web interface  
- `relay_controller.py` - Relay hardware control  
- `logger.py` - Logging system  

### Step 4: Hardware Assembly
- Connect the relay module to Pico W as per the circuit diagram  
- Connect your AC load through the relay's **NO** and **COM** terminals  
- **⚠️ Ensure all AC connections are made safely by a qualified person**  

### 🧪 **Step 4: Test the System (Recommended)**

Before deploying to your Pico W, test the system on your computer:

1. **Run the Demonstration**

   **Windows Users:**
   ```cmd
   # Open Command Prompt and navigate to project folder
   cd "path\to\pico-w-iot-relay-controller"
   python run_demo.py
   ```

   **If you get "python is not recognized" error:**
   ```cmd
   py run_demo.py
   ```

   **Mac/Linux Users:**
   ```bash
   cd /path/to/pico-w-iot-relay-controller
   python3 run_demo.py
   ```

2. **Expected Output**
   You should see:
   ```
   🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!
   ```

   If you see this message, your system is ready to deploy!

3. **Troubleshooting**
   - **Windows PowerShell Issues:** See `WINDOWS_SETUP.md` for detailed solutions
   - **Python Not Found:** Install Python from [python.org](https://python.org) or Microsoft Store
   - **Module Errors:** Ensure you're in the correct project directory

### 🚀 **Step 5: Deploy to Pico W**

1. **Start the Application**
   - In Thonny: Open `main.py` and click the "Run" button
   - The system will start automatically and display status messages

2. **Find Your Device IP**
   - Watch the console output for a message like: `Web server started on http://192.168.1.100`
   - Note down this IP address

3. **First Login**
   - Open a web browser and go to the IP address shown
   - You'll be redirected to the login page
   - Enter username: `admin` and your configured password
   - Click "Login" to access the control interface

## 🌐 **Using the Web Interface**

### 🏠 **Main Control Panel**
After logging in, you'll see the main control interface with:
- **Relay Control Toggle** - Click to turn your device ON/OFF
- **Real-time Status** - Live updates of relay state and system health
- **Safety Information** - Current safety timer settings
- **Usage Statistics** - Runtime, cycles, and session information

### ⚙️ **Configuration Dashboard**
Click "Settings" to view:
- Security settings status
- Hardware configuration
- Network information
- System details

### 🔐 **Security Features**
- **Automatic Logout** - Sessions expire after 30 minutes of inactivity
- **Rate Limiting** - Protection against excessive requests
- **Secure Communication** - All state changes are protected

## 🔌 **API Documentation**

For developers who want to integrate with the relay system programmatically.

### 🔐 **Authentication**
All API endpoints require authentication using HTTP Basic Auth:
```bash
curl -u admin:yourpassword http://device-ip/api/status
```

### 📡 **Main Endpoints**

#### **Get System Status**
```http
GET /api/status
```
Returns relay state, runtime statistics, and system information.

#### **Control Relay**
```http
POST /api/relay/set
Content-Type: application/json

{"state": true}  // true = ON, false = OFF
```

#### **Toggle Relay**
```http
POST /api/relay/toggle
```
Switches relay to opposite state (ON→OFF or OFF→ON).

#### **System Information**
```http
GET /api/system/info
```
Returns device information, memory usage, and network status.

### 🔧 **Example Usage**
```bash
# Check relay status
curl -u admin:yourpassword http://192.168.1.100/api/status

# Turn relay ON
curl -u admin:yourpassword -X POST http://192.168.1.100/api/relay/set \
  -H "Content-Type: application/json" -d '{"state": true}'

# Turn relay OFF
curl -u admin:yourpassword -X POST http://192.168.1.100/api/relay/set \
  -H "Content-Type: application/json" -d '{"state": false}'

# Toggle relay state
curl -u admin:yourpassword -X POST http://192.168.1.100/api/relay/toggle
```

## 🔐 **Security & Best Practices**

### ⚠️ **Important Security Steps**

1. **⚠️ CRITICAL: Change Default Password**
   - The default password is `SecureRelay2024!`
   - **You MUST change this before deployment**
   - Use a strong password with 8+ characters, mixed case, numbers, and symbols

2. **Network Security**
   - Use a secure WiFi network (WPA2/WPA3)
   - Consider isolating IoT devices on a separate network
   - Monitor access logs for suspicious activity

3. **Physical Security**
   - Secure the Pico W device in an appropriate enclosure
   - Ensure proper electrical installation for AC loads
   - Keep the device in a safe, dry location

### 🛡️ **Built-in Security Features**

- **User Authentication** - Secure login required for all access
- **Rate Limiting** - Protection against excessive requests (60/minute)
- **Session Management** - Automatic logout after 30 minutes
- **Input Validation** - All user inputs are validated and sanitized
- **CSRF Protection** - Protection against cross-site request forgery
- **Secure Error Handling** - No sensitive information disclosed in errors

## 🔧 **Configuration Reference**

### 📡 **WiFi Settings**
```json
{
  "wifi": {
    "ssid": "YourWiFiNetwork",
    "password": "YourWiFiPassword",
    "timeout": 30,
    "max_attempts": 10,
    "reconnect_delay": 5
  }
}
```

### 🔌 **Relay Configuration**
```json
{
  "relay": {
    "pin": 18,
    "active_low": true,
    "safety_timeout": 300,
    "max_on_time": 86400,
    "rapid_switching_delay": 1
  }
}
```

### 🌐 **Web Server Settings**
```json
{
  "web_server": {
    "port": 80,
    "max_connections": 5,
    "request_timeout": 10,
    "enable_auth": true,
    "session_timeout": 1800
  }
}
```

### 🔒 **Security Configuration**
```json
{
  "security": {
    "input_validation": true,
    "rate_limiting": true,
    "csrf_protection": true,
    "max_login_attempts": 5,
    "lockout_duration": 300
  }
}
```

**Web Server Settings**
```python
'web_server': {
    'port': 80,
    'max_connections': 5,
    'request_timeout': 10
}
```

## 📊 Usage Statistics

The system automatically tracks:
- Total Runtime: Cumulative time relay has been ON
- Cycle Count: Number of ON/OFF cycles
- Session Duration: Current continuous ON time
- Power-on Events: Total number of times turned ON
- Average Session: Mean duration per ON cycle
- Statistics persist across system reboots and are accessible via web interface or API.

## 🔧 **Troubleshooting Guide**

### 🐍 **Setup Issues**

**❌ "python is not recognized" (Windows)**
```
Problem: PowerShell/Command Prompt can't find Python
Solutions:
✅ Try: py run_demo.py (instead of python)
✅ Install Python from Microsoft Store (easiest)
✅ Add Python to PATH in Environment Variables
✅ Use full path: C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
```

**❌ Demo Script Fails**
```
Problem: run_demo.py shows errors or failures
Solutions:
✅ Ensure you're in the correct project directory
✅ Check that all .py files are present
✅ Verify config.json exists and is valid
✅ Try: python -c "import json; print('JSON module works')"
```

### 🌐 **Network Issues**

**❌ WiFi Connection Failed**
```
Problem: Pico W can't connect to WiFi
Solutions:
✅ Verify SSID and password in config.json
✅ Ensure 2.4GHz network (Pico W doesn't support 5GHz)
✅ Check WiFi signal strength at device location
✅ Try mobile hotspot for testing
✅ Check for special characters in WiFi password
```

**❌ Can't Access Web Interface**
```
Problem: Browser can't reach device IP
Solutions:
✅ Check device IP in console output
✅ Ensure device and computer on same network
✅ Try: ping [device-ip] to test connectivity
✅ Disable firewall temporarily for testing
✅ Try different browser or incognito mode
```

### 🔐 **Authentication Issues**

**❌ Login Failed**
```
Problem: Invalid username/password error
Solutions:
✅ Default username: admin, password: SecureRelay2024!
✅ Check for typos (password is case-sensitive)
✅ Wait 1 minute if rate limited
✅ Verify config.json has correct credentials
```

**❌ Session Expired**
```
Problem: Redirected to login unexpectedly
Solutions:
✅ Normal after 30 minutes inactivity - just login again
✅ Check system time if sessions expire immediately
✅ Clear browser cookies and try again
```

### 🔌 **Hardware Issues**

**❌ Relay Not Responding**
```
Problem: Web shows state change but relay doesn't switch
Solutions:
✅ Check wiring: VCC→3.3V, GND→GND, IN→GP18
✅ Verify relay module power (LED should light up)
✅ Test with multimeter on relay input pin
✅ Try different GPIO pin and update config.json
✅ Check if relay module is 3.3V or 5V compatible
```

**❌ System Crashes or Restarts**
```
Problem: Pico W reboots unexpectedly
Solutions:
✅ Check power supply (use quality USB cable)
✅ Monitor memory usage in web interface
✅ Reduce log level to WARNING in config.json
✅ Check for loose connections
✅ Try different relay module
```

### 🆘 **Emergency Recovery**

**🔄 Factory Reset**
```
1. Connect Pico W via USB
2. Delete config.json from device
3. Restart device (creates default config)
4. Reconfigure WiFi and password
```

**🔍 Debug Mode**
```json
{
  "system": {
    "log_level": "DEBUG"
  }
}
```

**📞 Get Help**
```
1. Run: python run_demo.py
2. Check output for specific error messages
3. Verify all hardware connections
4. Try the system with minimal configuration
5. Check WINDOWS_SETUP.md for Windows-specific issues
```
- Verify relay module power supply  
- Test relay with manual commands  

**Web Interface Not Accessible**
- Confirm Pico W IP address  
- Check firewall settings  
- Ensure devices are on same network  

**Memory Issues**
- Automatic garbage collection  
- Restart if warnings persist  

**Debug Mode**
```python
'system': {
    'log_level': 'DEBUG'
}
```

## 🔐 Security Considerations

- Local Network Only: System operates on local WiFi network
- No Internet Required: Fully self-contained operation
- Rate Limiting: Built-in protection against rapid switching
- Input Validation: All web inputs are validated
- Safety Timeouts: Hardware protection against stuck-on conditions

## 🚧 Future Enhancements

- Scheduling System: Timer-based automation
- Multiple Relay Support: Control multiple devices
- Mobile App: Native iOS/Android application
- Cloud Integration: Remote access via cloud service
- User Authentication: Password protection
- HTTPS Support: Encrypted communication
- Energy Monitoring: Power consumption tracking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes
- Feature enhancements
- Documentation improvements
- Hardware compatibility updates

Development Setup

- Fork the repository
- Create a feature branch
- Test changes thoroughly
- Submit pull request with detailed description

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors
M Hamza Ummer - Project Lead

M Armughan Ur Rahim - Hardware Design

C Rahul Anand Rao - Software Development

## 🙏 Acknowledgments
- Raspberry Pi Foundation for the excellent Pico W platform
- MicroPython community for the robust embedded Python implementation
- How2Electronics for project inspiration
