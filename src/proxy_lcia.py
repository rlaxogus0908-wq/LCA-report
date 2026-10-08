"""Transparent numerical GWP proxy scenario; not a supplier-closed process LCA."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def compute() -> dict:
    bom = csv_rows(ROOT / "data/kettle_bom.csv")
    factors = {r["material"]: r for r in csv_rows(ROOT / "data/proxy_factors.csv")}
    scenario = json.loads((ROOT / "data/proxy_scenario.json").read_text(encoding="utf-8"))
    if len(bom) != 12 or set(factors) != {r["material"] for r in bom}:
        raise ValueError("Proxy factor rows must match the 12 BOM materials")
    yield_fraction = Decimal(str(scenario["yield_fraction_all_materials"]))
    if not Decimal(0) < yield_fraction <= Decimal(1):
        raise ValueError("yield_fraction_all_materials must be in (0,1]")
    grid = Decimal(str(scenario["grid_factor_kg_co2e_per_kwh"]))
    forming_rate = Decimal(str(scenario["conversion_electricity_kwh_per_kg_for_materials_without_included_conversion"]))
    rows = []
    total_material = Decimal(0)
    total_purchase = Decimal(0)
    total_finished = Decimal(0)
    forming_kwh = Decimal(0)
    for item in bom:
        name = item["material"]
        f = factors[name]
        finished = Decimal(item["finished_mass_g"]) / Decimal(1000)
        purchased = finished / yield_fraction
        factor = Decimal(f["factor_kg_co2e_per_kg"])
        impact = purchased * factor
        included = f["conversion_included"].strip().lower() == "yes"
        electricity = Decimal(0) if included else purchased * forming_rate
        rows.append({
            "material": name, "scope": item["scope"], "finished_mass_kg": float(finished),
            "assumed_purchased_mass_kg": float(purchased), "proxy_product": f["proxy_product"],
            "factor_kg_co2e_per_kg": float(factor), "factor_source_type": f["source_type"],
            "factor_source_url": f["source_url"], "model_choice": f["model_choice"],
            "conversion_included_in_factor": included,
            "material_kg_co2e": float(impact), "additional_conversion_kwh": float(electricity),
            "additional_conversion_kg_co2e": float(electricity * grid),
        })
        total_material += impact
        total_purchase += purchased
        total_finished += finished
        forming_kwh += electricity
    if total_finished != Decimal("0.8608"):
        raise ValueError("BOM mass balance failed")
    assembly_kwh = Decimal(str(scenario["assembly_electricity_kwh_per_kettle"]))
    transport_km = Decimal(str(scenario["inbound_transport_distance_km"]))
    transport_factor = Decimal(str(scenario["inbound_transport_factor_kg_co2e_per_tkm"]))
    scrap_factor = Decimal(str(scenario["scrap_treatment_factor_kg_co2e_per_kg_scrap"]))
    transport = total_purchase / Decimal(1000) * transport_km * transport_factor
    scrap_mass = total_purchase - total_finished
    scrap_treatment = scrap_mass * scrap_factor
    conversion = forming_kwh * grid
    assembly = assembly_kwh * grid
    total = total_material + conversion + assembly + transport + scrap_treatment
    parts = {
        "material_proxy_factors": total_material,
        "additional_component_conversion_electricity": conversion,
        "assembly_electricity": assembly,
        "inbound_transport": transport,
        "scrap_treatment": scrap_treatment,
    }
    if abs(sum(parts.values()) - total) > Decimal("0.0000000001"):
        raise ValueError("Contribution sum failed")
    return {
        "schema": "kettle-proxy-scenario-v1",
        "scenario_id": scenario["scenario_id"],
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "status": "calculated proxy scenario; not a supplier-closed process LCA",
        "declared_unit": scenario["declared_unit"],
        "gwp100_proxy_kg_co2e_per_packaged_kettle": float(total),
        "impact_method": "Precharacterized published material kg CO2e/kg factors plus China 2024 electricity kg CO2e/kWh; heterogeneous original GWP methods/versions not fully documented; IPCC AR6 factors are not reapplied",
        "sourced_values": {"finished_masses": "12-row classroom BOM", "material_proxy_factors": "data/proxy_factors.csv", "china_grid_factor_kg_co2e_per_kwh": float(grid)},
        "assumed_values": {key: value for key, value in scenario.items() if key in {
            "assumed_manufacturing_country", "yield_fraction_all_materials",
            "conversion_electricity_kwh_per_kg_for_materials_without_included_conversion",
            "assembly_electricity_kwh_per_kettle", "inbound_transport_distance_km",
            "inbound_transport_factor_kg_co2e_per_tkm", "scrap_treatment_factor_kg_co2e_per_kg_scrap"}},
        "masses_kg": {"finished_total": float(total_finished), "purchased_total_assumed": float(total_purchase), "scrap_total_assumed": float(scrap_mass)},
        "energy_kwh": {"additional_component_conversion": float(forming_kwh), "assembly": float(assembly_kwh)},
        "contributions_kg_co2e": {key: float(value) for key, value in parts.items()},
        "materials": rows,
        "checks": {"bom_mass_pass": True, "factor_coverage": "12 of 12", "contribution_sum_pass": True},
        "limitations": [
            "Material coefficients are secondary/product proxies, not verified TianGong or USLCI supplier-closed inventories.",
            "Original characterization method/version for every precharacterized factor is not harmonized to IPCC AR6 GWP100.",
            "Nylon 6, Chinese manufacture, yields, conversion electricity, transport and scrap treatment are assumptions.",
            "PP injection moulding and LDPE film factors may already contain normal process losses; applying purchased mass can overestimate these parts.",
            "Silicone PDMS fluid proxy does not represent a measured kettle seal formulation.",
            "No direct process elementary inventory, provider closure, primary plant measurements, or uncertainty distribution was available.",
        ],
    }


if __name__ == "__main__":
    result = compute()
    path = ROOT / "results/proxy_baseline.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = ROOT / "results/proxy_material_contributions.csv"
    columns = ["material", "scope", "finished_mass_kg", "assumed_purchased_mass_kg", "proxy_product",
               "factor_kg_co2e_per_kg", "material_kg_co2e", "additional_conversion_kwh",
               "additional_conversion_kg_co2e", "factor_source_type", "factor_source_url", "model_choice"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(result["materials"])
    print(f"{result['gwp100_proxy_kg_co2e_per_packaged_kettle']:.6f} kg CO2e/packaged kettle (proxy scenario)")
