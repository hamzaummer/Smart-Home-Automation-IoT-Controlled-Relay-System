"""
Web Server Module
Handles HTTP server, web interface, and API endpoints
"""

import socket
import json
import time
import gc

class WebServer:
    """HTTP Web Server for IoT Relay Control"""
    
    def __init__(self, config, logger, relay_controller):
        """Initialize web server"""
        self.config = config
        self.logger = logger
        self.relay_controller = relay_controller
        self.server_config = config.get_web_server_config()
        
        self.socket = None
        self.running = False
        self.request_count = 0
        self.last_request_time = 0
        
        self.logger.info("Web Server initialized")
    
    def start(self):
        """Start the web server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', self.server_config['port']))
            self.socket.listen(self.server_config['max_connections'])
            self.socket.settimeout(0.1)  # Non-blocking with timeout
            
            self.running = True
            self.logger.info(f"Web server started on port {self.server_config['port']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start web server: {e}")
            return False
    
    def stop(self):
        """Stop the web server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
                self.logger.info("Web server stopped")
            except:
                pass
            self.socket = None
    
    def handle_request(self):
        """Handle incoming HTTP requests"""
        if not self.running or not self.socket:
            return
        
        try:
            conn, addr = self.socket.accept()
            self.request_count += 1
            self.last_request_time = time.time()
            
            conn.settimeout(self.server_config['request_timeout'])
            self.logger.debug(f"Connection from {addr[0]}:{addr[1]}")
            
            try:
                # Read request
                request = conn.recv(1024).decode('utf-8')
                if not request:
                    return
                
                # Parse request
                response = self._process_request(request, addr[0])
                
                # Send response
                conn.send(response.encode('utf-8'))
                
            except Exception as e:
                self.logger.error(f"Request processing error: {e}")
                error_response = self._create_error_response(500, "Internal Server Error")
                conn.send(error_response.encode('utf-8'))
            finally:
                conn.close()
                
        except OSError:
            # No connection available (non-blocking socket)
            pass
        except Exception as e:
            self.logger.error(f"Connection handling error: {e}")
    
    def _process_request(self, request, client_ip):
        """Process HTTP request and return response"""
        try:
            # Parse request line
            lines = request.split('\\n')
            if not lines:
                return self._create_error_response(400, "Bad Request")
            
            request_line = lines[0].strip()
            parts = request_line.split(' ')
            
            if len(parts) < 2:
                return self._create_error_response(400, "Bad Request")
            
            method = parts[0]
            path = parts[1]
            
            self.logger.debug(f"{method} {path} from {client_ip}")
            
            # Route request
            if method == "GET":
                return self._handle_get_request(path, request, client_ip)
            elif method == "POST":
                return self._handle_post_request(path, request, client_ip)
            else:
                return self._create_error_response(405, "Method Not Allowed")
                
        except Exception as e:
            self.logger.error(f"Request parsing error: {e}")
            return self._create_error_response(500, "Internal Server Error")
    
    def _handle_get_request(self, path, request, client_ip):
        """Handle GET requests"""
        # Main web interface
        if path == "/" or path.startswith("/?"):
            return self._handle_main_page(path)
        
        # API endpoints
        elif path == "/api/status":
            return self._handle_api_status()
        elif path == "/api/relay/state":
            return self._handle_api_relay_state()
        elif path == "/api/system/info":
            return self._handle_api_system_info()
        elif path == "/api/stats":
            return self._handle_api_stats()
        
        # Static files
        elif path == "/style.css":
            return self._serve_css()
        elif path == "/script.js":
            return self._serve_javascript()
        
        # Configuration page
        elif path == "/config":
            return self._handle_config_page()
        
        # 404 Not Found
        else:
            return self._create_error_response(404, "Not Found")
    
    def _handle_post_request(self, path, request, client_ip):
        """Handle POST requests"""
        if path == "/api/relay/toggle":
            return self._handle_api_relay_toggle(request)
        elif path == "/api/relay/set":
            return self._handle_api_relay_set(request)
        elif path == "/api/config/save":
            return self._handle_api_config_save(request)
        else:
            return self._create_error_response(404, "Not Found")
    
    def _handle_main_page(self, path):
        """Handle main web interface"""
        # Check for relay control parameters
        if "relay=on" in path:
            self.relay_controller.set_relay_state(True)
            self.logger.info("Relay turned ON via web interface")
        elif "relay=off" in path:
            self.relay_controller.set_relay_state(False)
            self.logger.info("Relay turned OFF via web interface")
        
        # Generate main page HTML
        html = self._generate_main_page_html()
        
        return self._create_http_response(html, content_type="text/html")
    
    def _generate_main_page_html(self):
        """Generate main page HTML"""
        relay_state = self.relay_controller.get_relay_state()
        relay_status = self.relay_controller.get_status()
        device_name = self.config.get('system.device_name', 'Pico W Relay')
        
        # Toggle switch checked state
        checked = 'checked' if relay_state else ''
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{device_name} Control</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .container {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .status {{
            margin-bottom: 30px;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
        }}
        
        .status.on {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .status.off {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .switch {{
            position: relative;
            display: inline-block;
            width: 120px;
            height: 68px;
            margin: 20px 0;
        }}
        
        .switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}
        
        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }}
        
        .slider:before {{
            position: absolute;
            content: "";
            height: 52px;
            width: 52px;
            left: 8px;
            bottom: 8px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }}
        
        input:checked + .slider {{
            background-color: #4CAF50;
        }}
        
        input:checked + .slider:before {{
            transform: translateX(52px);
        }}
        
        .info {{
            margin-top: 30px;
            text-align: left;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        
        .info h3 {{
            margin-top: 0;
            color: #333;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .info-item:last-child {{
            border-bottom: none;
        }}
        
        .links {{
            margin-top: 30px;
        }}
        
        .links a {{
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
            padding: 10px 15px;
            border: 1px solid #667eea;
            border-radius: 5px;
            transition: all 0.3s;
        }}
        
        .links a:hover {{
            background-color: #667eea;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{device_name}</h1>
        
        <div class="status {'on' if relay_state else 'off'}">
            Relay Status: {'ON' if relay_state else 'OFF'}
        </div>
        
        <label class="switch">
            <input type="checkbox" onchange="toggleRelay(this)" {checked}>
            <span class="slider"></span>
        </label>
        
        <div class="info">
            <h3>System Information</h3>
            <div class="info-item">
                <span>Current Session:</span>
                <span>{relay_status['current_session_duration']:.1f}s</span>
            </div>
            <div class="info-item">
                <span>Total Runtime:</span>
                <span>{relay_status['total_runtime']:.1f}s</span>
            </div>
            <div class="info-item">
                <span>Total Cycles:</span>
                <span>{relay_status['total_cycles']}</span>
            </div>
            <div class="info-item">
                <span>GPIO Pin:</span>
                <span>{relay_status['pin']}</span>
            </div>
        </div>
        
        <div class="links">
            <a href="/config">Settings</a>
            <a href="/api/status">API</a>
        </div>
    </div>
    
    <script>
        function toggleRelay(element) {{
            const xhr = new XMLHttpRequest();
            const state = element.checked ? 'on' : 'off';
            xhr.open('GET', `/?relay=${{state}}`, true);
            xhr.onreadystatechange = function() {{
                if (xhr.readyState === 4 && xhr.status === 200) {{
                    // Update status display
                    const statusDiv = document.querySelector('.status');
                    if (element.checked) {{
                        statusDiv.textContent = 'Relay Status: ON';
                        statusDiv.className = 'status on';
                    }} else {{
                        statusDiv.textContent = 'Relay Status: OFF';
                        statusDiv.className = 'status off';
                    }}
                }}
            }};
            xhr.send();
        }}
        
        // Auto-refresh system info every 5 seconds
        setInterval(function() {{
            window.location.reload();
        }}, 5000);
    </script>
</body>
</html>"""
        
        return html
    
    def _handle_api_status(self):
        """Handle API status request"""
        status = {
            'relay': self.relay_controller.get_status(),
            'system': {
                'uptime': time.time(),
                'free_memory': gc.mem_free(),
                'request_count': self.request_count
            },
            'timestamp': time.time()
        }
        
        return self._create_json_response(status)
    
    def _handle_api_relay_state(self):
        """Handle relay state API request"""
        state = {
            'state': self.relay_controller.get_relay_state(),
            'timestamp': time.time()
        }
        
        return self._create_json_response(state)
    
    def _handle_api_relay_toggle(self, request):
        """Handle relay toggle API request"""
        success = self.relay_controller.toggle_relay()
        
        response = {
            'success': success,
            'new_state': self.relay_controller.get_relay_state(),
            'timestamp': time.time()
        }
        
        return self._create_json_response(response)
    
    def _handle_api_relay_set(self, request):
        """Handle relay set state API request"""
        try:
            # Parse JSON body
            body = self._extract_request_body(request)
            data = json.loads(body) if body else {}
            
            state = data.get('state', False)
            success = self.relay_controller.set_relay_state(state)
            
            response = {
                'success': success,
                'state': self.relay_controller.get_relay_state(),
                'timestamp': time.time()
            }
            
            return self._create_json_response(response)
        except:
            return self._create_json_response({'error': 'Invalid request'}, status=400)
    
    def _handle_api_system_info(self):
        """Handle system info API request"""
        info = {
            'device_name': self.config.get('system.device_name'),
            'uptime': time.time(),
            'free_memory': gc.mem_free(),
            'request_count': self.request_count,
            'relay_pin': self.config.get('relay.pin'),
            'firmware': 'MicroPython'
        }
        
        return self._create_json_response(info)
    
    def _handle_api_stats(self):
        """Handle statistics API request"""
        stats = self.relay_controller.get_statistics()
        return self._create_json_response(stats)
    
    def _handle_config_page(self):
        """Handle configuration page"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Configuration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>System Configuration</h1>
    <p>Configuration interface coming soon...</p>
    <a href="/">Back to Main</a>
</body>
</html>"""
        
        return self._create_http_response(html, content_type="text/html")
    
    def _serve_css(self):
        """Serve CSS file"""
        css = "/* CSS styles would go here */"
        return self._create_http_response(css, content_type="text/css")
    
    def _serve_javascript(self):
        """Serve JavaScript file"""
        js = "/* JavaScript code would go here */"
        return self._create_http_response(js, content_type="application/javascript")
    
    def _create_http_response(self, content, status=200, content_type="text/html"):
        """Create HTTP response"""
        status_text = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}.get(status, "OK")
        
        response = f"""HTTP/1.1 {status} {status_text}\r
Content-Type: {content_type}\r
Content-Length: {len(content.encode('utf-8'))}\r
Connection: close\r
\r
{content}"""
        
        return response
    
    def _create_json_response(self, data, status=200):
        """Create JSON HTTP response"""
        json_content = json.dumps(data)
        return self._create_http_response(json_content, status, "application/json")
    
    def _create_error_response(self, status, message):
        """Create error HTTP response"""
        html = f"""<!DOCTYPE html>
<html>
<head><title>Error {status}</title></head>
<body>
    <h1>Error {status}</h1>
    <p>{message}</p>
</body>
</html>"""
        
        return self._create_http_response(html, status)
    
    def _extract_request_body(self, request):
        """Extract body from HTTP request"""
        try:
            parts = request.split('\r\n\r\n', 1)
            return parts[1] if len(parts) > 1 else ""
        except:
            return ""
    
    def get_server_stats(self):
        """Get web server statistics"""
        return {
            'running': self.running,
            'port': self.server_config['port'],
            'request_count': self.request_count,
            'last_request_time': self.last_request_time
        }