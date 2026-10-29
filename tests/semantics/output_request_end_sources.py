#!/usr/bin/env python3
"""Request-end scalar output handlers and explicit abnormal-finalization bounds."""
from pathlib import Path
import function_scope as scope

HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('output_request_end_' + name + '.php')).read_bytes()
    for name in (
        'disabled',
        'exit_integer',
        'method_shutdown',
        'named_force',
        'nested_closure',
        'positive_empty',
        'positive_tail',
        'peer_exit_string',
        'peer_nested_invokable',
        'peer_positive_nested',
        'peer_warning_callback',
        'final_local_destructor',
        'peer_default_to_positive',
        'final_typed_diagnostic',
        'final_global_retirement',
    )
}
BOUNDARIES = {
    name: (HERE / ('output_request_end_' + name + '.php')).read_bytes()
    for name in (
        'held_throw',
        'peer_captured_throw',
    )
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-request-end', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
