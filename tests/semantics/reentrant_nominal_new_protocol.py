#!/usr/bin/env python3
"""Reach fixed/dynamic NEW across supported nominal declaration publication."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

import interface_dependency_autoload_protocol as iface
import reentrant_unlinked_new_protocol as source
import reentrant_nominal_new_review_protocol as review
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
CASES = ('interface-publication', 'interface-unwind-retry', 'trait-publication', 'independent-helper')
term, b64 = source.term, source.b64
PREFIX = iface.PREFIX + r'''
dec $s119_front(pstate, preqbytes, nat) : bool
def $s119_front(S, preqbytes, 0) = true
  -- if S.TODO = (EVAL (NExprNew name phpType6 metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $new_source_name(S,porigin) = (preqbytes)
def $s119_front(S, preqbytes, 1) = true
  -- if S.TODO = (DYNAMIC_NEW_CLASS z z_fetch) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if S_read = $resolve_at(S,S.RESULT,z_fetch)
  -- if S_read.RESULT = KNOWN pvalue
  -- if $dynamic_new_value_name(S_read,porigin,pvalue) = (ptbytes)
  -- if $ptlc(ptbytes) = $ptlc(preqbytes)
def $s119_front(S, preqbytes, n) = false -- otherwise
dec $s119_seek(pstate, preqbytes, nat, nat) : pstate
def $s119_seek(S, preqbytes, n_phase, 0) = S
def $s119_seek(S, preqbytes, n_phase, n) = S
  -- if $(n > 0)
  -- if $s119_front(S,preqbytes,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $s119_seek(S, preqbytes, n_phase, n) = $s119_seek($drive_steps($test_iface_running(S),1),preqbytes,n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$s119_front(S,preqbytes,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $s119_marker(ptask*) : bool
def $s119_marker(eps) = false
def $s119_marker(ptask :: ptask_tail*) = ($dynamic_new_marker(ptask) \/ $s119_marker(ptask_tail*))
'''


def reach(label, prior, target, phase):
    return [label + '_found = $s119_seek(' + prior + ',' + term(target) + ',' + str(phase) + ',5000)',
        label + r'_found.COMPLETION = NORMAL \/ ' + label + '_found.COMPLETION = BUDGET',
        label + ' = ' + label + '_found[.COMPLETION = NORMAL]',
        '$s119_front(' + label + ',' + term(target) + ',' + str(phase) + ')',
        '$call_descriptors_valid(' + label + ')']


def assertions(row, main, path, responses, expected):
    kind = row['kind']
    target, dependency = (b'I119', b'J119') if kind == 'interface' else (b'T119', b'U119')
    raw = b'\\' + target.lower()
    resume = 'AUTO_INTERFACE' if kind == 'interface' else 'AUTO_TRAIT'
    checks = [
        'S_wait = $php_run(' + main + ',5000,' + json.dumps(b64(str(path).encode())) + ')',
        'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.EVALCONTEXTS = pevalcontext_outer :: eps',
        'pevalcontext_outer.UNIT = 1',
        '$eval_response_valid(S_wait,' + responses['outer'] + ')',
        'S_body = $eval_resume(S_wait,' + responses['outer'] + ')',
        *reach('S_F', 'S_body', target, 0),
        'S_F.TODO = (EVAL (NExprNew name_F (SEQUENCE phpType7_F*) metadata_F)) :: ptask_F*',
        'S_F.ORIGIN = (porigin_F)',
        'S_F.FRAMES = pframe_wait :: eps',
        'pframe_wait.TODO = (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_wait*',
        'pautoloadcall.RESUME = ' + resume + ' porigin_target ' + term(dependency),
        'S_scope = $constant_frame_scope(S_F,pframe_wait,eps)',
        '$autoload_selected_valid(S_scope,pautoloadcall,pautoloadentry)',
        '$class_at(S_scope.CLASSES,porigin_target) = (pclassdesc_target)',
        'pclassdesc_target.NAME = ' + term(target),
        'pclassdesc_target.KIND = ' + json.dumps(kind),
        '$autoload_' + kind + '_kind($origin_node(S_scope.SOURCES,porigin_target)) = (' + json.dumps(kind) + ')',
        '$class_named(S_F.CLASSNAMES,$ptlc(' + term(target) + ')) = eps',
        '$autoload_pending(S_F,' + term(target) + ')',
        '~$autoload_new_pending(S_F,' + term(target) + ')',
        '$autoload_new_unlinked_call(S_scope,pautoloadcall,' + term(target) + ')',
        '$autoload_new_pending(S_F,$ptascii("Unrelated119"))',
        'pclassdesc_wrong = pclassdesc_target[.KIND = "enum"]',
        'S_wrong = S_scope[.CLASSES = $test_iface_replace(S_scope.CLASSES,pclassdesc_wrong)]',
        '~$autoload_new_unlinked_call(S_wrong,pautoloadcall,' + term(target) + ')',
        '~$autoload_selected_valid(S_wrong,pautoloadcall,pautoloadentry)',
        'pautoloadcall_wrong = pautoloadcall[.RESUME = AUTO_PUBLISH porigin_F]',
        '~$autoload_new_unlinked_call(S_scope,pautoloadcall_wrong,' + term(target) + ')',
        'pautoloadcall_explicit = pautoloadcall[.MODE = AUTO_EXPLICIT pautoloadentry.CALL]',
        '~$autoload_new_unlinked_call(S_scope,pautoloadcall_explicit,' + term(target) + ')',
        'S_budgetF = $drive_steps(S_F,0)',
        'S_budgetF = S_F[.COMPLETION = BUDGET]',
        'S_resumeF = S_budgetF[.COMPLETION = NORMAL]',
        'S_resumeF = S_F',
        'PhpStep: S_resumeF ~> S_rawF',
        'S_rawF.COMPLETION = THROWN "Error" (' + term(b'Class "' + target + b'" not found') + ') ' + str(row['lines']['BF']),
        'S_rawF.TODO = ptask_F*',
        'S_rawF.AUTOLOAD = S_F.AUTOLOAD',
        'S_rawF.CLASSNAMES = S_F.CLASSNAMES',
        'S_rawF.EVENTS = S_F.EVENTS',
        'S_rawF.ALLOCATIONS = S_F.ALLOCATIONS',
        'S_budgetF1 = $drive_steps(S_resumeF,1)',
        'S_budgetF1.COMPLETION = BUDGET',
        'S_afterF = S_budgetF1[.COMPLETION = NORMAL]',
        *reach('S_D', 'S_afterF', target, 1),
        'S_D.TODO = (DYNAMIC_NEW_CLASS z_D z_fetchD) :: ptask_D*',
        'z_fetchD = ' + str(row['lines']['BD']),
        'S_D.ORIGIN = (porigin_D)',
        'S_D.FRAMES = pframe_wait :: eps',
        'S_readD = $resolve_at(S_D,S_D.RESULT,z_fetchD)',
        'S_readD.RESULT = KNOWN pvalue_D',
        'pvalue_D = PSTRING_CARRIER (REQUEST_STRING n_string) ptbytes_D',
        '$string_carrier_valid(S_readD,pvalue_D)',
        '$string_bytes(pvalue_D) = (' + term(raw) + ')',
        '$dynamic_new_value_name(S_readD,porigin_D,pvalue_D) = (' + term(target.lower()) + ')',
        '~$s119_marker(S_D.TODO)',
        '$autoload_pending(S_readD,' + term(target.lower()) + ')',
        '~$autoload_new_pending(S_readD,' + term(target.lower()) + ')',
        'PhpStep: S_D ~> S_rawD',
        'S_rawD.COMPLETION = THROWN "Error" (' + term(b'Class "' + raw + b'" not found') + ') z_fetchD',
        'S_rawD.TODO = S_D.TODO',
        'S_rawD.AUTOLOAD = S_D.AUTOLOAD',
        'S_rawD.CLASSNAMES = S_D.CLASSNAMES',
        'S_rawD.EVENTS = S_D.EVENTS',
        'S_rawD.ALLOCATIONS = S_D.ALLOCATIONS',
        'S_budgetD1 = $drive_steps(S_D,1)',
        'S_budgetD1.COMPLETION = BUDGET',
        'S_afterD = S_budgetD1[.COMPLETION = NORMAL]',
    ]
    if row['retry']:
        checks += [
            *reach('S_retryF', 'S_afterD', target, 0),
            'S_retryF.FRAMES = eps',
            '$class_named(S_retryF.CLASSNAMES,$ptlc(' + term(target) + ')) = eps',
            '~$autoload_new_unlinked_frames(S_retryF,S_retryF.FRAMES,' + term(target) + ')',
            '$autoload_new_pending(S_retryF,' + term(target) + ')',
            'PhpStep: S_retryF ~> S_beginF',
            'S_beginF.TODO = (AUTO_NEXT pautoloadcall_retryF) :: ptask_retryF*',
            'pautoloadcall_retryF.NAME = ' + term(target),
            '$autoload_call_valid(S_beginF,pautoloadcall_retryF)',
            *reach('S_retryD', 'S_beginF', target, 1),
            'S_retryD.TODO = (DYNAMIC_NEW_CLASS z_retry z_fetch_retry) :: ptask_retryD*',
            'S_retryD.FRAMES = eps',
            'S_read_retry = $resolve_at(S_retryD,S_retryD.RESULT,z_fetch_retry)',
            'S_read_retry.RESULT = KNOWN pvalue_retry',
            '$string_bytes(pvalue_retry) = (' + term(raw) + ')',
            '$autoload_new_pending(S_read_retry,' + term(target.lower()) + ')',
            'PhpStep: S_retryD ~> S_beginD',
            'S_beginD.TODO = (AUTO_NEXT pautoloadcall_retryD) :: (DYNAMIC_NEW_FINISH pdynamicnew_retry) :: ptask_retryD*',
            'pdynamicnew_retry.SOURCE = pvalue_retry',
            'pdynamicnew_retry.CLASS = ' + term(target.lower()),
            '$dynamic_new_valid(S_beginD,pdynamicnew_retry)',
            '$autoload_call_valid(S_beginD,pautoloadcall_retryD)',
            '$call_descriptors_valid(S_beginD)',
            'S_finish = $drive_steps(S_beginD,5000)',
        ]
    else:
        checks += [
            'S_wait_dependency = $drive_steps(S_afterD,5000)',
            'S_wait_dependency.COMPLETION = SOURCE_PENDING',
            'S_wait_dependency.EVALCONTEXTS = pevalcontext_dependency :: pevalcontext_outer2 :: eps',
            'pevalcontext_dependency.UNIT = 2',
            '$eval_response_valid(S_wait_dependency,' + responses['dependency'] + ')',
            'S_body_dependency = $eval_resume(S_wait_dependency,' + responses['dependency'] + ')',
            *reach('S_published', 'S_body_dependency', target, 0),
            '$class_named(S_published.CLASSNAMES,$ptlc(' + term(target) + ')) = (porigin_target)',
            '$dynamic_new_known(S_published,' + term(target) + ')',
            '~$autoload_new_pending(S_published,' + term(target) + ')',
            'S_finish = $drive_steps(S_published,5000)',
        ]
    checks += ['S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.FRAMES = eps', '~$s119_marker(S_finish.TODO)',
        '$test_iface_outputs(S_finish.EVENTS) = ' + term(expected), '$call_descriptors_valid(S_finish)']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('fixtures', 'check'), required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--reviewer-sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    inputs, reviewer, out = args.sources.resolve(), args.reviewer_sources.resolve(), args.output.resolve()
    selected = (args.case,) if args.case else CASES
    if args.phase == 'fixtures':
        out.mkdir()
    paths = [Path(__file__), Path(iface.__file__), Path(source.__file__), Path(review.__file__),
        ROOT / 'tests/semantics/static_types.py', ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/typed_static_invoke_set_protocol.py',
        ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/277-autoload.watsup',
        ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe', RUNNER,
        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
        inputs / 'freeze.json', inputs / 'native-report.json', inputs / 'changed-report.json']
    for name in selected:
        directory = reviewer if name == 'independent-helper' else inputs / name
        paths += [directory / 'main.php', directory / 'native.stdout']
        if name == 'independent-helper':
            paths += [directory / 'freeze.json', directory / 'native-report.json', directory / 'changed-report.json']
        if args.phase == 'check':
            paths += [out / name / 'assertions.json', out / name / 'protocol.watsup']
    pins = lambda: {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    before = pins()
    report = {'phase': args.phase, 'selected': selected, 'inputs': before,
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
        'affinity': sorted(os.sched_getaffinity(0)), 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            adapter = None
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                freeze = json.loads((inputs / 'freeze.json').read_text())
                changed = json.loads((inputs / 'changed-report.json').read_text())
                for name in selected:
                    directory = reviewer if name == 'independent-helper' else inputs / name
                    if name == 'independent-helper':
                        row = json.loads((directory / 'freeze.json').read_text())
                        outcome = json.loads((directory / 'changed-report.json').read_text())
                        expected_hash = row['source_sha256']
                    else:
                        row, = [x for x in freeze['cases'] if x['id'] == name]
                        outcome, = [x for x in changed['records'] if x['id'] == name]
                        expected_hash = row['main_sha256']
                    assert outcome['exact'] and outcome['status'] == 'normal'
                    path = directory / 'main.php'
                    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash
                    parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
                    assert parsed['accepted']
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok']
                    strings = [base64.b64decode(node['fields'][0]['bytes']) for node in source.nodes(parsed['ast']) if node['node'] == 'Scalar_String']
                    outer = next(x for x in strings if x.startswith(b'function mark119r(){' if name == 'independent-helper' else b'function mark119(){'))
                    responses = {'outer': source.response(frontend, adapter, outer, 1)}
                    if name == 'independent-helper':
                        dependency = next(x for x in strings if x == b'interface J119R {}')
                    elif not row['retry']:
                        dependency = next(x for x in strings if x == (b'interface J119 {}' if row['kind'] == 'interface' else b'trait U119 {}'))
                    else:
                        dependency = None
                    if dependency is not None:
                        responses['dependency'] = source.response(frontend, adapter, dependency, 2)
                    expected = (directory / 'native.stdout').read_bytes()
                    if name == 'independent-helper':
                        prefix = review.PREFIX
                        checks = review.assertions(checked['fixture'], path, responses['outer'], responses['dependency'], expected)
                    else:
                        prefix = PREFIX
                        checks = assertions(row, checked['fixture'], path, responses, expected)
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
            modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
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
