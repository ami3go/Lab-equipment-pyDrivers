# Contributing

## Adding a new equipment driver

1. Create a new repository named `<device>-driver`, using the manufacturer/model
   in lowercase with no spaces (e.g. `keithley2400-driver`, `lakeshore335-driver`).
2. Use MIT license unless there's a specific reason not to.
3. Follow the [Lab pyDrivers Standard (`AI_Guides/`)](AI_Guides/README.md) for the
   driver's design, public API, error handling, logging, testing, and release process.
   The core rule: the driver itself must be plain, framework-independent Python, fully
   usable and testable without any test-automation framework installed. If you also want
   a pytest-fixture, CLI, REST, etc. binding, write it as a separate adapter
   per [LPDS-015](AI_Guides/LPDS-015_Plugin_and_Adapter_Architecture.md) — it should never
   live inside the driver itself.
4. Recommended structure for a driver repo:
   ```
   <device>-driver/
     README.md          # what it is, wiring/connection notes, usage example
     LICENSE
     pyproject.toml      # or setup.py
     src/<device>/
       __init__.py
       driver.py
     adapters/           # optional; one subfolder per framework adapter, if any
     tests/
   ```
5. README should include at minimum:
   - Supported model(s) and communication interface (GPIB/USB/Serial/Ethernet/VISA/etc.)
   - Install instructions
   - A minimal usage example
6. Open a PR against this hub repo (`Lab-equipment-pyDrivers`) adding a row to the
   driver table in `README.md` with the device name, a link to the new repo, and status
   (e.g. `stable`, `wip`, `untested`).

## Reporting issues with an existing driver

File the issue in that driver's own repository, not here.
