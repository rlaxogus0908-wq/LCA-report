"""Strict matrix LCI/LCIA calculator and BC1 kettle input audit.

Only a supplier-closed, fully characterized model can produce a kettle GWP100.
The bundled matrix example is fictitious and is never reported as the kettle result.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BOM = ROOT / "data" / "kettle_bom.csv"
FOREGROUND = ROOT / "data" / "foreground_parameters.csv"
FACTORS = ROOT / "data" / "ipcc_ar6_gwp100.csv"
MAPPING = ROOT / "data" / "candidate_mapping.csv"
SYSTEM = ROOT / "data" / "system_parameters.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def finite_number(value: object, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number; got {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def audit_bom() -> dict:
    rows = read_csv(BOM)
    product = sum(Decimal(row["finished_mass_g"]) for row in rows if row["scope"] == "Kettle")
    packaging = sum(Decimal(row["finished_mass_g"]) for row in rows if row["scope"] == "Packaging")
    expected = {"product_g": Decimal("723"), "packaging_g": Decimal("137.8"), "total_g": Decimal("860.8")}
    actual = {"product_g": product, "packaging_g": packaging, "total_g": product + packaging}
    checks = {name: actual[name] == expected[name] for name in expected}
    if len(rows) != 12 or not all(checks.values()):
        raise ValueError(f"BOM mass/row check failed: rows={len(rows)}, actual={actual}")

    foreground = read_csv(FOREGROUND)
    by_name = {row["input"]: row for row in foreground}
    if len(by_name) != len(rows) or set(by_name) != {row["material"] for row in rows}:
        raise ValueError("Foreground rows must match all twelve BOM materials exactly")
    for row in rows:
        fg = by_name[row["material"]]
        if Decimal(fg["finished_mass_g"]) != Decimal(row["finished_mass_g"]):
            raise ValueError(f"Foreground finished mass mismatch: {row['material']}")

    mapping_rows = read_csv(MAPPING)
    mapping = {row["foreground_input"]: row for row in mapping_rows}
    if len(mapping) != len(rows) or set(mapping) != set(by_name):
        raise ValueError("Candidate mapping must contain exactly the twelve BOM materials")
    system = json.loads(SYSTEM.read_text(encoding="utf-8"))
    blockers = []

    def block(scope: str, item: str, needed: str, evidence: str) -> None:
        blockers.append({"scope": scope, "item": item, "needed": needed, "current_evidence": evidence})

    for row in foreground:
        name = row["input"]
        finished_kg = Decimal(row["finished_mass_g"]) / Decimal(1000)
        yield_text, purchase_text = row["yield_fraction"], row["purchase_mass_kg"]
        if not yield_text and not purchase_text:
            block(name, "procurement_mass", "Measured or justified yield/scrap rate or purchased kg per kettle", f"Finished mass only: {finished_kg} kg")
        else:
            if yield_text:
                yield_fraction = Decimal(yield_text)
                if not 0 < yield_fraction <= 1:
                    raise ValueError(f"Yield must be in (0,1]: {name}")
            if purchase_text:
                purchase_kg = Decimal(purchase_text)
                if purchase_kg < finished_kg:
                    raise ValueError(f"Purchased mass below finished mass: {name}")
            if yield_text and purchase_text and abs(purchase_kg * yield_fraction - finished_kg) > Decimal("0.000001"):
                raise ValueError(f"Purchased mass and yield disagree: {name}")
        conversion = (row["conversion_service"], row["conversion_amount"], row["conversion_unit"])
        if not all(conversion):
            block(name, "component_conversion", "Process route and quantified forming/fabrication service, or evidence that selected dataset includes it", "No conversion service/amount/unit")
        selected = mapping[name]
        if selected["decision_status"] != "accepted" or not selected["dataset_id"] or selected["dataset_id"] == "unknown":
            block(name, "material_provider", "Accepted compatible production process with version, reference unit and full exchanges", f"{selected['database']} {selected['dataset_id']}; status={selected['decision_status']}")
        elif selected["dataset_version"] == "unknown" or selected["reference_unit"] == "unknown":
            block(name, "provider_metadata", "Exact dataset version and reference unit", f"version={selected['dataset_version']}; unit={selected['reference_unit']}")

    required_system = {
        "manufacturing_geography": "Manufacturing location and matching electricity region",
        "assembly_electricity_kwh": "Measured or justified assembly electricity per packaged kettle",
        "assembly_other_energy": "Quantified other assembly energy or sourced evidence for none",
        "inbound_transport": "Inbound freight amounts or explicit supported boundary decision",
        "scrap_treatment_allocation": "Scrap fate, treatment and allocation/credit rule",
        "supplier_closed_inventory": "Imported full technosphere and elementary exchanges with resolved upstream providers",
        "characterization_coverage": "CFs for every climate-relevant elementary flow including fossil/biogenic distinctions",
    }
    for item, needed in required_system.items():
        value = system.get(item)
        if value is None or value == "":
            block("system", item, needed, "not established")
    missing = [f"{entry['scope']}: {entry['item']}" for entry in blockers]
    return {
        "schema": "kettle-lcia-run-v1",
        "run_label": "independent-baseline",
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "declared_unit": "One manufactured and packaged BC1 1 L plastic electric kettle at the factory gate",
        "calculation_status": "incomplete: required inputs and supplier inventory are missing",
        "gwp100_kg_co2e_per_packaged_kettle": None,
        "contributions_kg_co2e": None,
        "characterization_method": "IPCC AR6 WGI GWP100, 100 years; selected gas factors only",
        "checks": {
            "bom_row_count": len(rows),
            "mass_balance": {key: {"actual_g": str(actual[key]), "expected_g": str(expected[key]), "pass": checks[key]} for key in checks},
            "supplier_closure": "fail: suppliers have not been linked",
            "uncharacterized_flows": "unknown until inventory is imported",
            "contribution_sum": "not calculated",
            "double_counting": "not fully checked: conversion services and background boundaries unknown",
        },
        "missing_inputs": missing,
        "blocking_items": blockers,
        "interpretation": "No kettle GWP100 is reported. BOM mass alone is not an elementary-flow inventory.",
    }


def load_factors(path: Path) -> dict[tuple[str, str, str], float]:
    factors = {}
    for row in read_csv(path):
        if row["category"] != "climate_change_gwp100":
            continue
        if row["indicator_unit"] != "kg CO2-eq":
            raise ValueError("Only kg CO2-eq factors are supported")
        key = (row["flow_id"], row["compartment"], row["unit"])
        if key in factors:
            raise ValueError(f"Duplicate characterization factor: {key}")
        factors[key] = finite_number(row["cf"], f"factor {key}")
    if not factors:
        raise ValueError("No GWP100 characterization factors found")
    return factors


def calculate(model_path: Path, factor_path: Path) -> dict:
    model = json.loads(model_path.read_text(encoding="utf-8"))
    processes = model.get("processes", [])
    if not processes:
        raise ValueError("Model has no processes")
    ids = [proc["id"] for proc in processes]
    if len(ids) != len(set(ids)):
        raise ValueError("Process IDs must be unique")
    by_id = {proc["id"]: proc for proc in processes}
    references = {}
    for proc in processes:
        ref = proc["reference"]
        flow = ref["flow_id"]
        if flow in references:
            raise ValueError(f"Multiple providers for reference flow {flow}")
        amount = finite_number(ref["amount"], f"reference amount {proc['id']}")
        if amount <= 0:
            raise ValueError(f"Reference amount must be positive: {proc['id']}")
        references[flow] = (proc["id"], ref["unit"], amount)

    n = len(processes)
    A = np.zeros((n, n), dtype=float)
    row_for_flow = {proc["reference"]["flow_id"]: i for i, proc in enumerate(processes)}
    biosphere = defaultdict(lambda: np.zeros(n, dtype=float))
    for j, proc in enumerate(processes):
        ref = proc["reference"]
        A[row_for_flow[ref["flow_id"]], j] += float(ref["amount"])
        for exchange in proc.get("technosphere", []):
            flow = exchange["flow_id"]
            if flow not in references:
                raise ValueError(f"Unresolved upstream provider for {flow} in {proc['id']}")
            provider, unit, _ = references[flow]
            if exchange.get("provider") != provider:
                raise ValueError(f"Provider mismatch for {flow} in {proc['id']}: expected {provider}")
            if exchange["unit"] != unit:
                raise ValueError(f"Unit mismatch for {flow} in {proc['id']}: {exchange['unit']} vs {unit}")
            amount = finite_number(exchange["amount"], f"technosphere {flow} in {proc['id']}")
            if amount < 0:
                raise ValueError("Technosphere input amounts must be nonnegative")
            A[row_for_flow[flow], j] -= amount
        for exchange in proc.get("elementary", []):
            key = (exchange["flow_id"], exchange["compartment"], exchange["unit"])
            biosphere[key][j] += finite_number(exchange["amount"], f"elementary {key} in {proc['id']}")

    if not biosphere:
        raise ValueError("Model has no elementary-flow inventory; missing flows are not zero")
    factors = load_factors(factor_path)
    unmatched = sorted(set(biosphere) - set(factors))
    if unmatched:
        raise ValueError(f"Uncharacterized elementary flows: {unmatched}")

    demand = model["demand"]
    demand_flow = demand["flow_id"]
    if demand_flow not in references:
        raise ValueError(f"Demand flow has no provider: {demand_flow}")
    if demand["unit"] != references[demand_flow][1]:
        raise ValueError("Demand unit differs from its reference flow unit")
    f = np.zeros(n)
    f[row_for_flow[demand_flow]] = finite_number(demand["amount"], "final demand")
    if f[row_for_flow[demand_flow]] <= 0:
        raise ValueError("Final demand must be positive")
    try:
        s = np.linalg.solve(A, f)
    except np.linalg.LinAlgError as exc:
        raise ValueError("Technosphere matrix is singular; check providers and cycles") from exc
    if np.any(s < -1e-10):
        raise ValueError("Negative process activity found; check signs and provider links")
    if not np.allclose(A @ s, f, rtol=1e-10, atol=1e-10):
        raise ValueError("Matrix balance A s = f failed")

    flow_keys = sorted(biosphere)
    B = np.vstack([biosphere[key] for key in flow_keys])
    C = np.array([factors[key] for key in flow_keys])
    g = B @ s
    h = float(C @ g)
    contributions = [float(s[j] * (C @ B[:, j])) for j in range(n)]
    if not math.isclose(h, sum(contributions), rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError("Contribution sum does not equal characterized total")

    return {
        "schema": "kettle-lcia-run-v1",
        "study_id": model.get("study_id", "unknown"),
        "declared_unit": model.get("declared_unit", "unknown"),
        "calculation_status": "matrix model solved and all listed flows characterized; boundary completeness requires separate audit",
        "method": "IPCC AR6 WGI GWP100, 100 years, selected gas factors",
        "gwp100_kg_co2e": h,
        "process_activities": [{"process_id": ids[j], "activity": float(s[j])} for j in range(n)],
        "elementary_inventory": [{"flow_id": key[0], "compartment": key[1], "unit": key[2], "amount": float(g[i]), "cf": factors[key]} for i, key in enumerate(flow_keys)],
        "contributions_kg_co2e": [{"process_id": ids[j], "amount": contributions[j]} for j in range(n)],
        "checks": {"matrix_balance_max_abs": float(np.max(np.abs(A @ s - f))), "contribution_sum_difference": h - sum(contributions), "uncharacterized_flow_count": 0, "supplier_links": "all listed technosphere flows linked"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Check BC1 BOM and report missing model inputs")
    audit.add_argument("--out", type=Path, default=ROOT / "results" / "independent_run.json")
    audit.add_argument("--gaps", type=Path, default=ROOT / "results" / "gap_register.csv")
    calc = sub.add_parser("calculate", help="Solve a supplied complete A/B/C model")
    calc.add_argument("--model", type=Path, required=True)
    calc.add_argument("--factors", type=Path, default=FACTORS)
    calc.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = audit_bom() if args.command == "audit" else calculate(args.model, args.factors)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Calculation refused: {exc}\n")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.command == "audit":
        args.gaps.parent.mkdir(parents=True, exist_ok=True)
        with args.gaps.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["scope", "item", "needed", "current_evidence"])
            writer.writeheader()
            writer.writerows(result["blocking_items"])
    print(json.dumps({"status": result["calculation_status"], "gwp100_kg_co2e": result.get("gwp100_kg_co2e", result.get("gwp100_kg_co2e_per_packaged_kettle")), "output": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
