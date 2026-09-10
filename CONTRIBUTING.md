# Contributing

## Adding a new equipment driver

1. Create a new repository named `<device>-driver`, using the manufacturer/model
   in lowercase with no spaces (e.g. `keithley2400-driver`, `lakeshore335-driver`).
2. Use MIT license unless there's a specific reason not to.
3. Recommended structure for a driver repo:
   ```
   <device>-driver/
     README.md          # what it is, wiring/connection notes, usage example
     LICENSE
     pyproject.toml      # or setup.py
     src/<device>/
       __init__.py
       driver.py
     tests/
   ```
4. README should include at minimum:
   - Supported model(s) and communication interface (GPIB/USB/Serial/Ethernet/VISA/etc.)
   - Install instructions
   - A minimal usage example
5. Open a PR against this hub repo (`Lab-equipment-pyDrivers`) adding a row to the
   driver table in `README.md` with the device name, a link to the new repo, and status
   (e.g. `stable`, `wip`, `untested`).

## Reporting issues with an existing driver

File the issue in that driver's own repository, not here.
