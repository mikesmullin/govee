# govee

CLI tool to control Govee H6046 RGBIC TV Light Bars via Bluetooth Low Energy.

## Installation

### Global install (recommended)

```bash
uv tool install --editable .
```

This installs `govee` globally while keeping it editable, so config.yml changes are picked up immediately.

### Local development

```bash
cd /path/to/govee
uv pip install -e .
```

## Quick Start

### 1. Find your device

```bash
govee scan
```

This will output something like:
```
Found 1 device(s):

  C5:37:32:32:2C:43  Govee_H6046_2C43
```

### 2. Configure your device

Edit `config.yml` in the project directory:

```yaml
device: "C5:37:32:32:2C:43"
```

Or set an environment variable:

```bash
export GOVEE_DEVICE="C5:37:32:32:2C:43"
```

### 3. Control your light

```bash
# Power on/off
govee on
govee off

# Set color by name
govee color red
govee color blue
govee color warm

# Set color by hex code
govee color "#FF5500"
govee color 00FF00

# Set color by RGB values
govee rgb 255 128 0

# Set brightness (0-100%)
govee brightness 50
govee brightness 100
```

### Using -m flag to override MAC:

```bash
govee -m C5:37:32:32:2C:43 on
govee -m C5:37:32:32:2C:43 color purple
govee -m C5:37:32:32:2C:43 brightness 75
```

## Device Configuration Priority

1. `-m` / `--mac` command line flag
2. `GOVEE_DEVICE` environment variable
3. `device` field in `config.yml`

## Available Colors

- `red`, `green`, `blue`, `white`
- `yellow`, `cyan`, `magenta`, `purple`
- `orange`, `pink`
- `warm` (warm white), `cool` (cool white)

Or use any hex color code: `#RRGGBB` or `RRGGBB`

## Python API

```python
import asyncio
from govee import GoveeDevice

async def main():
    async with GoveeDevice("C5:37:32:32:2C:43") as device:
        await device.power_on()
        await device.set_color("red")
        await device.set_brightness(50)
        await device.set_rgb(255, 128, 0)
        await device.power_off()

asyncio.run(main())
```

## Supported Devices

- Govee H6046 RGBIC TV Light Bars (verified)
- Other Govee RGBIC devices may work (untested)

## Requirements

- Python 3.10+
- Linux with BlueZ (Arch, Ubuntu, Debian, etc.)
- Bluetooth adapter

## Troubleshooting

### Device not found during scan
- Ensure Bluetooth is enabled: `sudo systemctl start bluetooth`
- Make sure the Govee light is powered on
- Try moving closer to the device

### Connection fails
- Another device may be connected (phone app)
- Try power cycling the Govee light
- Check `bluetoothctl` to see if device is visible

### Commands not working
- Ensure you're using the correct MAC address
- Try power cycling the device
- Some commands may need the light to be ON first

## License

MIT
