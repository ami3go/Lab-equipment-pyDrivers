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
| Keysight/Agilent N6700 modular power system | [keysight-n6700-driver](https://github.com/ami3go/keysight-n6700-driver) | untested |
| Vötschtechnik (Weiss Technik) climate chamber | [VotschTechnik-climate-chamber-Python](https://github.com/ami3go/VotschTechnik-climate-chamber-Python) | stable |
| NGI N83624 multi-channel battery/cell simulator | [NGI-N83624-Battery-simulator](https://github.com/ami3go/NGI-N83624-Battery-simulator) | stable |
| Tektronix DPO4000-family oscilloscopes | [Tektronix_DPO4000_utils](https://github.com/ami3go/Tektronix_DPO4000_utils) | stable |
| TI TMP116/TMP117/TMP119 temperature sensors (CircuitPython) | [Adafruit_CircuitPython_TMP11X](https://github.com/ami3go/Adafruit_CircuitPython_TMP11X) | stable |
| DeVaSys USB-I2C/IO adapter | [USB-I2CIO-python](https://github.com/ami3go/USB-I2CIO-python) | stable |
| EA Elektro-Automatik PS 9000 T programmable DC power supply | [EA-PS-9000T](https://github.com/ami3go/EA-PS-9000T) | wip |
| Agilent/Keysight 34970A/34972A data acquisition/switch unit (RS232 + USB-GPIB) | [LOG34970A-RS232-Python](https://github.com/ami3go/LOG34970A-RS232-Python) | wip |
| Agilent/Keysight 33220A function/arbitrary waveform generator (VISA) | [GEN33220A-USB-Python](https://github.com/ami3go/GEN33220A-USB-Python) | wip |
| FNIRSI DC6006L programmable DC power supply (front USB) | [dc6006l-USB-Python](https://github.com/ami3go/dc6006l-USB-Python) | wip |
| Agilent/Keysight 34411A high-resolution multimeter (VISA) | [DMM34411A-USB-Python](https://github.com/ami3go/DMM34411A-USB-Python) | wip |
| Agilent/Keysight N6700B 4-channel modular power supply (VISA) | [PS_N6700B-USB-Python](https://github.com/ami3go/PS_N6700B-USB-Python) | wip |
| ELEKTRO-AUTOMATIK EA-PS series DC power supply (serial) | [ES-PS-controll](https://github.com/ami3go/ES-PS-controll) | wip |
| ITECH IT-M3900D high-power DC power supply (SCPI) | [itech_driver](https://github.com/ami3go/itech_driver) | wip |
| Panasonic VP-8122A FM/AM signal generator (GPIB) | [Panasonic_vp-8122a](https://github.com/ami3go/Panasonic_vp-8122a) | wip |
| Rohde & Schwarz UPV audio analyzer (VISA) | [Rohde-Schwarz_UPV-K7](https://github.com/ami3go/Rohde-Schwarz_UPV-K7) | wip |
| Phidgets 8-channel USB relay boards | [phidgets_relay](https://github.com/ami3go/phidgets_relay) | wip |
| E-Resistor programmable resistor matrix (SCPI over TCP) | [E-resistor-matrix-python-driver](https://github.com/ami3go/E-resistor-matrix-python-driver) | wip |
| E-Resistor 8-bit relay-based resistor switch board | [E-resistor-relay-8bits](https://github.com/ami3go/E-resistor-relay-8bits) | wip |
| EM TEST AutoWave signal generator (GPIB/VISA) | [AutoWave](https://github.com/ami3go/AutoWave) | wip |

> Adding a new driver? Open a PR here to add it to this table once its repo exists.
>
> Status labels follow [LPDS-001 §9](AI_Guides/LPDS-001_Platform_Requirements.md):
> `wip` (in development), `untested` (feature-complete, simulator-verified, not yet
> verified on real hardware), `stable` (verified end-to-end on real hardware).

## Shared libraries

| Purpose | Repository | Status |
|---|---|---|
| SCPI interface core (transport, session and error-handling base classes shared by SCPI-speaking instrument drivers) | [scpi-driver-core](https://github.com/ami3go/scpi-driver-core) | wip |
| CH9120 / YHQ001 eight-channel Ethernet relay board toolkit (discovery, configuration, relay control, CLI and Tkinter GUIs) | [ch9120-ethernet-relay-toolkit](https://github.com/ami3go/ch9120-ethernet-relay-toolkit) | untested |
| PicoSDK Python bindings (official Pico Technology SDK for PicoScope/PicoLog devices, used for test equipment) | [picosdk-python-wrappers](https://github.com/picotech/picosdk-python-wrappers) | external |

## Adapters and integrations

An adapter binds an already-published driver to one framework — Robot Framework, a
web UI, a CLI — and contains no device logic of its own. See
[LPDS-015](AI_Guides/LPDS-015_Plugin_and_Adapter_Architecture.md).

| Framework | Repository | Status |
|---|---|---|
| Robot Framework libraries for several of the drivers indexed above | [RobotFrameworks_hw_drivers](https://github.com/ami3go/RobotFrameworks_hw_drivers) | wip |
| NiceGUI browser interface for the Vötschtechnik climate chamber driver | [VotschTechnik-climate-chamber-GUI](https://github.com/ami3go/VotschTechnik-climate-chamber-GUI) | wip |

> Adding an adapter or a shared library? Open a PR here to add it to the matching
> table once its repo exists.

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
