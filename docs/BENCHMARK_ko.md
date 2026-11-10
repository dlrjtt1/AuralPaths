# AuralPaths는 얼마나 정확한가? (공개 실측 데이터 벤치마크)

마지막 실행: 2026-11-10, 그날 기준 엔진. English: [BENCHMARK_en.md](BENCHMARK_en.md), 日本語:
[BENCHMARK_ja.md](BENCHMARK_ja.md).

이 페이지의 모든 수치는 공개 실측 데이터와 이 저장소의 스크립트에서 나왔으며, 데이터가 있으면 누구나 다시 실행할 수
있다(6절). 실측 데이터 자체는 여기서 재배포하지 않는다. 이 장면들에서 점수가 좋다고 모든 홀이 똑같이 잘 시뮬레이션된다는
뜻은 아니며, 약점은 5절에 적었다.

## 1. 요약

| 항목 | 결과 | 상세 |
|---|---|---|
| 2019 라운드 로빈 기준 사례 15개의 스펙트럼(바닥·판·어레이·평행판 반사) | 형태 오차 중앙값 **1.5 dB**; 결과를 낸 참가 프로그램 5개는 1.0 – 2.8 dB | 2절 |
| 단일 반사와 유한 판(BRAS RS1, RS2, RS4) | 1/3옥타브 대역 평균 절대 차이 1.2 – 3.4 dB | 3절 |
| 칸막이 뒤와 두꺼운 물체 뒤의 회절(BRAS RS5, RS6) | 평균 절대 차이 2.6 dB(RS5), 2.3 – 2.8 dB(RS6), 3절의 회절 옵션 사용 | 3절 |
| 콘서트홀, 바이노럴 음원-좌석 136쌍(Detmold Konzerthaus) | 후기 공간감(IACC_L3)이 96 %의 쌍에서 0.075 이내; EDT 편차 0 – 3 %; C80 0.3 – 0.8 dB 낮음 | 4절 |
| 알려진 약점 | 첫 열 뒤 객석 바로 위를 지나는 소리: 5 – 11 dB 과대; 초기 IACC 낮음 | 5절 |

형태 오차: 시뮬레이션과 실측의 1/3옥타브 레벨 차에서 평균 차이를 뺀 rms. 평균 절대 차이: 절대 레벨 기준. 스피커는
문서에 적힌 교정값을 가진 평탄한 점음원으로 모델링했다. 라운드 로빈 참가자들은 스피커 지향성 데이터를 썼고 이 실행은
쓰지 않았다.

## 2. 2019 라운드 로빈

Brinkmann et al. (2019), "A round robin on room acoustical simulation and auralization", J. Acoust. Soc. Am. 145,
2746, https://doi.org/10.1121/1.5096178. 프로그램 6개가 참가했다(익명, 문자 A – F; B는 이 장면들에 결과가 없음).
AuralPaths는 참가하지 않았고, 같은 그림에 대해 사후에 점수를 냈다. 논문은 스펙트럼을 그림으로만
비교하며(III.A절) 오차 지표를 제시하지 않는다. 형태 오차와 그 중앙값은 여기서 정의하고 계산한 것이다. 부록(SuppPub2)의 스펙트럼을 PDF 벡터 그래픽에서 읽어
각 그림의 실측 곡선과 비교했고, AuralPaths는 같은 창 처리를 한 실측 임펄스 응답과 비교했다(두 실측 곡선은 0.1 – 0.9 dB
이내로 일치).

| | A | C | D | E | F | AuralPaths |
|---|---|---|---|---|---|---|
| 형태 오차 중앙값, dB(그림 수) | 2.3 (9) | 1.0 (15) | 2.8 (15) | 1.3 (13) | 1.4 (13) | **1.5** (15) |

그림별 값: [validation/bras_rs.md](../validation/bras_rs.md) 2절.

## 3. BRAS 기준 장면

Aspöck et al., BRAS – Benchmark for Room Acoustical Simulation, https://doi.org/10.14279/depositonce-6726.3
(CC BY-SA 4.0). 125 Hz – 4 kHz, 음원-수음점 쌍에 대한 중앙값.

| 장면 | 쌍 | 형태 오차 | 평균 절대 차이 | 엔진 설정 |
|---|---|---|---|---|
| RS1 바닥 / 흡음재 / 확산체 반사 | 10 / 9 / 10 | 2.3 / 3.1 / 3.6 dB | 2.3 / 3.2 / 3.4 dB | 기본 |
| RS2 유한 판 1 m / 2 m(강체) | 15 / 15 | 1.3 / 1.6 dB | 1.3 / 1.4 dB | 기본 |
| RS3 평행 판 두 장(600 ms) | 1 | 1.8 dB | 2.6 dB | 기본 |
| RS4 반사판 어레이, 중앙 / 비중앙 | 9 / 9 | 1.8 / 1.5 dB | 2.4 / 1.2 dB | 기본 |
| RS5 2.07 m 칸막이, 뒤쪽 11곳 | 11 | 2.7 dB | 2.6 dB | `diffraction_refl` 1 |
| RS6 0.72 m 물체, 뒤쪽 8곳 | 8 | 3.0 – 3.5 dB | 2.3 – 2.8 dB | `diffraction_order` 2, `diffraction_refl` 1, `finite_reflectors` false |
| RS7 낮은 블록 15줄(객석 딥 구성), 음원이 보임 | 4 | 4.6 – 6.4 dB | 3.8 – 6.4 dB | 기본 |
| RS7, 첫 블록 뒤 | 4 | 5.2 – 7.4 dB | 5.6 – 9.1 dB | 기본(과대, 5절) |

기본 설정에서는 RS5가 평균 절대 차이 3.9 dB이고, RS6는 8곳 중 4곳에 소리가 없다. 이 옵션들은 계산 시간이 길어서(음원-수음점
쌍당 최대 수십 초) 기본으로 꺼져 있다. 상세: [validation/bras_rs.md](../validation/bras_rs.md),
[validation/bras_rs5_engine.md](../validation/bras_rs5_engine.md).

## 4. 홀 전체

| 홀 | 데이터 | 결과 | 상세 |
|---|---|---|---|
| Detmold Konzerthaus(약 600석), 무대 음원 4 × 좌석 34, KU100 더미헤드 | Detmold SRIR database, https://zenodo.org/records/4116247 (CC BY 4.0) | IACC_L3: 96 %의 쌍에서 0.075 이내; IACC_E3: 평균 0.15 낮음(0.075 이내 18 %); EDT 편차 0 – 3 %(5 % 이내 27 – 45 %); C80 0.3 – 0.8 dB 낮음(1 dB 이내 38 – 51 %); T30 교정 후 2.7 % 이내 | [validation/detmold_kh.md](../validation/detmold_kh.md) |
| BRAS CR3 실내악홀, CR4 강당(바이노럴, FABIAN 헤드) | BRAS | 직접음 ITD 5 µs 이내, 2 – 4 kHz 스펙트럼 1.4 dB 이내; 직접음 후 14 – 70 ms의 개별 반사: 실측 − 모델 −1.1 dB(중앙값, 두 홀); CR4에서 천장 패널–통로 플러터 아래 좌석의 후기 IACC 낮음 | [validation/bras_brir_iacc_diag.md](../validation/bras_brir_iacc_diag.md) |
| Fratoni 강의실(ULH)과 돔형 홀(STC) | Fratoni et al. 데이터셋 | ULH: 500 Hz – 4 kHz에서 약 1 JND 이내; STC: T30 약 15 % 김(이런 홀은 먼저 교정할 것) | [validation/](../validation/) `fratoni_*.md` |

기준값: EDT 5 %와 C80 1 dB는 ISO 3382-1:2009 Annex A; IACC 0.075는 Detmold 데이터에 딸린 학위논문에서 가정한 값(1차 출처는
확인하지 않음).

## 5. 알려진 약점

- **객석 열 바로 위를 지나는 소리**(스치는 입사), 첫 열 뒤: 5 – 11 dB 과대; 객석 딥(여기서는 약 500 Hz)이 나타나지 않음
  (BRAS RS7). 이런 위치는 실측으로 확인할 것.
- **초기 공간감**(IACC_E3)이 콘서트홀에서 약 0.15 낮음(Detmold); C80 약간 낮음.
- **평행면 사이 플러터**: 유한 패널 사이의 반복 반사가 기본 유한 반사판 계수에서는 저역에서 너무 약함(RS3), CR4에서 천장–
  통로 플러터를 과소평가.
- 모서리 끝점 회절, 3차 이상의 회절, 두께 5 cm – 수십 cm의 판: 확인하지 않음.
- 청취 실험은 아직 없음: 이 확인들은 물리적인 것이지 지각적인 것이 아니다.

## 6. 다시 실행하기

데이터: BRAS 장면 설명 RS1 – RS7과 표면 설명, Detmold SRIR database(위 링크에서 내려받기). 그다음:

    python validation/bras_rs.py <BRAS 폴더> --scene RS2          # RS1 – RS4, RS6, RS7
    python validation/bras_rs5.py <BRAS 폴더> --variant thin+floor
    python validation/rr_extract.py <SuppPub2.pdf> out/rs/rr_curves.csv
    python validation/rr_compare.py
    python validation/detmold_kh.py ...                            # 스크립트 docstring 참조

출력은 `out/`에 저장된다(실측 데이터에서 파생되므로 저장소에는 넣지 않음).
