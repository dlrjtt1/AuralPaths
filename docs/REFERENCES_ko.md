# AuralPaths 참고문헌·자료 정리

작성: 2026-11-03 · 대상: AuralPaths v0.5 (`brir_proto.py`, `engine_geom.js`, `viewer_template.html` 외)

**표기 원칙**
- 각 항목은 **무엇을 썼나 → 어디에 썼나(파일·기능) → 어떻게 썼나 / 한계** 순서로 적었다.
- 링크: DOI는 이번 작업 중 웹에서 확인한 것만 적었다. 확인하지 못한 문헌은 Google Scholar 검색 링크로 대신하고 "DOI 미확인"이라고 표시했다.
- "공학적 가정" 표시는 문헌 근거가 없고 이 도구에서 정한 값이라는 뜻이다.

---

## 1. 한눈에 보기

| 만든 것 | 쓴 것 | 파일 |
|---|---|---|
| 바이노럴 렌더링 (초기부 HRIR, 후기부 확산음장 이득) | KU100 HRIR 세트 (Bernschütz 2013) | `hrir/KU100.sofa`, `brir_proto.load_hrir` |
| 헤드폰 보정 | KU100 컴필레이션의 HD600 HPCF (Bernschütz 2013) | `hrir/HPCF_Sennheiser-HD600.mat` |
| 슈박스·그린 홀 Python 기준 계산 | pyroomacoustics (ISM + 광선추적) | `brir_proto.py`, `geometry.py` |
| 후기 잔향 양귀 상관 | Habets, Cohen & Gannot 2008 (상관 제약 혼합) | `coherent_pair`, `coherentPair` |
| 방향성 후기 잔향 | 위 혼합법의 복소 상관 확장 + 자체 광선추적 | `dirrays.py`, `late_field`, `lateDir` |
| 1차 모서리 회절 | UTD: Kouyoumjian & Pathak 1974, Tsingos et al. 2001 | `diffraction.py`, `GEOM.diffract` |
| 정반사 계수 (유한 반사판·산란 손실) | Rindel 2005 (Kirchhoff–Fresnel), Rindel 1992 | `reflections.py`, `GEOM.specFactor` |
| 재료 보정 (실측 T30에 맞추기) | ISO 3382-1 Annex A (JND 5 %) | `calibrate.py` |
| 회절 실측 검증 (RS5, 500 Hz–2 kHz 평균 1.8 dB 차) | BRAS RS5 (Aspöck et al. 2020) | `validate_bras.py`, `validation/` |
| 실제 홀 위치별 검증 (CR3·CR4: T30 8–11% 김, C80·Ts 0.8–2.3 JND, 1차 반사 중앙값 CR3 +1.6 dB·CR4 +2.7 dB(보정 전 +6.5)) | BRAS CR3·CR4 (Aspöck et al. 2020) | `validate_bras_cr.py`, `validation/bras_CR*` |
| OBJ 3D 홀 계산·2.5D 변환 | 복셀 채우기 + 메시 Sabine 면적 → 2.5D Eyring 지수(자체 구현), fast-simplification(MIT) | `geometry.py`, `obj_to_hall.py` |
| 실측 홀 지표 대조 (ULH 500 Hz–4 kHz 약 1 JND 이내, STC 약 15% 김) | Fratoni 데이터셋(CC BY 4.0), Fratoni 2022, Fratoni et al. 2023 | `validate_fratoni.py`, `validation/fratoni_*` |
| 좌석 dip — **만들지 않음** | Meyer, Tahvanainen, Saarelma & Lokki 2023 (모델 부재 확인) | README "Seat dip" |
| 음원 지향성 CSV | B&K BP 1689, NTi DS3 데이터시트, Meyer CQ-1 / UPM-1P 데이터시트 | `directivity/*.csv` |
| SOFA 지향성 불러오기 | h5wasm (브라우저) | `viewer_template.html` |
| 도면 PDF 불러오기 | pdf.js (브라우저) | `viewer_template.html` |

---

## 2. 시뮬레이션 엔진

### 2.1 실내음향 계산: pyroomacoustics
- **무엇:** pyroomacoustics 0.10.1 (Python 패키지). 근거 논문: Scheibler, Bezzam & Dokmanić (2018), ICASSP. DOI 미확인 → [Google Scholar](https://scholar.google.com/scholar?q=Pyroomacoustics+A+Python+package+for+audio+room+simulation+and+array+processing+algorithms)
- **어디:** `make_room`, `energy_hist`, `early_binaural`, `geometry.pra_walls`
- **어떻게:**
  - 슈박스: 고차 ISM 에너지를 비간섭(incoherent)으로 합산한다.
  - 그린 홀: ISM에 광선추적의 잔여분을 더한다. H = H_ism + max(0, smooth(H_rt) − smooth(H_ism)).
  - 브라우저 엔진(`engine_geom.js`)은 같은 모델을 독자적으로 구현한 것이다. 같은 형상에서 허상 목록이 pyroomacoustics와 정확히 일치하는 것을 확인했다.
- **발견한 문제 (v0.5에서 수정):** 0.10의 광선추적 히스토그램에는 공기흡음이 빠져 있다(켜고 끈 결과가 동일). 그래서 시간 칸마다 exp(−m·c·t)를 직접 곱하도록 고쳤다.

### 2.2 1차 모서리 회절: UTD
- **무엇:**
  - Kouyoumjian, R. G., & Pathak, P. H. (1974). A uniform geometrical theory of diffraction for an edge in a perfectly conducting surface. *Proc. IEEE*, 62, 1448–1461. DOI 미확인 → [Google Scholar](https://scholar.google.com/scholar?q=A+uniform+geometrical+theory+of+diffraction+for+an+edge+in+a+perfectly+conducting+surface) (서지는 [Wikipedia: UTD](https://en.wikipedia.org/wiki/Uniform_theory_of_diffraction)에서 확인)
  - Tsingos, N., Funkhouser, T., Ngan, A., & Carlbom, I. (2001). Modeling acoustics in virtual environments using the uniform theory of diffraction. *SIGGRAPH 2001*. [doi:10.1145/383259.383323](https://doi.org/10.1145/383259.383323)
- **어디:** `diffraction.py` (Python), `GEOM.edges` / `GEOM.diffract` (브라우저). 두 구현의 차이는 1e-10 이내다.
- **어떻게:**
  - 구면파 입사, 강체 쐐기의 회절계수를 쓴다.
  - 반사항에는 각 면의 R = √(1−α)를 곱한다. 이것은 Tsingos 등이 쓴 경험적 처리다.
  - 전이함수 F(X)는 X ≤ 16에서 멱급수, X > 16에서 점근급수로 계산한다.
  - 볼록 모서리만 대상으로 하고, 회절점 방향의 HRIR로 렌더링한다.
- **한계:**
  - 1차만 계산한다. 반사+회절 조합과 모서리 끝점 회절은 없다.
  - UTD는 고주파 점근해라서 저주파와 모서리 근처에서 오차가 커진다.
  - 더 정확한 대안은 BTM 계열의 시간영역 해석해다. 예: Svensson, Fred & Vanderkooy (1999), JASA, DOI 미확인 → [Google Scholar](https://scholar.google.com/scholar?q=An+analytic+secondary+source+model+of+edge+diffraction+impulse+responses). 계산량 때문에 채택하지 않았다.

### 2.2a 정반사 계수: 유한 반사판(Kirchhoff–Fresnel)과 산란 손실 (2026-11-05)
- **무엇:**
  - Rindel, J. H. (2005). Reflection of sound from finite-size plane and curved surfaces. 150th ASA meeting, Minneapolis, *J. Acoust. Soc. Am.* 118(3), 4pAAb3 (초록). DOI 미확인 → 발표 자료 [core.ac.uk/download/13729852.pdf](https://core.ac.uk/download/13729852.pdf). 직사각 반사판의 두 단면 Fresnel 적분식 K = ½[(C(v₂) − C(v₁))² + (S(v₂) − S(v₁))²], a* = 2a₁a₂/(a₁ + a₂)를 그대로 썼다.
  - Rindel, J. H. (1992). Acoustic design of reflectors in auditoria. *Proc. Institute of Acoustics* 14(2). [PDF](https://www.ioa.org.uk/system/files/publications/JH%20RINDEL%20ACOUSTIC%20DESIGN%20OF%20REFLECTORS%20IN%20AUDITORIA.pdf). 한계 주파수 f_g = c a*/(2 S cos θ), 가장자리 반사점에서 −6 dB(K = ¼)의 확인용.
- **어디:** `reflections.py`(Python), `engine_geom.js`의 `specFactor`·`panels`·`fresnel`(브라우저). Fresnel 적분은 두 쪽 모두 같은 급수·점근 전개로 직접 구현했다(scipy 대비 오차 4·10⁻⁷, JS–Python 차이 10⁻¹⁶). 허상 에너지는 4차까지 2·10⁻⁶ 이내로 일치.
- **어떻게:** 허상 경로의 반사마다 (1 − s)·K₁·K₂를 곱한다. 패널은 1 cm 이내로 닿고 법선 차 2° 이내인 면들. 고차 반사에 a₁, a₂를 펼친 경로 길이로 쓰는 것은 공학적 확장이다(Rindel의 식은 반사 1회용).
- **근거와 결과:** BRAS CR4에서 흰 패널(콘크리트 보 사이의 유한한 판) 반사가 +8.6 dB 과대였던 진단에서 시작했다. 적용 후 같은 반사 35개의 예측 − 실측 중앙값 +6.5 → +2.7 dB. CR3는 +1.2 → +1.6 dB로 거의 그대로. 패널 허용각 10°는 CR4에서 +4.1 dB로 나빠 채택하지 않았다.
- **한계:** 반사 하나하나의 정확도(상관)는 CR4에서 여전히 낮다(r 0.35). 곡면 반사판의 집속·확산은 다루지 않는다.

### 2.3 후기 잔향의 양귀 상관
- **무엇:** Habets, E. A. P., Cohen, I., & Gannot, S. (2008). Generating nonstationary multisensor signals under a spatial coherence constraint. *J. Acoust. Soc. Am.*, 124(5). [doi:10.1121/1.2987429](https://doi.org/10.1121/1.2987429)
- **어디:** `coherent_pair`, `coherent_pair_complex` (Python), `coherentPair`, `lateDir` (브라우저)
- **어떻게:**
  - 두 독립 잡음을 주파수별로 L = cos a·n1 + sin a·n2, R = cos a·n1 − sin a·n2로 섞는다(a = arccos(Γ)/2). 논문의 2채널 경우에 해당한다.
  - 목표 Γ(f)는 KU100 전 방향의 면적 가중 확산음장 상관이다.
  - v0.5부터 그린 홀에서는 광선추적으로 얻은 실제 도래 방향 분포로 Γ(복소)와 양귀 에너지를 구한다. 오른쪽 채널에 위상을 회전시키는 방식은 이 논문의 확장으로 직접 만든 것이다(공학적 구현).
- **한계:** 후기부 전체에 방향 분포 하나만 쓴다(시간에 따른 변화 없음). 음원 지향성은 방향 분포에 반영하지 않는다.

### 2.4 잔향 지표·보정 기준
- **무엇:** ISO 3382-1 Annex A. 반향 지표의 JND로 EDT 5 % 등을 제시한다. 규격 원문은 유료여서 웹에서 이번에 다시 확인하지는 않았다.
- **어디:** `calibrate.py`의 허용 오차(기본 2 %)를 정할 때 참고값으로 썼다.
- **공학적 가정:** 갱신식 k ← k·T_sim/T_meas(Sabine식 비례)와 계수 범위 0.01–0.95.

---

## 3. 바이노럴 데이터

### 3.1 KU100 HRIR
- **무엇:** Bernschütz, B. (2013). A Spherical Far Field HRIR/HRTF Compilation of the Neumann KU 100. *Proc. AIA-DAGA 2013*, Merano, 592–595. [PDF](https://audiogroup.web.th-koeln.de/FILES/AIA-DAGA2013_HRIRs.pdf) · 데이터: [Zenodo 3928297](https://zenodo.org/records/3928297) (HRIR_FULL2DEG.sofa)
- **어디:**
  - `load_hrir`: 초기부 최근접 HRIR, 확산음장 대역 이득, 확산 상관.
  - `late_dir_tables`: 방향 칸별 표.
  - `export_viewer.hrir_subset`: 브라우저용으로 약 4° 간격으로 솎아 낸 세트.
- **한계:** HRIR 보간 없이 최근접 방향만 쓴다. 비개인화 HRTF다. 비개인화 HRTF의 정위 문제는 계획서의 Wenzel et al. (1993)을 참조.

### 3.2 HD600 헤드폰 보정 필터
- **무엇:** 같은 KU100 컴필레이션(Zenodo 3928297)의 HPCF. 라이선스는 CC BY 3.0으로 기록되어 있으며, 재배포할 때는 저작자 표시가 필요하다.
- **어디:** `load_hpcf`, `run.py`(`brir_Sennheiser-HD600/`), `make_stimuli.py`(최종 믹스에만 적용).
- **한계:** KU100 더미헤드에서 측정한 값이라 청취자 개인의 착용 상태는 반영되지 않는다.

---

## 4. 음원 지향성 데이터

| 파일 | 출처 | 만든 방법 | 상태 |
|---|---|---|---|
| `dodeca_HBK_4292L.csv` | B&K Product Data **BP 1689**, Fig. 6 (수평면, 1/2/4/8 kHz) | PDF 벡터 곡선을 5° 간격으로 추출(링 맞춤 잔차 0.09 dB). 1 kHz 미만은 "유의한 편차 없음"이라는 문구에 따라 무지향 처리 | 실측(모델 대표값). 수직면은 미상이라 수평면과 같다고 가정 |
| `dodeca_NTi_DS3.csv` | NTi Audio **DS3** 데이터시트 2쪽 극좌표 (1/2/4/5 kHz) | 래스터 이미지를 색상으로 추적. 판독 불확도 약 ±0.5 dB | 실측(모델 대표값). 어느 평면인지 미표기. 캡션의 첫 번째 대역이 실선이라고 가정 |
| `meyer_CQ-1_nominal.csv` | Meyer Sound **CQ-1** 데이터시트·매뉴얼 (80°×40°) | 공칭 커버리지에 AuralPaths 일반 패턴을 적용 | **실측 아님.** Meyer는 극좌표 데이터를 공개하지 않는다(MAPP 내부에만 있음) |
| `meyer_UPM-1P_nominal.csv` | Meyer Sound **UPM-1P** 데이터시트 (100°×100°) | 위와 같음. 커버리지 정의 레벨이 미표기라 −6 dB로 가정 | **실측 아님** |

- **일반 PA 패턴(공학적 가정):** BW(f) = min(360°, cov·max(1, (2000/f)^0.7)), 진폭 ((1+cos θ)/2)^n, 하한 −30 dB.

**검토했지만 쓰지 않은 지향성 DB** (README Third-party에 기록)
- TU Berlin 악기·소프라노 지향성 (Ackermann, Brinkmann & Weinzierl; CC BY-SA 4.0)
- TH Köln 음성 지향성 (Pörschmann & Arend; CC BY 4.0)
- IEM DirPat 스피커 (Brandner; public domain mark)
- 피아노 지향성: 목적에 맞는 공개 데이터를 찾지 못했다. Meyer의 *Acoustics and the Performance of Music*(서적)도 검토했지만, 그림을 그대로 쓰기에는 부족하다고 판단해 진행하지 않았다(사용자 결정).

---

## 5. 검증·문헌 확인

### 5.1 BRAS (회절·실제 홀 실측 비교용)
- **무엇:** Aspöck, L., Brinkmann, F., Ackermann, D., Weinzierl, S., & Vorländer, M. (2020). *BRAS – Benchmark for Room Acoustical Simulation* (v3). TU Berlin DepositOnce. [doi:10.14279/depositonce-6726.3](https://doi.org/10.14279/depositonce-6726.3) · 관련 논문 doi:10.1016/j.apacoust.2020.107867 (저장소 페이지에 표기된 것)
- **라이선스:** 저장소 페이지 기준 CC BY-SA 4.0. 예전에 CC BY-NC-ND라고 말했던 것은 틀렸다.
- **어디:** `validate_bras.py`. RS5(무한 모서리: MDF 칸막이, 높이 2.07 m, 4×4 위치, Genelec 8020c, 44.1 kHz)의 게이트 IR을 UTD 예측과 1/3옥타브로 비교한다.
- **상태 (2026-11-03 실행):** RS5의 16개 RIR을 UTD + 바닥 영상 모델과 비교했다. 500 Hz–2 kHz 평균 절대 차이는 그림자 위치 11개에서 2.2 dB, 전체 16개에서 1.8 dB다. 예측이 평균 0.1–1.9 dB 높은데, 스피커 응답·지향성, 칸막이 두께(25 mm), 공기흡음을 넣지 않은 영향이 포함된다. 음원이나 수음점이 바닥 높이인 3개는 칸막이 투과음으로 보이는 성분이 먼저 도달한다(모델 밖). 결과 파일: `validation/bras_RS5.png/.csv/.md`. RS6(유한 물체)와 RS7(좌석 dip)은 다중 회절이 필요해 이 모델의 범위 밖이다.
- **CR3·CR4 (2026-11-05 실행, `validate_bras_cr.py`):** 실제 홀 두 곳(CR3 실내악 홀 3331 m³, CR4 대학 강당 8657 m³)의 12면체 RIR 각 10개를 3D 모델(SketchUp → Blender OBJ)과 BRAS `fitted_estimates` 재료로 위치별 비교했다. T30은 7–18% 길다(Eyring으로 맞춘 계수는 비확산 음장의 광선추적에는 작다, 슈박스·타일 메시 확인으로 엔진 경로 문제는 배제). C80·C50·Ts는 0.9–1.6 JND. LS1으로 한 번 보정하면 보정 밖 LS2의 T30이 CR4 0.8 JND, CR3 1.6 JND. 1차 반사는 CR3에서 시각·레벨이 맞고(+1.6 dB 중앙값), CR4는 처음 +6.5 dB 과대였으나 유한 반사판 계수(2.2a) 후 같은 반사로 +2.7 dB(반사 하나하나의 상관은 낮음). 발코니가 있는 홀의 2.5D 버전은 잔향은 대체로 유지하지만 개별 초기 반사는 맞지 않는다. 이 과정에서 `obj_to_hall.py`의 평면 외곽선 버그(여러 조각이 하나로 이어짐)를 찾아 고쳤다. 결과: `validation/bras_CR3.*`, `bras_CR4.*`.

### 5.2 좌석 dip — 모델 부재 확인
- **무엇:** Meyer, J., Tahvanainen, H., Saarelma, J., & Lokki, T. (2023). Investigation of the seat-dip effect using finite-difference time-domain simulations. *J. Acoust. Soc. Am.*, 154(3), 1628–1639. [doi:10.1121/10.0020826](https://doi.org/10.1121/10.0020826)
- **결론:**
  - 해석적 모델들은 정성적이거나 실측과 맞지 않는다(Takahashi 1997, Ishida 1995, Sakurai et al. 1993; 원문은 위 논문 안에서 인용된 것으로만 확인했다).
  - 좌석마다 적용할 수 있는 매개변수 모델이 없어서 **구현하지 않았다.**
- **참고 수치(FDTD, 단순화 형상):**
  - 80–100 Hz와 약 250 Hz에 dip이 나타난다.
  - 좌석 아래 공간, 단의 기울기, 무대 높이에 의존한다.
  - 주로 초기 응답에서 나타난다.
- **앞으로의 선택지:** 2단계 실측의 좌석 구역별 응답을 쓰거나, 파동 기반 시뮬레이션을 하는 것.

### 5.3 시뮬레이션 신뢰도 근거 (계획서에서 인용)
- Brinkmann, F., Aspöck, L., Ackermann, D., Lepa, S., Vorländer, M., & Weinzierl, S. (2019). A round robin on room acoustical simulation and auralization. *J. Acoust. Soc. Am.*, 145(4), 2746–2760. [doi:10.1121/1.5096178](https://doi.org/10.1121/1.5096178)
- 용도: 기하음향 시뮬레이션의 한계를 서술할 때 인용(계획서 3장). AuralPaths 코드에서 직접 쓰지는 않았다.

### 5.4 Fratoni 데이터셋 (실측 홀 지표 대조용)
- **무엇:** Fratoni, G. *Materials for calibrating four complex virtual environments through acoustic simulations*. Mendeley Data, v1. [doi:10.17632/y7xnv6xg5s.1](https://doi.org/10.17632/y7xnv6xg5s.1). 홀 4곳(TCB, DUS, STC, ULH)의 SketchUp 모델, ISO 3382-1 실측 지표(음원별 수음점 평균), 경계 조건(GA용 흡음·산란, FDTD용 LRC), FDTD IR.
- **라이선스:** CC BY 4.0(데이터셋 페이지 표기).
- **관련 문헌:**
  - Fratoni, G. (2022). Simulazioni acustiche di ambienti complessi tramite algoritmi FDTD innovativi. *48° Convegno Nazionale AIA*, Matera. ISBN 978-88-88942-62-9. DOI는 찾지 못했다. 표 1(체적·좌석 수: 타원형 홀 950 m³, 계단식 강의실 900 m³, 각 200석)을 형상 확인에 썼다.
  - Fratoni, G., D'Orazio, D., & Garai, M. (2023). Uncertainty of input data for wave-based room acoustic simulations in large non-trivial environments. *Forum Acusticum 2023*, Turin. [doi:10.61782/fa.2023.1114](https://doi.org/10.61782/fa.2023.1114). CC BY 3.0. Odeon에서 GA 계수를 실측에 맞춘 절차와, 보정된 GA의 잔차(오페라 극장 4곳, 500–1000 Hz T30 −0.06 … +0.12 s)를 비교 기준으로 인용했다. 이 논문의 홀 4곳은 오페라 극장(그림 1(a)의 25,400 m³는 TCB와 같다)이며 ULH·STC는 포함되지 않는다.
  - Christensen, C. L., & Rindel, J. H. (2005). A new scattering method that combines roughness and diffraction effects. *Forum Acusticum 2005*, Budapest. [DTU Orbit](https://orbit.dtu.dk/en/publications/a-new-scattering-method-that-combines-roughness-and-diffraction-e/). Odeon이 산란 계수에 면 크기·경로 길이에 따른 회절 산란을 더한다는 근거(STC 차이의 해석에 사용).
- **어디:** `validate_fratoni.py`(ULH, STC), `obj_to_hall.py`. TCB와 DUS는 박스석·발코니가 있어 2.5D 범위 밖이다.
- **상태 (2026-11-05 실행):** ULH는 3D 메시 기준 500 Hz–4 kHz에서 EDT·T30·C50·Ts가 약 1 JND 이내, 125–250 Hz에서 T30이 1–2 JND 짧다. STC는 3D 메시·2.5D 모두 T30이 약 15% 길다(입력이 Odeon용으로 보정된 영향으로 해석, 엔진 오류는 슈박스 확인에서 보이지 않음). 위치는 시트 그림에서 읽었고(±0.3 m), STC 재료 대응 일부는 판단이다. 결과 파일: `validation/fratoni_*`.

---

## 6. 브라우저 쪽 외부 라이브러리 (논문 아님)

| 라이브러리 | 용도 | 라이선스 | 비고 |
|---|---|---|---|
| h5wasm 0.10.3 | 지향성 SOFA(HDF5) 읽기 | NIST 소프트웨어 라이선스 (HDF5 포함) | 사용할 때만 jsDelivr에서 불러옴, 번들하지 않음 |
| pdf.js 3.11.174 | 도면 PDF 밑그림 | Apache 2.0 | 사용할 때만 cdnjs에서 불러옴 |

---

## 7. 연구계획서 쪽 문헌 (시뮬레이터 코드에는 직접 쓰지 않음)

전체 서지는 `2026-10-24_Research_Proposal_Draft.md` 6장에 있다. 아래는 주제별 위치만 정리한 것이다. 각 주장을 인용하기 전에 원문에서 해당 내용을 다시 확인할 것.

- **선행음 효과 기초:** Wallach, Newman & Rosenzweig (1949); Haas (1951/1972); Litovsky et al. (1999); Litovsky & Shinn-Cunningham (2001); Brown, Stecker & Tollin (2015); Clifton et al. (1994); Ege et al. (2018); Blauert (1996, Ch. 3, [doi:10.7551/mitpress/6391.003.0007](https://doi.org/10.7551/mitpress/6391.003.0007))
- **확성·투사음 시나리오:** Wühle, Merchel & Altinsoy (2019); Ootomo et al. (2007); Hashimoto & Kimura (2001); Davis, Patronis & Brown (2013, Ch. 21)
- **전기음향 강화·홀 측정:** Griesinger (1999); Möller & Pätynen (2025); Möller & Błasiński (2023); Adelman-Larsen (2023); Cassidy et al. (2026, 제목 TODO)
- **지각·평가 척도:** Larsen et al. (2008, DRR JND); Le Bagousse et al. (2012); Larrosa-Navarro et al. (2023, C80); Gabrielsson et al. (1990); Kuusinen (2011)
- **BRIR·HRTF:** Bacila & Lee (2019); Bernschütz (2013); Wenzel et al. (1993)
- **본인 파일럿:** You, Kamekawa & Marui (2026a, 日本音響学会 2-5-11); 유동균 외 (2026b, 학회명 TODO)
- **계획서에 남아 있는 TODO:** Hidaka (2005), Christensen et al. (2013), Pätynen et al. (2013), Moore & Hill (2017), Hill (2024)의 제목·출처 확인

---

## 8. 버전별로 무엇을 근거로 바꿨나 (요약)

| 시점 | 변경 | 근거 |
|---|---|---|
| 초기 | 슈박스 ISM + KU100 렌더링 | pyroomacoustics, Bernschütz 2013 |
| 그린 홀 도입 | 2.5D 형상, 자체 JS 엔진, pyroomacoustics와 교차 확인 | (자체 구현) |
| HD600 보정 | HPCF 적용 | Bernschütz 2013 컴필레이션 |
| 후기 양귀 상관 | 확산음장 상관 잡음 | Habets et al. 2008 |
| 지향성 | CSV/SOFA 불러오기, 12면체·Meyer CSV | B&K BP 1689, NTi DS3, Meyer 데이터시트, h5wasm |
| 보정 도구 | 실측 T30에 재료 맞춤 | ISO 3382-1 Annex A |
| **v0.5** | 반자동 트레이스(축척 지정, 도면 선 스냅), UTD 1차 회절, 방향성 후기부, 공기흡음 버그 수정, Python 초기부 확산 에너지 추가, BRAS 스크립트, 좌석 dip 검토 | Kouyoumjian & Pathak 1974, Tsingos et al. 2001, Habets et al. 2008, Aspöck et al. 2020, Meyer et al. 2023 |
| 2026-11-05 | OBJ 3D 홀(Python), OBJ → 2.5D 변환(체적 보존, 흡음은 메시 Sabine 면적 → 2.5D Eyring 지수), 실측 홀 2곳 지표 대조 | Fratoni 데이터셋, Fratoni 2022, Fratoni et al. 2023, Christensen & Rindel 2005, ISO 3382-1 Annex A |
| 2026-11-05 | BRAS CR3·CR4 위치별 검증(지표·1차 반사), `obj_to_hall.py` 외곽선 버그 수정, `calibrate.py` 메시 홀 가속 | Aspöck et al. 2020 (BRAS v3) |
| 2026-11-05 | 허상 반사에 유한 반사판 계수(Kirchhoff–Fresnel)와 산란 손실, 대역별 산란 계수 | Rindel 2005, Rindel 1992, BRAS CR3·CR4 대조 |
