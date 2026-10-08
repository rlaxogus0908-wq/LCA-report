# Decision and prompt log

This is a curated record of consequential modeling choices. It omits personal messages and credentials.

| Date | Decision or prompt | Resolution | Effect |
|---|---|---|---|
| 2026-10-08 | Model the BC1 1 L plastic kettle using the classroom BOM. | Use one packaged kettle at the factory gate; include material supply, component manufacture, assembly, and packaging. | Use and end of life are outside the common result. |
| 2026-10-08 | Implement characterization to GWP100. | Use IPCC AR6 WGI 100-year factors for four explicitly identified gas flows, with exact flow, compartment, and unit matching. | Any other elementary flow stops the calculation until a compatible factor is added. |
| 2026-10-08 | Decide whether finished BOM mass can be used as purchased input. | No. Purchased mass requires a measured or justified yield and scrap route. | All twelve purchase quantities remain unknown. |
| 2026-10-08 | Search TianGong and USLCI. | Record candidate datasets and reject unsupported bridges or product flows as complete LCI substitutes. | No background dataset is marked accepted or supplier-closed yet. |
| 2026-10-08 | Produce a supplier-closed GWP100 total. | Deferred because component conversion, assembly energy, upstream providers, and complete elementary inventories are missing. | The strict process-model result is `null`, not zero. |
| 2026-10-08 | User requested a numerical result using explicit proxies and assumptions. | Create a separately labelled proxy scenario from 12 published CO2e material factors, the official China 2024 grid factor, and declared assumptions for yield, conversion, assembly, freight and scrap. | `results/proxy_baseline.json` gives 4.062264 kg CO2e/packaged kettle. It is not an IPCC AR6-harmonized or supplier-closed result. |
| 2026-10-08 | Publish on GitHub. | Student created `https://github.com/rlaxogus0908-wq/LCA-report` and asked Codex to upload. GitHub connector file write returned 403; authenticated local Git push succeeded. | First result commit `7991eb7bcbcbd68f30e008f13a6fd2ab588b7202` is preserved by tag `independent-proxy-baseline`. |

## Human review required before first public submission

Review the proxy assumptions and method mismatch before submission. For a full process LCA, confirm nylon grade; stock form and alloy for steel, brass and copper; manufacturing geography; yields and scrap treatment; component conversion routes; assembly electricity; upstream transport; allocation and recycling treatment; and dataset permissions. Then inspect all provider links and elementary-flow mappings. Record any accepted or rejected data matches in `data/candidate_mapping.csv`.
