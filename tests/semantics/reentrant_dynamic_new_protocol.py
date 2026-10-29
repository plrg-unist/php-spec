#!/usr/bin/env python3
"""Reach dynamic NEW before suppressed lookup and through genuine retry."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

import reentrant_unlinked_new_protocol as prior
import reentrant_dynamic_new_review_protocol as review
import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
CASES = ('reference-case-leading-slash', 'acquired-selector-once', 'carrier-retry-after-unwind', 'independent-interface-alias')
term, b64 = prior.term, prior.b64
PREFIX = prior.PREFIX + r'''
dec $s118_front(pstate, nat) : bool
def $s118_front(S, 0) = true
  -- if S.TODO = (DYNAMIC_NEW_CLASS z z_fetch) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if S_read = $resolve_at(S,S.RESULT,z_fetch)
  -- if S_read.RESULT = KNOWN pvalue
  -- if $dynamic_new_value_name(S_read,porigin,pvalue) = (ptbytes)
  -- if $ptlc(ptbytes) = $ptascii("c118")
def $s118_front(S, 1) = true
  -- if S.TODO = (AUTO_NEW ptbytes phpType7* z z_fetch) :: ptask_tail*
  -- if $ptlc(ptbytes) = $ptascii("c118")
def $s118_front(S, n) = false -- otherwise
dec $s118_seek(pstate, nat, nat) : pstate
def $s118_seek(S, n_phase, 0) = S
def $s118_seek(S, n_phase, n) = S
  -- if $(n > 0)
  -- if $s118_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $s118_seek(S, n_phase, n) = $s118_seek($drive_steps($s117_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$s118_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $s118_marker(ptask*) : bool
def $s118_marker(eps) = false
def $s118_marker(ptask :: ptask_tail*) = ($dynamic_new_marker(ptask) \/ $s118_marker(ptask_tail*))
'''


def assertions(name, source, main, code, responses, row, expected):
    raw = b'C118' if name == 'acquired-selector-once' else b'\\c118'
    target = raw.lstrip(b'\\')
    checks = [
        'S_wait0 = $php_run(' + main + ',5000,' + json.dumps(b64(str(source).encode())) + ')',
        'S_wait0.COMPLETION = SOURCE_PENDING',
        'S_wait0.EVALCONTEXTS = pevalcontext_outer :: eps',
        'pevalcontext_outer.UNIT = 1',
        'pevalcontext_outer.BYTES = ' + term(code['outer']),
        '$eval_response_valid(S_wait0,' + responses['outer'] + ')',
        'S_body0 = $eval_resume(S_wait0,' + responses['outer'] + ')',
        'S_waitP = $drive_steps(S_body0,5000)',
        'S_waitP.COMPLETION = SOURCE_PENDING',
        'S_waitP.EVALCONTEXTS = pevalcontext_P :: pevalcontext_outer2 :: eps',
        'pevalcontext_P.UNIT = 2',
        'pevalcontext_P.BYTES = ' + term(code['parent']),
        '$eval_response_valid(S_waitP,' + responses['parent'] + ')',
        'S_bodyP = $eval_resume(S_waitP,' + responses['parent'] + ')',
        'S_found = $s118_seek(S_bodyP,0,5000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_front = S_found[.COMPLETION = NORMAL]',
        'S_front.TODO = (DYNAMIC_NEW_CLASS z_new z_fetch) :: ptask_tail*',
        'S_front.ORIGIN = (porigin_new)',
        '$dynamic_new_site(S_front,porigin_new,z_new,z_fetch)',
        'z_fetch = ' + str(row['fetchline']),
        'S_read = $resolve_at(S_front,S_front.RESULT,z_fetch)',
        'S_read.COMPLETION = NORMAL',
        'S_read.RESULT = KNOWN pvalue_selected',
        '$string_bytes(pvalue_selected) = (' + term(raw) + ')',
        '$dynamic_new_value_name(S_read,porigin_new,pvalue_selected) = (' + term(target) + ')',
        '~$dynamic_new_known(S_read,' + term(target) + ')',
        '~$s118_marker(S_front.TODO)',
        'S_front.FRAMES = pframe_Q :: pframe_P :: eps',
        'pframe_P.TODO = (AUTO_RESULT pautoloadcall_C pautoloadentry_C poperand_C) :: ptask_P*',
        'pautoloadcall_C.RESUME = AUTO_PUBLISH porigin_C',
        'S_saved = $constant_frame_scope(S_front,pframe_P,eps)',
        '$autoload_selected_valid(S_saved,pautoloadcall_C,pautoloadentry_C)',
        '$autoload_new_unlinked_call(S_saved,pautoloadcall_C,' + term(target) + ')',
        '$autoload_pending(S_read,' + term(target) + ')',
        '~$autoload_new_pending(S_read,' + term(target) + ')',
        '$autoload_new_pending(S_read,$ptascii("Unrelated118"))',
        '$call_descriptors_valid(S_front)',
        'S_budget0 = $drive_steps(S_front,0)',
        'S_budget0 = S_front[.COMPLETION = BUDGET]',
        'S_resume = S_budget0[.COMPLETION = NORMAL]',
        'S_resume = S_front',
        'PhpStep: S_resume ~> S_raw',
        'S_raw.COMPLETION = THROWN "Error" (' + term(b'Class "' + raw + b'" not found') + ') z_fetch',
        'S_raw.TODO = S_front.TODO',
        'S_raw.FRAMES = S_front.FRAMES',
        'S_raw.AUTOLOAD = S_front.AUTOLOAD',
        'S_raw.SOURCES = S_front.SOURCES',
        'S_raw.CLASSNAMES = S_front.CLASSNAMES',
        'S_raw.EVENTS = S_front.EVENTS',
        'S_step_budget = $drive_steps(S_resume,1)',
        'S_step_budget.COMPLETION = BUDGET',
        'S_after = S_step_budget[.COMPLETION = NORMAL]',
    ]
    if name == 'carrier-retry-after-unwind':
        checks += [
            'pvalue_selected = PSTRING_CARRIER pstringidentity_active ptbytes_active',
            '$string_carrier_valid(S_read,pvalue_selected)',
            'S_retry_found = $s118_seek(S_after,0,5000)',
            r'S_retry_found.COMPLETION = NORMAL \/ S_retry_found.COMPLETION = BUDGET',
            'S_retry = S_retry_found[.COMPLETION = NORMAL]',
            'S_retry.TODO = (DYNAMIC_NEW_CLASS z_retry z_retry_fetch) :: ptask_retry*',
            'S_retry.ORIGIN = (porigin_retry)',
            'S_retry.FRAMES = eps',
            'S_retry_read = $resolve_at(S_retry,S_retry.RESULT,z_retry_fetch)',
            'S_retry_read.RESULT = KNOWN pvalue_retry',
            'pvalue_retry = PSTRING_CARRIER pstringidentity_retry ptbytes_retry',
            '$string_carrier_valid(S_retry_read,pvalue_retry)',
            '$string_bytes(pvalue_retry) = (' + term(raw) + ')',
            '$autoload_new_pending(S_retry_read,' + term(target) + ')',
            '~$s118_marker(S_retry.TODO)',
            'PhpStep: S_retry ~> S_begin',
            'S_begin.TODO = (AUTO_NEXT pautoloadcall_retry) :: (DYNAMIC_NEW_FINISH pdynamicnew_retry) :: ptask_retry*',
            'pdynamicnew_retry.SITE = porigin_retry',
            'pdynamicnew_retry.SOURCE = pvalue_retry',
            'pdynamicnew_retry.CLASS = ' + term(target),
            'pdynamicnew_retry.FETCHLINE = z_retry_fetch',
            '$dynamic_new_valid(S_begin,pdynamicnew_retry)',
            '$autoload_resume_valid(S_begin,pautoloadcall_retry)',
            '$call_descriptors_valid(S_begin)',
            'S_nomarker = S_begin[.TODO = (AUTO_NEXT pautoloadcall_retry) :: ptask_retry*]',
            '~$autoload_resume_valid(S_nomarker,pautoloadcall_retry)',
            '~$call_descriptors_valid(S_nomarker)',
            'pdynamicnew_wrong = pdynamicnew_retry[.CLASS = $ptascii("Wrong118")]',
            '~$dynamic_new_valid(S_begin,pdynamicnew_wrong)',
            'pdynamicnew_line = pdynamicnew_retry[.FETCHLINE = $(z_retry_fetch + 1)]',
            '~$dynamic_new_valid(S_begin,pdynamicnew_line)',
            'S_missing_found = $s118_seek(S_begin,1,5000)',
            r'S_missing_found.COMPLETION = NORMAL \/ S_missing_found.COMPLETION = BUDGET',
            'S_missing = S_missing_found[.COMPLETION = NORMAL]',
            'S_missing.TODO = (AUTO_NEW ptbytes_missing phpType7* z_retry z_retry_fetch) :: (DYNAMIC_NEW_FINISH pdynamicnew_retry) :: ptask_retry*',
            '$autoload_new_diagnostic(S_missing,ptbytes_missing) = ' + term(raw),
            '$call_descriptors_valid(S_missing)',
            'PhpStep: S_missing ~> S_retry_error',
            'S_retry_error.COMPLETION = THROWN "Error" (' + term(b'Class "' + raw + b'" not found') + ') z_retry_fetch',
            'S_finish = $drive_steps(S_missing,5000)',
        ]
    else:
        checks += [
            'S_waitQ = $drive_steps(S_after,5000)',
            'S_waitQ.COMPLETION = SOURCE_PENDING',
            'S_waitQ.EVALCONTEXTS = pevalcontext_Q :: pevalcontext_tail*',
            'pevalcontext_Q.UNIT = 3',
            'pevalcontext_Q.BYTES = ' + term(code['Q']),
            '$eval_response_valid(S_waitQ,' + responses['Q'] + ')',
            'S_finish = $drive_steps($eval_resume(S_waitQ,' + responses['Q'] + '),5000)',
        ]
    checks += ['S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps', '~$s118_marker(S_finish.TODO)',
        '$s117_output(S_finish.EVENTS) = ' + term(expected), '$call_descriptors_valid(S_finish)']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('fixtures', 'check'), required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--reviewer-sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    sources, reviewer_sources, out = args.sources.resolve(), args.reviewer_sources.resolve(), args.output.resolve()
    selected = (args.case,) if args.case else CASES
    if args.phase == 'fixtures':
        out.mkdir()
    freeze = json.loads((sources / 'freeze.json').read_text())
    paths = [Path(__file__), Path(prior.__file__), Path(review.__file__), Path(types.__file__),
        ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/typed_static_invoke_set_protocol.py',
        ROOT / 'spec/semantics/modules.json',
        ROOT / 'spec/semantics/260-dynamic-new.watsup', ROOT / 'spec/semantics/277-autoload.watsup',
        ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe', RUNNER,
        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
        ROOT / 'tests/semantics/profile.json', sources / 'freeze.json',
        sources / 'native-report.json', sources / 'changed-report.json']
    for name in selected:
        directory = reviewer_sources if name == 'independent-interface-alias' else sources / name
        paths += [directory / 'main.php', directory / 'native.stdout']
        if name == 'independent-interface-alias':
            paths += [directory / 'freeze.json', directory / 'native-report.json', directory / 'changed-report.json']
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    before = pins()
    report = {'phase': args.phase, 'selected': selected, 'inputs': before,
        'affinity': sorted(os.sched_getaffinity(0)),
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
        'records': [], 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            adapter = None
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                changed = json.loads((sources / 'changed-report.json').read_text())
                for name in selected:
                    directory = reviewer_sources if name == 'independent-interface-alias' else sources / name
                    source = directory / 'main.php'
                    if name == 'independent-interface-alias':
                        row = json.loads((directory / 'freeze.json').read_text())
                        checked_row = json.loads((directory / 'changed-report.json').read_text())
                        source_sha = row['source_sha256']
                    else:
                        row, = [x for x in freeze['cases'] if x['id'] == name]
                        checked_row, = [x for x in changed['records'] if x['id'] == name]
                        source_sha = row['main_sha256']
                    assert checked_row['exact'] and checked_row['status'] == 'normal'
                    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
                    parsed = frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})
                    assert parsed['accepted']
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok']
                    strings = [base64.b64decode(node['fields'][0]['bytes']) for node in prior.nodes(parsed['ast']) if node['node'] == 'Scalar_String']
                    if name == 'independent-interface-alias':
                        code = {'outer': next(x for x in strings if x.startswith(b'function mark118r(){')),
                            'D': next(x for x in strings if x.startswith(b'class D118R ')),
                            'I': next(x for x in strings if x == b'interface I118R {}')}
                    else:
                        code = {'outer': next(x for x in strings if x.startswith(b'function mark118(){')),
                            'parent': next(x for x in strings if x == b'class P118 extends Q118 {}')}
                        if name != 'carrier-retry-after-unwind':
                            code['Q'] = next(x for x in strings if x.startswith(b'class Q118 {function q()'))
                    responses = {label: prior.response(frontend, adapter, value, unit)
                        for unit, (label, value) in enumerate(code.items(), 1)}
                    if name == 'independent-interface-alias':
                        prefix = review.PREFIX
                        checks = review.assertions(checked['fixture'], source,
                            responses['outer'], responses['I'], responses['D'],
                            (directory / 'native.stdout').read_bytes(),
                            temporary=row.get('temporary_carrier', False))
                    else:
                        prefix = PREFIX
                        checks = assertions(name, source, checked['fixture'], code, responses, row,
                            (directory / 'native.stdout').read_bytes())
                    target = out / name
                    target.mkdir()
                    (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
                    (target / 'protocol.watsup').write_text(prefix + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join(('  -- ' if x.startswith('PhpStep:') else '  -- if ') + x + '\n' for x in checks))
            finally:
                try:
                    if adapter:
                        adapter.close()
                finally:
                    frontend.close()
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            from typed_static_invoke_set_protocol import process
            for name in selected:
                target = out / name
                command = [str(RUNNER), '--sl', *modules, str(target / 'protocol.watsup')]
                result = process(command, target / 'check', 120, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                report['records'].append({'case': name, 'command': command, 'exit': result.returncode,
                    'passed': passed, 'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(name, 'pass' if passed else 'fail', flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(selected) and all(x['passed'] for x in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (args.phase + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
