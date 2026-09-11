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
| HP/Agilent/Keysight 34401A | [hp34401a-driver](https://github.com/ami3go/hp34401a-driver) | wip |

> Adding a new driver? Open a PR here to add it to this table once its repo exists.

## Shared libraries

| Purpose | Repository | Status |
|---|---|---|
| SCPI interface core (base classes for SCPI-speaking instrument drivers) | [scpi-driver-core](https://github.com/ami3go/scpi-driver-core) (private) | wip |

## Driver & AI Guide Standards

[`AI_Guides/`](AI_Guides/README.md) holds the Lab pyDrivers Standard (LPDS): the
normative spec set for designing, building, testing, and releasing a driver in this
ecosystem. The core idea: a driver is plain, framework-independent Python verified
completely on its own, and any test-automation framework (pytest, a CLI, REST, ...) is
bolted on afterward as a separate, thin adapter. New driver repos should
follow this standard; see [`AI_Guides/README.md`](AI_Guides/README.md) for the full
document index.

## Adding a new driver

See [CONTRIBUTING.md](CONTRIBUTING.md) for the naming convention, expected repo
structure, and how to register a new driver repo in the table above.

## License

Code in this repository is licensed under the [MIT License](LICENSE). Individual
driver repositories may specify their own license, which should also be MIT unless
noted otherwise.
