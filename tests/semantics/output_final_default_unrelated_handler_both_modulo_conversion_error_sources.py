#!/usr/bin/env python3
"""Two same-class MOD notices leave the opposite numeric handler uncalled."""
from pathlib import Path
import function_scope as scope
import output_final_default_unrelated_handler_right_modulo_conversion_error_sources as previous

LEFT = {'leading': b"'1x'", 'string': b"'1.5'", 'float': b'1.5',
        'finite': b'1e30', 'infinite': b'1e999'}
CASES = {}
for name, source in previous.CASES.items():
    kind = name.rsplit('-', 1)[1]
    old = b'$left = 1;' if b'$left = 1;' in source else b'return 1 %'
    new = b'$left = ' + LEFT[kind] + b';' if old.startswith(b'$left') else b'return ' + LEFT[kind] + b' %'
    assert source.count(old) == 1
    CASES[name.replace('-right-modulo-', '-both-modulo-')] = source.replace(old, new)
for kind, (value, _) in previous.VALUES.items():
    source = previous.CASES['native-default-unrelated-handler-right-modulo-conversion-error-constant-' + kind]
    old = b'return 1 % ' + value + b';'
    assert source.count(old) == 1
    body = b'$value = ' + value + b';\n        return $value % $value;'
    CASES['native-default-unrelated-handler-both-modulo-conversion-error-same-cv-' + kind] = source.replace(old, body)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-unrelated-handler-both-modulo-conversion-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
