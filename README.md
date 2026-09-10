# Lab Equipment pyDrivers

A collective index of Python drivers for lab equipment (instruments, sensors, controllers, etc.).

Each driver lives in its own repository under this account, named `<device>-driver`
(e.g. `keithley2400-driver`, `lakeshore335-driver`). This repository is the hub:
it hosts shared documentation, contribution guidelines, and the master list of
all driver repositories.

## Why a hub + many repos?

- Each driver can be versioned, tagged, and released independently.
- Contributors can pick up a single driver without cloning everything else.
- New equipment gets its own repo without bloating a monolith.

## Driver repositories

| Device | Repository | Status |
|---|---|---|
| Keysight U1242C | [Keysight_U1242C](https://github.com/ami3go/Keysight_U1242C) | wip |

> Adding a new driver? Open a PR here to add it to this table once its repo exists.

## Adding a new driver

See [CONTRIBUTING.md](CONTRIBUTING.md) for the naming convention, expected repo
structure, and how to register a new driver repo in the table above.

## License

Code in this repository is licensed under the [MIT License](LICENSE). Individual
driver repositories may specify their own license, which should also be MIT unless
noted otherwise.
