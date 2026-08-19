# Grid axis enumeration fallback rule

Pre-registered by session 16b on 2026-08-19, written and hashed BEFORE any
part of step 1 read the register on the axes. The hash below is the evidence
that the rule preceded the reading. The rule is transcribed verbatim from the
session prompt.

## Precedence

For each axis, if the register records explicit values, those values are used
and nothing is chosen. If the register records a cardinality but not values,
the cardinality is binding and values follow the construction below. If the
register records neither, the construction below supplies both, and the axis is
flagged as discretionary.

## Construction

Values are the canonical value plus and minus whole steps, symmetric, at the
axis's natural granularity. Granularity is one day for any period expressed in
sessions, five points for any RSI threshold, and one vote for any vote count. A
cardinality of 3 gives canonical minus one step, canonical, canonical plus one
step. A cardinality of 5 extends symmetrically by a second step. Where symmetry
would cross a domain boundary, being an RSI threshold outside 0 to 100 or a
vote count outside 0 to the number of voters, the range shifts inward to stay
in domain and the shift is reported.

The canonical value is never changed and always appears on its axis. The
canonical point was fixed before any result existed and the enumeration
surrounds it rather than moving it.

## Function-tied axes

Function-tied axes move together or not at all. The three RSI periods under 6.1
and 7.2 are recorded as function-tied. If the register records them as a single
axis they enumerate as one. If it records them as three, they enumerate as
three. The reading is taken from the register rather than chosen.
