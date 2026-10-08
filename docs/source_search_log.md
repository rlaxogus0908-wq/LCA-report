# Background search log

Search date: 2026-10-08 UTC. Candidate details and unresolved gaps are in [`../data/candidate_mapping.csv`](../data/candidate_mapping.csv).

## TianGong

The [public catalog](https://www.tiangong.earth/en/lca-database) and [TianGong LCDN](https://lcdn.tiangong.earth/) were searched with material names plus production terms. Records inspected include Chinese PP production (`90cdb77a-9999-4bf5-bcb5-3923f8a46274`, version `00.01.005`), brass alloy production (`d58c2083-cf82-402e-8ba1-b14a39d6195a`, version `00.01.005`), cathode copper (`632ea2c6-0980-47dd-920e-14d04ffc957c`, version `01.01.001`), and PVC production (`24fca75a-cefc-483b-8168-e349eb15c25b`, version `00.01.005`). Exact links appear in the mapping table. Public availability varies by version; a description-only record does not provide emissions or an impact score. No TianGong account was available in this run.

## USLCI

The [Federal LCA Commons API](https://www.lcacommons.gov/lca-commons-api-guide) was queried with `type=PROCESS`, `pageSize=50`, and the terms `stainless steel`, `brass`, `copper`, `polypropylene`, `polyvinyl chloride`, `nylon`, `polyoxymethylene`, `polycarbonate`, and `acrylonitrile butadiene styrene`. The official `DEMO_KEY` was used only for initial exploration, as the API guide permits; later queries returned HTTP 429. Automated production use requires a personal data.gov API key, supplied privately through `FLCAC_API_KEY`. The [USLCI release table](https://github.com/FLCAC-admin/uslci-content/blob/dev/docs/release_info/release-downloads.md) lists release `1.2026-09.0`.

The search found material unit-process candidates for stainless 304 coil, virgin PP, suspension-grade PVC, and ABS. It did not return a brass or POM process in the results inspected. Nylon 6/66 and PC hits are bridges to USEEIO; they are not direct cradle-to-gate mass-based resin inventories. A copper bridge likewise needs a sector and price basis. We have not solved their upstream network or downloaded a complete merged package.

## Selection rule

Accept a dataset only after checking the exact product and form, reference amount and unit, geography and year, technology, license, complete exchanges, provider links, and method compatibility. A unit process is not a cumulative factor. If a monetary bridge is chosen later, record sector, currency, price year, purchaser/basic-price basis, unit price, and amount. Do not sum direct emissions with an already cumulative result for the same process.

## Published proxy factors for the numerical scenario

After the user requested a numerical estimate using assumptions, material kg CO2e/kg values were transcribed into [`../data/proxy_factors.csv`](../data/proxy_factors.csv). The main source is the [September 2024 Westminster City Council/WSP embodied-carbon report, PDF page 83](https://www.westminster.gov.uk/sites/default/files/media/documents/EV_R_003%20Embodied%20Carbon%20Evidence%20Study%20Update_0.pdf), which reproduces material/ICE factors. POM uses the [CarbonCloud POM resin page](https://apps.carboncloud.com/climatehub/product-reports/id/9394755343364), and silicone uses a [Global Silicones Council PDMS fluid proxy](https://www.silicones.eu/wp-content/uploads/2019/05/SIL_exec-summary_en.pdf). Electricity uses the [Chinese government's 2024 national average carbon footprint factor, 0.5777 kg CO2e/kWh](https://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/202510/W020251024569470952545.pdf). These are aggregate, already-characterized proxies. Their original GWP factor versions and boundaries are not harmonized; they do not close the TianGong/USLCI process network.
