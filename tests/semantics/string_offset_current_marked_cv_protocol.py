#!/usr/bin/env python3
"""Check marked current CV reads after the initial undefined-CV Warning."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from string_offset_current_marked_cv_review import render
from string_offset_current_marked_cv_cases import CASES
from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--peer', action='store_true', help='check the independent reference-rebinding source')
    kinds = parser.add_mutually_exclusive_group()
    kinds.add_argument('--strings', action='store_true', help='check marked INTERNED/REQUEST string carriers')
    kinds.add_argument('--arrays', action='store_true', help='check the marked current ARRAY domain')
    kinds.add_argument('--variable-base', action='store_true', help='check the selected interned CV-base header')
    kinds.add_argument('--undefined-throw', action='store_true', help='check diagnostics after an undefined-key handler throws')
    kinds.add_argument('--variable-throw', action='store_true', help='check a saved VARIABLE base after an undefined-key handler throws')
    kinds.add_argument('--request-base', action='store_true', help='check an outside ordinary keeper of a selected REQUEST base')
    kinds.add_argument('--request-throw', action='store_true', help='check a retained REQUEST base after the first undefined-key handler throws')
    kinds.add_argument('--request-release', action='store_true', help='check last-owner REQUEST release after Undefined or CAST')
    kinds.add_argument('--request-release-registered', action='store_true', help='check last-owner release with the literal handler still registered')
    kinds.add_argument('--request-release-prior', action='store_true', help='check last-owner release through a nonowning prior callback stack')
    kinds.add_argument('--request-release-distinct', action='store_true', help='check release beside live independent REQUEST headers')
    kinds.add_argument('--request-release-key', action='store_true', help='check NULL release before current-key conversion')
    kinds.add_argument('--request-release-callback', action='store_true', help='check nonowning REQUEST callback headers')
    kinds.add_argument('--request-callback-owner', action='store_true', help='check selected REQUEST callback owners')
    args = parser.parse_args()
    cases = CASES
    selected_render = render
    if args.strings:
        from string_offset_current_marked_string_cv_cases import CASES as string_cases
        from string_offset_current_marked_string_cv_review import render as render_strings
        cases = string_cases
        selected_render = render_strings
    elif args.arrays:
        from string_offset_current_marked_array_cv_cases import CASES as array_cases
        from string_offset_current_marked_array_cv_review import render as render_arrays
        cases = array_cases
        selected_render = render_arrays
    elif args.variable_base:
        from string_offset_variable_base_cv_cases import CASES as base_cases
        from string_offset_variable_base_cv_review import render as render_base
        cases = base_cases
        selected_render = render_base
    elif args.undefined_throw:
        from string_offset_undefined_throw_cases import CASES as throw_cases
        from string_offset_undefined_throw_review import render as render_throw
        cases = throw_cases
        selected_render = render_throw
    elif args.variable_throw:
        from string_offset_variable_throw_cases import CASES as throw_cases
        from string_offset_variable_throw_review import render as render_throw
        cases = throw_cases
        selected_render = render_throw
    elif args.request_base:
        from string_offset_request_base_cv_cases import CASES as request_cases
        from string_offset_request_base_cv_review import render as render_request
        cases = request_cases
        selected_render = render_request
    elif args.request_throw:
        from string_offset_request_throw_cases import CASES as throw_cases
        from string_offset_request_throw_review import render as render_throw
        cases = throw_cases
        selected_render = render_throw
    elif args.request_release:
        from string_offset_request_release_cv_cases import CASES as release_cases
        from string_offset_request_release_cv_review import render as render_release
        cases = release_cases
        selected_render = render_release
    elif args.request_release_registered:
        from string_offset_request_release_registered_cv_cases import CASES as registered_cases
        from string_offset_request_release_registered_cv_review import render as render_registered
        cases = registered_cases
        selected_render = render_registered
    elif args.request_release_prior:
        from string_offset_request_release_prior_cv_cases import CASES as prior_cases
        from string_offset_request_release_prior_cv_review import render as render_prior
        cases = prior_cases
        selected_render = render_prior
    elif args.request_release_distinct:
        from string_offset_request_release_distinct_cv_cases import CASES as distinct_cases
        from string_offset_request_release_distinct_cv_review import render as render_distinct
        cases = distinct_cases
        selected_render = render_distinct
    elif args.request_release_key:
        from string_offset_request_release_key_cv_cases import CASES as key_cases
        from string_offset_request_release_key_cv_review import render as render_key
        cases = key_cases
        selected_render = render_key
    elif args.request_release_callback:
        from string_offset_request_release_callback_cv_cases import CASES as callback_cases
        from string_offset_request_release_callback_cv_review import render as render_callback
        cases = callback_cases
        selected_render = render_callback
    elif args.request_callback_owner:
        from string_offset_request_callback_owner_cv_cases import CASES as owner_cases
        from string_offset_request_callback_owner_cv_review import render as render_owner
        cases = owner_cases
        selected_render = render_owner
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'original.php'
    source.write_text(cases[int(args.peer)]['source'])
    control_source = None
    if args.undefined_throw and args.peer:
        control_source = out / 'literal-key-control.php'
        assert cases[1]['source'].count('"abc"[$key]') == 1
        control_source.write_text(cases[1]['source'].replace('"abc"[$key]', '"abc"[true]'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), source]
    if control_source is not None:
        watched.append(control_source)
    watched += [ROOT / name for name in (
        'spec/semantics/modules.json', 'tests/semantics/string_offset_current_marked_cv_review.py',
        'tests/semantics/string_offset_current_marked_cv_cases.py',
        'tests/semantics/string_offset_undefined_cv_review.py',
        'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/numeric_runner.ml',
        'tests/semantics/_build/default/numeric_runner.exe', 'frontend/worker.php', '.tools/php/bin/php',
        '.tools/php-file.so', '_build/default/adapter/main.exe', '.tools/spectec/bin/p4spectec')]
    if args.strings:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_current_marked_string_cv_cases.py',
            'tests/semantics/string_offset_current_marked_string_cv_review.py')]
    elif args.arrays:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_current_marked_array_cv_cases.py',
            'tests/semantics/string_offset_current_marked_array_cv_review.py')]
    elif args.variable_base:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_variable_base_cv_cases.py',
            'tests/semantics/string_offset_variable_base_cv_review.py')]
    elif args.undefined_throw:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_undefined_throw_cases.py',
            'tests/semantics/string_offset_undefined_throw_review.py',
            'tests/semantics/string_offset_undefined_throw_peer_review.py')]
    elif args.variable_throw:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_variable_throw_cases.py',
            'tests/semantics/string_offset_variable_throw_review.py',
            'tests/semantics/string_offset_undefined_throw_peer_review.py')]
    elif args.request_base:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_base_cv_cases.py',
            'tests/semantics/string_offset_request_base_cv_review.py')]
    elif args.request_throw:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_throw_cases.py',
            'tests/semantics/string_offset_request_throw_review.py',
            'tests/semantics/string_offset_undefined_throw_peer_review.py')]
    elif args.request_release:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_cv_cases.py',
            'tests/semantics/string_offset_request_release_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_registered:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_registered_cv_cases.py',
            'tests/semantics/string_offset_request_release_registered_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_prior:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_prior_cv_cases.py',
            'tests/semantics/string_offset_request_release_prior_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_distinct:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_distinct_cv_cases.py',
            'tests/semantics/string_offset_request_release_distinct_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_key_cv_cases.py',
            'tests/semantics/string_offset_request_release_key_cv_review.py',
            'tests/semantics/string_offset_request_release_distinct_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_callback:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_callback_cv_cases.py',
            'tests/semantics/string_offset_request_release_callback_cv_review.py',
            'tests/semantics/string_offset_request_release_key_cv_review.py',
            'tests/semantics/string_offset_request_release_distinct_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_callback_owner:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_owner_cv_cases.py',
            'tests/semantics/string_offset_request_callback_owner_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    if args.peer:
        if args.strings:
            from string_offset_current_marked_string_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_current_marked_string_cv_peer_review.py')
        elif args.arrays:
            from string_offset_current_marked_array_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_current_marked_array_cv_peer_review.py')
        elif args.variable_base:
            from string_offset_variable_base_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_variable_base_cv_peer_review.py')
        elif args.undefined_throw:
            from string_offset_undefined_throw_peer_review import render as render_peer
        elif args.variable_throw:
            from string_offset_variable_throw_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_variable_throw_peer_review.py')
        elif args.request_base:
            from string_offset_request_base_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_base_cv_peer_review.py')
        elif args.request_throw:
            from string_offset_request_throw_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_throw_peer_review.py')
        elif args.request_release:
            from string_offset_request_release_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_release_cv_peer_review.py')
        elif args.request_release_registered:
            from string_offset_request_release_registered_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_release_registered_cv_peer_review.py')
        elif args.request_release_prior:
            from string_offset_request_release_prior_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')
        elif args.request_release_distinct:
            from string_offset_request_release_distinct_cv_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_release_distinct_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_release_key:
            from string_offset_request_release_key_cv_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_release_key_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_distinct_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_release_callback:
            from string_offset_request_release_callback_cv_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_release_callback_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_key_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_distinct_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_callback_owner:
            from string_offset_request_callback_owner_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_owner_cv_peer_review.py')
        else:
            from string_offset_current_marked_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_current_marked_cv_peer_review.py')
        selected_render = render_peer
    before = {str(path): digest(path) for path in watched}
    report = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'case_id': cases[int(args.peer)]['id'], 'strings': args.strings, 'arrays': args.arrays,
        'variable_base': args.variable_base,
        'undefined_throw': args.undefined_throw,
        'variable_throw': args.variable_throw,
        'request_base': args.request_base,
        'request_throw': args.request_throw,
        'request_release': args.request_release,
        'request_release_registered': args.request_release_registered,
        'request_release_prior': args.request_release_prior,
        'request_release_distinct': args.request_release_distinct,
        'request_release_key': args.request_release_key,
        'request_release_callback': args.request_release_callback,
        'request_callback_owner': args.request_callback_owner,
        'inputs': before, 'mode': 'production SL fixture' if (args.request_release_prior or args.request_release_distinct or args.request_release_key or args.request_release_callback or args.request_callback_owner) else 'AL fixture',
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'source_credit': 0, 'passed': False}
    if control_source is not None:
        report['derived_source'] = {'path': str(control_source), 'parent': str(source),
            'change': 'replace the sole outer key CV with literal true', 'source_credit': 0}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            if control_source is not None:
                parsed_control = frontend.request({'op': 'parse',
                    'source': base64.b64encode(control_source.read_bytes()).decode()})
                assert parsed_control['accepted']
                checked_control = adapter.request({'op': 'check', 'ast': parsed_control['ast'], 'fixture': True})
        finally:
            adapter.close()
        program = out / 'original.program'
        program.write_text(checked['fixture'])
        generated = [program]
        render_args = [checked['fixture'], base64.b64encode(bytes(source)).decode()]
        if control_source is not None:
            control_program = out / 'literal-key-control.program'
            control_program.write_text(checked_control['fixture'])
            generated.append(control_program)
            render_args += [checked_control['fixture'], base64.b64encode(bytes(control_source)).decode()]
        fixture = out / 'continuation.watsup'
        text, report['premises'], report['derived_conditions'] = selected_render(*render_args)
        fixture.write_text(text)
        generated.append(fixture)
        report['generated'] = {str(path): digest(path) for path in generated}
        report['compiler'] = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo',
            *map(str, modules), str(fixture)], out / 'compiler', 120)
        assert report['compiler']['exit'] == 0 and not report['compiler']['timeout']
        assert not (out / 'compiler.stderr').read_bytes()
        assert b'def $main' in (out / 'compiler.stdout').read_bytes()
        report['execution'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
            *(['--sl'] if (args.request_release_prior or args.request_release_distinct or args.request_release_key or args.request_release_callback or args.request_callback_owner) else []),
            *map(str, modules), str(fixture)], out / 'state', 180)
        report['passed'] = (report['execution']['exit'] == 0 and not report['execution']['timeout']
            and (out / 'state.stdout').read_bytes() == b'true\n'
            and not (out / 'state.stderr').read_bytes())
        report['generated_stable'] = report['generated'] == {str(path): digest(path) for path in generated}
        report['passed'] = report['passed'] and report['generated_stable']
    finally:
        frontend.close()
        report['inputs_stable'] = before == {str(path): digest(path) for path in watched}
        report['head_stable'] = report['head'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['premises'], 'pass' if report['passed'] else 'fail')
    assert report['passed']


if __name__ == '__main__':
    main()
