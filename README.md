# ASDA Soft Linux

[![CI](https://github.com/Beovoxo/ASDA-Soft-Linux-Debian/actions/workflows/ci.yml/badge.svg)](https://github.com/Beovoxo/ASDA-Soft-Linux-Debian/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Debian%20%2F%20LinuxCNC-orange)](https://www.debian.org/)
[![License: MIT](https://img.shields.io/badge/License-GPL--3.0--only-blue.svg)](LICENSE)

An independent, native Debian/Linux desktop foundation for a future Delta
ASDA-A2 configuration and diagnostics application.

> **Development status: pre-alpha.** This repository is not a Linux port of
> Delta's proprietary Windows ASDA_Soft 4.08.09 source code. It is a clean-room
> application scaffold based on the supplied installer metadata and publicly
> documented interfaces. No undocumented servo commands are sent.

## Current scope

- Native Python 3 + PySide6 application.
- Dark industrial desktop interface.
- Serial adapter discovery and safe open/close.
- Parameter workspace with JSON/CSV import and export.
- Packaging metadata, tests and CI baseline.

## Not yet implemented

- Reading/writing actual ASDA-A2 parameters.
- Delta protocol frames, checksums and parameter scaling.
- Servo tuning, enable, jog, alarm reset or motion commands.
- EtherCAT CoE / CiA-402 integration.
- Import of the original Paradox/BDE database.

These features must wait for verified documentation for the exact drive
model, firmware and physical interface. A serial port opening successfully
does not mean that the drive protocol is working.

## Screens / modules

| Module | Current state |
|---|---|
| Overview / drive profile | Basic UI |
| Serial communication | Port discovery and open/close only |
| Parameter table | Local editable workspace |
| JSON / CSV | Import and export |
| LinuxCNC / HAL | Planned adapter; not active |

## Requirements

- Debian 12/13 or a compatible Debian-based Linux distribution.
- Python 3.10 or newer.
- Desktop session supported by Qt (X11 or Wayland).
- Serial adapter only if you want to test port discovery.

## Install from a Git checkout

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip

git clone https://github.com/Beovoxo/ASDA-Soft-Linux-Debian.git
cd ASDA-Soft-Linux-Debian

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
asda-soft-linux
```

If the desktop app cannot find a serial port, add your user to the serial
access group and log out/in:

```bash
sudo usermod -aG dialout "$USER"
```

## Run from source

```bash
python run_asda_linux.py
```

## Developer setup and tests

```bash
python -m pip install -e ".[dev]"
pytest
```

## LinuxCNC integration design

The GUI is a normal desktop process and must not run inside a real-time HAL
thread. Future machine integration should use a separate adapter layer:
- LinuxCNC HAL pins or supported LinuxCNC Python interfaces for status and
  non-real-time configuration.
- A verified EtherCAT master / CiA-402 stack for cyclic servo control, where
  supported by the exact drive.
- No GUI event loop, file I/O or blocking serial calls in a real-time thread.

This application currently does not command any axis and must not be treated
as a safety system, emergency-stop circuit or motion controller.

## Hardware target

The initial development target is Delta ASDA-A2. The user's machine-specific
configuration may later be added as an optional profile; do not assume that
all A2 variants share identical interfaces, firmware features or parameters.

## License and trademarks

The original code in this repository is licensed under MIT.
This is an independent project and is not affiliated with Delta Electronics.
Delta and ASDA are trademarks of their respective owners. The proprietary
Windows installer and its extracted contents are not redistributed here.
