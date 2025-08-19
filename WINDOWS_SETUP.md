# Windows Setup Guide for IoT Relay System

This guide helps you run the IoT Relay System demonstration and resolve common Windows PowerShell issues.

## 🐍 Python Installation

### Step 1: Install Python

1. **Download Python**
   - Go to [python.org](https://python.org/downloads/)
   - Download Python 3.8 or newer
   - **Important:** Check "Add Python to PATH" during installation

2. **Verify Installation**
   Open Command Prompt (cmd) and run:
   ```cmd
   python --version
   ```
   You should see something like: `Python 3.11.5`

### Step 2: Alternative - Install from Microsoft Store

1. Open Microsoft Store
2. Search for "Python"
3. Install "Python 3.11" (or latest version)
4. This automatically adds Python to PATH

## 🚀 Running the Demonstration

### Method 1: Using Command Prompt (Recommended)

1. **Open Command Prompt**
   - Press `Win + R`
   - Type `cmd` and press Enter

2. **Navigate to Project Folder**
   ```cmd
   cd "C:\Users\HAMZU\OneDrive - iTouch Solutions\Desktop\pico-w-iot-relay-controller"
   ```

3. **Run the Demo**
   ```cmd
   python run_demo.py
   ```

### Method 2: Using PowerShell (If Python is in PATH)

1. **Open PowerShell**
   - Press `Win + X`
   - Select "Windows PowerShell"

2. **Navigate to Project Folder**
   ```powershell
   cd "C:\Users\HAMZU\OneDrive - iTouch Solutions\Desktop\pico-w-iot-relay-controller"
   ```

3. **Run the Demo**
   ```powershell
   python run_demo.py
   ```

### Method 3: Using File Explorer (Easiest)

1. **Navigate to Project Folder**
   - Open File Explorer
   - Go to: `C:\Users\HAMZU\OneDrive - iTouch Solutions\Desktop\pico-w-iot-relay-controller`

2. **Right-click in Empty Space**
   - Select "Open in Terminal" (Windows 11)
   - Or "Open PowerShell window here" (Windows 10)

3. **Run the Demo**
   ```cmd
   python run_demo.py
   ```

## 🔧 Troubleshooting Common Issues

### Issue 1: "python is not recognized"

**Problem:** PowerShell says `python : The term 'python' is not recognized...`

**Solutions:**

1. **Try `py` instead of `python`:**
   ```cmd
   py run_demo.py
   ```

2. **Use full Python path:**
   ```cmd
   C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe run_demo.py
   ```

3. **Add Python to PATH:**
   - Search "Environment Variables" in Start Menu
   - Click "Environment Variables"
   - Under "System Variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311`
   - Add: `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts`
   - Click "OK" and restart Command Prompt

### Issue 2: "Execution Policy" Error in PowerShell

**Problem:** PowerShell blocks script execution

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Module Import Errors

**Problem:** `ModuleNotFoundError` when running the demo

**Solution:**
Make sure you're in the correct directory:
```cmd
dir
```
You should see files like `main.py`, `config.py`, `run_demo.py`

### Issue 4: Permission Denied

**Problem:** Access denied errors

**Solutions:**
1. Run Command Prompt as Administrator
2. Check file permissions
3. Move project to a simpler path like `C:\IoT-Relay`

## 📋 Expected Demo Output

When you run `python run_demo.py`, you should see:

```
======================================================================
🔌 IoT Relay System - Professional Demonstration
   WiFi Relay Controller for Raspberry Pi Pico W
======================================================================
Author: M Hamza Ummer
Version: 2.0.0
License: MIT License
======================================================================

📋 CONFIGURATION TEST
------------------------------
✅ Configuration loaded successfully
   Device Name: Pico-W-Relay
   Authentication: ✅ Enabled
   Relay Pin: GPIO 18
   Rate Limit: 60 requests/minute

🔐 SECURITY FEATURES TEST
-----------------------------------
✅ Security manager initialized

   Input Validation Tests:
   ✅ relay_command='on' -> Valid
   ✅ relay_command='malicious_input' -> Invalid
   ✅ pin_number='18' -> Valid
   ✅ pin_number='999' -> Invalid

   Authentication Tests:
   ✅ Valid credentials test
   ✅ Invalid credentials test

   Session Management Tests:
   ✅ Session created: 1234567890abcdef...
   ✅ Session validation test

   CSRF Protection Tests:
   ✅ CSRF token generated: abcdef1234567890...
   ✅ CSRF validation test

🔧 SYSTEM COMPONENTS TEST
-----------------------------------
✅ Logger system working
✅ Configuration access working
✅ Security manager working

======================================================================
📊 DEMONSTRATION RESULTS
======================================================================
Configuration Test:     ✅ PASSED
Security Features Test: ✅ PASSED
System Components Test: ✅ PASSED

----------------------------------------------------------------------
🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!

✅ The IoT Relay System is working correctly and ready to use.
✅ All security features are active and functioning.
✅ Configuration is loaded and valid.
```

## 🎯 Quick Test Commands

Try these commands to verify your setup:

```cmd
# Check Python installation
python --version

# Check if you're in the right directory
dir

# List Python files
dir *.py

# Run the demonstration
python run_demo.py
```

## 📞 Still Having Issues?

If you're still having problems:

1. **Check Python Installation:**
   ```cmd
   where python
   ```

2. **Try Python Launcher:**
   ```cmd
   py -3 run_demo.py
   ```

3. **Use IDLE (Python's built-in IDE):**
   - Search "IDLE" in Start Menu
   - Open the file `run_demo.py`
   - Press F5 to run

4. **Install Python from Microsoft Store** (easiest option)
   - This handles PATH automatically
   - Works with both `python` and `py` commands

## ✅ Success Indicators

You'll know everything is working when:
- ✅ `python --version` shows a version number
- ✅ `python run_demo.py` runs without errors
- ✅ All tests in the demo show "✅ PASSED"
- ✅ You see "🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!"

Once you see these success indicators, your system is ready to deploy to the Raspberry Pi Pico W!
