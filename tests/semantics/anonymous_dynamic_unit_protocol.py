#!/usr/bin/env python3
"""Dynamic anonymous-class compilation names, site reuse and closed RTD history."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = {'eval': ('static-native-v58', 'eval-anonymous', 'native_observation'),
         'include': ('static-native-v58', 'include-anonymous', 'native_observation')}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'

PREFIX = r'''
dec $test_anon_output(pevent) : nat*
def $test_anon_output(OUTPUT n*) = n*
def $test_anon_output(pevent) = eps -- otherwise
dec $test_anon_outputs(pevent*) : nat*
def $test_anon_outputs(eps) = eps
def $test_anon_outputs(pevent :: pevent_tail*) = $test_anon_output(pevent) ++ $test_anon_outputs(pevent_tail*)
dec $test_anon_running(pstate) : pstate
def $test_anon_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_anon_running(S) = S -- otherwise
dec $test_anon_front(pstate, nat, nat, int) : bool
def $test_anon_front(S,n_unit,0,z) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE eps) metadata)) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN n_unit pcpath)
def $test_anon_front(S,n_unit,1,z) = true
  -- if S.TODO = (STMT statement) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN n_unit pcpath)
  -- if $origin_node(S.SOURCES,PORIGIN n_unit pcpath) = (statement)
  -- if $plcompileline(statement) = z
def $test_anon_front(S,n_unit,n_mode,z) = false -- otherwise
dec $test_anon_seek(pstate, nat, nat, int, nat) : pstate
def $test_anon_seek(S,n_unit,n_mode,z,0) = S
def $test_anon_seek(S,n_unit,n_mode,z,n) = S
  -- if $(n > 0)
  -- if $test_anon_front(S,n_unit,n_mode,z) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_anon_seek(S,n_unit,n_mode,z,n) = $test_anon_seek($drive_steps($test_anon_running(S),1),n_unit,n_mode,z,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_anon_front(S,n_unit,n_mode,z)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(s):
    return [f'$call_descriptors_valid({s})', f'$declaration_entry_check({s}) = {s}',
            f'$heap_valid($heap_graph({s}))']


def reach(s, previous, unit, mode=0, line=0):
    return [f'{s}_found = $test_anon_seek({previous},{unit},{mode},{line},5000)',
            fr'{s}_found.COMPLETION = NORMAL \/ {s}_found.COMPLETION = BUDGET',
            f'{s} = {s}_found[.COMPLETION = NORMAL]',
            f'$test_anon_front({s},{unit},{mode},{line})', *public(s)]


def object_cv(s, suffix):
    return [f'$lookup({s}.ENV,$ptascii("localObject")) = (n_cell_{suffix})',
            f'{s}.STORE[n_cell_{suffix}] = DEFINED (POBJECT n_object_{suffix})',
            f'{s}.OBJECTS[n_object_{suffix}] = INSTANCE pclassdesc_first.ORIGIN',
            f'(HOBJECT n_object_{suffix}) <- {s}.ALLOCATIONS']


def shared_first(checks, names, ifline, budget):
    checks += [
        'S_wait1.CLASSES = [pclassdesc_seed]', 'pclassdesc_seed.NAME = ' + term(names[0]),
        'pclassdesc_seed.ORIGIN = PORIGIN 0 pcpath_seed',
        '$anonymous_history_seed(S_wait1,1) = (1)',
    ]
    checks += reach('S_new1', 'S_body1', 1)
    checks += [
        'S_new1.ORIGIN = (PORIGIN 1 pcpath_first)',
        'porigin_first = PORIGIN 1 pcpath_first',
        'S_new1.CLASSES = [pclassdesc_seed,pclassdesc_first]',
        'pclassdesc_first.ORIGIN = PORIGIN 1 (pcpath_first ++ [PCFIELD 0])',
        'pclassdesc_first.NAME = ' + term(names[1]),
        '$anonymous_new_name(S_new1,porigin_first) = (pclassdesc_first.NAME)',
        '$anonymous_history_seed(S_new1,1) = (1)',
        '$source_unit(S_new1.SOURCES,1) = (pcunit_first)',
        '$anonymous_rtd_unit(pcunit_first) = (1)',
        '$anonymous_rtd_site(pcunit_first,pcpath_first ++ [PCFIELD 0])',
    ]
    # These source/history/name projections are helper-only and never driven.
    checks += [
        '$anonymous_rtd_history(S_new1,eps,0,1,0) = eps',
        '$anonymous_rtd_history(S_new1,[PDENTER 0 eps S_new1.REPORTING,PDENTER 1 eps S_new1.REPORTING,PDEXIT 0 PCSCOMPLETE],0,1,0) = eps',
        '$anonymous_rtd_unit(pcunit_first[.OCCURRENCES = eps]) = eps',
        'S_new1.TODO = (EVAL expression_new) :: ptask_new*',
        'pcunit_skipped = $pcsource(0,PROGRAM ([(NStmtExpression (NExprBinaryOpBooleanAnd (NExprConstFetch (NName (BYTES "ZmFsc2U=") eps) eps) expression_new eps) eps)]))',
        '$anonymous_rtd_unit(pcunit_skipped) = eps',
        'S_wrongname = S_new1[.CLASSES = [pclassdesc_seed,pclassdesc_first[.NAME = $ptascii("wrong")]]]',
        '$anonymous_new_name(S_wrongname,porigin_first) = eps',
    ]
    checks += reach('S_first', 'S_new1', 1, 1, ifline) + object_cv('S_first', 'first')
    checks += reach('S_again', 'S_first', 1)
    checks += ['S_again.ORIGIN = S_new1.ORIGIN',
               *[f'S_again.{field} = S_new1.{field}' for field in ['SOURCES','DECLARATIONS','CLASSES','CODE']],
               '$anonymous_new_name(S_again,porigin_first) = (pclassdesc_first.NAME)']
    previous = 'S_again'
    if budget:
        checks += ['S_budget = $drive_steps(S_again,0)', 'S_budget = S_again[.COMPLETION = BUDGET]',
                   '$call_descriptors_valid(S_budget)', 'S_resume = S_budget[.COMPLETION = NORMAL]',
                   'S_resume = S_again']
        previous = 'S_resume'
    checks += reach('S_second', previous, 1, 1, ifline) + object_cv('S_second', 'second')
    checks += ['n_object_first =/= n_object_second']
    return checks


def shared_second(checks, names, stdout):
    checks += ['$anonymous_history_seed(S_wait2,2) = (2)']
    checks += reach('S_new2', 'S_body2', 2)
    checks += [
        'S_new2.ORIGIN = (PORIGIN 2 pcpath_second)',
        'S_new2.CLASSES = [pclassdesc_seed,pclassdesc_first,pclassdesc_second]',
        'pclassdesc_second.ORIGIN = PORIGIN 2 (pcpath_second ++ [PCFIELD 0])',
        'pclassdesc_second.NAME = ' + term(names[2]),
        'pclassdesc_first.NAME =/= pclassdesc_second.NAME',
        '$anonymous_new_name(S_new2,PORIGIN 2 pcpath_second) = (pclassdesc_second.NAME)',
        '$anonymous_new_name(S_new2,porigin_first) = (pclassdesc_first.NAME)',
        '$anonymous_history_seed(S_new2,1) = (1)', '$anonymous_history_seed(S_new2,2) = (2)',
        '$source_unit(S_new2.SOURCES,2) = (pcunit_second)', 'pcunit_second.AST = pcunit_first.AST',
        '$call_sourcefile(S_new2.FILES,pclassdesc_first.ORIGIN) = $call_sourcefile(S_new2.FILES,pclassdesc_second.ORIGIN)',
        'S_final = $drive_steps(S_new2,5000)', 'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CLASSES = S_new2.CLASSES', 'S_final.SOURCES = S_new2.SOURCES',
        '$test_anon_outputs(S_final.EVENTS) = ' + term(stdout.encode()),
        *public('S_final'),
    ]
    return checks


def eval_checks(main, responses, code, case, names, ifline, stdout):
    checks = ['S_wait1 = $php_run(' + main + ',5000,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
              'S_wait1.COMPLETION = SOURCE_PENDING', *public('S_wait1'),
              'S_wait1.EVALCONTEXTS = pevalcontext_first :: eps',
              'pevalcontext_first.UNIT = 1', 'pevalcontext_first.BYTES = ' + term(code),
              '$eval_response_valid(S_wait1,' + responses[0] + ')',
              'S_body1 = $eval_resume(S_wait1,' + responses[0] + ')']
    checks = shared_first(checks, names, ifline, True)
    checks += ['S_wait2 = $drive_steps(S_second,5000)', 'S_wait2.COMPLETION = SOURCE_PENDING',
               *public('S_wait2'), 'S_wait2.EVALCONTEXTS = pevalcontext_second :: eps',
               'pevalcontext_second.UNIT = 2', 'pevalcontext_second.BYTES = pevalcontext_first.BYTES',
               'pevalcontext_second.SITE = pevalcontext_first.SITE', 'pevalcontext_second.FILE = pevalcontext_first.FILE',
               '$eval_response_valid(S_wait2,' + responses[1] + ')',
               'S_body2 = $eval_resume(S_wait2,' + responses[1] + ')']
    return shared_second(checks, names, stdout)


def include_checks(main, responses, code, case, names, ifline, stdout):
    filename, cwd, child = [term(str(p).encode()) for p in [case / 'main.php',case,case / 'unit.php']]
    def opened(context):
        return 'FILE_OPENED ' + context + '.NONCE ' + context + '.CALLER ' + context + '.REQUESTED ' + child + ' ' + child + ' ' + term(code)
    checks = ['S_open1 = $php_file_run(' + main + ',5000,' + filename + ',' + cwd + ')',
              'S_open1.COMPLETION = SOURCE_PENDING', 'S_open1.FILECONTEXTS = pfilecontext_first :: eps',
              '$file_open_response_valid(S_open1,' + opened('pfilecontext_first') + ')',
              'S_wait1 = $file_open_resume(S_open1,' + opened('pfilecontext_first') + ')',
              'S_wait1.COMPLETION = SOURCE_PENDING', *public('S_wait1'),
              '$file_parse_response_valid(S_wait1,' + responses[0] + ')',
              'S_body1 = $file_parse_resume(S_wait1,' + responses[0] + ')']
    checks = shared_first(checks, names, ifline, False)
    checks += ['S_skip = $drive_steps(S_second,5000)', 'S_skip.COMPLETION = SOURCE_PENDING',
               'S_skip.FILECONTEXTS = pfilecontext_skip :: eps', '$file_once_kind(pfilecontext_skip.KIND)',
               '$file_open_response_valid(S_skip,' + opened('pfilecontext_skip') + ')',
               'S_skipped = $file_open_resume(S_skip,' + opened('pfilecontext_skip') + ')',
               'S_skipped.COMPLETION = NORMAL', 'S_skipped.RESULT = KNOWN (PBOOL true)',
               *[f'S_skipped.{field} = S_skip.{field}' for field in ['SOURCES','DECLARATIONS','CLASSES','CODE','FILES']],
               *public('S_skipped'),
               'S_open2 = $drive_steps(S_skipped,5000)', 'S_open2.COMPLETION = SOURCE_PENDING',
               'S_open2.FILECONTEXTS = pfilecontext_second :: eps', '~$file_once_kind(pfilecontext_second.KIND)',
               '$file_open_response_valid(S_open2,' + opened('pfilecontext_second') + ')',
               'S_wait2 = $file_open_resume(S_open2,' + opened('pfilecontext_second') + ')',
               'S_wait2.COMPLETION = SOURCE_PENDING', *public('S_wait2'),
               '$file_parse_response_valid(S_wait2,' + responses[1] + ')',
               'S_body2 = $file_parse_resume(S_wait2,' + responses[1] + ')']
    return shared_second(checks, names, stdout)


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def prepare(out, sources):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for stage, (suite, name, result) in CASES.items():
            case = sources / suite / name
            native = json.loads((case.parent / 'report.json').read_text())
            assert native['result'] == result and native['stable_inputs'] and native['target'] == types.PROFILE
            row, = [item for item in native['records'] if item['id'] == name]
            assert row['probe_sanity'] and row['exit'] == 0 and not row['stderr']
            for filename, digest in row['originals'].items():
                assert hashlib.sha256((case / filename).read_bytes()).hexdigest() == digest
            assert (case / 'native/stdout').read_bytes() == row['stdout'].encode()
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            code = ((case / 'unit.php').read_bytes() if stage == 'include' else next(
                base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'$localFirst = null;')))
            responses = []
            for unit in [1,2]:
                request = {'op': 'parse-file' if stage == 'include' else 'parse-eval', 'id': str(unit),
                           'mode': 'file' if stage == 'include' else 'eval', 'profile': 'cli-raw-85', 'source': b64(code)}
                if stage == 'include':
                    request.update(requested=b64(b'unit.php'), resolved=b64(str(case / 'unit.php').encode()), opened=b64(str(case / 'unit.php').encode()))
                parsed_unit = frontend.request(request)
                assert parsed_unit['accepted']
                checked = adapter.request({'op': 'check', 'ast': parsed_unit['ast'], 'fixture': True})['fixture']
                responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(code) + ' ' + checked)
            ifnode, = [node for node in nodes(parsed_unit['ast']) if node['node'] == 'Stmt_If']
            ifline = int(ifnode['meta']['startLine']['int'])
            seed = row['stdout'].split('S:',1)[1].split('|',1)[0].encode()
            marker = '|E:' if stage == 'eval' else '|U:'
            names = [seed] + [part.split('|C:',1)[0].encode() for part in row['stdout'].split(marker)[1:]]
            assert len(names) == 3
            checks = (include_checks if stage == 'include' else eval_checks)(main, responses, code, case, names, ifline, row['stdout'])
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = list(CASES)
    sources, out = args.sources.resolve(), args.output.resolve()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for suite, name, _ in CASES.values():
        case = sources / suite / name
        paths += [case.parent / 'run.py', case.parent / 'report.json', *sorted(case.glob('*.php')),
                  *[case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
    if args.phase == 'check':
        for stage in selected:
            paths += [out / stage / 'protocol.watsup', out / stage / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    assert not (out / (args.phase + '-report.json')).exists()
    report = {'phase': args.phase, 'selected': selected, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
              'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
              'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'sl_timeout': 90, 'result': 'fail', 'records': [], 'agreement_credit': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for stage in selected:
                target = out / stage
                assert not (target / 'check').exists()
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules,
                                  str(target / 'protocol.watsup')], target / 'check', 90, ROOT)
                passed = runner.returncode == 0 and runner.stdout == b'true\n' and not runner.stderr
                report['records'].append({'id': stage, 'pass': passed, 'runner_exit': runner.returncode,
                                          'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]), flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(selected) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'], record['premises'] = False, 0
        (out / (args.phase + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
