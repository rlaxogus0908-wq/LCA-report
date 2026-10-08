# Copy into Codex

Create a reproducible Python LCA project for one manufactured and packaged BC1 1 L plastic electric kettle at the factory gate. Include raw-material supply, component manufacture, assembly, and packaging. Exclude customer delivery, use, and end of life.

Use `data/kettle_bom.csv` as the finished-mass BOM, not procurement quantities. Check product mass 723 g, packaging 137.8 g, and total 860.8 g. The source is the EU Electric Kettles preparatory study (2020), Task 4, Tables 4-3, 4-4 and 4-8: https://publica-rest.fraunhofer.de/server/api/core/bitstreams/3df3f4d6-3717-4261-99e3-a232323111d6/content

Search and inspect candidate processes in BOTH TianGong and USLCI:
- https://www.tiangong.earth/en/lca-database
- https://github.com/tiangong-lca/cli
- https://www.lcacommons.gov/lca-collaboration/National_Renewable_Energy_Laboratory/USLCI_Database_Public/datasets
- https://www.lcacommons.gov/lca-commons-api-guide

For every selected or rejected match, record database, release, process name, UUID, exact version, geography, year, reference flow/amount/unit, URL, retrieval date, alternatives, and reason. Distinguish unit-process inventory from cumulative factors and monetary bridges. Resolve upstream providers; a unit process's direct emissions are not its full footprint.

Implement LCIA through characterization: solve `A s = f`, calculate `g = B s`, then `h = C g`. Report GWP100 in kg CO2-eq per packaged kettle with characterization method, version, 100-year horizon, factor source, and exact elementary-flow matching. Check units, mass balance, supplier closure, missing and uncharacterized flows, contribution sums, and double counting. Never silently replace missing inputs with zero.

Investigate and document material yields/losses, nylon grade, conversion services, assembly electricity, transport inside the boundary, scrap/allocation, and geography. Mark every input as sourced, estimated, or assumed. If complete data cannot be obtained, report `not calculated` for the total, list exactly what is missing, and still deliver executable code plus a verified teaching example. Do not invent a kettle result.

Create actual code, input files, mapping table, data manifest, run output, and README.md with all ten sections of `docs/readme-requirements.md`. Keep names/emails, API keys, course code, and restricted raw databases out of public files. Preserve the independent run before a later scenario. The student will create and upload the GitHub repository. Prioritize a runnable first version and show the exact command and result/status immediately.
