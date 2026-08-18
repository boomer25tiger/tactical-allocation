# Project context

Daily multi-model tactical allocation study. Specification is being frozen.
No strategy returns, Sharpe ratios, allocations, or performance statistics are
computed in any session until SPEC is frozen. Sessions before the freeze may
compute counts, distributions, and data properties only.

Standing rules:
- Never commit. Report results as text and leave the working tree dirty.
- Write every intermediate artifact to disk under outputs/<session>/.
- Stop at the stated stop condition. Do not continue into adjacent work.
- If a pre-registered rule produces an unexpected result, report it. Do not
  adjust the rule.
