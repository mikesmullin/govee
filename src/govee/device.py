"""Govee BLE device connection and control."""

import asyncio
from typing import Optional, List
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

from .commands import GoveeCommands, RGB, CONTROL_CHAR_UUID, SERVICE_UUID


class GoveeDevice:
    """Represents a Govee LED device accessible via Bluetooth LE.
    
    Example:
        async with GoveeDevice("C5:37:32:32:2C:43") as device:
            await device.power_on()
            await device.set_color("red")
            await device.set_brightness(50)
    """
    
    def __init__(self, mac_address: str):
        """Initialize with device MAC address.
        
        Args:
            mac_address: Bluetooth MAC address (e.g., "C5:37:32:32:2C:43")
        """
        self.mac_address = mac_address.upper()
        self._client: Optional[BleakClient] = None
    
    async def __aenter__(self) -> "GoveeDevice":
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self._client is not None and self._client.is_connected
    
    async def connect(self, timeout: float = 10.0) -> None:
        """Connect to the device.
        
        Args:
            timeout: Connection timeout in seconds
        """
        if self.is_connected:
            return
        self._client = BleakClient(self.mac_address)
        await self._client.connect(timeout=timeout)
    
    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client:
            await self._client.disconnect()
            self._client = None
    
    async def _send(self, command: bytes) -> None:
        """Send a command to the device.
        
        Args:
            command: 20-byte command packet
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to device")
        await self._client.write_gatt_char(CONTROL_CHAR_UUID, command)
    
    async def power_on(self) -> None:
        """Turn the light on."""
        await self._send(GoveeCommands.power(True))
    
    async def power_off(self) -> None:
        """Turn the light off."""
        await self._send(GoveeCommands.power(False))
    
    async def set_brightness(self, percent: int) -> None:
        """Set brightness level.
        
        Args:
            percent: Brightness percentage 0-100
        """
        await self._send(GoveeCommands.brightness_percent(percent))
    
    async def set_color(self, color: str) -> None:
        """Set light color.
        
        Args:
            color: Color name (e.g., 'red') or hex code (e.g., '#FF0000')
        """
        if color.startswith('#') or (len(color) == 6 and all(c in '0123456789abcdefABCDEF' for c in color)):
            await self._send(GoveeCommands.color_hex(color))
        else:
            await self._send(GoveeCommands.color_name(color))
    
    async def set_rgb(self, r: int, g: int, b: int) -> None:
        """Set light color by RGB values.
        
        Args:
            r: Red value 0-255
            g: Green value 0-255
            b: Blue value 0-255
        """
        await self._send(GoveeCommands.color(RGB(r, g, b)))
    
    @staticmethod
    async def scan(timeout: float = 10.0) -> List[BLEDevice]:
        """Scan for Govee devices.
        
        Args:
            timeout: Scan timeout in seconds
            
        Returns:
            List of discovered Govee BLE devices
        """
        devices = []
        
        def detection_callback(device: BLEDevice, advertisement_data):
            name = device.name or ""
            if "Govee" in name or "ihoment" in name:
                devices.append(device)
        
        scanner = BleakScanner(detection_callback=detection_callback)
        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()
        
        return devices
