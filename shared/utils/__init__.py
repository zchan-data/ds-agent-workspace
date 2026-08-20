"""Reusable helpers shared across projects.

Add `shared/`'s parent (the workspace root) to `PYTHONPATH`, then:

    from shared.utils import assert_no_lookahead, WalkForwardSplit

Everything here was harvested from a project that needed it and proved it works
— see each module's docstring for provenance. Keep it that way: promote code up
here once a second project wants it, not on speculation.
"""
from shared.utils.leakage import assert_no_lookahead, lookahead_columns
from shared.utils.panel import neutralize_cross_section
from shared.utils.stats import effective_sample_size, mean_significance, newey_west_se
from shared.utils.validation import WalkForwardSplit

__all__ = [
    "assert_no_lookahead",
    "lookahead_columns",
    "neutralize_cross_section",
    "effective_sample_size",
    "mean_significance",
    "newey_west_se",
    "WalkForwardSplit",
]
