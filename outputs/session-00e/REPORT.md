# Session 00e report — panel truncation, SMH return basis, vote leave-one-out

Written 2026-08-17. Applies decision **1.14**, informs
**3.12**, informs **6.7**.

No strategy return, Sharpe ratio, allocation, portfolio weight or performance
statistic is computed anywhere in this session. RSI values, SMA comparisons and
vote classifications are properties of individual price series.

---

## 0. Two blocking-adjacent facts established before any work

Both are reported rather than worked around.

### 0.1 `outputs/session-00d/REPORT.md` does not exist

The prompt directs that it be read for context. The directory
`outputs/session-00d/` **exists but is completely empty** — no REPORT.md, no CSVs,
no artifacts of any kind. A filesystem search for anything matching `*00d*`
outside `.venv` and `.git` returns only the empty directory itself, and no file
under `docs/` or `scripts/` references a Session 00D.

Consequence for the Step 1 instruction "if Session 00D wrote any artifact derived
from the equity panel, list it in the report as carrying the partial bar":
**Session 00D wrote no artifact of any kind**, so there is nothing to list. This
session was therefore run without the 00D context the prompt assumes.

### 0.2 Three of the four decisions cited are not in the register

`docs/DECISIONS-OPEN-v2.md` was read. It is unmodified since 2026-08-17 12:06,
which predates Session 00A. Enumerating every decision ID it contains:

| Decision cited by this prompt | Present in register? | Status in register |
|---|---|---|
| **1.14** panel truncation | **No.** Highest 1.x present is 1.13 | — |
| **3.12** SMH return basis | **No.** Highest 3.x present is 3.11 | — |
| **6.7** vote threshold | Yes | **Part 1, Closed**: "Vote threshold — Simple majority" |
| 2.22 (closed by Session 00B) | **No.** Highest 2.x present is 2.21 | — |

So the register on disk is stale relative to the session sequence: it does not
carry 1.14, 3.12 or 2.22, and it records 6.7 as already closed rather than open.
The work below is fully specified by the prompt independently of the register, so
it proceeded. But the instruction to "flag any result contradicting an expectation
in `docs/DECISIONS-OPEN-v2.md`" can only be applied against the expectations the
file actually contains. Section 3.4 does that for the one place it bites.

---

## 1. Panel truncation (step 1, applies 1.14)

Cutoff: **2026-08-14**. Rows dropped, never adjusted. VX files untouched.

Original manifests were copied to `outputs/session-00e/pre-truncation-hashes/`
**before** anything was modified:

- `session-00c__etf-manifest.csv`
- `session-00c__pull-metadata.json`
- `session-00a__vx-manifest.csv`

with their at-copy hashes in `_copied-manifests.csv`. The pre-truncation ETF
manifest records `last_date = 2026-08-17` for all 35 tickers, confirming the
partial bar was present.

A file was rewritten **only** where rows were actually removed, so files needing
no truncation keep their original bytes and therefore their original hash. Where
`old_sha256 == new_sha256`, the file was not touched.

**Result: 39 target files. 36 truncated, 3 needed no truncation, 1 dropped more
than one row.** Every file now ends 2026-08-14.

### 1.1 Anomaly A — three files were already at or before the cutoff

| filename | old_last_date | old_rows | rows_dropped |
|---|---|---|---|
| data/interim/vixy-yfinance-raw-s00b.parquet | 2026-08-14 | 3926 | 0 |
| data/interim/vxx-yfinance-raw-s00b.parquet | 2026-08-14 | 2150 | 0 |
| data/interim/vixy-nav-proshares-s00b.parquet | 2026-08-14 | 3927 | 0 |

The prompt states "Sessions 00A and 00B pulled VXX and VIXY at the same time and
carry the same defect." **They do not.** All three Session 00B series already
ended 2026-08-14 and contained no partial bar:

- The Session 00B yfinance pulls for VIXY and VXX were issued with
  `end="2026-08-16"`, which excludes 2026-08-17 entirely, so no 2026-08-17 bar was
  ever ingested.
- `vixy-nav-proshares-s00b.parquet` is issuer end-of-day NAV from ProShares, which
  only publishes a settled NAV; its last row was 2026-08-14.

These three files were left byte-identical. This is an assumption failure in the
prompt's premise, reported rather than worked around.

### 1.2 Anomaly B — one file dropped 35 rows, not 1

| filename | old_rows | new_rows | rows_dropped | old_last_date | new_last_date |
|---|---|---|---|---|---|
| data/interim/etf-panel.parquet | 180142 | 180107 | 35 | 2026-08-17 | 2026-08-14 |

`etf-panel.parquet` is a **long** panel, one row per (date, ticker) pair across 35
tickers. A single partial session is therefore 35 rows, not 1. Verified: every
date in the truncated panel now carries exactly 35 rows, the panel holds exactly
35 distinct tickers, and the new final date is 2026-08-14.

This is a layout artifact, not a data defect. The check as the prompt states it —
"any where more than one row was dropped ... would indicate an assumption
failure" — does not distinguish long-format from wide-format files. Reported as
instructed rather than reconciled.

### 1.3 Full truncation manifest

Also written to `manifest-truncated.csv` with the `status`, `date_carrier` and
`rows_dropped` columns omitted here for width.

| filename | old_sha256 | new_sha256 | old_rows | new_rows | old_last_date | new_last_date |
|---|---|---|---|---|---|---|
| data/raw/etf/AGG.parquet | 9214524a578dcc56ca7722145cd7d9caef0e5b159fd4d0c62bdadc8377a942f0 | 5363092132ca6e8dc43ac891604ef226602aebf896b2a2bb79f40dbaefd9896d | 5757 | 5756 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/BIL.parquet | 865b78af4753b4ca2f47566f6da03ea95cd48db4a2e12b3cc8f3b9b0df1073b7 | fb1c737fb5a737184d151c58ea608e7ba36848aae7235a2c35f7473284b34311 | 4835 | 4834 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/BND.parquet | d41c65dfc9e4de27cd949ac4f12e7e75382a265c9ce12343e5c20dff852644a8 | 05534b74d367f09283c02366cbf26ce185390c263e8576b19d5bd25153b904ae | 4870 | 4869 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/BSV.parquet | f195340fa10913fdb6ca25263d0aa5e27ff2d7c76f84f74c6a4b4347eda5e902 | 612e5f816dea5d0247c29754c88a8b4f6b41d341c1c37c20b0f9f4a92d538c43 | 4870 | 4869 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/BTAL.parquet | dfaa7cafa2c22d2d0858863d24fe1a992c3cb2906913952a519757dff122acbf | 195466ff136cdce72f43fa867980f13badbefb5bf569acaf372ca04c1f3cb9b4 | 3753 | 3752 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/FAS.parquet | 0432511d59ad049f66694b819e044d4c4308c27f52cd5bdfd34f9e7557e8ca35 | a21c4e84a5a4d1da5c8f3b9c10e6c489174f9a09f90aa75a001307c3e32a99b4 | 4461 | 4460 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/IBB.parquet | 3b6406bd927b8d37562146e9ee549f77378e85bab7039996ff1f14abde88520d | b3c5278ab743d514df939b6dce0d266cfdd959dd002d5ad35aa10ac0f8928438 | 6415 | 6414 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/IEF.parquet | 151edd375258e7b23a1496b341190d75231ef82fddca8dc01f179c39d852d943 | b1dfedfadb1c8fa2346424f0979a699d682927b864a494d5e3227d89daddb5e7 | 6051 | 6050 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/IOO.parquet | fdb75ea749335345c51a1525e518dc553cae8713a2cbb004a92a4a01942775a3 | 5842dc5c61000aba059239081b7967fd9b69aa905af5558c4bd0e5ce9125f1ea | 6458 | 6457 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/KMLM.parquet | 36d95c5fef2dbaaa68a90fd54c2991dc5d75efd6cfbec2e74bc50a630ad0d11f | 2bc5c8bbf18667b25d131eb342a5d3d1b20bda40bd1041e36b44421282e53643 | 1432 | 1431 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/LABU.parquet | 62d7a7cd9bde57f68adebac279ab300c5a2a065453151bae6069a34a0759d752 | a79835f32d5ef8475d85c175aa6808077ed49e87573181088e6ae13fb2a1b923 | 2822 | 2821 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/PSQ.parquet | f224eae51760d18a27e13540d416b5fa14352bccee18c26543b756dca690699f | f3d643baad58a1a5ab0245981b5383fd085f1f525c59b469665e1c89db18cac4 | 5070 | 5069 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/QLD.parquet | 7c184d31896e0f89125b90514b79cd15409357d65ca13cfa6678f67ecb4bbaff | dd4f80277cc499333f775e7b5bcf5dae1673ff79df3415bed043cc9e9703a792 | 5070 | 5069 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/QQQ.parquet | 6d47bc4b9b6884a74d2208d993e57934170b0dfd8acf974fd860c9509aaf1250 | c6e29c5fec7e34d3e612960adfd068b2c2023c8e05b950d30cb47e22d0763abd | 6902 | 6901 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/QQQE.parquet | e0b7c863428158a6ffd2bf54f74bfbd7f8df07a0ba76ebe6d702301248842b11 | b65ebfa18f89d6b961874b8f681e1ce82147a57bd5fbad0b4d29f02a6f6f8f6c | 3622 | 3621 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/SH.parquet | 19344e21692867dad02a49684fd71b5c2ee5d35833b6ffa9e4f0faed3ee7fc83 | 8ddd1ef2a9433fb08b50975b6331ca1582174ee4795c20cf27b6a3f46d6f1558 | 5070 | 5069 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/SMH.parquet | cfe21eb2088a8202271df9e4dbc69fbab7a5e7ffc318e857f121abd6db11d74a | 051b8393be19df699a12681265333234fa79162041ce687e3ae4dd80e10e3b90 | 6589 | 6588 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/SOXL.parquet | 66beaac659044c4d4eebc485ff16eb6a259450e3367142edd97f01d7125ddd62 | 03fc0100ff3b3a0ef7170258e81a24add6f1a947d8818d73fca419d1732162a9 | 4134 | 4133 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/SOXS.parquet | b5d07514f35ab40154a0a37dd70359209cd7dcb553a43c1b72308e66d593928f | b66d2a7012c307214d47aeb19528071e4bc9650f28b5ad0e22fe83cbddde77d8 | 4134 | 4133 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/SPXL.parquet | d91621b3f2da4c821e44f227bdadd1b8c79be8b533478ed0f5f379fda95293f7 | ae97bca64c4c92fe3e51eb6085e477d3e297f2175d4f0ede7a7343d6a4aaf572 | 4471 | 4470 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/SPY.parquet | 49a318be9c9df7959df9de3ceacab9dca9280df965418b5376ad7cc97014939f | ae615869bef84e6bfc938d241807ccac547da3acc77ea508687c98e2234dc48e | 7958 | 7957 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/SQQQ.parquet | bb98accaf834eab4a1ab91e3a9ae3239149bd132dc6ffaf5462f655683ce7bc3 | ef4904342448520bb78ed21fd64c17ebfc82a5ef637c00bb491489185e502a58 | 4153 | 4152 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/TECL.parquet | e0c69276a2149c54eda281a6c828d2b6eefae07242baf071630b09d26ba973be | f79667e76db2a2bae040aacb4b3a1acf6875186cc9c55be5b6383f40b571ccc5 | 4434 | 4433 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/TECS.parquet | 04a2503119e99638366f50897a925db3c07ad833622ef76f9937f9a27655a4ae | 74cd5b0ef0066d6a309611f045d73673e1073e297ceb4c38f13435b9b93d854d | 4434 | 4433 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/TLT.parquet | a5bbc473b2545e35eb3b66dc3a3905c217f1ad94f4fce75dc07735d5b237c2d5 | ff6a4f0b530e11b0a0c3784d9564fe380537abb9fc2348f8b4b572efaeef9590 | 6051 | 6050 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/TQQQ.parquet | bafac583c9c049ee5661ff271e28d33c0c9b03e9efd483a13f02c56b57c4df62 | d578afff3009020384529cdee2f1c9f833a4f45ae25d67d58c34a11a0f3b8d53 | 4153 | 4152 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/VOOG.parquet | e9172fad251f574aa4661c9d7b77dec9a66667c25c8c9e3b6957f12eb71aac66 | c0f32be1798e4780f81752496952c8b2dad5067cd3e07d709f383f28393a1ae1 | 4008 | 4007 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/VOOV.parquet | ac9d0dd8d46e107c240a790d8c6b494e6af1809adb0b58bb2a1f49a298140dc9 | 7bd32aa97fb78b334d324bf52002da17683fd9def4e03fa49e4ab1915fc10b1c | 4008 | 4007 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/VOX.parquet | 65099d35e821e951490047117ace5e857871ed6802955b939a71a763a3a80109 | f38c7e2b0498411e3de2d6a46d1a27bb9d7f4e00006dfef6e5a0147f968f23c1 | 5505 | 5504 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/VTV.parquet | a34e8e47d8d5600ac074b26ce4249c9b9f71f337726b36a682c1c7eefb96d631 | 775001e9c2e6bf4c1e8ccf992b80edc30984ea473c200452975116d7d712bcc1 | 5672 | 5671 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/XBI.parquet | 0accde5a8650c556951b2a44191e7831f9c663367780b9fe97d920d65ea4733c | a22622e1831063fa991c0fe899bc2e255d8a22cd54f52a0754554a2c41c4ec51 | 5164 | 5163 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/XLF.parquet | 48c8448008b498ebffe0df4b81ef962f86c2e84d662feeaa7cbf3ee695ef3d56 | 9bb5697317e58bb363dea05b704a1475223d530e8d9e91d6dc22f57a58d697d9 | 6954 | 6953 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/XLK.parquet | 56ef71579009af27f4be81dcc782aa1d60edb4bfc5e116a5abcb41ab67516451 | 7d2c09c5747471e2898a1c02d40a74210f3a409c08084b639560e6c5fa4f2385 | 6954 | 6953 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/XLP.parquet | 0ca2466533d10350e8dbdf85a6f48ddb1695d4a3b82a6caf98a91c074c577e71 | b7c98a0ac0735c11318d83c7c7e5da9acd55607a911fe0de9a26c355752fda0b | 6954 | 6953 | 2026-08-17 | 2026-08-14 |
| data/raw/etf/XLY.parquet | ddf13247ba87468be0b97920a9115da29698a80bbbc977676286d901c39f8e0c | d38ca7774db2f5a5e1db80f9cf4a2886a6eba4f8bd836918cf1776735cfd6b51 | 6954 | 6953 | 2026-08-17 | 2026-08-14 |
| data/interim/etf-panel.parquet | a2d802de1d21441381edcbe90a28ebbcfba5e1124890e5f46202b94fbac3ff0f | 2ef90923e0561f6e4ecfcb986580eb20c68feaa493650b70aedb5dc33378e16c | 180142 | 180107 | 2026-08-17 | 2026-08-14 |
| data/interim/vixy-yfinance-raw-s00b.parquet | 7391f73e47527134703f310b5ef528fa8ba9cd51c868bb72b35ff09134d61de3 | 7391f73e47527134703f310b5ef528fa8ba9cd51c868bb72b35ff09134d61de3 | 3926 | 3926 | 2026-08-14 | 2026-08-14 |
| data/interim/vxx-yfinance-raw-s00b.parquet | 2c2fe9977b7f6eca533dd52d120c0de355d55b1123e98a524f6c4081e7188f98 | 2c2fe9977b7f6eca533dd52d120c0de355d55b1123e98a524f6c4081e7188f98 | 2150 | 2150 | 2026-08-14 | 2026-08-14 |
| data/interim/vixy-nav-proshares-s00b.parquet | 5ec9d8da427acf16fab3507beb9f269a1f7e49ecf57e5eddb4364ee8f480c7eb | 5ec9d8da427acf16fab3507beb9f269a1f7e49ecf57e5eddb4364ee8f480c7eb | 3927 | 3927 | 2026-08-14 | 2026-08-14 |

### 1.4 Statistics in earlier reports were not recomputed

No CSV under `outputs/session-00a/`, `outputs/session-00b/`, `outputs/session-00c/`
or `outputs/session-00d/` was modified. Those record what was measured at the time.

**Statistics in the 00B, 00C and 00D reports include the partial 2026-08-17 bar
and were not recomputed.** Concretely, every Session 00C table carries
`last_date = 2026-08-17`, and the Session 00B VIXY/VXX validation windows end
2026-08-14 already (section 1.1) so those are unaffected. Session 00D wrote
nothing, so it has no affected artifact (section 0.1).

---

## 2. SMH pre-2013 return basis (step 2, informs 3.12)

### 2.1 The yields are assumptions, not measurements

**Stated plainly: the 1.0, 1.5 and 2.0 percent figures are assumptions. They are
not measured distributions. No actual pre-2013 SMH distribution data was
located.**

The feed records **zero** distributions for SMH before **2012-12-24**, which is
the first of 14 in its whole history. Within the 2006-01-01 to 2013-12-31 build
window there are exactly two actual distributions, 2012-12-24 and 2013-12-23, and
only the first falls inside the 2007-2012 measurement window.

Attempts made to locate a pre-2013 distribution record, all unsuccessful:

| # | Attempt | Result |
|---|---|---|
| 1 | Web search for Semiconductor HOLDRS Trust distribution history 2007-2012 | Returned the trust's structure, the 2011-11-10 Merrill Lynch early-termination notice and the VanEck asset purchase, but **no distribution schedule** |
| 2 | `slickcharts.com/symbol/SMH/dividend` | **HTTP 403** |
| 3 | SEC EDGAR company browse for CIK 0001110511 (SEMICONDUCTOR HOLDRS TRUST) | **HTTP 403** |
| 4 | SEC filing tool, entity resolved as CIK 1110511 "SEMICONDUCTOR HOLDRS TRUST", filing history requested at the maximum 730-day lookback | Entity resolves and reports **87 total filings**, but **0 within reach** — the trust terminated in 2011, roughly 15 years outside the tool's maximum window |

Session 00C had already established the same negative result from the feed side:
14 distributions in full history, first 2012-12-24, and no dividend or split
within 200 calendar days either side of the 2011 HOLDRS-to-VanEck conversion.

### 2.2 Construction

Build window **2006-01-03 to 2013-12-31**, 2,013 sessions. Measurement window
**2007-01-03 to 2012-12-31**, **1,510 sessions**. The 2006 lead-in is sufficient
for every SMA length including 250 — all five lengths report the full 1,510
sessions, with no warm-up loss inside the measurement window.

- **PR**, price return: the series as the feed provides it, `ret_price`
  compounded. Since SMH paid nothing before 2012-12-24 this is also its realised
  total return over almost the whole window.
- **TR(y)**, estimated total return: `ret_tr = ret_price + y/252`, compounded.
  That is a constant annual yield `y` accrued daily on a 252-day basis, which is
  the standard identity `TR_t/TR_{t-1} = P_t/P_{t-1} + d_t/P_{t-1}` with
  `d_t/P_{t-1} = y/252`.

Indicators use the Session 00C library unchanged: Wilder RSI with alpha = 1/n and
an SMA seed (decision 1.6), SMA with `min_periods = n`.

### 2.3 Mean absolute RSI difference, PR against TR(y)

| rsi_period | 1.0 | 1.5 | 2.0 |
|---|---|---|---|
| 7.0 | 0.1596380573361387 | 0.2394423958250355 | 0.3192371025387858 |
| 14.0 | 0.1603865988312367 | 0.2405695490458202 | 0.3207456629975716 |
| 28.0 | 0.1593636138354106 | 0.239042338813884 | 0.3187190256584603 |

Maximum absolute RSI difference over the same window:

| rsi_period | 1.0 | 1.5 | 2.0 |
|---|---|---|---|
| 7.0 | 0.5687548600798706 | 0.8527072304378436 | 1.1363768027934498 |
| 14.0 | 0.4046337466758558 | 0.6066261282942804 | 0.8084025541208035 |
| 28.0 | 0.3063059521558813 | 0.459356206176821 | 0.6123378847457985 |

The mean difference is essentially flat across RSI period — 0.159 to 0.161 points
at 1.0 percent, 0.319 to 0.321 at 2.0 percent — and scales almost exactly linearly
in the assumed yield. The maximum difference does fall with period, from 1.14
points at RSI 7 to 0.61 at RSI 28 under the 2.0 percent assumption.

### 2.4 RSI threshold-crossing agreement

Agreement fraction. Thresholds 70 and 80 are read as `RSI >= t`, thresholds 30 and
20 as `RSI <= t`.

| rsi_period | threshold | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|
| 7.0 | 20.0 | 1.0 | 0.9986754966887416 | 0.9986754966887416 |
| 7.0 | 30.0 | 0.9993377483443708 | 0.9973509933774836 | 0.9966887417218544 |
| 7.0 | 70.0 | 0.9973509933774836 | 0.9966887417218544 | 0.9940397350993376 |
| 7.0 | 80.0 | 0.9986754966887416 | 0.9986754966887416 | 0.9986754966887416 |
| 14.0 | 20.0 | 1.0 | 1.0 | 1.0 |
| 14.0 | 30.0 | 0.9986754966887416 | 0.9966887417218544 | 0.9966887417218544 |
| 14.0 | 70.0 | 0.9986754966887416 | 0.9986754966887416 | 0.9986754966887416 |
| 14.0 | 80.0 | 1.0 | 1.0 | 0.9993377483443708 |
| 28.0 | 20.0 | 1.0 | 1.0 | 1.0 |
| 28.0 | 30.0 | 1.0 | 1.0 | 1.0 |
| 28.0 | 70.0 | 1.0 | 0.9993377483443708 | 0.9986754966887416 |
| 28.0 | 80.0 | 1.0 | 1.0 | 1.0 |

Sessions on which the two bases disagree, out of 1,510:

| rsi_period | threshold | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|
| 7.0 | 20.0 | 0 | 2 | 2 |
| 7.0 | 30.0 | 1 | 4 | 5 |
| 7.0 | 70.0 | 4 | 5 | 9 |
| 7.0 | 80.0 | 2 | 2 | 2 |
| 14.0 | 20.0 | 0 | 0 | 0 |
| 14.0 | 30.0 | 2 | 5 | 5 |
| 14.0 | 70.0 | 2 | 2 | 2 |
| 14.0 | 80.0 | 0 | 0 | 1 |
| 28.0 | 20.0 | 0 | 0 | 0 |
| 28.0 | 30.0 | 0 | 0 | 0 |
| 28.0 | 70.0 | 0 | 1 | 2 |
| 28.0 | 80.0 | 0 | 0 | 0 |

Worst case anywhere in the grid is **9 sessions of 1,510**, at RSI 7 / threshold
70 / 2.0 percent. RSI 28 disagrees on at most 2 sessions at any threshold or
yield, and never at 20, 30 or 80.

### 2.5 SMA above-or-below agreement

Agreement fraction:

| sma_length | 1.0 | 1.5 | 2.0 |
|---|---|---|---|
| 50.0 | 0.9940397350993376 | 0.9920529801324504 | 0.9887417218543046 |
| 100.0 | 0.9933774834437086 | 0.9894039735099338 | 0.9821192052980132 |
| 150.0 | 0.9887417218543046 | 0.9834437086092715 | 0.9735099337748344 |
| 200.0 | 0.9867549668874172 | 0.97682119205298 | 0.9688741721854304 |
| 250.0 | 0.9841059602649008 | 0.9794701986754968 | 0.9748344370860929 |

Sessions on which the two bases disagree, out of 1,510:

| sma_length | 1.0 | 1.5 | 2.0 |
|---|---|---|---|
| 50.0 | 9 | 12 | 17 |
| 100.0 | 10 | 16 | 27 |
| 150.0 | 17 | 25 | 40 |
| 200.0 | 20 | 35 | 47 |
| 250.0 | 24 | 31 | 38 |

The SMA comparison is the more sensitive of the two. Disagreement rises with SMA
length to a peak at 200 — 20, 35 and 47 sessions at 1.0, 1.5 and 2.0 percent — and
eases slightly at 250. This is the expected direction: an accrual applied to the
price makes it drift above its own trailing average, and the longer the average
the longer the lag it has to overcome.

### 2.6 S3 vote outcome, SPY / QQQ / SMH / SOXL, SMA 200, three of four

| assumed_yield_pct | s3_vote_bull_differs | s3_vote_bull_frac_PR | s3_vote_bull_frac_TR |
|---|---|---|---|
| 1.0 | 6 | 0.51081 | 0.52259 |
| 1.5 | 16 | 0.51081 | 0.54224 |
| 2.0 | 19 | 0.51081 | 0.54813 |

| Assumed yield | Sessions where bull classification differs | Of |
|---|---|---|
| 1.0 % | **6** | 509 |
| 1.5 % | **16** | 509 |
| 2.0 % | **19** | 509 |

**Window limitation, flagged.** The prompt asks for "the number of sessions in
2007 through 2012". That window is **not attainable for the four-member S3 vote**.
SOXL's first session in the panel is **2010-03-11**, and the SMA 200 warm-up
pushes the first evaluable vote session to **2010-12-22**. The vote comparison
therefore covers **2010-12-22 to 2012-12-31, 509 sessions**, which is the last
two years of the requested six, not the whole of it. The RSI and SMA measurements
in 2.3 to 2.5 are unaffected — those are SMH alone and do cover the full 1,510
sessions.

Truncation from Step 1 removed only 2026-08-17 and therefore cannot influence any
measurement in this section, all of which end 2012-12-31.

---

## 3. Vote leave-one-out (step 3, informs 6.7)

### 3.1 Which treatment Session 00C applied — determined

**Session 00C held the threshold constant.** Stated plainly, and established two
independent ways.

**From the code.** `scripts/s00c_structure.py`, in `_vote_rows`:

```python
for thr in range(1, k + 1):
    bull = counts >= thr
    for a in range(k):
        drop = (counts - V[:, a].astype(int)) >= thr    # same thr
```

The reduced three-vote count is compared against the **same** `thr` used for the
full four-vote set. At `thr = 3` that makes the three-vote set require unanimity.

**From reproduction.** Recomputing under the held treatment returns
408 for SPY,
404 for QQQ,
412 for SMH and
12 for SOXL at SMA 200 —
exactly the 408 / 404 / 412 / 12 Session 00C reported.

The session count is **3,934** here against Session 00C's 3,935, because the
partial 2026-08-17 bar has now been truncated. That session changed none of the
four flip counts.

### 3.2 Windows

Native basis per SMA length, matching Session 00C.

| sma_length | n_sessions | first_date | last_date | frac_bull_full |
|---|---|---|---|---|
| 50 | 4084 | 2010-05-20 | 2026-08-14 | 0.64202 |
| 100 | 4034 | 2010-08-02 | 2026-08-14 | 0.72360 |
| 150 | 3984 | 2010-10-12 | 2026-08-14 | 0.75301 |
| 200 | 3934 | 2010-12-22 | 2026-08-14 | 0.76868 |
| 250 | 3884 | 2011-03-07 | 2026-08-14 | 0.78167 |

### 3.3 Both treatments

**Treatment 1, threshold held at 3.** A three-vote set requires unanimity. Flip
counts:

| sma_length | SPY | QQQ | SMH | SOXL |
|---|---|---|---|---|
| 50 | 285 | 305 | 364 | 174 |
| 100 | 404 | 349 | 422 | 106 |
| 150 | 392 | 376 | 401 | 34 |
| 200 | 408 | 404 | 412 | 12 |
| 250 | 483 | 481 | 488 | 12 |

As fractions:

| sma_length | SPY | QQQ | SMH | SOXL |
|---|---|---|---|---|
| 50 | 0.06978 | 0.07468 | 0.08913 | 0.04261 |
| 100 | 0.10015 | 0.08651 | 0.10461 | 0.02628 |
| 150 | 0.09839 | 0.09438 | 0.10065 | 0.00853 |
| 200 | 0.10371 | 0.10269 | 0.10473 | 0.00305 |
| 250 | 0.12436 | 0.12384 | 0.12564 | 0.00309 |

**Treatment 2, threshold moved to 2 of 3.** Flip counts:

| sma_length | SPY | QQQ | SMH | SOXL |
|---|---|---|---|---|
| 50 | 80 | 81 | 287 | 332 |
| 100 | 54 | 83 | 225 | 308 |
| 150 | 59 | 68 | 251 | 344 |
| 200 | 55 | 63 | 213 | 309 |
| 250 | 46 | 43 | 215 | 300 |

As fractions:

| sma_length | SPY | QQQ | SMH | SOXL |
|---|---|---|---|---|
| 50 | 0.01959 | 0.01983 | 0.07027 | 0.08129 |
| 100 | 0.01339 | 0.02058 | 0.05578 | 0.07635 |
| 150 | 0.01481 | 0.01707 | 0.06300 | 0.08635 |
| 200 | 0.01398 | 0.01601 | 0.05414 | 0.07855 |
| 250 | 0.01184 | 0.01107 | 0.05536 | 0.07724 |

### 3.4 The two treatments invert the ranking

This is the substantive result of Step 3.

At SMA 200, under the held treatment SOXL is by far the **least** consequential
vote to remove, 12 flips against 404 to 412 for the other three. Under the moved
treatment SOXL becomes the **most** consequential, 309 flips against 55, 63 and
213. The same inversion holds at every SMA length from 50 to 250.

The mechanism is exact, not approximate. With the full-set threshold at 3 of 4:

- **Held at 3.** Removing member `a` flips exactly when `a` is bullish and the
  vote count is exactly 3. If `a` is bearish the classification cannot change.
- **Moved to 2.** Removing member `a` flips exactly when `a` is bearish and the
  vote count is exactly 2. If `a` is bullish the classification cannot change.

The two treatments therefore measure disjoint, complementary session sets. Both
identities were verified to hold exactly at SMA 200.

The asymmetry follows from SOXL's much lower bullish rate:

| member | bull_fraction_sma200 |
|---|---|
| SPY | 0.8467 |
| QQQ | 0.8475 |
| SMH | 0.8012 |
| SOXL | 0.6698 |

Vote count distribution at SMA 200, 3,934 sessions:

| bullish_votes | sessions |
|---|---|
| 0 | 462 |
| 1 | 128 |
| 2 | 320 |
| 3 | 412 |
| 4 | 2612 |

Of the 412 sessions with exactly three bullish votes, SOXL is the bullish
dissenter on only 12 — it is the odd one out on the other 400. Of the 320 sessions
with exactly two bullish votes, SOXL is bearish on 309. SOXL is simply the member
most often on the bearish side, so it is nearly absent from the set the held
treatment measures and nearly ubiquitous in the set the moved treatment measures.

**Flagged against the register.** `docs/DECISIONS-OPEN-v2.md` records decision 6.8
with the stated rationale "Add a non-equity leg, **since SOXL and SMH votes are
near-duplicates**". The leave-one-out evidence does not support that rationale
symmetrically: it supports it under the held treatment and contradicts it under
the moved treatment, where SOXL is the single most influential vote in the set.
Session 00C's separate pairwise-agreement measurement — SMH and SOXL agreeing on
0.9143 of sessions at SMA 50, the highest of the six pairs — is independent of any
threshold treatment and is not disturbed by this. The two lines of evidence point
in different directions and are reported, not reconciled.

---

## 4. Artifacts written

| Path | Contents |
|---|---|
| `outputs/session-00e/manifest-truncated.csv` | 39 files: old and new hash, rows, last dates, status |
| `outputs/session-00e/pre-truncation-hashes/` | original 00A and 00C manifests, copied before modification |
| `outputs/session-00e/smh-return-basis.csv` | step 2, 180 rows, long form |
| `outputs/session-00e/vote-leave-one-out.csv` | step 3, 40 rows, both treatments |
| `outputs/session-00e/REPORT.md` | this file |

Modified in place: 35 files under `data/raw/etf/` and `data/interim/etf-panel.parquet`.
Byte-identical, not rewritten: the three Session 00B interim files in section 1.1.
Untouched: all VX files, and every CSV under `outputs/session-00a/` through
`outputs/session-00d/`.

No decision is recommended and no parameter is selected. Working tree left dirty.
Nothing committed.
