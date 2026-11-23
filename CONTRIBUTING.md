# Contributing

Thanks for helping improve ASDA Soft Linux.

## Before submitting
1. Open an issue describing the use case or bug.
2. Do not add guessed Delta register addresses, parameter IDs or protocol
   frames. Include the exact manual revision and page for protocol changes.
3. Keep machine motion and safety functions disabled unless their behavior
   has been independently reviewed and tested.

## Development
- Python 3.10+
- Format/style: follow the existing code and use clear type hints.
- Run `pytest` before submitting.
- Keep GUI work out of LinuxCNC real-time threads.

## Pull requests
Describe the change, test environment, drive model/firmware (if relevant),
and whether any physical drive was connected. Never include passwords,
access tokens, serial numbers or private machine network details.
