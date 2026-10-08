# BC1 주전자 GWP100 계산 가능성 평가

기준일: 2026-10-08. 선언 단위는 공장 출고 시점에 포장된 BC1 1 L 플라스틱 전기주전자 1개이다. 고객 배송, 사용, 폐기는 제외한다.

## 실제 출처로 확인한 값

| 값 | 확인 결과 | 출처 |
|---|---:|---|
| 주전자 완제품 질량 | 723 g | [수업 BOM](../data/kettle_bom.csv), [원연구 Task 4](https://publica-rest.fraunhofer.de/server/api/core/bitstreams/3df3f4d6-3717-4261-99e3-a232323111d6/content) |
| 포장재 완제품 질량 | 137.8 g | 같은 BOM |
| 총 완제품 및 포장 질량 | 860.8 g | BOM 12행의 합계; 코드 재계산 |
| IPCC AR6 GWP100 계수 | 화석 CO2 1, 화석 CH4 29.8, 비화석 CH4 27.0, N2O 273 kg CO2-eq/kg | [IPCC AR6 WGI 제7장 표 7.15](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/) |
| USLCI 배포 버전 | 1.2026-09.0 | [공식 배포 목록](https://github.com/FLCAC-admin/uslci-content/blob/dev/docs/release_info/release-downloads.md) |

이 질량은 **완성된 부품과 포장재의 질량**이다. 구매 원료량, 제조 전력, 공정 손실, 공급망 배출량이 아니다. [후보 매핑](../data/candidate_mapping.csv)의 데이터셋 ID도 생산 공정 후보가 있다는 뜻이지, 해당 공정의 연결된 배출 인벤토리를 확보했다는 뜻이 아니다.

## proxy 시나리오 실행 결과

사용자가 proxy/가정값으로 반드시 수치를 계산하도록 요청하여 [`proxy_lcia.py`](../src/proxy_lcia.py)를 실행했다. 결과는 **4.062264 kg CO2e/포장 주전자 1개**이다. [`proxy_baseline.json`](../results/proxy_baseline.json)에 12개 재료별 기여량과 중간 계산을 저장했다. 이 값은 실제 TianGong/USLCI 공급망을 모두 연결한 엄밀한 LCA가 아니라 **가정 조건부 추정치**이다.

원료 proxy 계수는 [Westminster City Council/WSP 보고서의 재료 탄소계수 표(PDF 83쪽)](https://www.westminster.gov.uk/sites/default/files/media/documents/EV_R_003%20Embodied%20Carbon%20Evidence%20Study%20Update_0.pdf), [POM 수지 제품 계수](https://apps.carboncloud.com/climatehub/product-reports/id/9394755343364), [실리콘 PDMS 유체 업계 연구값](https://www.silicones.eu/wp-content/uploads/2019/05/SIL_exec-summary_en.pdf)에서 가져왔다. 2024년 중국 전국 평균 전력 탄소발자국 계수 **0.5777 kg CO2e/kWh**는 [중국 생태환경부 발표 표 1](https://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/202510/W020251024569470952545.pdf)을 사용했다. 12개 계수와 각 제품 대리 선택은 [`proxy_factors.csv`](../data/proxy_factors.csv)에 적었다.

| 가정 | 사용값 | 실제로 모르는 것 |
|---|---:|---|
| 제조 위치 | 중국 | BC1 실제 조립국 |
| 나일론 등급 | 나일론 6 | 실제 6/66 등급 |
| 실리콘 대리 물질 | PDMS 유체 | 실제 실링재 배합 |
| 모든 재료의 수율 | 95% | 재료별 실제 손실률 |
| 별도 성형 전력 | 가공이 계수에 포함되지 않은 재료에 0.5 kWh/kg 구매량 | 공정별 실제 전력 |
| 조립 전력 | 0.1 kWh/개 | 조립공장 전력 |
| 원료 입고 운송 | 500 km, 0.1 kg CO2e/t·km | 공급자 위치/운송수단 |
| 스크랩 처리 | 0.1 kg CO2e/kg 스크랩, 재활용 크레딧 없음 | 처리 방식·할당 |

재료 계수는 이미 CO2e로 특성화된 값이다. 따라서 IPCC AR6 계수를 재적용하지 않았다. **원재료 proxy마다 원래 사용된 GWP 특성화 방법과 버전이 일치하는지 확인되지 않았다.** 이 수치를 “IPCC AR6 GWP100 검증 결과”라고 표기하면 안 된다. PP 사출성형과 LDPE 필름 계수에는 가공이 포함된 것으로 처리하여 별도 성형 전력을 추가하지 않았다. 95% 수율 보정은 계수에 이미 포함된 평균 손실과 중복될 가능성이 있다. 수업 사이트의 `0.0175 kg CO2e/kWh`는 별도 가상 행렬 검산이다.

**A 행렬 관련 확인:** 4.062264 kg 결과는 역행렬을 사용한 계산이 아니다. 엄밀한 공정 모델의 코드는 `A·s=f`를 `numpy.linalg.solve(A,f)`로 풀며, 수학적으로 `s=A⁻¹f`와 같다. 다만 A에 상위 공급자의 투입 계수가, B에 기초 배출량이 입력되어 있어야 한다. 역행렬은 알려진 공급망을 거슬러 필요한 활동량을 구할 뿐, 비어 있는 공정 데이터나 배출계수를 만들어내지 않는다.

| 기여 항목 | kg CO2e/개 |
|---|---:|
| 12개 재료 proxy | 3.801339 |
| 추가 부품 가공 전력 | 0.153319 |
| 조립 전력 | 0.057770 |
| 입고 운송 | 0.045305 |
| 스크랩 처리 | 0.004531 |
| **합계** | **4.062264** |

## 엄밀한 공정 모델의 미결정 사항

## 정확한 계산 장애물

[`results/gap_register.csv`](../results/gap_register.csv)는 실행 시점의 감사 코드가 생성했다. 43개 항목은 다음처럼 묶인다.

| 묶음 | 항목 수 | 확보해야 할 것 |
|---|---:|---|
| 원료 구매량 | 12 | 각 재료의 수율/스크랩률 또는 실제 구매 kg/개. `완제품 kg ÷ 수율`을 사용하려면 수율 근거 필요 |
| 부품 및 포장 가공 | 12 | 사출·압출·금속 성형·상자 제작 등의 공정, 처리량, 에너지; 선택한 공급자 데이터가 이 단계를 포함한다면 그 증거 |
| 재료 공급자 | 12 | 제품·등급·지역이 맞는 수용 데이터셋, 정확한 버전/기준 단위, 전체 교환 목록 및 상위 공급자 연결. 후보만으로는 부족 |
| 공통 모델 설정 | 7 | 제조지/전력망, 조립 전력, 기타 조립 에너지, 원료 입고 운송 경계/량, 스크랩 처리 및 할당, 공급망 전체 연결, 실제 배출 흐름에 맞는 특성화계수 |

특히 나일론은 6/66 중 등급이 불명이고, 폴리카보네이트의 USLCI 검색 결과는 USEEIO 연결용 브리지라서 kg 원료 데이터로 바로 사용할 수 없다. POM, 실리콘, LDPE 필름, 판지 상자에 대해서는 이 프로젝트에서 검증·수용된 생산 및 가공 공정이 없다. 다른 재료도 후보 기록의 직접 배출만 꺼내 전체 공급망 결과로 간주할 수 없다. [TianGong](https://www.tiangong.earth/en/lca-database)은 공개 목록과 상세 교환 데이터의 접근 범위가 기록별로 다르다고 명시한다. [LCA Commons](https://www.lcacommons.gov/lca-collaboration/)는 공개 데이터에 계정 없이 접근할 수 있지만, [API 안내](https://www.lcacommons.gov/lca-commons-api-guide)는 `DEMO_KEY`를 탐색용으로 제한한다. 이번 탐색에서도 HTTP 429가 발생했다.

## 실행 결과

`python src/lcia.py audit`를 실행해 BOM 12행과 723 g + 137.8 g = 860.8 g을 통과시켰다. [`results/independent_run.json`](../results/independent_run.json)의 **엄밀한 공정 모델** `gwp100_kg_co2e_per_packaged_kettle`은 여전히 `null`이다. 이 값과 proxy 추정치 4.062264를 혼동하면 안 된다. 비어 있는 실제 측정값을 0으로 대체하지 않고, 별도의 proxy 시나리오에서만 수치 가정을 명시했다.

다음 작업은 구매량/수율과 제조 공정을 명시하고, 사용 가능한 TianGong 또는 USLCI 원시 데이터의 라이선스·교환 목록을 확인해 공급자망을 연결한 다음, **실제** 기초 흐름의 이름·배출 구획·단위에 맞는 GWP100 계수를 모두 매칭하는 것이다. 이후 행렬 계산을 실행할 수 있다.
