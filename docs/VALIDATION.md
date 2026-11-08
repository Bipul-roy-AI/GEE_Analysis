# Preparation validation

Preparation date: 2026-11-08.

## Passed locally

- `pip install -e '.[dev]'`: editable installation of the national toolkit and development tools.
- `python -m bdgee --help`: CLI loads and exposes all 16 national workflows.
- `python tools/validate_sources.py`: 245 original hashes match; 146 adapted Python scripts parse; 99 adapted JavaScript scripts parse; all 146 output-free notebook schemas and code cells validate.
- `python -m pytest -q`: **27 tests passed, 16 workflow subtests passed**. Coverage includes all national EE computation/export graphs, typed class-area/population aggregation, theme-folder routing, complete inventory, robust trends, seasonal anomalies and missing-data spell handling.
- `python -m compileall -q bdgee tools tests`: toolkit, importer, status helper and tests compile.

The EE graph tests use the official SDK's bundled API signatures offline. They detected and corrected an unsupported list-intersection method during preparation. They do not fetch imagery, simulate numerical results or verify catalog asset availability.

## Sequential automation checks

- Queue preview accounts for all 245 sources: **213 eligible tutorials, 32 explicitly deferred**; a separate queue exposes all 16 national workflows.
- Ordering tests cover one task at a time, no next source before delivery verification, failed/unknown status, absent/empty Drive files, multipart files, local-upload failures, durable resume, source-only refresh, configuration mismatch, and the single-runner lock.
- Actual Earth Engine JavaScript SDK 1.7.51 installed with npm. Two tutorial graphs pass through the Node planner and Python export builders using official offline API signatures. Export graph serialization and stable request-ID restoration are tested for both image and table tasks.
- Master notebook schema/code cells and JavaScript planner syntax validate. Python modules/tools compile.
- Windows launchers are provided for the requested D: workspace but have not been executed on a Windows machine.
- A live batch launch was attempted here and stopped during Earth Engine initialization with the authorization message. No source computation or export began.

## Not executed / outstanding

- `ee.Initialize(project='axial-paratext-491911-b6')` failed with the SDK's **please authorize access** message. No authorized Earth Engine credentials were available to this process. Presence of a general Google credential environment binding did not supply an EE session.
- Live dataset queries, calculations, coverage checks, all tutorial execution and scientific validation remain unrun.
- The optional complete notebook dependency set is not installed/tested; some experimental libraries need separate version-compatible environments.
- No EE tasks were started; no Drive folders/files were created and no numerical outputs are claimed.
- Some tutorial-specific training features/private assets must be supplied and reviewed. Empirical models require Bangladesh calibration and independent validation.

Next steps: authenticate your EE account, verify project/API permissions, run a national workflow without `--submit`, review the plan, submit a representative product, inspect task completion and Drive outputs, then validate each scientific method needed for your study. See [RUNNING.md](RUNNING.md) and [METHODS.md](METHODS.md).
