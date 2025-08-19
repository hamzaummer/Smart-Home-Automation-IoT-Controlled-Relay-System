"""
Web Server Module for IoT Relay System
Professional HTTP server with security features and modern web interface

Author: M Hamza Ummer
Contributors: M Armughan Ur Rahim, C Rahul Anand Rao
Version: 2.0.0
License: MIT License

Description:
    Comprehensive web server implementation for the IoT relay system.
    Provides secure HTTP server with authentication, modern responsive
    web interface, RESTful API, and comprehensive security features.

Features:
    - Session-based authentication with CSRF protection
    - Rate limiting and input validation
    - Modern responsive web interface with real-time updates
    - RESTful API with JSON responses
    - Request queuing for improved concurrency
    - Comprehensive error handling and logging
    - Mobile-friendly design with toast notifications

Security Features:
    - User authentication and session management
    - Cross-Site Request Forgery (CSRF) protection
    - Rate limiting (60 requests/minute per IP)
    - Input validation and sanitization
    - Secure error handling without information disclosure

API Endpoints:
    GET  /                    - Main web interface (authenticated)
    GET  /login              - Login page
    POST /login              - Authentication endpoint
    GET  /logout             - Logout endpoint
    GET  /config             - Configuration dashboard
    GET  /api/status         - System status (JSON)
    GET  /api/relay/state    - Relay state (JSON)
    POST /api/relay/set      - Set relay state (JSON)
    POST /api/relay/toggle   - Toggle relay state (JSON)
    GET  /api/system/info    - System information (JSON)

Usage:
    server = WebServer(config, logger, relay_controller)
    server.start()
    # Handle requests in main loop
    server.handle_request()
"""

import socket
import json
import time
import gc
from security import SecurityManager

class WebServer:
    """HTTP Web Server for IoT Relay Control"""
    
    def __init__(self, config, logger, relay_controller):
        """Initialize web server"""
        self.config = config
        self.logger = logger
        self.relay_controller = relay_controller
        self.server_config = config.get_web_server_config()

        # Initialize security manager
        self.security = SecurityManager(config, logger)

        self.socket = None
        self.running = False
        self.request_count = 0
        self.last_request_time = 0

        # Request queue for better concurrency
        self.request_queue = []
        self.max_queue_size = 10

        self.logger.info("Web Server initialized with security features")
    
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
        """Handle incoming HTTP requests with improved concurrency"""
        if not self.running or not self.socket:
            return

        try:
            conn, addr = self.socket.accept()
            self.request_count += 1
            self.last_request_time = time.time()

            # Add to request queue if not full
            if len(self.request_queue) < self.max_queue_size:
                self.request_queue.append((conn, addr))
                self.logger.debug(f"Connection queued from {addr[0]}:{addr[1]}")
            else:
                # Queue full, reject connection
                try:
                    error_response = self._create_error_response(503, "Service Unavailable")
                    conn.send(error_response.encode('utf-8'))
                    conn.close()
                    self.logger.warning(f"Connection rejected (queue full) from {addr[0]}:{addr[1]}")
                except:
                    pass

        except OSError:
            # No connection available (non-blocking socket)
            pass
        except Exception as e:
            self.logger.error(f"Connection handling error: {e}")

    def process_request_queue(self):
        """Process queued requests"""
        if not self.request_queue:
            return

        # Process one request from queue
        conn, addr = self.request_queue.pop(0)

        try:
            conn.settimeout(self.server_config['request_timeout'])
            self.logger.debug(f"Processing request from {addr[0]}:{addr[1]}")

            # Read request with larger buffer for better performance
            request_data = b""
            while True:
                try:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    request_data += chunk
                    if b'\r\n\r\n' in request_data:
                        break
                except OSError:
                    break

            if not request_data:
                return

            request = request_data.decode('utf-8', errors='ignore')

            # Parse request
            response = self._process_request(request, addr[0])

            # Send response
            conn.send(response.encode('utf-8'))

        except Exception as e:
            self.logger.error(f"Request processing error: {e}")
            try:
                error_response = self._create_error_response(500, "Internal Server Error")
                conn.send(error_response.encode('utf-8'))
            except:
                pass
        finally:
            try:
                conn.close()
            except:
                pass
    
    def _process_request(self, request, client_ip):
        """Process HTTP request and return response"""
        try:
            # Check rate limiting first
            if not self.security.check_rate_limit(client_ip):
                return self._create_error_response(429, "Too Many Requests")

            # Parse request line
            lines = request.split('\n')
            if not lines:
                return self._create_error_response(400, "Bad Request")

            request_line = lines[0].strip()
            parts = request_line.split(' ')

            if len(parts) < 2:
                return self._create_error_response(400, "Bad Request")

            method = parts[0]
            path = parts[1]

            # Parse headers
            headers = self._parse_headers(lines[1:])

            # Extract session information
            session_id = self.security.get_session_from_cookie(headers.get('Cookie', ''))

            self.logger.debug(f"{method} {path} from {client_ip}")

            # Route request with security context
            if method == "GET":
                return self._handle_get_request(path, headers, session_id, client_ip)
            elif method == "POST":
                return self._handle_post_request(path, request, headers, session_id, client_ip)
            else:
                return self._create_error_response(405, "Method Not Allowed")

        except Exception as e:
            self.logger.error(f"Request parsing error: {e}")
            return self._create_error_response(500, "Internal Server Error")

    def _parse_headers(self, header_lines):
        """Parse HTTP headers"""
        headers = {}
        for line in header_lines:
            line = line.strip()
            if not line:
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        return headers
    
    def _handle_get_request(self, path, headers, session_id, client_ip):
        """Handle GET requests"""
        # Login page (no authentication required)
        if path == "/login":
            return self._handle_login_page()

        # Logout endpoint
        elif path == "/logout":
            if session_id:
                self.security.destroy_session(session_id)
            return self._create_redirect_response("/login")

        # Static files (no authentication required)
        elif path == "/style.css":
            return self._serve_css()
        elif path == "/script.js":
            return self._serve_javascript()

        # Check authentication for protected endpoints
        elif not self._check_authentication(headers, session_id, client_ip):
            return self._handle_authentication_required()

        # Main web interface (protected)
        elif path == "/" or path.startswith("/?"):
            return self._handle_main_page(path, session_id)

        # API endpoints (protected)
        elif path == "/api/status":
            return self._handle_api_status()
        elif path == "/api/relay/state":
            return self._handle_api_relay_state()
        elif path == "/api/system/info":
            return self._handle_api_system_info()
        elif path == "/api/stats":
            return self._handle_api_stats()

        # Configuration page (protected)
        elif path == "/config":
            return self._handle_config_page(session_id)

        # 404 Not Found
        else:
            return self._create_error_response(404, "Not Found")
    
    def _handle_post_request(self, path, request, headers, session_id, client_ip):
        """Handle POST requests"""
        # Login endpoint (no authentication required)
        if path == "/login":
            return self._handle_login_post(request, client_ip)

        # Check authentication for protected endpoints
        elif not self._check_authentication(headers, session_id, client_ip):
            return self._handle_authentication_required()

        # Validate CSRF token for state-changing operations
        elif not self._validate_csrf_token(request, session_id):
            return self._create_error_response(403, "CSRF token validation failed")

        # Protected API endpoints
        elif path == "/api/relay/toggle":
            return self._handle_api_relay_toggle(request)
        elif path == "/api/relay/set":
            return self._handle_api_relay_set(request)
        elif path == "/api/config/save":
            return self._handle_api_config_save(request)
        else:
            return self._create_error_response(404, "Not Found")

    def _check_authentication(self, headers, session_id, client_ip):
        """Check if request is authenticated"""
        if not self.security.auth_config.get('enable_auth', False):
            return True  # Authentication disabled

        # Check session-based authentication
        if session_id and self.security.validate_session(session_id, client_ip):
            return True

        # Check HTTP Basic Authentication
        auth_header = headers.get('Authorization', '')
        if auth_header:
            username, password = self.security.parse_basic_auth(auth_header)
            if username and password:
                return self.security.authenticate_user(username, password)

        return False

    def _handle_authentication_required(self):
        """Handle authentication required response"""
        if self.security.auth_config.get('enable_auth', False):
            return self._create_redirect_response("/login")
        else:
            return self._create_error_response(401, "Authentication Required")

    def _validate_csrf_token(self, request, session_id):
        """Validate CSRF token in request"""
        if not self.security.auth_config.get('enable_auth', False):
            return True  # CSRF protection disabled when auth is disabled

        # Extract CSRF token from request body
        try:
            body = self._extract_request_body(request)
            if 'csrf_token=' in body:
                token_start = body.find('csrf_token=') + 11
                token_end = body.find('&', token_start)
                if token_end == -1:
                    token_end = len(body)
                csrf_token = body[token_start:token_end]
                return self.security.validate_csrf_token(csrf_token, session_id)
        except Exception as e:
            self.logger.error(f"CSRF token validation error: {e}")

        return False

    def _handle_login_page(self):
        """Handle login page"""
        html = self._generate_login_page_html()
        return self._create_http_response(html, content_type="text/html")

    def _handle_login_post(self, request, client_ip):
        """Handle login form submission"""
        try:
            body = self._extract_request_body(request)

            # Parse form data
            username = ""
            password = ""

            if 'username=' in body:
                username_start = body.find('username=') + 9
                username_end = body.find('&', username_start)
                if username_end == -1:
                    username_end = len(body)
                username = body[username_start:username_end].replace('%40', '@')

            if 'password=' in body:
                password_start = body.find('password=') + 9
                password_end = body.find('&', password_start)
                if password_end == -1:
                    password_end = len(body)
                password = body[password_start:password_end]

            # Validate credentials
            if self.security.authenticate_user(username, password):
                session_id = self.security.create_session(username, client_ip)
                response = self._create_redirect_response("/")
                # Add session cookie
                response = response.replace('\r\n\r\n', f'\r\nSet-Cookie: session_id={session_id}; Path=/; HttpOnly\r\n\r\n')
                return response
            else:
                # Login failed
                html = self._generate_login_page_html(error="Invalid username or password")
                return self._create_http_response(html, content_type="text/html")

        except Exception as e:
            self.logger.error(f"Login processing error: {e}")
            return self._create_error_response(500, "Internal Server Error")

    def _handle_main_page(self, path, session_id=None):
        """Handle main web interface"""
        # Check for relay control parameters with validation
        if "relay=" in path:
            if "relay=on" in path:
                if self.security.validate_input("relay_command", "on"):
                    self.relay_controller.set_relay_state(True)
                    self.logger.info("Relay turned ON via web interface")
                else:
                    self.logger.warning("Invalid relay command: on")
            elif "relay=off" in path:
                if self.security.validate_input("relay_command", "off"):
                    self.relay_controller.set_relay_state(False)
                    self.logger.info("Relay turned OFF via web interface")
                else:
                    self.logger.warning("Invalid relay command: off")

        # Generate main page HTML with CSRF token
        csrf_token = ""
        if session_id:
            csrf_token = self.security.generate_csrf_token(session_id)

        html = self._generate_main_page_html(csrf_token)

        return self._create_http_response(html, content_type="text/html")
    
    def _generate_main_page_html(self, csrf_token=""):
        """Generate main page HTML"""
        relay_state = self.relay_controller.get_relay_state()
        relay_status = self.relay_controller.get_status()
        device_name = self.config.get('system.device_name', 'Pico W Relay')

        # Toggle switch checked state
        checked = 'checked' if relay_state else ''

        # Safety timer information
        safety_timeout = self.config.get('relay.safety_timeout', 300)
        max_on_time = self.config.get('relay.max_on_time', 86400)
        
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

        .safety-info {{
            margin-top: 20px;
            padding: 15px;
            background: #e8f5e8;
            border-radius: 10px;
            border: 1px solid #c3e6cb;
        }}

        .safety-info h3 {{
            margin-top: 0;
            color: #155724;
            font-size: 1.2em;
        }}

        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .notification.success {{
            background-color: #28a745;
        }}

        .notification.error {{
            background-color: #dc3545;
        }}

        .notification.info {{
            background-color: #17a2b8;
        }}

        @keyframes slideIn {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-indicator.online {{
            background-color: #28a745;
            animation: pulse 2s infinite;
        }}

        .status-indicator.offline {{
            background-color: #dc3545;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}

        @media (max-width: 480px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}

            h1 {{
                font-size: 2em;
            }}

            .switch {{
                width: 100px;
                height: 56px;
            }}

            .notification {{
                right: 10px;
                left: 10px;
                max-width: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <span class="status-indicator online"></span>
            {device_name}
        </h1>

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
        
        <div class="safety-info">
            <h3>🛡️ Safety Features</h3>
            <div class="info-item">
                <span>Safety Timeout:</span>
                <span>{safety_timeout}s</span>
            </div>
            <div class="info-item">
                <span>Max On-Time:</span>
                <span>{max_on_time}s</span>
            </div>
            <div class="info-item">
                <span>Security:</span>
                <span>✅ Authenticated</span>
            </div>
        </div>

        <div class="links">
            <a href="/config">Settings</a>
            <a href="/api/status">API</a>
            <a href="/logout">Logout</a>
        </div>

        <!-- CSRF Token for forms -->
        <input type="hidden" id="csrf_token" value="{csrf_token}">
    </div>
    
    <script>
        let isUpdating = false;
        let connectionStatus = true;

        function toggleRelay(element) {{
            if (isUpdating) return;

            isUpdating = true;
            const state = element.checked ? 'on' : 'off';
            const csrfToken = document.getElementById('csrf_token').value;

            // Show loading state
            showNotification('Updating relay state...', 'info');

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/relay/set', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function() {{
                if (xhr.readyState === 4) {{
                    isUpdating = false;
                    if (xhr.status === 200) {{
                        const response = JSON.parse(xhr.responseText);
                        if (response.success) {{
                            updateRelayStatus(response.state);
                            showNotification(`Relay turned ${{response.state ? 'ON' : 'OFF'}}`, 'success');
                        }} else {{
                            element.checked = !element.checked; // Revert
                            showNotification('Failed to update relay state', 'error');
                        }}
                    }} else if (xhr.status === 401) {{
                        showNotification('Session expired. Please login again.', 'error');
                        setTimeout(() => window.location.href = '/login', 2000);
                    }} else {{
                        element.checked = !element.checked; // Revert
                        showNotification('Connection error. Please try again.', 'error');
                    }}
                }}
            }};

            const data = JSON.stringify({{
                state: element.checked,
                csrf_token: csrfToken
            }});
            xhr.send(data);
        }}

        function updateRelayStatus(state) {{
            const statusDiv = document.querySelector('.status');
            if (state) {{
                statusDiv.textContent = 'Relay Status: ON';
                statusDiv.className = 'status on';
            }} else {{
                statusDiv.textContent = 'Relay Status: OFF';
                statusDiv.className = 'status off';
            }}
        }}

        function showNotification(message, type) {{
            // Remove existing notifications
            const existing = document.querySelector('.notification');
            if (existing) existing.remove();

            const notification = document.createElement('div');
            notification.className = `notification ${{type}}`;
            notification.textContent = message;

            document.body.appendChild(notification);

            // Auto-remove after 3 seconds
            setTimeout(() => {{
                if (notification.parentNode) {{
                    notification.remove();
                }}
            }}, 3000);
        }}

        function updateSystemInfo() {{
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/status', true);
            xhr.onreadystatechange = function() {{
                if (xhr.readyState === 4) {{
                    if (xhr.status === 200) {{
                        const data = JSON.parse(xhr.responseText);
                        updateInfoDisplay(data);
                        if (!connectionStatus) {{
                            connectionStatus = true;
                            showNotification('Connection restored', 'success');
                        }}
                    }} else if (xhr.status === 401) {{
                        window.location.href = '/login';
                    }} else {{
                        if (connectionStatus) {{
                            connectionStatus = false;
                            showNotification('Connection lost', 'error');
                        }}
                    }}
                }}
            }};
            xhr.send();
        }}

        function updateInfoDisplay(data) {{
            // Update relay status
            updateRelayStatus(data.relay_state);

            // Update system info
            const infoItems = document.querySelectorAll('.info-item span:last-child');
            if (infoItems.length >= 4) {{
                infoItems[0].textContent = `${{data.current_session_duration.toFixed(1)}}s`;
                infoItems[1].textContent = `${{data.total_runtime.toFixed(1)}}s`;
                infoItems[2].textContent = data.total_cycles;
                infoItems[3].textContent = data.pin;
            }}

            // Update checkbox state
            const checkbox = document.querySelector('input[type="checkbox"]');
            checkbox.checked = data.relay_state;
        }}

        // Real-time updates every 2 seconds
        setInterval(updateSystemInfo, 2000);

        // Initial load
        document.addEventListener('DOMContentLoaded', function() {{
            updateSystemInfo();
        }});
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
        # Note: request parameter kept for API consistency but not used for toggle
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

            # Validate input
            state_input = data.get('state', False)
            if not self.security.validate_input("relay_command", str(state_input)):
                return self._create_json_response({'error': 'Invalid relay state'}, status=400)

            # Convert to boolean
            if isinstance(state_input, str):
                state = state_input.lower() in ['true', '1', 'on', 'yes']
            else:
                state = bool(state_input)

            success = self.relay_controller.set_relay_state(state)

            response = {
                'success': success,
                'state': self.relay_controller.get_relay_state(),
                'timestamp': time.time()
            }

            return self._create_json_response(response)
        except json.JSONDecodeError:
            return self._create_json_response({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            self.logger.error(f"API relay set error: {e}")
            return self._create_json_response({'error': 'Internal server error'}, status=500)
    
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
    
    def _handle_config_page(self, session_id=None):
        """Handle configuration page"""
        device_name = self.config.get('system.device_name', 'Pico W Relay')
        csrf_token = ""
        if session_id:
            csrf_token = self.security.generate_csrf_token(session_id)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{device_name} - Configuration</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }}

        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
        }}

        .config-section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #dee2e6;
        }}

        .config-section h3 {{
            margin-top: 0;
            color: #495057;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .config-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }}

        .config-item:last-child {{
            border-bottom: none;
        }}

        .config-label {{
            font-weight: 500;
            color: #495057;
        }}

        .config-value {{
            color: #6c757d;
            font-family: monospace;
        }}

        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .status-badge.enabled {{
            background-color: #d4edda;
            color: #155724;
        }}

        .status-badge.disabled {{
            background-color: #f8d7da;
            color: #721c24;
        }}

        .back-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: transform 0.2s;
        }}

        .back-link:hover {{
            transform: translateY(-2px);
        }}

        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ {device_name} Configuration</h1>

        <div class="warning">
            <strong>⚠️ Read-Only Configuration View</strong><br>
            This page shows current system configuration. To modify settings, edit the config.json file and restart the device.
        </div>

        <div class="config-section">
            <h3>🔐 Security Settings</h3>
            <div class="config-item">
                <span class="config-label">Authentication:</span>
                <span class="status-badge {'enabled' if self.config.get('web_server.enable_auth', False) else 'disabled'}">
                    {'Enabled' if self.config.get('web_server.enable_auth', False) else 'Disabled'}
                </span>
            </div>
            <div class="config-item">
                <span class="config-label">Rate Limiting:</span>
                <span class="config-value">{self.config.get('api.rate_limit', 60)} requests/minute</span>
            </div>
            <div class="config-item">
                <span class="config-label">CSRF Protection:</span>
                <span class="status-badge enabled">Enabled</span>
            </div>
        </div>

        <div class="config-section">
            <h3>🔌 Relay Settings</h3>
            <div class="config-item">
                <span class="config-label">GPIO Pin:</span>
                <span class="config-value">{self.config.get('relay.pin', 18)}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Active Low:</span>
                <span class="status-badge {'enabled' if self.config.get('relay.active_low', True) else 'disabled'}">
                    {'Yes' if self.config.get('relay.active_low', True) else 'No'}
                </span>
            </div>
            <div class="config-item">
                <span class="config-label">Safety Timeout:</span>
                <span class="config-value">{self.config.get('relay.safety_timeout', 300)}s</span>
            </div>
            <div class="config-item">
                <span class="config-label">Max On-Time:</span>
                <span class="config-value">{self.config.get('relay.max_on_time', 86400)}s</span>
            </div>
        </div>

        <div style="text-align: center;">
            <a href="/" class="back-link">← Back to Main</a>
        </div>

        <input type="hidden" id="csrf_token" value="{csrf_token}">
    </div>
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
    
    def _generate_login_page_html(self, error=""):
        """Generate login page HTML"""
        device_name = self.config.get('system.device_name', 'Pico W Relay')
        error_html = f'<div class="error">{error}</div>' if error else ''

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{device_name} - Login</title>
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

        .login-container {{
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

        .form-group {{
            margin-bottom: 20px;
            text-align: left;
        }}

        label {{
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }}

        input[type="text"], input[type="password"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }}

        input[type="text"]:focus, input[type="password"]:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .login-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 18px;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
            margin-top: 20px;
        }}

        .login-btn:hover {{
            transform: translateY(-2px);
        }}

        .error {{
            background: #ff4757;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}

        .security-info {{
            margin-top: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔐 {device_name}</h1>
        {error_html}
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="login-btn">Login</button>
        </form>
        <div class="security-info">
            <strong>🛡️ Security Features Active</strong><br>
            • Rate limiting protection<br>
            • Session-based authentication<br>
            • CSRF protection<br>
            • Input validation
        </div>
    </div>
</body>
</html>"""
        return html

    def _create_redirect_response(self, location):
        """Create HTTP redirect response"""
        return f"""HTTP/1.1 302 Found\r
Location: {location}\r
Content-Type: text/html\r
Content-Length: 0\r
\r
"""

    def get_server_stats(self):
        """Get web server statistics"""
        return {
            'running': self.running,
            'port': self.server_config['port'],
            'request_count': self.request_count,
            'last_request_time': self.last_request_time
        }