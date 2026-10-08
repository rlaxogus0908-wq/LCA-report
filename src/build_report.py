"""Build a standalone Korean HTML report from the saved proxy and audit results."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROXY = json.loads((ROOT / "results/proxy_baseline.json").read_text(encoding="utf-8"))
AUDIT = json.loads((ROOT / "results/independent_run.json").read_text(encoding="utf-8"))
SCENARIO = json.loads((ROOT / "data/proxy_scenario.json").read_text(encoding="utf-8"))


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def num(value: float, digits: int = 3) -> str:
    return f"{value:,.{digits}f}"


def link(url: str, label: str) -> str:
    return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}</a>'


total = PROXY["gwp100_proxy_kg_co2e_per_packaged_kettle"]
parts = PROXY["contributions_kg_co2e"]
items = sorted(PROXY["materials"], key=lambda r: r["material_kg_co2e"] + r["additional_conversion_kg_co2e"], reverse=True)
max_item = max(r["material_kg_co2e"] + r["additional_conversion_kg_co2e"] for r in items)
colors = ["#247b78", "#d58141", "#795ba4", "#7a8f37", "#b66169"]
part_labels = [
    ("material_proxy_factors", "재료 proxy"),
    ("additional_component_conversion_electricity", "추가 부품 가공 전력"),
    ("assembly_electricity", "조립 전력"),
    ("inbound_transport", "원료 입고 운송"),
    ("scrap_treatment", "스크랩 처리"),
]
segments = "".join(
    f'<span style="width:{parts[key] / total * 100:.5f}%;background:{colors[i]}" title="{e(label)}: {num(parts[key], 4)} kg CO₂e"></span>'
    for i, (key, label) in enumerate(part_labels)
)
legend = "".join(
    f'<div class="legend-item"><span class="dot" style="background:{colors[i]}"></span><span>{e(label)}</span><strong>{num(parts[key], 3)}</strong></div>'
    for i, (key, label) in enumerate(part_labels)
)
material_rows = "".join(
    f'''<tr><td><strong>{e(r['material'])}</strong><small>{e(r['proxy_product'])}</small></td>
      <td class="right">{num(r['finished_mass_kg'] * 1000, 2)}</td>
      <td class="right">{num(r['factor_kg_co2e_per_kg'], 2)}</td>
      <td class="impact"><div class="rowbar"><span style="width:{(r['material_kg_co2e'] + r['additional_conversion_kg_co2e']) / max_item * 100:.2f}%"></span></div>
      <strong>{num(r['material_kg_co2e'] + r['additional_conversion_kg_co2e'], 3)}</strong></td>
      <td>{link(r['factor_source_url'], '원문 ↗')}</td></tr>'''
    for r in items
)
assumption_rows = [
    ("제조 위치", "중국", "BC1 실제 제조지는 확인되지 않음"),
    ("나일론 종류", "나일론 6", "BOM의 등급은 불명"),
    ("실리콘", "PDMS 유체 계수", "완제품 실링재 배합의 대리값"),
    ("재료 수율", "95% 공통", "실제 재료별 수율 없음"),
    ("별도 부품 가공 전력", "0.5 kWh/kg 구매량", "성형이 계수에 포함된 PP·LDPE는 제외"),
    ("조립 전력", "0.1 kWh/개", "실측값 없음"),
    ("입고 운송", "500 km, 0.1 kg CO₂e/t·km", "운송 거리·수단 추정"),
    ("스크랩 처리", "0.1 kg CO₂e/kg", "재활용 크레딧 없음"),
]
assumptions_html = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in assumption_rows)

document = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BC1 전기주전자 LCA proxy 결과</title>
<style>
:root{{--ink:#172c3b;--muted:#526576;--teal:#247b78;--paper:#f5f7f6;--line:#dce5e5;--warn:#fff4df}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,'Segoe UI',sans-serif;line-height:1.55}}
header{{background:linear-gradient(120deg,#163445,#205d61);color:white;padding:48px max(24px,calc((100vw - 1160px)/2)) 42px}}
header .kicker{{letter-spacing:.16em;text-transform:uppercase;color:#afd8d3;font-weight:700;font-size:.78rem}}h1{{font-size:clamp(1.9rem,4vw,3rem);line-height:1.2;margin:12px 0}}header p{{max-width:800px;color:#e1eded;margin:0}}
main{{max-width:1160px;margin:0 auto;padding:28px 24px 72px}}.grid{{display:grid;grid-template-columns:1.25fr .75fr;gap:20px}}.card{{background:white;border:1px solid var(--line);border-radius:16px;padding:24px;box-shadow:0 7px 22px #1634450b;margin-bottom:20px}}.eyebrow{{font-size:.72rem;letter-spacing:.13em;color:var(--teal);font-weight:800;text-transform:uppercase}}h2{{font-size:1.35rem;margin:6px 0 14px}}h3{{font-size:1.05rem;margin:18px 0 8px}}p{{margin:10px 0;color:var(--muted)}}.metric{{font-size:clamp(2.7rem,6vw,4.7rem);font-weight:800;line-height:1.1;letter-spacing:-.05em;margin:10px 0;color:var(--teal)}}.metric small{{font-size:1rem;letter-spacing:0;font-weight:600;color:var(--muted)}}.badge{{display:inline-block;background:#daf0e9;color:#155a52;border-radius:999px;padding:5px 11px;font-size:.75rem;font-weight:750}}.warning{{background:var(--warn);border-left:4px solid #cc873b;border-radius:8px;padding:13px 16px;color:#704411;font-size:.9rem}}.stack{{display:flex;height:24px;border-radius:999px;overflow:hidden;background:#e7ecec;margin:20px 0}}.stack span{{height:100%}}.legend{{display:grid;grid-template-columns:1fr 1fr;gap:9px 24px}}.legend-item{{display:grid;grid-template-columns:11px 1fr auto;align-items:center;gap:8px;font-size:.86rem;color:var(--muted)}}.legend-item strong{{color:var(--ink)}}.dot{{width:10px;height:10px;border-radius:50%}}.summary{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:16px 0}}.summary div{{background:#f0f6f4;padding:12px;border-radius:10px}}.summary b{{display:block;font-size:1.1rem}}.summary span{{font-size:.75rem;color:var(--muted)}}.tablewrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:.84rem}}th,td{{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}}thead th{{background:#f1f6f5;font-size:.75rem;white-space:nowrap}}tbody tr:last-child td{{border-bottom:0}}td small{{display:block;color:var(--muted);font-size:.72rem}}.right{{text-align:right;white-space:nowrap}}.impact{{min-width:190px;display:flex;align-items:center;gap:12px}}.rowbar{{background:#ecf1f0;height:9px;border-radius:10px;overflow:hidden;flex:1}}.rowbar span{{display:block;background:var(--teal);height:100%;border-radius:10px}}.impact strong{{width:48px;text-align:right}}a{{color:#126a74;text-decoration:none;font-weight:650}}a:hover{{text-decoration:underline}}.method{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.method div{{border:1px solid var(--line);border-radius:10px;padding:13px;font-size:.82rem}}.method b{{display:block;color:var(--teal);margin-bottom:5px}}.foot{{font-size:.77rem;color:var(--muted);margin-top:24px}}.code{{font-family:ui-monospace,Consolas,monospace;background:#edf3f2;border-radius:5px;padding:2px 5px}}@media(max-width:760px){{.grid,.method{{grid-template-columns:1fr}}.summary{{grid-template-columns:1fr 1fr}}.legend{{grid-template-columns:1fr}}.card{{padding:18px}}}}
</style></head><body>
<header><div class="kicker">LCA / CODEX LAB · BC1 KETTLE</div><h1>포장된 1 L 전기주전자<br>공장 출고 전 탄소발자국</h1><p>수업 BOM과 공개 탄소계수로 계산한 가정 기반 시나리오입니다. 원재료 공급, 부품 제조, 조립, 포장을 포함하며 고객 배송·사용·폐기는 제외합니다.</p></header>
<main><div class="grid"><section class="card"><div class="eyebrow">계산된 proxy 시나리오</div><div class="metric">{num(total,3)} <small>kg CO₂e / 포장 주전자 1개</small></div><span class="badge">계산 완료 · 가정 기반 추정치</span><div class="summary"><div><b>860.8 g</b><span>완제품 + 포장 질량 · 출처 확인</span></div><div><b>95%</b><span>재료 수율 · 가정</span></div><div><b>0.5777</b><span>중국 2024 전력 kg CO₂e/kWh · 출처 확인</span></div></div><div class="warning"><strong>방법 해석:</strong> 재료계수는 이미 CO₂e로 환산된 공개 대리값입니다. 원자료의 GWP 특성화 방법·버전이 모두 같다고 검증되지 않아, 이 결과를 “IPCC AR6로 통일된 GWP100” 또는 실측 제품 LCA로 표기하지 않습니다.</div></section>
<section class="card"><div class="eyebrow">기여도</div><h2>어디서 발생하나</h2><div class="stack">{segments}</div><div class="legend">{legend}</div><p style="margin-top:20px">재료 proxy가 총량의 {parts['material_proxy_factors']/total*100:.1f}%를 차지합니다. 상위 재료는 PP, 스테인리스강, 나일론 6 가정입니다.</p></section></div>
<section class="card"><div class="eyebrow">12개 BOM 항목</div><h2>재료별 결과</h2><p>마지막 기여량에는 재료계수와 해당 재료에 추가한 부품 가공 전력이 합산되어 있습니다. 수율 95%로 구매량을 추정했습니다.</p><div class="tablewrap"><table><thead><tr><th>재료 / 선택한 대리 제품</th><th class="right">완제품 g</th><th class="right">계수<br>kg CO₂e/kg</th><th>기여량 kg CO₂e</th><th>계수 출처</th></tr></thead><tbody>{material_rows}</tbody></table></div></section>
<div class="grid"><section class="card"><div class="eyebrow">증거와 가정</div><h2>무엇을 확인했고, 무엇을 정했나</h2><div class="method"><div><b>① BOM · 출처 확인</b>12개 완제품 질량. 주전자 723 g, 포장 137.8 g.</div><div><b>② 재료계수 · 공개 proxy</b>Westminster/WSP 표, POM 제품값, PDMS 업계값.</div><div><b>③ 전력계수 · 출처 확인</b>중국 정부 2024 전국 평균 0.5777 kg CO₂e/kWh.</div><div><b>④ 수율·제조·물류 · 가정</b>아래 값을 바꾸면 결과가 달라집니다.</div></div><div class="tablewrap"><table><tbody>{assumptions_html}</tbody></table></div></section>
<section class="card"><div class="eyebrow">계산식과 한계</div><h2>Characterization과 A 행렬</h2><p><span class="code">재료 영향 = Σ(완제품 kg ÷ 0.95 × kg CO₂e/kg)</span></p><p><span class="code">전력 영향 = (추가 가공 kWh + 조립 kWh) × 0.5777</span></p><p><span class="code">전체 = 재료 + 전력 + 입고 운송 + 스크랩 처리</span></p><p><strong>이 4.062 kg 결과는 A 행렬의 역행렬 계산값이 아닙니다.</strong> 재료계수는 이미 기초 배출량이 특성화된 누적 proxy이므로 IPCC AR6 계수를 다시 곱하지 않습니다.</p><p>별도의 엄밀한 행렬 코드는 <span class="code">A·s=f, g=B·s, h=C·g</span>를 구현하고, <span class="code">numpy.linalg.solve(A,f)</span>로 풉니다. 이는 수학적으로 <span class="code">s=A⁻¹f</span>와 같지만 역행렬을 직접 계산하지 않습니다. A의 상위 공정 투입량과 B의 배출량이 있어야 전체 영향이 나오며, 모르는 데이터를 역행렬만으로 알아낼 수는 없습니다.</p><div class="warning"><strong>엄밀한 모델의 남은 데이터:</strong> 감사 결과 {len(AUDIT['blocking_items'])}개. 재료별 구매량 12, 가공공정 12, 검증된 공급자 12, 공통 설정 7입니다. 이들은 proxy 계산에서 명시적 가정·계수로 대체되었습니다.</div></section></div>
<section class="card"><div class="eyebrow">재현과 출처</div><h2>같은 결과 다시 만들기</h2><p>프로젝트 폴더에서 <span class="code">python src/proxy_lcia.py</span>, <span class="code">python src/build_report.py</span>를 차례로 실행합니다. 설정은 <span class="code">data/proxy_scenario.json</span>, 재료계수는 <span class="code">data/proxy_factors.csv</span>에 있습니다. 결과 원본은 <span class="code">results/proxy_baseline.json</span>입니다.</p><p>주요 출처: {link('https://tiangong-lca-decision-lab.ecodino73.chatgpt.site/classroom/kettle-bom.csv','수업 BOM')} · {link('https://www.westminster.gov.uk/sites/default/files/media/documents/EV_R_003%20Embodied%20Carbon%20Evidence%20Study%20Update_0.pdf','Westminster/WSP 재료계수 표')} · {link('https://apps.carboncloud.com/climatehub/product-reports/id/9394755343364','POM proxy')} · {link('https://www.silicones.eu/wp-content/uploads/2019/05/SIL_exec-summary_en.pdf','PDMS proxy')} · {link('https://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/202510/W020251024569470952545.pdf','중국 2024 전력계수')}</p><p class="foot">생성일: {e(PROXY['run_date_utc'])} · 실측 생산자료, 완전한 공급망 연결, 통일된 특성화계수, 통계적 불확실성 분석은 포함되지 않았습니다. GitHub 저장소 URL과 커밋 SHA는 사용자가 업로드 후 기입해야 합니다.</p></section></main></body></html>'''

path = ROOT / "report.html"
path.write_text(document, encoding="utf-8")
print(path)
