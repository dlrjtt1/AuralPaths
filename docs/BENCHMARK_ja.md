# AuralPaths の精度(公開実測データによるベンチマーク)

最終実行: 2026-11-10、同日時点のエンジン。English: [BENCHMARK_en.md](BENCHMARK_en.md)、한국어:
[BENCHMARK_ko.md](BENCHMARK_ko.md)。

本ページの数値はすべて公開実測データと本リポジトリのスクリプトから得たものであり、データがあれば誰でも再実行できる
(6 節)。実測データそのものはここでは再配布しない。これらの場面で良い成績であっても、すべてのホールが同程度に
よくシミュレーションされることを意味しない。弱点は 5 節に示す。

## 1. 要約

| 項目 | 結果 | 詳細 |
|---|---|---|
| 2019 年ラウンドロビンの基準事例 15 件のスペクトル(床・板・アレイ・平行板の反射) | 形状誤差の中央値 **1.5 dB**; 結果のある参加プログラム 5 本は 1.0 – 2.8 dB | 2 節 |
| 単一反射と有限板(BRAS RS1, RS2, RS4) | 1/3 オクターブ帯域の平均絶対差 1.2 – 3.4 dB | 3 節 |
| 衝立の背後と厚い物体の背後の回折(BRAS RS5, RS6) | 平均絶対差 2.6 dB(RS5)、2.3 – 2.8 dB(RS6)、3 節の回折オプションを使用 | 3 節 |
| コンサートホール、バイノーラルの音源–座席 136 組(Detmold Konzerthaus) | 後期の空間印象(IACC_L3)が 96 % の組で 0.075 以内; EDT の偏り 0 – 3 %; C80 は 0.3 – 0.8 dB 低い | 4 節 |
| 既知の弱点 | 最前列より後ろで座席列のすぐ上を通る音: 5 – 11 dB 過大; 初期 IACC が低い | 5 節 |

形状誤差: シミュレーションと実測の 1/3 オクターブレベル差から平均差を除いた rms。平均絶対差: 絶対レベルによる。
スピーカーは文書記載の校正値をもつ平坦な点音源としてモデル化した。ラウンドロビン参加者はスピーカーの指向性データを
用いたが、本実行では用いていない。

## 2. 2019 年ラウンドロビン

Brinkmann et al. (2019), "A round robin on room acoustical simulation and auralization", J. Acoust. Soc. Am. 145,
2746, https://doi.org/10.1121/1.5096178。6 本のプログラムが参加した(匿名、A – F; B はこれらの場面の結果なし)。
AuralPaths は参加しておらず、同じ図に対して事後に評価した。論文はスペクトルを図でのみ比較しており
(III.A 節)、誤差指標を示していない。形状誤差とその中央値は本ページで定義・算出したものである。補足資料(SuppPub2)のスペクトルを PDF のベクター図形から
読み取り、各図の実測曲線と比較した。AuralPaths は同じ窓処理を施した実測インパルス応答と比較した(2 つの実測曲線は
0.1 – 0.9 dB 以内で一致)。

| | A | C | D | E | F | AuralPaths |
|---|---|---|---|---|---|---|
| 形状誤差の中央値、dB(図の数) | 2.3 (9) | 1.0 (15) | 2.8 (15) | 1.3 (13) | 1.4 (13) | **1.5** (15) |

図ごとの値: [validation/bras_rs.md](../validation/bras_rs.md) 2 節。

## 3. BRAS 基準場面

Aspöck et al., BRAS – Benchmark for Room Acoustical Simulation, https://doi.org/10.14279/depositonce-6726.3
(CC BY-SA 4.0)。125 Hz – 4 kHz、音源–受音点の組に対する中央値。

| 場面 | 組 | 形状誤差 | 平均絶対差 | エンジン設定 |
|---|---|---|---|---|
| RS1 床 / 吸音材 / 拡散体での反射 | 10 / 9 / 10 | 2.3 / 3.1 / 3.6 dB | 2.3 / 3.2 / 3.4 dB | 既定 |
| RS2 有限板 1 m / 2 m(剛) | 15 / 15 | 1.3 / 1.6 dB | 1.3 / 1.4 dB | 既定 |
| RS3 平行板 2 枚(600 ms) | 1 | 1.8 dB | 2.6 dB | 既定 |
| RS4 反射板アレイ、中央 / 非中央 | 9 / 9 | 1.8 / 1.5 dB | 2.4 / 1.2 dB | 既定 |
| RS5 高さ 2.07 m の衝立、背後 11 位置 | 11 | 2.7 dB | 2.6 dB | `diffraction_refl` 1 |
| RS6 0.72 m の物体、背後 8 位置 | 8 | 3.0 – 3.5 dB | 2.3 – 2.8 dB | `diffraction_order` 2, `diffraction_refl` 1, `finite_reflectors` false |
| RS7 低いブロック 15 列(座席ディップの構成)、音源が見える | 4 | 4.6 – 6.4 dB | 3.8 – 6.4 dB | 既定 |
| RS7、最初のブロックの背後 | 4 | 5.2 – 7.4 dB | 5.6 – 9.1 dB | 既定(過大、5 節) |

既定の設定では RS5 の平均絶対差は 3.9 dB であり、RS6 では 8 位置のうち 4 位置で音が生じない。これらのオプションは
計算時間がかかる(音源–受音点の組あたり最大数十秒)ため、既定ではオフである。詳細:
[validation/bras_rs.md](../validation/bras_rs.md)、[validation/bras_rs5_engine.md](../validation/bras_rs5_engine.md)。

## 4. ホール全体

| ホール | データ | 結果 | 詳細 |
|---|---|---|---|
| Detmold Konzerthaus(約 600 席)、舞台音源 4 × 座席 34、KU100 ダミーヘッド | Detmold SRIR database, https://zenodo.org/records/4116247 (CC BY 4.0) | IACC_L3: 96 % の組で 0.075 以内; IACC_E3: 平均 0.15 低い(0.075 以内は 18 %); EDT の偏り 0 – 3 %(5 % 以内 27 – 45 %); C80 は 0.3 – 0.8 dB 低い(1 dB 以内 38 – 51 %); T30 は校正後 2.7 % 以内 | [validation/detmold_kh.md](../validation/detmold_kh.md) |
| BRAS CR3 室内楽ホール、CR4 講堂(バイノーラル、FABIAN ヘッド) | BRAS | 直接音の ITD 5 µs 以内、2 – 4 kHz のスペクトル 1.4 dB 以内; 直接音後 14 – 70 ms の個別反射: 実測 − モデル −1.1 dB(中央値、両ホール); CR4 では天井パネル–通路のフラッター下の座席で後期 IACC が低い | [validation/bras_brir_iacc_diag.md](../validation/bras_brir_iacc_diag.md) |
| Fratoni の講義室(ULH)とドーム型ホール(STC) | Fratoni et al. のデータセット | ULH: 500 Hz – 4 kHz で約 1 JND 以内; STC: T30 が約 15 % 長い(このようなホールではまず校正すること) | [validation/](../validation/) `fratoni_*.md` |

基準値: EDT 5 % と C80 1 dB は ISO 3382-1:2009 Annex A; IACC 0.075 は Detmold データに付随する学位論文で仮定された値
(一次出典は未確認)。

## 5. 既知の弱点

- **座席列のすぐ上を通る音**(掠め入射)、最前列より後ろ: 5 – 11 dB 過大; 座席ディップ(ここでは約 500 Hz)が
  現れない(BRAS RS7)。このような位置は実測で確認すること。
- **初期の空間印象**(IACC_E3)がコンサートホールで約 0.15 低い(Detmold); C80 がやや低い。
- **平行面間のフラッター**: 有限パネル間の反復反射が既定の有限反射板係数では低域で弱すぎる(RS3)。CR4 では天井–通路の
  フラッターを過小評価。
- エッジ端点の回折、3 次以上の回折、厚さ 5 cm – 数十 cm の板: 未確認。
- 聴取実験はまだない: これらの確認は物理的なものであり、知覚的なものではない。

## 6. 再実行

データ: BRAS の場面記述 RS1 – RS7 と表面記述、Detmold SRIR database(上記リンクから入手)。その後:

    python validation/bras_rs.py <BRAS フォルダ> --scene RS2          # RS1 – RS4, RS6, RS7
    python validation/bras_rs5.py <BRAS フォルダ> --variant thin+floor
    python validation/rr_extract.py <SuppPub2.pdf> out/rs/rr_curves.csv
    python validation/rr_compare.py
    python validation/detmold_kh.py ...                                # スクリプトの docstring を参照

出力は `out/` に保存される(実測データからの派生物のため、リポジトリには含めない)。
