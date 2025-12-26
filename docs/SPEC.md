# Govee H6046 BLE Protocol Specification

> **Status**: Research in progress  
> **Last Updated**: 2025-12-26  
> **Device**: Govee H6046 RGBIC TV Light Bars  
> **MAC Address**: `C5:37:32:32:2C:43` (device-specific)

---

## Verified Facts ✓

### Bluetooth Connection
- **Device Name**: `Govee_H6046_2C43` (pattern: `Govee_H6046_XXXX`)
- **Connection Type**: Bluetooth Low Energy (BLE)
- **Service UUID**: `00010203-0405-0607-0809-0a0b0c0d1910`
- **Control Characteristic UUID**: `00010203-0405-0607-0809-0a0b0c0d2b11`
  - Properties: `read, write-without-response, write, notify`
- **Notification Characteristic UUID**: `00010203-0405-0607-0809-0a0b0c0d2b10`
  - Properties: `read, notify`

### Packet Structure
All command packets are **20 bytes**:
```
[IDENTIFIER] [CMD] [PAYLOAD...] [CHECKSUM]
   1 byte    1 byte  17 bytes    1 byte
```
- **Checksum**: XOR of all preceding 19 bytes
- Unused payload bytes are zero-padded

### Working Commands

#### Power On/Off ✓ VERIFIED
```
Power ON:  33 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 33
Power OFF: 33 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 32
```
- Identifier: `0x33`
- Command: `0x01`
- Payload[0]: `0x01` = ON, `0x00` = OFF

#### Set RGB Color ✓ VERIFIED (MODE_1501 with FF FF)
```
Format: 33 05 15 01 RR GG BB 00 00 00 00 00 FF FF 00 00 00 00 00 [XOR]
```
- Identifier: `0x33`
- Command: `0x05`
- Mode: `0x15 0x01` (RGBIC segment mode)
- RR, GG, BB: RGB values (0x00-0xFF each)
- Bytes 7-11: Must be `00 00 00 00 00` (non-zero values have side effects)
- Bytes 12-13: Segment mask `FF FF` = ALL segments
- **Example PURPLE**: `33051501ff00ff0000000000ffff000000000022`

**Segment Byte Side Effects (bytes 7-11)**:
- Byte 7 = `0xFF`: Turns light OFF
- Byte 9 = `0xFF`: May turn light ON
- All bytes `0xFF`: Sets color to WHITE (overrides RGB)

#### Scene/Effect Presets ✓ VERIFIED (partial)
```
Format: 33 05 04 [SCENE_ID] 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 [XOR]
```
- Command `0x05`, Mode `0x04` = Scene mode
- Scene ID `0x04` = Movie (animated effect)
- Other scene IDs likely work (see H6127/H6199 docs for full list)

### Commands That Had Partial Effect
| Format | Notes |
|--------|-------|
| `33 05 02 RR GG BB` (MODE_2) | Some effect observed |
| `33 05 0D RR GG BB` (MODE_D) | Some effect observed |

---

## Unverified / Needs Testing

### Brightness Control ✓ VERIFIED
```
Format: 33 04 [BRIGHTNESS] 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 [XOR]
```
- BRIGHTNESS: 0x00-0xFF (0-255 scale)
- 0xFF = 100%, 0x80 = 50%, 0x40 = 25%, etc.
- **Example 50%**: `33048000000000000000000000000000000000b7`

### Segment Addressing
- The H6046 has 2 light bars (TV left + right sides)
- The `FF 74` segment mask works, but individual segment control is untested
- Segment bitmask format may differ from H6102/H6199

### Keep-Alive Packets
```
AA 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 AB
```
- Govee app sends this every 2 seconds
- **NOT YET TESTED** - may be needed for persistent connections

### Alternative Characteristics
Second vendor-specific service exists but is untested:
- Service: `02f00000-0000-0000-0000-00000000fe00`
- Write char: `02f00000-0000-0000-0000-00000000ff01`
- Read char: `02f00000-0000-0000-0000-00000000ff00`, `ff02`, `ff03`

### Query Device State
```
Likely format: 81 8a 8b 00... [XOR] or AA 05 01 00... [XOR]
```
- Would return current power state, color, brightness
- **NOT YET TESTED**

---

## Command Formats That Did NOT Work

| Format | Result |
|--------|--------|
| `33 05 02 RR GG BB 00 FF AE 54` | No effect |
| `33 05 0b RR GG BB FF FF` | No effect |
| `33 05 15 RR GG BB` (without 0x01) | No effect |
| `33 05 15 01 ... FF 7F` | Only partial segments |
| `33 05 15 01 ... FF FF` | No effect |

---

## Development Environment

### Dependencies
- **Python 3.12+** with `bleak` BLE library
- **BlueZ** (Linux Bluetooth stack): `bluez`, `bluez-utils`
- Virtual environment: `/workspace/cli/govee/.venv`

### Quick Test Commands
```bash
# Activate environment
cd /workspace/cli/govee && source .venv/bin/activate

# Run test script
python govee_test.py
```

### Key Files
- Test script: `/workspace/cli/govee/govee_test.py`
- Reference repos cloned to: `/workspace/cli/govee/tmp/`
  - `Bash-Govee/` - Simple bash + gatttool
  - `govee_btled/` - Python + pygatt
  - `govee-ble/` - Home Assistant integration (sensors only)
  - `Govee-Reverse-Engineering/` - Protocol documentation
  - `govee-py/` - Python + bleak (comprehensive)

---

## References
- https://github.com/egold555/Govee-Reverse-Engineering
- https://github.com/wez/govee-py
- https://github.com/chvolkmann/govee_btled
- H6102 uses MODE_1501 (same as H6046)
- H6127/H6199 protocol docs most comprehensive
