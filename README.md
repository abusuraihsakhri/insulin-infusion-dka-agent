# Insulin Infusion DKA Agent

Research-oriented laboratory monitoring worksheet for **adult diabetic ketoacidosis (DKA)**, together with legacy generic task-audit demonstrations. The browser worksheet is self-contained; it does not require Python, a server API, accounts, or an internet connection after the page loads.

> **Research/education only — not for clinical care.** This repository is not a validated medical device or a treatment protocol. It does not diagnose DKA/HHS, prescribe insulin or potassium, control infusion pumps, or perform real-time patient surveillance. Do not enter identifiable patient information. Pediatric DKA and HHS are outside the worksheet's scope.

## Browser worksheet

The static application in [`index.html`](index.html) provides:

- Current adult DKA biochemical resolution comparison: blood β-hydroxybutyrate **<0.6 mmol/L** and (**venous pH ≥7.3** or **bicarbonate ≥18 mmol/L**).
- Glucose <200 mg/dL as a desirable additional marker, not a mandatory biochemical resolution criterion.
- Potassium <3.5 mmol/L flagged for clinician review, without medication instructions.
- Optional signed hourly change in glucose, calculated as (previous glucose − current glucose) / elapsed hours.
- Range/finite-value checks, synthetic defaults, keyboard-accessible inputs, and no data persistence.

Clinical source: Umpierrez et al. *Hyperglycemic Crises in Adults With Diabetes: A Consensus Report*. *Diabetes Care*. 2024;47:1257–1275. [doi:10.2337/dci24-0032](https://doi.org/10.2337/dci24-0032). The consensus report describes DKA biochemical resolution with ketones and pH/bicarbonate rather than the anion gap.

To run the site locally, from the repository root:

```bash
python -m http.server 8001
# Open http://127.0.0.1:8001/
```

Modern browsers with JavaScript ES module support are required. No Pyodide is needed: the standalone calculations use JavaScript (`dka_math.mjs`), with a corresponding Python reference implementation (`insulin_infusion_dka_agent/dka_monitor.py`).

## Python installation and tests

Requires Python 3.9+ (CI tests 3.10–3.12); Node.js 22 is used for the browser calculation regression tests.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
node --test tests/test_browser_math.mjs
```

Python example using synthetic measurements:

```python
from insulin_infusion_dka_agent.dka_monitor import evaluate_adult_dka_labs

result = evaluate_adult_dka_labs(
    glucose_mg_dl=190,
    potassium_mmol_l=4.0,
    beta_hydroxybutyrate_mmol_l=0.5,
    venous_ph=7.31,
    bicarbonate_mmol_l=17.0,
)
print(result.to_dict())
```

## Legacy generic metric-audit CLI and REST API

The three historical entry points (`cli.py`, `dka_guard.py`, and `insulin_infusion_dka_agent/cli.py`) remain for compatibility. Their *primary/secondary metric* cutoffs are **illustrative and not clinically validated DKA or insulin infusion rules**.

```bash
python cli.py audit --task-id DEMO-1 --target SYNTH-01 --primary 28.5 --secondary 14.2
python cli.py chat "status"
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The FastAPI server exposes `GET /health`, `GET /metrics` (JSON), `POST /api/audit` (legacy generic audit), `POST /api/chat` (mock only), and `POST /api/dka-monitor` (research-only lab calculations). Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

Sample laboratory-monitoring request:

```bash
curl -X POST http://127.0.0.1:8000/api/dka-monitor \
  -H 'Content-Type: application/json' \
  -d '{"glucose_mg_dl":190,"potassium_mmol_l":4.0,"beta_hydroxybutyrate_mmol_l":0.5,"venous_ph":7.31,"bicarbonate_mmol_l":17.0}'
```

The packaged CLI `insulin-infusion-dka-engine` serves the alternative legacy API in `insulin_infusion_dka_agent/server.py`, which also provides `POST /api/dka-monitor`. It is not interchangeable with the root CLI's generic audit schema. `sample.csv` is in the alternative legacy case-audit format; it is not directly compatible with the root `cli.py batch` schema.

## Security and data handling

- The **browser worksheet processes inputs entirely in the browser**; it does not send inputs to a backend, use browser storage, or log values. The external DOI link is followed only when clicked.
- The REST API receives request data and keeps generic audit dossiers in process memory. The regex-based PHI guard is **best effort**, not de-identification, regulatory compliance certification, or a guarantee that identifiers cannot be received.
- Generic audit entries form an HMAC-SHA256 verified **in-memory** chain. This is not durable, immutable, cross-process, or a compliant medical audit record.
- Set a strong `AUDIT_SECRET_KEY` for server use. Otherwise a random, ephemeral process key is generated. Example/default keys are rejected. `GET /api/audit/logs` is disabled unless `AUDIT_LOG_READ_TOKEN` is configured; a matching `X-Audit-Token` header is required.
- Keep the API bound to localhost or protected behind appropriate application authentication, transport security and access controls. Docker Compose binds to `127.0.0.1:8000` by default.

Optional local Docker use, after configuring a strong secret:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(40))')"
docker compose up --build
```

## Structure and technology

- `index.html`, `app.mjs`, `dka_math.mjs`: static offline-capable worksheet (HTML/CSS/vanilla JavaScript).
- `insulin_infusion_dka_agent/dka_monitor.py`: corresponding Python clinical-laboratory calculations.
- `agents/`: older generic task auditing, in-memory HMAC logging, optional REST API.
- `insulin_infusion_dka_agent/`, `dka_guard.py`, `enrichment.py`: legacy demonstration modules; do not interpret their generic scores as validated clinical assessments.
- `tests/`: Python, API, security, and browser calculation regressions.
- `.github/workflows/ci.yml`: tests, package build, dependency audit, and GitHub Pages publication when available.

License: [MIT](LICENSE).
