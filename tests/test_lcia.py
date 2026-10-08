import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lcia import FACTORS, audit_bom, calculate  # noqa: E402
from proxy_lcia import compute  # noqa: E402


class LciaTests(unittest.TestCase):
    def test_bom_mass_and_incomplete_status(self):
        result = audit_bom()
        self.assertEqual(Decimal(result["checks"]["mass_balance"]["product_g"]["actual_g"]), Decimal("723"))
        self.assertEqual(Decimal(result["checks"]["mass_balance"]["packaging_g"]["actual_g"]), Decimal("137.8"))
        self.assertIsNone(result["gwp100_kg_co2e_per_packaged_kettle"])

    def test_site_matrix_example_characterization(self):
        result = calculate(ROOT / "examples" / "site_matrix_example.json", FACTORS)
        self.assertAlmostEqual(result["gwp100_kg_co2e"], 0.0175)
        self.assertEqual(result["checks"]["uncharacterized_flow_count"], 0)

    def test_missing_supplier_is_not_zero(self):
        with self.assertRaisesRegex(ValueError, "Unresolved upstream provider"):
            calculate(ROOT / "examples" / "kettle_model_template.json", FACTORS)

    def test_proxy_scenario_has_complete_factor_coverage_and_balance(self):
        result = compute()
        self.assertEqual(len(result["materials"]), 12)
        self.assertAlmostEqual(result["gwp100_proxy_kg_co2e_per_packaged_kettle"], 4.062264, places=5)
        self.assertAlmostEqual(sum(result["contributions_kg_co2e"].values()), result["gwp100_proxy_kg_co2e_per_packaged_kettle"])


if __name__ == "__main__":
    unittest.main()
