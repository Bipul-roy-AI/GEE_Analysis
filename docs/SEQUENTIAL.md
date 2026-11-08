# Windows / Jupyter: one analysis and export at a time

Workspace requested: **`D:\Gihub_Projects\BD_GEE_Analysis`**. The runner is portable; this path is a local-PC instruction, not a claim that the cloud session can access your D: drive.

## Install on your PC

Install **Python 3.12**, Git, and **Node.js 22 or newer** (Node is needed for the JavaScript tutorial bridge). Clone into the requested folder if it does not already contain your checkout:

```powershell
git clone https://github.com/Bipul-roy-AI/GEE_Analysis.git D:\Gihub_Projects\BD_GEE_Analysis
Set-Location D:\Gihub_Projects\BD_GEE_Analysis
# If already cloned here, use git pull instead, preserving your own changes.
.\setup_windows.ps1 -Tutorials
```

If your Windows policy does not allow running local PowerShell scripts, use the equivalent commands in a terminal instead of changing system policy:

```text
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev,notebooks]"
npm.cmd ci --ignore-scripts
```

The common notebook dependencies are installed. A few tutorials additionally need `standard-precip`, `xclim`, `xeofs`, `xrscipy`, `xarray-spatial` or `dea-tools`; install these in this environment if the current source's log reports a missing module, checking package compatibility. TensorFlow and the deferred supervised models are not needed for this initial queue. A Bangladesh-wide high-resolution xarray analysis can require substantial memory/disk and spatial tiling; a sequential runner does not eliminate that requirement.

## Authenticate once

```text
.venv\Scripts\python.exe -c "from bdgee.core import initialize; initialize(authenticate=True)"
```

This opens Google's authorization flow for your own account with Earth Engine and Drive scopes. The account must be registered for Earth Engine and have permission to use **`axial-paratext-491911-b6`**. Enable the Earth Engine and Drive APIs as required for that account/project. No key belongs in the notebook, repository or chat. The runner checks Drive access before planning/submitting any analysis.

## Option A: master notebook

```text
.venv\Scripts\python.exe -m jupyter lab
```

Open [`notebooks/Run_Bangladesh_Sequential.ipynb`](../notebooks/Run_Bangladesh_Sequential.ipynb). Use the `.venv` Python kernel. The notebook explicitly sets the workspace to your D: path. It previews the source queue/deferred list, runs the queue and displays saved progress. After the first login, skip the authentication cell when resuming. Do not run a second notebook or launcher while the first is working.

## Option B: terminal (recommended for long runs)

Preview all individual sources without authentication or execution:

```text
.venv\Scripts\python.exe -m bdgee.batch --mode tutorials
```

Initial source queue: **213 individual examples selected, 32 deferred**. All 245 originals are accounted for; supervised/empirical calibration methods are deferred, including water-quality concentration methods. Clustering and other methods that do not need manual labels remain eligible. Eligibility is a static selection, **not a guarantee that all examples will execute successfully**. The full queue and exact exclusions/reasons are written to `outputs/tutorials_queue.json`.

Run the non-deferred tutorials, grouped by theme and then source number:

```text
run_sequential.bat tutorials
```

Or run the improved national workflows separately:

```text
run_sequential.bat national
```

National mode has **16 workflows**. It is an alternative to running all tutorials, not a substitute secretly applied to the 213-source queue. It avoids many local-array/tutorial dependencies and exports typed national raster/administrative products. Do not launch both modes simultaneously.

You can select themes explicitly:

```text
.venv\Scripts\python.exe -m bdgee.batch --mode tutorials --themes climate water --run
.venv\Scripts\python.exe -m bdgee.batch --mode national --themes climate water --start 2024-01-01 --end 2025-01-01 --run
```

Tutorial mode preserves the original source's time windows; national mode uses the supplied dates except for the documented fixed-period products. Changing the selection/dates is a deliberate new run: use a separate `--state outputs/my_other_run.json`. Never delete an existing state to get around an incomplete export. The global lock still prevents two batches in one checkout; the runner also refuses to start a new task while your account has an active EE task visible to it. A different account/project can run work beyond the runner's visibility.

## Exact completion contract

For each source/workflow, the runner:

1. Waits for the previous source to have fully verified exports. Only then does it launch the next source's planning process. Workers cannot submit tasks themselves.
2. Plans the source's outputs. Python executes in an isolated subprocess with a fresh output directory; JavaScript uses the official Earth Engine Node SDK and a headless Code Editor adapter. Chart values are exported numerically; no interactive map-window screenshot is claimed. Native raster values and administrative tables are exported. Individual tutorials retain existing export settings and the generic displayed-map/export helper defaults to 1000 m; review/change a source's `BD_SCALE` or final `export_outputs(..., scale=...)` before its first run if another scale is required. Use national mode for the explicitly typed/native-resolution products.
3. Persists the task configuration and a unique submission request ID **before** submitting anything.
4. Submits **one** EE export task and polls its real status. `READY` and `RUNNING` do not permit advancing. `FAILED`, `CANCELLED`, unknown status and network errors stop the run.
5. After EE reports **`COMPLETED`**, checks Drive for the uniquely named destination files in `BD_GEE_<theme>`. Matching files must exist and have nonzero sizes; multipart files must all be nonempty. EE completion is the authoritative export-completion signal; Drive listing is an additional delivery/visibility check, not a validation of raster science or a separately known expected shard count.
6. Only after that verification submits the next EE export. After all EE tasks, uploads local plots, CSV, NetCDF and scalar files **one at a time**, verifying size and MD5 checksum in Drive.
7. Marks the source complete only after every task/upload passes. Then, and only then, starts the next source.

Each file prefix includes a unique run/task suffix, so an older export cannot accidentally satisfy the delivery gate. This also prevents image/table names being confused with another task. Repeated intentional new runs will create additional Drive files; resuming an existing run does not deliberately resubmit verified tasks.

## Stop and resume

Keep the PC awake with internet access. Closing the notebook or pressing Ctrl+C stops local monitoring; a task already submitted to Google may continue. Resume with the **same command/settings and the same state file**. A known submitted task is monitored by saved task ID, and completed/verified exports are skipped. State is written atomically under `outputs/`; keep that folder and local staged files.

- State/progress: `outputs/tutorials_state.json` or `outputs/national_state.json`.
- Worker logs: `outputs/batch_plans/<source>/worker.log`.
- Source-local files: fresh `attempt_.../local/` directories under that source's plan folder. These are retained for upload/recovery, not committed to Git.
- Any Python `export_errors.json` entry stops the source rather than silently losing a result.
- Drive visibility timeout: ten minutes. If the export is complete but the files are not yet visible, the run stops. Resume later; the export is not resubmitted.

### A source fails before exports

Read its log and fix the reported dependency, missing input or code error. Dependency fixes do not require changing the saved run. If you edit **only the currently stopped tutorial source** after a `PLAN_FAILED` error, resume explicitly with:

```text
.venv\Scripts\python.exe -m bdgee.batch --mode tutorials --refresh-planning-source --run
```

Repeat any original theme/date/state arguments. This accepts a source checksum change only for the current failed planning job before any exports started, preserving completed jobs. It rejects queue/runner/settings changes or edits to a different job. There is no automatic skip-failed option.

### An EE export fails/cancels

Inspect the saved task error and fix the underlying cause. To explicitly retry the **current failed task**, without skipping it:

```text
.venv\Scripts\python.exe tools/retry_failed_export.py outputs/tutorials_state.json
run_sequential.bat tutorials
```

The helper verifies server-side failure/cancellation and absence of active tasks. It preserves attempt history and creates a new request ID/output prefix, so old partial files cannot pass verification. Previously verified exports are not repeated. It does not submit anything until the runner resumes.

### Submission response was lost before a task ID was saved

The request ID is persisted and the EE API's request-id mechanism makes replay idempotent. If an active task is present but the response/ID was lost, the runner stops instead of guessing which task it owns. Match the exact unique `description` in saved state with the task in Google's task list and recover its ID into that `SUBMITTING` record, changing its local state to the server's current state. Do not assign an unrelated task or delete state. This rare ambiguous case requires reconciliation; safety takes precedence over automatically moving to another job.

## What has actually been verified

The state-machine tests verify strict ordering, Drive/upload failure gates, unknown-status stops, resumability, no repeated verified work, and the single-runner lock. Integration tests exercise two real tutorial graphs through the official JS SDK and back into Python export builders using offline API signatures. They do not compute satellite results. Live EE/Drive execution is still blocked in the preparation machine by missing account authorization, and this code has not been executed on your Windows PC. The runner will surface remaining tutorial defects rather than label them successful or quietly skip them.

## Recover the reported first climate projection failure (ZIP checkout)

Do not delete `outputs` or rerun the unmodified failed task. From the project folder in PowerShell:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Bipul-roy-AI/GEE_Analysis/main/tools/repair_projection_failure.py" -OutFile ".\tools\repair_projection_failure.py"
.\.venv\Scripts\python.exe .\tools\repair_projection_failure.py .\outputs\climate_test_state.json
```

This self-contained helper works in the previous ZIP checkout: it checks the failed task and EPSG:4326 on Google's server, creates state/code backups, patches the legacy national projection default and updates unfinished task graphs. It resets only the failed task with a fresh request ID/prefix, preserving verified work. It accepts this specific national projection failure, not arbitrary failures, and submits no exports. It also refreshes the engine fingerprint using the exact on-disk code, avoiding a configuration-mismatch error on resume.

After the helper reports success:

```powershell
.\.venv\Scripts\python.exe -m bdgee.batch --mode national --themes climate --state outputs\climate_test_state.json --run
```

The GAUL 2015 deprecation warning is separate from the projection error. Its dated boundary is retained during recovery so the study area does not silently change. Migrating to GAUL 2025 requires reviewing the new dataset's coverage/property schema.
