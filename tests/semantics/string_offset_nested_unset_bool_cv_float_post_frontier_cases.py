"""Returning range casts and live handler masks expose secondary Warnings."""
import string_offset_nested_unset_bool_cv_float_post_cases as prior

CASES = {}
OUTPUTS = {}
for tag, index in (('range-return', 0), ('masked-range-throw', 3)):
    old_name = tuple(prior.CASES)[index]
    source = prior.CASES[old_name].replace(b'BoolFloatPost', b'BoolFloatRangePost')
    output = prior.OUTPUTS[old_name]
    if index == 0:
        assert source.count(b'1.5') == 2
        source = source.replace(b'1.5', b'1.0e20')
        first, rest = output.split(b';', 1)
        output = first + b';H:2:The float 1.0E+20 is not representable as an int, cast occurred;' + rest
    else:
        old = b'throw new Exception("handler");'
        assert source.count(old) == 1
        source = source.replace(old, b'set_error_handler("nestedUnsetBoolFloatRangePostWarningThrow", E_USER_WARNING); ' + old)
    name = 'nested-unset-bool-cv-float-post-frontier-' + tag
    CASES[name], OUTPUTS[name] = source, output

WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_float_post_cases.py',
    'vendor/php-src/Zend/zend_operators.h',
    'vendor/php-src/Zend/zend_operators.c',
    'vendor/php-src/Zend/zend.c',
    'vendor/php-src/Zend/zend_execute_API.c',
    'spec/semantics/206-error-handlers.watsup',
    'spec/semantics/207-error-handler-runtime.watsup',
)
