# Step 1 — closing price provenance

**Question.** 4.1 fills at the T+1 close; 4.2 closed on the official closing
print. Do the frozen files carry the primary-exchange closing auction price
or the consolidated last sale?

**Comparison source and dates.** Alpha Vantage `TIME_SERIES_DAILY` (raw,
unadjusted closes) via the connected MCP server, an independent vendor from
Yahoo. Free tier serves the trailing ~100 sessions only, so the stated
comparison dates are 2026-04-15, 2026-06-30, and 2026-08-14 — all after
every sampled ticker's last split, so frozen split-adjusted Close equals
as-traded on those dates. Stooq was attempted first as the independent
source and returns an HTML interstitial to scripted access (404/consent
page under both plain and browser user agents); it was abandoned.

**Sample.** The prompt's six names, with one substitution: UVIX has no
frozen file (volatility ETPs are not in the 36-ticker panel; their series
arrive via the VX synthetic build), so KMLM stands in as the thin-name
slot. Sampled: SPY, QQQ, LABU, QQQE, BTAL, KMLM — spanning $16.7B to $1.8M
median daily dollar volume.

**Positive control.** SPY, the most liquid name, matched to the cent on all
three dates before any thin-name comparison was read.

**Result.** 18 of 18 comparisons match exactly (to the cent, differences
0.0000): every ticker, every date, including the thinnest names. No
systematic difference appears, and none differs by liquidity.

**What this does and does not establish.** Both Yahoo (the frozen source)
and Alpha Vantage redistribute consolidated-tape data. Their exact
agreement establishes that the frozen closes are the standard vendor
consolidated close, consistently recorded — it **cannot distinguish the
primary-exchange official closing auction print from the consolidated last
sale**, because a source carrying the exchange-official auction print
(direct exchange data) is not available to this study without licensing.
For most ETF sessions the two coincide; they can differ for thin names on
sessions with post-auction consolidated prints — exactly the case 4.2 cares
about — and on the evidence available the two cannot be told apart. Per the
step instruction, that indistinguishability is the finding; no match to the
official print is claimed.

Also outside reach on the free tier: the historical stress dates
(2015-08-24, 2020-03-16) — Alpha Vantage full history is a premium feature
and Stooq blocks scripted access, so cross-vendor checks on those dates
were not performed.

**Consequence for the register.** 4.2's "official closing print" remains an
assumption about the feed rather than a verified property. The frozen data
is internally consistent and cross-vendor identical; whether it is the
auction print is unverifiable from what is available.
