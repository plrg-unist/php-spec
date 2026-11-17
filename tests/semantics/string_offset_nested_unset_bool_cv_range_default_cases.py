"""Normal first handlers leave live Warning-excluding masks for a range cast."""
import os

import string_offset_nested_unset_bool_cv_range_warning_cases as prior

CASES = {}
OUTPUTS = {}
MASKS = {}
old_name = b'nestedUnsetBoolFloatRangePostWarningReturn'
for tag, new_name, change, mask in (
    ('other-mask', b'nestedUnsetBoolFloatRangeDefaultOtherMask',
     b'set_error_handler("nestedUnsetBoolFloatRangeDefaultOtherMask", E_USER_WARNING); ', 512),
    ('restored-mask', b'nestedUnsetBoolFloatRangeDefaultRestoredMask',
     b'restore_error_handler(); ', 0),
):
    source = prior.CASES[prior.RETURN]
    assert source.count(old_name) == 2
    source = source.replace(old_name, new_name)
    assert source.count(b'return true;') == 1
    name = 'nested-unset-bool-cv-range-default-' + tag
    CASES[name] = source.replace(b'return true;', change + b'return true;')
    second = b'H:2:The float 1.0E+20 is not representable as an int, cast occurred;'
    assert prior.OUTPUTS[prior.RETURN].count(second) == 1
    OUTPUTS[name] = prior.OUTPUTS[prior.RETURN].replace(second, b'')
    MASKS[name] = mask

BITS = prior.BITS
MESSAGE = b'The float 1.0E+20 is not representable as an int, cast occurred'


def stderr(path):
    return b'Warning: ' + MESSAGE + b' in ' + os.fsencode(path) + b' on line 5\n'


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_range_warning_cases.py',
    'spec/semantics/101-error-suppression.watsup',
    'spec/semantics/237-display-errors.watsup',
    'spec/semantics/391-output-buffers.watsup',
)
