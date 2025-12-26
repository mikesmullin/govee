"""Govee LED CLI - Control Govee lights from the command line."""

import asyncio
import os
from pathlib import Path
from typing import Optional

import click
import yaml

from .device import GoveeDevice


def get_project_root() -> Path:
    """Get the project root directory (where config.yml lives)."""
    # Start from the directory containing this script
    current = Path(__file__).resolve().parent
    # Walk up to find config.yml
    for _ in range(5):  # Max 5 levels up
        config_path = current / "config.yml"
        if config_path.exists():
            return current
        # Also check parent's parent (src/govee -> project root)
        parent_config = current.parent.parent / "config.yml"
        if parent_config.exists():
            return current.parent.parent
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def load_config() -> dict:
    """Load configuration from config.yml."""
    config_path = get_project_root() / "config.yml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def get_default_device() -> Optional[str]:
    """Get default device MAC from config."""
    config = load_config()
    return config.get('device')


def run_async(coro):
    """Run an async coroutine."""
    return asyncio.run(coro)


@click.group()
@click.option('--mac', '-m', envvar='GOVEE_DEVICE',
              help='Device MAC address (default from config.yml or GOVEE_DEVICE env var)')
@click.version_option()
@click.pass_context
def main(ctx, mac: Optional[str]):
    """Control Govee LED lights via Bluetooth.
    
    Device MAC can be specified via:
      1. -m/--mac flag
      2. GOVEE_DEVICE environment variable  
      3. config.yml file (device: "MAC")
    
    Use 'govee scan' to find devices first.
    
    Examples:
    
        govee scan
        
        govee on
        
        govee color red
        
        govee -m C5:37:32:32:2C:43 brightness 50
    """
    ctx.ensure_object(dict)
    # Use provided MAC, or fall back to config.yml
    device = mac or get_default_device()
    ctx.obj['device'] = device


@main.command()
@click.option('--timeout', '-t', default=10.0, help='Scan timeout in seconds')
@click.pass_context
def scan(ctx, timeout: float):
    """Scan for Govee devices."""
    
    async def _scan():
        click.echo(f"Scanning for Govee devices ({timeout}s)...")
        devices = await GoveeDevice.scan(timeout=timeout)
        
        if not devices:
            click.echo("No Govee devices found.")
            click.echo("\nTips:")
            click.echo("  - Make sure your Govee light is powered on")
            click.echo("  - Try moving closer to the device")
            click.echo("  - Check that Bluetooth is enabled")
            return
        
        click.echo(f"\nFound {len(devices)} device(s):\n")
        for device in devices:
            click.echo(f"  {device.address}  {device.name or 'Unknown'}")
        
        click.echo("\nSet device in config.yml or use: govee -m <ADDRESS> <command>")
    
    run_async(_scan())


def require_device(ctx):
    """Get device from context or fail."""
    device = ctx.obj.get('device')
    if not device:
        raise click.ClickException(
            "Device MAC address required. Set 'device' in config.yml, "
            "use -m option, or set GOVEE_DEVICE env var."
        )
    return device


@main.command()
@click.pass_context
def on(ctx):
    """Turn the light on."""
    device = require_device(ctx)
    
    async def _on():
        click.echo(f"Connecting to {device}...")
        async with GoveeDevice(device) as dev:
            await dev.power_on()
            click.echo("Light turned ON")
    
    run_async(_on())


@main.command()
@click.pass_context
def off(ctx):
    """Turn the light off."""
    device = require_device(ctx)
    
    async def _off():
        click.echo(f"Connecting to {device}...")
        async with GoveeDevice(device) as dev:
            await dev.power_off()
            click.echo("Light turned OFF")
    
    run_async(_off())


@main.command()
@click.argument('color')
@click.pass_context
def color(ctx, color: str):
    """Set the light color.
    
    COLOR can be a name (red, green, blue, white, yellow, cyan, magenta,
    purple, orange, pink, warm, cool) or a hex code (#FF0000 or FF0000).
    
    Examples:
    
        govee color red
        
        govee color "#FF5500"
        
        govee color 00FF00
    """
    device = require_device(ctx)
    
    async def _color():
        click.echo(f"Connecting to {device}...")
        async with GoveeDevice(device) as dev:
            await dev.set_color(color)
            click.echo(f"Color set to: {color}")
    
    run_async(_color())


@main.command()
@click.argument('r', type=int)
@click.argument('g', type=int)
@click.argument('b', type=int)
@click.pass_context
def rgb(ctx, r: int, g: int, b: int):
    """Set the light color by RGB values (0-255 each).
    
    Examples:
    
        govee rgb 255 0 0      # Red
        
        govee rgb 0 255 0      # Green
        
        govee rgb 255 128 0    # Orange
    """
    device = require_device(ctx)
    
    async def _rgb():
        click.echo(f"Connecting to {device}...")
        async with GoveeDevice(device) as dev:
            await dev.set_rgb(r, g, b)
            click.echo(f"Color set to: RGB({r}, {g}, {b})")
    
    run_async(_rgb())


@main.command()
@click.argument('level', type=click.IntRange(0, 100))
@click.pass_context
def brightness(ctx, level: int):
    """Set the brightness level (0-100%).
    
    Examples:
    
        govee brightness 100   # Full brightness
        
        govee brightness 50    # Half brightness
        
        govee brightness 10    # Dim
    """
    device = require_device(ctx)
    
    async def _brightness():
        click.echo(f"Connecting to {device}...")
        async with GoveeDevice(device) as dev:
            await dev.set_brightness(level)
            click.echo(f"Brightness set to: {level}%")
    
    run_async(_brightness())


if __name__ == "__main__":
    main()
