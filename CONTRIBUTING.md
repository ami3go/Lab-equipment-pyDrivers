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
   (e.g. `stable`, `wip`, `untested`). The status label must be one of the three
   defined by [LPDS-001 §9](AI_Guides/LPDS-001_Platform_Requirements.md).

## Adding an adapter, or a shared library

The hub indexes two kinds of non-driver repository as well:

- **Adapters** — thin bindings of an already-published driver to one framework
  (Robot Framework, a GUI, a CLI), per
  [LPDS-015](AI_Guides/LPDS-015_Plugin_and_Adapter_Architecture.md). An adapter never
  contains device logic of its own; it translates calls and results only.
- **Shared libraries** — reusable infrastructure several drivers depend on, such as
  transport/session handling.

Add each one to the matching table in `README.md`, in its own PR.

## Running the checks locally

This repository has a CI workflow (`.github/workflows/ci.yml`) that validates the
index and lints the Markdown. Run the same checks before opening a PR:

```bash
./scripts/run_ci.sh            # index consistency, unit tests, markdown lint
./scripts/run_ci.sh --remote   # additionally resolve every indexed GitHub repository
```

`--remote` needs network access and honours `GITHUB_TOKEN`/`GH_TOKEN` if set; it
fails the run if an indexed repository has been deleted, renamed, archived, or
turned private. The anonymous GitHub API allows only 60 requests per hour,
which is fewer than the index needs, so set a token before using `--remote`.
The Markdown lint rule set lives in `.markdownlint-cli2.jsonc`.

## Reporting issues with an existing driver

File the issue in that driver's own repository, not here.
