"""Govee BLE command builders.

Protocol specification for Govee H6046 RGBIC TV Light Bars.
See docs/SPEC.md for full documentation.
"""

from dataclasses import dataclass
from typing import Tuple


# GATT UUIDs
SERVICE_UUID = "00010203-0405-0607-0809-0a0b0c0d1910"
CONTROL_CHAR_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"
NOTIFY_CHAR_UUID = "00010203-0405-0607-0809-0a0b0c0d2b10"

# Command identifiers
CMD_IDENTIFIER = 0x33
CMD_POWER = 0x01
CMD_BRIGHTNESS = 0x04
CMD_COLOR = 0x05

# Color mode for H6046 (MODE_1501)
COLOR_MODE_1501 = (0x15, 0x01)

# Segment mask for all LEDs on H6046
SEGMENT_ALL = (0xFF, 0xFF)


@dataclass
class RGB:
    """RGB color value."""
    r: int
    g: int
    b: int
    
    def __post_init__(self):
        self.r = max(0, min(255, self.r))
        self.g = max(0, min(255, self.g))
        self.b = max(0, min(255, self.b))
    
    @classmethod
    def from_hex(cls, hex_str: str) -> "RGB":
        """Create RGB from hex string like '#FF0000' or 'FF0000'."""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) != 6:
            raise ValueError(f"Invalid hex color: {hex_str}")
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return cls(r, g, b)
    
    @classmethod
    def from_name(cls, name: str) -> "RGB":
        """Create RGB from color name."""
        colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "purple": (128, 0, 128),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203),
            "warm": (255, 180, 100),
            "cool": (200, 220, 255),
        }
        name_lower = name.lower()
        if name_lower not in colors:
            raise ValueError(f"Unknown color name: {name}. Available: {', '.join(colors.keys())}")
        r, g, b = colors[name_lower]
        return cls(r, g, b)


class GoveeCommands:
    """Builder for Govee BLE command packets."""
    
    @staticmethod
    def _build_packet(cmd: int, payload: bytes) -> bytes:
        """Build a 20-byte command packet with checksum.
        
        Packet structure:
        [0x33] [CMD] [PAYLOAD...] [XOR_CHECKSUM]
          1      1       17            1
        """
        frame = bytes([CMD_IDENTIFIER, cmd]) + payload
        # Pad to 19 bytes
        frame += bytes(19 - len(frame))
        # Calculate XOR checksum
        checksum = 0
        for b in frame:
            checksum ^= b
        return frame + bytes([checksum])
    
    @classmethod
    def power(cls, on: bool) -> bytes:
        """Build power on/off command.
        
        Args:
            on: True to turn on, False to turn off
            
        Returns:
            20-byte command packet
        """
        return cls._build_packet(CMD_POWER, bytes([0x01 if on else 0x00]))
    
    @classmethod
    def brightness(cls, level: int) -> bytes:
        """Build brightness command.
        
        Args:
            level: Brightness level 0-255 (0=off, 255=max)
            
        Returns:
            20-byte command packet
        """
        level = max(0, min(255, level))
        return cls._build_packet(CMD_BRIGHTNESS, bytes([level]))
    
    @classmethod
    def brightness_percent(cls, percent: int) -> bytes:
        """Build brightness command from percentage.
        
        Args:
            percent: Brightness percentage 0-100
            
        Returns:
            20-byte command packet
        """
        level = int(percent * 255 / 100)
        return cls.brightness(level)
    
    @classmethod
    def color(cls, rgb: RGB) -> bytes:
        """Build RGB color command for all segments.
        
        Uses MODE_1501 format for H6046 RGBIC devices.
        
        Args:
            rgb: RGB color value
            
        Returns:
            20-byte command packet
        """
        # MODE_1501: 33 05 15 01 RR GG BB 00 00 00 00 00 FF FF ...
        payload = bytes([
            COLOR_MODE_1501[0], COLOR_MODE_1501[1],  # 0x15, 0x01
            rgb.r, rgb.g, rgb.b,                      # RGB values
            0x00, 0x00, 0x00, 0x00, 0x00,             # Reserved (must be 0)
            SEGMENT_ALL[0], SEGMENT_ALL[1],          # 0xFF, 0xFF = all segments
        ])
        return cls._build_packet(CMD_COLOR, payload)
    
    @classmethod
    def color_hex(cls, hex_str: str) -> bytes:
        """Build color command from hex string.
        
        Args:
            hex_str: Hex color like '#FF0000' or 'FF0000'
            
        Returns:
            20-byte command packet
        """
        return cls.color(RGB.from_hex(hex_str))
    
    @classmethod
    def color_name(cls, name: str) -> bytes:
        """Build color command from color name.
        
        Args:
            name: Color name like 'red', 'blue', 'green'
            
        Returns:
            20-byte command packet
        """
        return cls.color(RGB.from_name(name))
