# Step 5 — financing terms disclosed in filings (informs 2.14 and 2.15)

Three current registration documents were searched for financing-rate,
SOFR, swap-spread, and borrow-cost language (windows around each match
read in full):

1. ProShares Trust 485BPOS 2026-07-23 (`0001174610-26-000450`, primary
   document, 1.34M chars) — covers TQQQ, QLD, SQQQ, PSQ, SH.
2. Direxion Shares ETF Trust 485BPOS 2026-08-10
   (`0001193125-26-342375`, 1.44M chars) — covers the seven Direxion funds.
3. ProShares Trust II 10-K 2026-02-26 (`0001193125-26-077441`, 0.75M
   chars) — covers UVXY and SVXY.

## What is disclosed

**No prospectus states a numeric financing spread.** The ProShares Trust
document yields zero matches on any financing pattern. The Direxion
document mentions "financing rates associated with leveraged exposure"
only as an unnumbered factor in the long-horizon performance-illustration
boilerplate, and SOFR only inside LIBOR-transition risk language. Neither
names a reference rate for its swaps in the prospectus, and neither states
a spread.

**Year-end snapshots exist in shareholder-report schedules.** ProShares
Trust II's 10-K schedules of investments disclose, per swap position:
"Reflects the floating financing rate, as of December 31, on the notional
amount of the swap agreement paid to the counterparty or received from the
counterparty, excluding any commissions." The same schedule convention
appears in N-CSR shareholder reports for the 1940-Act trusts. So actual
paid financing rates ARE public — but only as point-in-time year-end
snapshots per counterparty, not as a stated spread over a named reference
rate, and harvesting them means reading every annual schedule.

**Borrow cost on inverse exposure is absorbed, by the filings' own
language.** The swap description states the interest-rate leg "will also
include the cost of borrowing for short swaps." No filing searched
discloses borrow separately from the swap financing leg.

## The 2.15 class question

Short-equity and short-volatility financing are **not the same class**,
structurally:

- SQQQ, PSQ, SH, SOXS, TECS hold **swap agreements** on equity indexes;
  their short financing (including borrow) is folded into the swap
  interest leg, per the language above. Absorbed, not separately visible.
- SVXY (and SVIX) hold **VIX futures positions**; there is no swap borrow
  leg at all — the economics of the short sit in the futures basis and
  collateral yield, which the study's 2.3 VX construction models directly.

So 2.15's premise that the five inverse-equity funds and the short-vol
funds form one class does not match the instruments' structure: the
question of "separately visible borrow" only arises for the swap-based
five, and for them the answer in current filings is "absorbed."

## What this gives 2.14

The filings do not disclose a usable prospectus-level financing spread.
What exists is (a) qualitative absorption language and (b) year-end
per-swap rate snapshots in annual schedules. Under 2.14's own terms —
anchor on filings disclosure with a sweep around it — the disclosure
available supports the sweep, and an anchor would have to be harvested
from annual schedules rather than read off a stated term. Reported without
recommending how 2.14 closes.

## Bounded-effort caveats

- The grep covered each accession's largest primary document. Statements
  of Additional Information filed as separate documents within the same
  accessions were not separately grepped; SAI swap descriptions are
  customarily qualitative, but that is a presumption, not a verified
  absence.
- N-CSR annual schedules for ProShares Trust / Direxion (where the
  1940-Act funds' per-swap rates would appear) were not harvested; their
  existence is inferred from the identical schedule convention in the
  PT2 10-K, which was read.
