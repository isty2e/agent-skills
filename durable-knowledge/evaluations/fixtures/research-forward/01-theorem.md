# Closure factorization result

Research subject: Auto-CP routing.

Definition: A routing policy selects one branch from a finite family after observing a calibration
statistic. A branch certificate is closure-valid when its certified event is preserved under the
policy's selection map.

Proved theorem: Under assumptions A1 (measurable finite routing), A2 (each branch certificate is
valid on its declared domain), and A3 (the selection map factors through the certified closure),
complete-policy marginal validity follows by closure factorization. The mathematical statement and
proof are complete. The exact prose used in the manuscript is still being edited, but the proposition
and assumptions are fixed.

Repository-owned details: exact Lean declaration `AutoCP.Closure.factor_valid`, proof term, toolchain
version, and source path `AutoCP/Closure/Factor.lean`.
