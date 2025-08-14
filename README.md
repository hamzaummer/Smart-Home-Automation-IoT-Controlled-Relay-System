# IoT Controlled Relay using Raspberry Pi Pico W
 
This is a professional IoT relay control system built with Raspberry Pi Pico W, enabling wireless control of electrical appliances through a modern web interface.

## 🚀 Features :

- **Remote Control:** Control electrical appliances via WiFi using any web browser  
- **Modern Web Interface:** Responsive, mobile-friendly control panel  
- **Safety Features:** Built-in safety timers and maximum on-time limits  
- **Real-time Monitoring:** Live status updates and usage statistics  
- **RESTful API:** Full API support for third-party integration  
- **Configuration Management:** Easy setup through web interface  
- **Statistics Tracking:** Monitor usage patterns and relay cycles  
- **Robust Error Handling:** Automatic reconnection and fault tolerance  
- **Memory Management:** Optimized for MicroPython with garbage collection 

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

## 📋 Installation Guide:

### Step 1: Setup Development Environment

Install Thonny IDE or your preferred MicroPython IDE
Download the latest MicroPython firmware for Raspberry Pi Pico W
Flash MicroPython to your Pico W following official instructions

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

### Step 5: Run the System
1. Connect Pico W via USB  
2. Run **main.py** in your IDE  
3. Monitor the console for the assigned IP address  
4. Open the IP address in your web browser  

### API Endpoints

**GET Endpoints**
- `/` - Main web interface  
- `/api/status` - Complete system status  
- `/api/relay/state` - Current relay state  
- `/api/system/info` - System information  
- `/api/stats` - Usage statistics  

**POST Endpoints**
- `/api/relay/toggle` - Toggle relay state  
- `/api/relay/set` - Set specific relay state  
```json
{"state": true}  // or false
```

Example API Usage:
```bash
# Get relay status
curl http://192.168.1.100/api/relay/state

# Turn relay ON
curl -X POST http://192.168.1.100/api/relay/set      -H "Content-Type: application/json"      -d '{"state": true}'
```

## ⚙️ Configuration Options

All configurations can be changed in **config.py**.

**WiFi Settings**
```python
'wifi': {
    'ssid': 'YOUR_WIFI_SSID',
    'password': 'YOUR_WIFI_PASSWORD',
    'max_connect_attempts': 10,
    'reconnect_delay': 5
}
```

**Relay Safety Settings**
```python
'relay': {
    'pin': 18,
    'active_low': True,
    'max_on_time': 86400,
    'safety_timeout': 300
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

## 🔧 Troubleshooting

**WiFi Connection Failed**
- Verify SSID/password  
- Check WiFi signal strength  
- Ensure 2.4GHz network  

**Relay Not Responding**
- Check GPIO pin connections  
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
