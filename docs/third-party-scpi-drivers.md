# Public GitHub SCPI Driver & Instrument-Control Catalog

**Catalog version:** 0.1.0 · **Research snapshot:** 2026-10-24 · **Repositories:** 82 · **Categories:** 8

> This is a curated research snapshot rather than an exhaustive inventory of GitHub SCPI drivers. Dates are the most recent default-branch commit dates checked on 2026-10-24. None of the tests were independently executed as part of catalog preparation. Catalog entries are not endorsements or certifications.

## Reading the test columns

- **Present:** public automated-test material was identified, but was not executed in this cataloging pass.
- **Evidence present:** some testing-related material was found, but completeness was not assessed.
- **Not verified:** evidence was not established; this does not mean a project was not tested.
- **Hardware evidence:** repository claims or supporting documents were identified where stated. These have not been independently reproduced.
- **Role:** a library, transport adapter, utility, or application is not necessarily a complete model-specific SCPI driver.

## Category summary

| Category | Repositories |
|---|---:|
| Multi-instrument frameworks | 18 |
| Power supplies | 9 |
| Oscilloscopes | 11 |
| Multimeters / SMUs | 6 |
| RF signal generators / analyzers | 11 |
| Vector network analyzers | 3 |
| Electronic loads | 4 |
| SCPI / VISA transport | 20 |

## Multi-instrument frameworks

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [microsoft/Qcodes](https://github.com/microsoft/Qcodes) | Python | 2026-10-23 | Present | Not independently verified | Framework |
| [QCoDeS/Qcodes_contrib_drivers](https://github.com/QCoDeS/Qcodes_contrib_drivers) | Python | 2026-10-24 | Present | Not independently verified | Driver collection |
| [pymeasure/pymeasure](https://github.com/pymeasure/pymeasure) | Python | 2026-10-23 | Present | Not independently verified | Driver collection |
| [Rohde-Schwarz/RsInstrument](https://github.com/Rohde-Schwarz/RsInstrument) | Python | 2026-08-17 | Evidence present | Not independently verified | Communication core |
| [nominal-io/instro](https://github.com/nominal-io/instro) | Python/Rust | 2026-10-24 | Present | Not independently verified | Driver collection |
| [abduznik/instrumation](https://github.com/abduznik/instrumation) | Python | 2026-10-21 | Present | Six validation reports claimed | Driver collection |
| [little-did-I-know/SCPI-Instrument-Control](https://github.com/little-did-I-know/SCPI-Instrument-Control) | Python | 2026-10-04 | Present | Not independently verified | Driver collection |
| [Scaxlibur/WaveBench](https://github.com/Scaxlibur/WaveBench) | Python | 2026-09-09 | Not verified | Not independently verified | Application / driver wrappers |
| [timhellwig/sci_instr](https://github.com/timhellwig/sci_instr) | Python | 2020-10-12 | Not verified | Not independently verified | Framework |
| [masonlab/labdrivers](https://github.com/masonlab/labdrivers) | Python | 2018-09-11 | Not verified | Not independently verified | Driver collection |
| [bendelathouwer/Visa-drivers](https://github.com/bendelathouwer/Visa-drivers) | Python | 2026-07-25 | Not verified | Not independently verified | Driver collection |
| [ogawa-ros/ogameasure](https://github.com/ogawa-ros/ogameasure) | Python | 2026-08-25 | Not verified | Not independently verified | Framework / application |
| [gb119/Python-SCPI-Driver](https://github.com/gb119/Python-SCPI-Driver) | Python | 2019-09-07 | Not verified | Not independently verified | Driver / framework |
| [charlesbaynham/GenericSCPIDriver](https://github.com/charlesbaynham/GenericSCPIDriver) | Python | 2026-04-23 | Not verified | Not independently verified | Generic driver |
| [LachlanGunn/oic](https://github.com/LachlanGunn/oic) | C++ | 2021-03-18 | Not verified | Not independently verified | Instrument-control framework |
| [colingimenez/SCPI_MCP](https://github.com/colingimenez/SCPI_MCP) | Python | 2026-08-30 | Not verified | Not independently verified | Application / MCP adapter |
| [mrn2se/AgenticWebInstrumentControl](https://github.com/mrn2se/AgenticWebInstrumentControl) | Rust | 2026-10-21 | Not verified | Not independently verified | Application / driver wrappers |
| [jfrancis42/rf-bench](https://github.com/jfrancis42/rf-bench) | Python | 2026-09-08 | Not verified | Not independently verified | Instrument-control application |

## Power supplies

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [ami3go/keysight-n6700-driver](https://github.com/ami3go/keysight-n6700-driver) | Python | 2026-10-22 | Present | Partial physical bench testing claimed | Instrument driver |
| [crogialli/Siglent3303C](https://github.com/crogialli/Siglent3303C) | Python | 2026-10-04 | Not verified | Not independently verified | Instrument controller |
| [kakuteki/owon-spe6103-mcp](https://github.com/kakuteki/owon-spe6103-mcp) | Python | 2026-08-02 | Not verified | Not independently verified | MCP instrument adapter |
| [lxkang00/spd-mcp](https://github.com/lxkang00/spd-mcp) | Python | 2026-07-05 | Not verified | Not independently verified | MCP instrument adapter |
| [ajs410/psu-monitor](https://github.com/ajs410/psu-monitor) | Python | 2026-05-19 | Not verified | Not independently verified | Monitoring application |
| [philpagel/udp3305s](https://github.com/philpagel/udp3305s) | Python | 2024-10-27 | Not verified | Not independently verified | Instrument tools |
| [briansune/SPD1000x-Tool-V1.0](https://github.com/briansune/SPD1000x-Tool-V1.0) | Python | 2022-12-30 | Not verified | Not independently verified | Instrument tool |
| [TychoBECH/microbench_psu](https://github.com/TychoBECH/microbench_psu) | Python | 2026-08-12 | Not verified | Not independently verified | Instrument controller |
| [shamrik-dmitriy/remote-control-of-instruments](https://github.com/shamrik-dmitriy/remote-control-of-instruments) | Python | 2020-10-25 | Not verified | Not independently verified | Multi-instrument scripts |

## Oscilloscopes

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [ami3go/Tektronix_DPO4000_utils](https://github.com/ami3go/Tektronix_DPO4000_utils) | Python | 2026-10-24 | Present | Partial; formal qualification pending | Instrument driver / utilities |
| [RoGeorge/DS1054Z_screen_capture](https://github.com/RoGeorge/DS1054Z_screen_capture) | Python | 2017-01-04 | Not verified | Not independently verified | Instrument utility |
| [jupitervolta/rigol-capture](https://github.com/jupitervolta/rigol-capture) | Python | 2023-09-25 | Not verified | Not independently verified | Instrument utility |
| [felixfinal/rigol-scope-kit](https://github.com/felixfinal/rigol-scope-kit) | Python | 2026-10-12 | Not verified | Not independently verified | Instrument toolkit |
| [mp911de/siglent-scpi-mcp](https://github.com/mp911de/siglent-scpi-mcp) | Python | 2026-09-01 | Not verified | Not independently verified | MCP instrument adapter |
| [ikatkov/rigol-mcp](https://github.com/ikatkov/rigol-mcp) | Python | 2026-10-03 | Not verified | Not independently verified | MCP instrument adapter |
| [bveina/Rigol-Scope-Snap](https://github.com/bveina/Rigol-Scope-Snap) | C# | 2021-09-20 | Not verified | Not independently verified | Instrument utility |
| [niksiboxi/mxo44-usbtmc-scpi](https://github.com/niksiboxi/mxo44-usbtmc-scpi) | Python | 2026-08-28 | Not verified | Not independently verified | Instrument controller |
| [sanderberents/eelab](https://github.com/sanderberents/eelab) | Python | 2026-07-05 | Not verified | Device-specific workarounds documented | Multi-instrument scripts |
| [JohnQsk/oscilloscope-cli](https://github.com/JohnQsk/oscilloscope-cli) | Python | 2026-09-23 | Not verified | Not independently verified | Instrument CLI |
| [OPROSVOs/Rigol-DS1000-series-automation](https://github.com/OPROSVOs/Rigol-DS1000-series-automation) | Python | 2026-09-13 | Not verified | Not independently verified | Instrument automation |

## Multimeters / SMUs

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [ami3go/hp34401a-driver](https://github.com/ami3go/hp34401a-driver) | Python | 2026-09-14 | Present | Not independently verified | Instrument driver |
| [Elektroarzt/owon-xdm-remote](https://github.com/Elektroarzt/owon-xdm-remote) | Python | 2025-08-13 | Not verified | Not independently verified | Instrument remote controller |
| [andrey-nakin/scpi-multimeter](https://github.com/andrey-nakin/scpi-multimeter) | Python | 2018-10-05 | Not verified | Not independently verified | Instrument utility |
| [is4rk/Fluke8588A-pyvisa](https://github.com/is4rk/Fluke8588A-pyvisa) | Python | 2026-08-27 | Not verified | Not independently verified | Instrument driver / examples |
| [khwas/UAFluke8846A](https://github.com/khwas/UAFluke8846A) | C# | 2019-03-22 | Not verified | Not independently verified | Instrument examples |
| [MubarakshinRuslan/AkipReader](https://github.com/MubarakshinRuslan/AkipReader) | C# | 2026-04-22 | Not verified | Not independently verified | Instrument application |

## RF signal generators / analyzers

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [mclim9/rssd](https://github.com/mclim9/rssd) | Python | 2024-07-08 | Not verified | Not independently verified | R&S instrument driver |
| [MatheusTimmers/specan-rs](https://github.com/MatheusTimmers/specan-rs) | Rust | 2026-03-29 | Not verified | Not independently verified | Instrument driver / application |
| [mbraune/dsa136socketscpi](https://github.com/mbraune/dsa136socketscpi) | Python | 2022-10-30 | Not verified | Not independently verified | Instrument driver |
| [CrinitusFeles/N9010A_Controller](https://github.com/CrinitusFeles/N9010A_Controller) | Python | 2025-03-06 | Not verified | Not independently verified | Instrument controller |
| [fiskusk/RS_FSEA_scripts](https://github.com/fiskusk/RS_FSEA_scripts) | Python | 2025-09-29 | Not verified | Not independently verified | Instrument scripts |
| [gx2g/rf-test-automation](https://github.com/gx2g/rf-test-automation) | Python | 2026-06-11 | Not verified | Not independently verified | RF automation scripts |
| [mtapalla/XsgLib](https://github.com/mtapalla/XsgLib) | Python | 2014-05-21 | Not verified | Not independently verified | Instrument library |
| [lheywang/SDGPy](https://github.com/lheywang/SDGPy) | Python | 2025-01-04 | Not verified | Not independently verified | Instrument library |
| [doug-gilbert/sdg-control](https://github.com/doug-gilbert/sdg-control) | Python | 2026-10-15 | Not verified | Not independently verified | Instrument controller |
| [kakuteki/rigol-dg900-mcp](https://github.com/kakuteki/rigol-dg900-mcp) | Python | 2026-08-02 | Not verified | Not independently verified | MCP instrument adapter |
| [lxkang00/sdg-mcp](https://github.com/lxkang00/sdg-mcp) | Python | 2026-07-05 | Not verified | Not independently verified | MCP instrument adapter |

## Vector network analyzers

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [Terrabits/vna-scpi-examples](https://github.com/Terrabits/vna-scpi-examples) | Python | 2016-12-15 | Not verified | Not independently verified | Examples |
| [AmanIITM02/pyvisa-vna-automation](https://github.com/AmanIITM02/pyvisa-vna-automation) | Python | 2026-08-06 | Not verified | Not independently verified | Instrument automation |
| [ZiadHatab/scpi-rohde-schwarz-vna](https://github.com/ZiadHatab/scpi-rohde-schwarz-vna) | Python | 2023-11-24 | Not verified | Not independently verified | Instrument scripts |

## Electronic loads

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [zeloscloud/zelos-extension-instruments](https://github.com/zeloscloud/zelos-extension-instruments) | Python | 2026-10-22 | Not verified | Not independently verified | Driver collection |
| [RajdeepMallick21/FB-DL3021](https://github.com/RajdeepMallick21/FB-DL3021) | Python | 2025-06-17 | Not verified | Not independently verified | Instrument controller |
| [shiaotao/IT8812C_battery_test](https://github.com/shiaotao/IT8812C_battery_test) | Python | 2025-09-02 | Not verified | Not independently verified | Instrument test application |
| [john3volts3/ET5410A-electronique-load](https://github.com/john3volts3/ET5410A-electronique-load) | Python | 2026-03-02 | Not verified | Not independently verified | Instrument controller |

## SCPI / VISA transport

| GitHub repository | Language | Last commit (UTC) | Automated tests | Hardware evidence | Role |
|---|---|---|---|---|---|
| [pyvisa/pyvisa](https://github.com/pyvisa/pyvisa) | Python | 2026-10-13 | Present | Not applicable to transport alone | Transport abstraction |
| [pyvisa/pyvisa-py](https://github.com/pyvisa/pyvisa-py) | Python | 2026-10-24 | Present | Not applicable to transport alone | Transport backend |
| [pyvisa/pyvisa-sim](https://github.com/pyvisa/pyvisa-sim) | Python | 2026-10-21 | Present | Simulated, not real hardware | Simulation backend |
| [pyvisa/pyvisa-drivers](https://github.com/pyvisa/pyvisa-drivers) | Python | 2019-06-28 | Not verified | Not independently verified | Driver collection (small) |
| [ami3go/scpi-driver-core](https://github.com/ami3go/scpi-driver-core) | Python | 2026-10-24 | Present | Not independently verified | Communication core |
| [gotmc/usbtmc](https://github.com/gotmc/usbtmc) | Go | 2026-04-14 | Not verified | Not applicable to transport alone | USBTMC transport |
| [gotmc/lxi](https://github.com/gotmc/lxi) | Go | 2026-04-16 | Not verified | Not applicable to transport alone | LXI transport |
| [gotmc/ivi](https://github.com/gotmc/ivi) | Go | 2026-08-19 | Not verified | Not applicable to transport alone | IVI abstraction |
| [gotmc/asrl](https://github.com/gotmc/asrl) | Go | 2026-04-16 | Not verified | Not applicable to transport alone | Serial transport |
| [gotmc/prologix](https://github.com/gotmc/prologix) | Go | 2026-04-16 | Not verified | Not applicable to transport alone | GPIB transport |
| [klasyc/ScpiNet](https://github.com/klasyc/ScpiNet) | C# | 2026-01-27 | Not verified | Not applicable to transport alone | Protocol / client |
| [cnxy/VISAInstrument](https://github.com/cnxy/VISAInstrument) | C# | 2022-03-26 | Not verified | Not applicable to transport alone | VISA wrapper |
| [ucdart/dart-scpi](https://github.com/ucdart/dart-scpi) | C# | 2016-07-11 | Not verified | Not applicable to transport alone | SCPI protocol library |
| [FlorianFrank/instrument_control_lib](https://github.com/FlorianFrank/instrument_control_lib) | C++ | 2023-03-22 | Not verified | Not independently verified | Instrument framework |
| [mcvsama/scpidev](https://github.com/mcvsama/scpidev) | C++ | 2016-07-06 | Not verified | Not applicable to transport alone | SCPI client |
| [marcopeereboom/scpi](https://github.com/marcopeereboom/scpi) | Go | 2019-03-21 | Not verified | Not applicable to transport alone | SCPI library |
| [yellow-pitaya/scpi-client](https://github.com/yellow-pitaya/scpi-client) | Rust | 2026-06-22 | Not verified | Not applicable to transport alone | SCPI client |
| [morgan-at-keysight/PyScpiInstrument](https://github.com/morgan-at-keysight/PyScpiInstrument) | Python | 2022-06-17 | Not verified | Not applicable to transport alone | Instrument communication core |
| [T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit](https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit) | Python | 2026-05-20 | Not verified | Not independently verified | Instrument toolkit |
| [m-chuu/RsInstrument_SCPI_commands](https://github.com/m-chuu/RsInstrument_SCPI_commands) | Python | 2024-01-16 | Not verified | Not independently verified | Command examples |

## Scope and exclusions

- This page mixes model-specific instrument drivers, instrument utilities, framework integrations, VISA transports, simulations, and general driver collections. Use the **Role** column when evaluating completeness.
- The Panasonic VP-8122A project is excluded as a standard SCPI driver because it implements a native, non-standard GPIB command language.
- Firmware/model compatibility and hardware qualification were not independently assessed. Before deployment, inspect tested command coverage, simulator tests, CI logs for an exact commit, safety behavior, and retained physical HIL evidence.

## Verification notes

The repository links above are the source references. The default-branch commit dates were checked using connected GitHub searches on 2026-10-24; the original research collected READMEs and searched for test-related source files. A future refresh should re-check repository ownership, current code, commit dates, and hardware evidence instead of carrying old statuses forward without verification.

Other reference projects: [QCoDeS](https://github.com/microsoft/Qcodes), [PyMeasure](https://github.com/pymeasure/pymeasure), [PyVISA](https://github.com/pyvisa/pyvisa), [Instro](https://github.com/nominal-io/instro), [Instrumation](https://github.com/abduznik/instrumation), [RsInstrument](https://github.com/Rohde-Schwarz/RsInstrument).
