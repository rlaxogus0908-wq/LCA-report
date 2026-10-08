# BC1 1 L electric kettle — factory-gate LCA workbench

**Numerical proxy result: 4.062 kg CO2-eq per packaged kettle.** This is a transparent scenario estimate using the sourced 12-row BOM, published embodied-carbon proxy factors, China's published 2024 electricity factor, and explicit assumed yields/energy/transport/scrap. It is **not** a supplier-closed TianGong/USLCI process LCA or an IPCC AR6-harmonized result. The strict process-model audit remains incomplete and lists [43 unresolved items](results/gap_register.csv). See the [Korean feasibility assessment](docs/feasibility_assessment_ko.md). The separate 0.0175 kg CO2-eq/kWh result is a fictitious matrix teaching example, **not** a kettle footprint.

## 1. Study identity and purpose

| Field | Current record |
|---|---|
| Study title | BC1 1 L plastic electric kettle, factory-gate GWP100 |
| Public student/group alias | Unknown; student to choose before public submission |
| Repository URL | https://github.com/rlaxogus0908-wq/LCA-report |
| Run identifier | `proxy_baseline_2026-10-08`; strict process audit: `independent-audit-2026-10-08` |
| Study date | 2026-10-08 |
| Goal | Build a reproducible model and compare defensible data/method choices in class |
| Intended comparison | The first preserved proxy run versus classmates' runs with compatible methods, then one changed choice |
| Independent/revised run and Git tag | First numerical proxy scenario in `results/proxy_baseline.json`; first-result commit `7991eb7bcbcbd68f30e008f13a6fd2ab588b7202`, tag `independent-proxy-baseline`; no revised run yet |

Use the first-result 40-character commit SHA above in the private course form after reviewing the submission. Personal name and email are intentionally absent from this public repository.

## 2. Product, declared unit, and boundary

Declared unit: **one manufactured and packaged BC1 1 L plastic electric kettle at the factory gate**. BC1 is a representative base case, not a named commercial product. The [original classroom CSV](data/kettle_bom.csv), obtained on 2026-10-08 from the [classroom site](https://tiangong-lca-decision-lab.ecodino73.chatgpt.site/classroom/kettle-bom.csv), traces its finished masses to the [EU Electric Kettles preparatory study (2020), Task 4, Tables 4-3, 4-4 and 4-8](https://publica-rest.fraunhofer.de/server/api/core/bitstreams/3df3f4d6-3717-4261-99e3-a232323111d6/content). The CSV contains 12 materials: 723 g kettle + 137.8 g packaging = 860.8 g packaged total.

Included: raw-material supply, component manufacture, assembly, and packaging. Customer delivery, use, and end of life are excluded. No quantitative cutoff has been applied in the strict model; missing inputs remain gaps there. Actual manufacturing geography is unknown; the proxy scenario assumes China. BOM reference year is 2020; candidate background process years vary and no common reference year has been established. No use-phase or end-of-life extension is included.

## 3. Foreground inventory and quantitative assumptions

All 12 finished masses are sourced from the BOM. The strict [foreground parameters](data/foreground_parameters.csv) separates them from unknown actual purchase quantities, yields, and conversion services. The numerical [proxy scenario](data/proxy_scenario.json) explicitly assumes 95% yield for each material, so purchased mass is `finished_mass_kg / 0.95`. Nylon 6 is an explicit material-grade assumption. These choices are not observed facts.

| Input or parameter | Value | Unit | Evidence/status |
|---|---:|---|---|
| Product finished mass | 723 | g/kettle | Sourced; classroom BOM and EU study |
| Packaging finished mass | 137.8 | g/kettle | Sourced; classroom BOM and EU study |
| Proxy purchased material mass | 0.906105 | kg/kettle | **Assumed** 95% yield; actual value unknown |
| Additional conversion electricity | 0.265395 | kWh/kettle | **Assumed** 0.5 kWh/kg purchased for materials whose factor does not explicitly include forming |
| Assembly electricity | 0.1 | kWh/kettle | **Assumed**; no numerical default in brief |
| Inbound transport | 500 | km | **Assumed** for all purchased material mass; customer delivery excluded |
| Scrap treatment | 0.1 | kg CO2e/kg scrap | **Assumed**; no recycling credit |
| Monetary proxy price | Not applicable | — | No monetary proxy selected |

Mass conversion is `finished_mass_kg = finished_mass_g / 1000`. Reference-flow normalization in a complete model uses each supplier's documented output amount/unit and the solved activity vector. Conversion energy must be entered once: a resin-production process does not automatically include component moulding, while a finished-part process may already include it. No background burden has been added to the current kettle audit.

## 4. Background data and matching decisions

The [candidate mapping table](data/candidate_mapping.csv) gives one row for every BOM input with database, release, candidate UUID/version, geography, year, reference unit, source link, retrieval time, alternatives, data type, and unresolved gap. [Search notes](docs/source_search_log.md) record the queries and decisions. No TianGong/USLCI candidate has been marked accepted or supplier-closed. The separate [proxy factor table](data/proxy_factors.csv) contains 12 published CO2e coefficients and the exact product proxies/assumptions used for the numerical scenario. Most are reprinted in [Westminster City Council/WSP's September 2024 report, PDF page 83](https://www.westminster.gov.uk/sites/default/files/media/documents/EV_R_003%20Embodied%20Carbon%20Evidence%20Study%20Update_0.pdf). POM uses a [CarbonCloud POM resin product footprint](https://apps.carboncloud.com/climatehub/product-reports/id/9394755343364), and silicone uses [Global Silicones Council's PDMS fluid value](https://www.silicones.eu/wp-content/uploads/2019/05/SIL_exec-summary_en.pdf). These are proxy factors, not the chosen TianGong/USLCI datasets. The USLCI [release table](https://github.com/FLCAC-admin/uslci-content/blob/dev/docs/release_info/release-downloads.md) lists `1.2026-09.0`; individual process-version values not retrieved are recorded as unknown.

USLCI nylon and polycarbonate `Bridge; USLCI to USEEIO` hits are **monetary bridges**, not mass-based resin LCIs. Their sector, currency, price year, purchaser/basic-price basis, quantity, and unit price are not available; they are rejected for the current baseline. A flow record alone is not a provider process. TianGong and USLCI unit-process direct emissions cannot be treated as cumulative factors without resolving their upstream product/energy suppliers. Dataset license and raw-file hash are unknown unless explicitly documented in the mapping table. The [data manifest](data/data_manifest.json) records local source hashes and missing background files.

## 5. Calculation and impact-assessment methods

[`src/lcia.py`](src/lcia.py) constructs a technosphere matrix `A` from positive product outputs and negative product inputs, solves `A s = f` with `numpy.linalg.solve`, builds elementary inventory `g = B s`, and characterizes `h = C g`. `solve(A,f)` obtains the same mathematical solution as `A⁻¹f` without explicitly forming the inverse. It propagates **known** upstream requirements; it cannot infer missing supplier exchanges or elementary emissions. It matches upstream providers explicitly and checks units. It requires every listed elementary flow to have a factor; an unmatched flow stops the calculation. Per-process contributions are `s_j × (C B)_j`. The reported **4.062264 kg** proxy estimate comes from factor multiplication in [`src/proxy_lcia.py`](src/proxy_lcia.py), not the `A` matrix solve.

The strict matrix model's provisional method is **IPCC AR6 WGI, GWP100, 100-year horizon**, sourced from [Chapter 7, Table 7.15](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/). Its [factor file](data/ipcc_ar6_gwp100.csv) contains a selected-gas subset. **The numerical proxy result uses a different method:** mass × already-characterized kg CO2e/kg material coefficients plus electricity × the [Chinese government 2024 national-average electricity carbon-footprint factor, 0.5777 kg CO2e/kWh](https://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/202510/W020251024569470952545.pdf), plus explicitly assumed freight and scrap factors. The original GWP characterization versions behind all published material coefficients are not consistently documented, so this result cannot honestly be labelled IPCC AR6 GWP100. Applying AR6 factors again to those CO2e values would double characterize them.

Actual allocation, recycling and scrap treatment are unknown. The proxy assigns a stated scrap-treatment factor and no recycling credit; its published coefficients may follow different allocation rules. Supplier links for all 12 material routes, component conversions, and assembly energy remain unresolved in the strict process model. A mathematical solve does not by itself certify boundary completeness. Do not mix direct unit-process emissions with a cumulative factor for the same supply chain.

## 6. Reproduce the analysis

File map: `data/` holds BOM, factor subset, proxy factors, foreground and system parameters, mapping, and manifest; `src/lcia.py` is the strict matrix calculator; `src/proxy_lcia.py` computes the numerical scenario; `src/build_report.py` regenerates the standalone [HTML report](report.html); `examples/` holds the fictitious matrix and incomplete kettle template; `results/` holds the proxy, audit, gap register and teaching-example outputs; `docs/` holds the decision/search/workflow logs and Korean feasibility assessment; `tests/` checks the calculations.

Verified environment: Windows, Python 3.13.1, NumPy 2.3.3. No random seed is used. For a clean environment:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python src\lcia.py audit
.venv\Scripts\python src\proxy_lcia.py
.venv\Scripts\python src\build_report.py
.venv\Scripts\python src\lcia.py calculate --model examples\site_matrix_example.json --out results\matrix_example.json
.venv\Scripts\python -m unittest discover -s tests -v
```

Open JSON outputs in any text editor. To calculate a real kettle result after completing the [modeling workflow](docs/modeling_workflow.md):

```powershell
.venv\Scripts\python src\lcia.py calculate --model PATH_TO_COMPLETE_KETTLE_MODEL.json --factors data\ipcc_ar6_gwp100.csv --out results\kettle_complete.json
```

The classroom BOM is redistributed as supplied. TianGong detailed data access varies by dataset and licence; no TianGong account was available for this run. The [LCA Commons public repository](https://www.lcacommons.gov/lca-collaboration/) says its public data are downloadable without an account. The [Federal LCA Commons API](https://www.lcacommons.gov/lca-commons-api-guide) says `DEMO_KEY` is only for testing and is rate limited; it returned HTTP 429 during this search. A personal data.gov API key is appropriate for automated retrieval; put it in a private `FLCAC_API_KEY` environment variable, never in Git. No background database dumps or credentials are included. The remaining manual steps are supplier selection, licensed data retrieval, foreground measurement/estimation, provider linking, and characterization of the full inventory.

## 7. Results, checks, and interpretation

The [proxy run](results/proxy_baseline.json) reports **4.062264 kg CO2e/packaged kettle**. Its [material-level CSV](results/proxy_material_contributions.csv) supports review. The material factor subtotal is 3.801339; additional component conversion electricity 0.153319; assembly electricity 0.057770; inbound transport 0.045305; scrap treatment 0.004531 kg CO2e. The largest modeled materials are PP, stainless steel, and assumed nylon 6. This ranking applies only to the stated proxies and assumptions. The [strict process audit](results/independent_run.json) remains `null`, with 12 procurement, 12 conversion, 12 provider, and 7 system-level unresolved items in the [gap register](results/gap_register.csv).

| Check | Result |
|---|---|
| BOM rows | 12; pass |
| Kettle mass | 723 g; pass |
| Packaging mass | 137.8 g; pass |
| Packaged mass | 860.8 g; pass |
| Unit conversion of finished BOM | g to kg supported; provider reference units pending |
| Proxy factor coverage | 12/12; pass |
| Proxy contribution sum | Equals 4.062264 kg CO2e; pass |
| Supplier closure | Fail for strict TianGong/USLCI model; proxy coefficients are aggregate substitutes |
| Method harmonization | Fail; original GWP method versions behind material proxies unknown |
| Double counting | Proxy factor for PP injection moulding and LDPE film contains conversion, so additional conversion electricity is excluded for those two; yield adjustment may still overlap normal losses |

The [fictitious matrix example](results/matrix_example.json) gives `0.0175 kg CO2-eq/kWh` for the website's coal/electricity teaching example; it verifies arithmetic only and has no empirical kettle interpretation. The 4.062264 result is a conditional estimate; unknown data quality and factor-method differences prevent using it as a measured or comparative product footprint.

## 8. Uncertainty and sensitivity

No probabilistic uncertainty interval was calculated. The proxy scenario has point assumptions only; no distributions, correlations, draw count, seed, convergence test, P05, or P95 exist. The largest decision risks are factor geography/year, 95% material yield, nylon 6 selection, PDMS fluid as a silicone-part proxy, conversion electricity, and method mismatch. A later sensitivity can vary these one at a time, but it must be kept separate from the first saved numerical proxy result.

## 9. Codex and human decisions

Codex-assisted project creation date: 2026-10-08. The exact model/version label and settings displayed by the client are **unknown** in this artifact; fill them from the UI before submission. [Decision log](docs/decision_log.md) summarizes consequential instructions and corrections without personal messages. The student supplied the BOM and confirmed no TianGong account. The student created the public repository and asked Codex to upload this project. The student must review selected matches, supply missing physical data for a strict LCA, and check generated results. No manual numerical correction has been made to a kettle result.

## 10. Independent and revised runs

The first numerical artifact is `results/proxy_baseline.json`, calculated before class comparison and preserved in commit `7991eb7bcbcbd68f30e008f13a6fd2ab588b7202` under tag `independent-proxy-baseline`. A revised run has not been performed; changed choice, predicted effect, revised total, absolute difference, and percentage difference are **not applicable**. Keep the first result unchanged, then make and explain exactly one changed modeling choice in a later commit.
