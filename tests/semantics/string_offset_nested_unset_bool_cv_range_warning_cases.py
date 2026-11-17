"""A copied finite range value causes a second Warning after the first return."""
import string_offset_nested_unset_bool_cv_float_post_frontier_cases as prior

RETURN = 'nested-unset-bool-cv-float-post-frontier-range-return'
THROW = 'nested-unset-bool-cv-range-warning-second-throw'
CASES = {RETURN: prior.CASES[RETURN]}
OUTPUTS = {RETURN: prior.OUTPUTS[RETURN]}
source = CASES[RETURN]
old_name = b'nestedUnsetBoolFloatRangePostWarningReturn'
new_name = b'nestedUnsetBoolFloatRangeSecondWarningThrow'
assert source.count(old_name) == 2
source = source.replace(old_name, new_name)
assert source.count(b'return true;') == 1
source = source.replace(b'return true;',
    b'if ($message !== "String offset cast occurred") { $GLOBALS["key"] = "done"; throw new Exception("range"); } return true;')
assert source.count(b'$key === 1.0e20') == 1
CASES[THROW] = source.replace(b'$key === 1.0e20', b'$key === "done"')
prefix, tail = OUTPUTS[RETURN].rsplit(b';', 1)
assert tail == b'Cannot use string offset as an array|5|7|ab|1|1'
OUTPUTS[THROW] = prefix + b';range|2|7|ab|0|1'
BITS = 4906019910204099648

WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_float_post_frontier_cases.py',
    'spec/semantics/30-storage.watsup',
    'spec/semantics/387-integer-operator-warnings.watsup',
    'spec/semantics/404-arithmetic-warning-continuations.watsup',
)
