# Virtual Environment Setup Guide

## Windows (PowerShell)

### Step 1: Create Virtual Environment
```powershell
python -m venv venv
```

### Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```powershell
pip install adafruit-circuitpython-ads1x15 adafruit-blinka
```

### Step 4: Run Your Script
```powershell
python sensor_tests/test_ads_all_channels.py
```

### Step 5: Deactivate (when done)
```powershell
deactivate
```

---

## Raspberry Pi (Linux)

### Step 1: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install adafruit-circuitpython-ads1x15 adafruit-blinka
```

**Note:** On Raspberry Pi, you may also need:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
```

### Step 4: Run Your Script
```bash
python3 sensor_tests/test_ads_all_channels.py
```

### Step 5: Deactivate (when done)
```bash
deactivate
```

---

## Quick Reference

| Action | Windows | Linux/Raspberry Pi |
|--------|---------|-------------------|
| Create | `python -m venv venv` | `python3 -m venv venv` |
| Activate | `.\venv\Scripts\Activate.ps1` | `source venv/bin/activate` |
| Deactivate | `deactivate` | `deactivate` |
| Install packages | `pip install package_name` | `pip install package_name` |

---

## Troubleshooting

### Windows: "Execution Policy" Error
If you see: `cannot be loaded because running scripts is disabled on this system`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "python3: command not found" (Windows)
On Windows, use `python` instead of `python3`

### "venv: command not found"
Make sure you're using Python 3.3+:
- Windows: `python --version`
- Linux: `python3 --version`

If Python 3 is not installed:
- Windows: Download from python.org
- Linux: `sudo apt-get install python3 python3-venv python3-pip`

