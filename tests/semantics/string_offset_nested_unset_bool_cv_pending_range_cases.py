"""A saved pending Exception still permits default finite-range reporting."""
import string_offset_nested_unset_bool_cv_float_post_frontier_cases as prior
from string_offset_nested_unset_bool_cv_range_default_cases import stderr

NAME = 'nested-unset-bool-cv-float-post-frontier-masked-range-throw'
CASES = {NAME: prior.CASES[NAME]}
OUTPUTS = {NAME: prior.OUTPUTS[NAME]}
BITS = 4906019910204099648
WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_float_post_frontier_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_range_default_cases.py',
    'spec/semantics/101-error-suppression.watsup',
    'spec/semantics/237-display-errors.watsup',
    'spec/semantics/391-output-buffers.watsup',
)
