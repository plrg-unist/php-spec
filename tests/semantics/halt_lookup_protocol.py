#!/usr/bin/env python3
"""Reached filename-local HALT registrations and the fixed defined emitter."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = {'include': 'included-halt-lookup', 'eval': 'repeated-eval-halt-lookup'}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
KEY = '$ptascii("__COMPILER_HALT_OFFSET__")'

PREFIX = r'''
dec $test_output_item(pevent) : nat*
def $test_output_item(OUTPUT n*) = n*
def $test_output_item(pevent) = eps -- otherwise
dec $test_outputs(pevent*) : nat*
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output_item(pevent) ++ $test_outputs(pevent_tail*)
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_halt_mode(pconfigcall, nat) : bool
def $test_halt_mode(pconfigcall, 0) = (pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.SELECTION =/= eps)
def $test_halt_mode(pconfigcall, 1) = (pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.SELECTION =/= eps)
def $test_halt_mode(pconfigcall, 2) = (pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.SELECTION = eps)
def $test_halt_mode(pconfigcall, n) = false -- otherwise
dec $test_halt_front(pstate, nat, nat) : bool
def $test_halt_front(S, n_unit, n_mode) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
  -- if $test_halt_mode(pconfigcall,n_mode)
  -- if $dynamic_halt_call(pconfigcall)
def $test_halt_front(S, n_unit, n_mode) = false -- otherwise
dec $test_halt_seek(pstate, nat, nat, nat) : pstate
def $test_halt_seek(S, n_unit, n_mode, 0) = S
def $test_halt_seek(S, n_unit, n_mode, n) = S
  -- if $(n > 0)
  -- if $test_halt_front(S,n_unit,n_mode) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_halt_seek(S, n_unit, n_mode, n) = $test_halt_seek($drive_steps($test_running(S),1),n_unit,n_mode,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_halt_front(S,n_unit,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def reach(state, previous, unit, mode):
    return [state + '_found = $test_halt_seek(' + previous + ',' + str(unit) + ',' + str(mode) + ',2500)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_halt_front(' + state + ',' + str(unit) + ',' + str(mode) + ')',
        state + '.TODO = (CONFIG_INVOKE pconfigcall_' + state + ') :: ptask_' + state + '*',
        '$config_invoke_valid(' + state + ',pconfigcall_' + state + ')',
        '$dynamic_halt_valid(' + state + ',pconfigcall_' + state + ')', *public(state)]


def step(state, previous, value):
    return [state + '_found = $drive_steps(' + previous + ',1)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        state + ' = $dynamic_halt_receive(' + previous + ',pconfigcall_' + previous + ')',
        state + '.RESULT = KNOWN (' + value + ')',
        *[state + '.' + field + ' = ' + previous + '.' + field for field in
            ('DECLARATIONS', 'SOURCES', 'FILES', 'ARRAYS', 'STORE', 'ALLOCATIONS', 'EVENTS')],
        *public(state)]


def final(state, previous, stdout):
    return [state + ' = $drive_steps(' + previous + ',3000)',
        state + '.COMPLETION = NORMAL', state + '.TODO = eps',
        '$test_outputs(' + state + '.EVENTS) = $ptascii(' + json.dumps(stdout) + ')',
        *public(state)]


def include_assertions(main, unit, case, stdout):
    filename, cwd, child = map(lambda p: term(os.fsencode(p)), [case / 'main.php', case, case / 'unit.php'])
    data = term((case / 'unit.php').read_bytes())
    opened = 'FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER pfilecontext.REQUESTED ' + child + ' ' + child + ' ' + data
    accepted = 'SOURCE_ACCEPT 1 ' + data + ' ' + unit
    lookup = lambda state, file=child, journal=None: '$dynamic_halt_lookup(' + state + ',' + file + ',' + (journal or state + '.DECLARATIONS') + ')'
    checks = ['S_open = $php_file_run(' + main + ',2500,' + filename + ',' + cwd + ')',
        'S_open.COMPLETION = SOURCE_PENDING', 'S_open.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
        '$file_open_response_valid(S_open,' + opened + ')',
        'S_parse = $file_open_resume(S_open,' + opened + ')',
        '$file_parse_response_valid(S_parse,' + accepted + ')',
        'S_body = $file_parse_resume(S_parse,' + accepted + ')',
        *reach('S', 'S_body', 1, 0),
        'pconfigcall_S.SELECTION = (n_nonce)', 'S.SELECTEDCALLS[n_nonce].KIND = INTRINSIC_DEFINED',
        'S.SELECTEDCALLS[n_nonce].SITE = pconfigcall_S.SITE',
        '$call_sourcefile(S.FILES,pconfigcall_S.SITE) = ' + child,
        lookup('S') + ' = HALT_OFFSET 207', lookup('S', filename) + ' = HALT_ABSENT',
        '~$dynamic_halt_literal_defined(S,pconfigcall_S)',
        '$source_unit(S.SOURCES,1) = (pcunit_halt)',
        '$pphalt_offset(pcunit_halt.AST) = (207)',
        'pdeclaration_enter = PDENTER 1 (pfilecontext.SITE) S.REPORTING',
        'pdeclaration_prefix* = [PDENTER 0 eps S.REPORTING,PDEXIT 0 PCSCOMPLETE]',
        'S.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter,PDEXIT 1 PCSCOMPLETE]',
        '$dynamic_halt_candidate(S,' + child + ',pdeclaration_enter) = ((1,HALT_OFFSET 207))',
        '$dynamic_halt_segment([PDEXIT 1 PCSCOMPLETE],1)',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        'S_resume = S_budget[.COMPLETION = NORMAL]', 'S_resume = S', 'pconfigcall_S_resume = pconfigcall_S',
        *step('S_defined', 'S_resume', 'PBOOL true'),
        *reach('S_constant', 'S_defined', 1, 1),
        *step('S_offset', 'S_constant', 'PINT 207'),
        *reach('S_literal', 'S_offset', 1, 2),
        '$dynamic_halt_literal_defined(S_literal,pconfigcall_S_literal)',
        lookup('S_literal') + ' = HALT_OFFSET 207',
        *step('S_literal_value', 'S_literal', 'PBOOL false'),
        *reach('S_main', 'S_literal_value', 0, 0),
        '$call_sourcefile(S_main.FILES,pconfigcall_S_main.SITE) = ' + filename,
        'S_main.FILECONTEXTS = eps', lookup('S_main', filename) + ' = HALT_ABSENT',
        *step('S_absent', 'S_main', 'PBOOL false'),
        *final('S_final', 'S_absent', stdout)]
    # Counterfactual histories and source images are projections, never driven.
    for name, segment in [
        ('pending', '[pdeclaration_enter]'),
        ('failed', '[pdeclaration_enter,PDEXIT 1 PCSCOMPILER]'),
        ('reentry', '[pdeclaration_enter,PDENTER 0 eps S.REPORTING,PDEXIT 1 PCSCOMPLETE]')]:
        checks += ['pdeclaration_' + name + '* = pdeclaration_prefix* ++ ' + segment,
            lookup('S', journal='pdeclaration_' + name + '*') + ' = HALT_UNKNOWN',
            'S_' + name + ' = S[.DECLARATIONS = pdeclaration_' + name + '*]',
            'S_' + name + '_refused = $dynamic_halt_receive(S_' + name + ',pconfigcall_S)',
            'S_' + name + '_refused.COMPLETION = UNSUPPORTED "halt offset constant query"']
    checks += [lookup('S', journal='(S.DECLARATIONS ++ [pdeclaration_enter])') + ' = HALT_OFFSET 207',
        '$pphalt_last($pcprogram(pcunit_halt.AST)) = (statement_halt)',
        'pcunit_nonterminal = $pcsource(1,PROGRAM ([statement_halt,(NStmtNop eps)]))',
        '$pphalt_offset(pcunit_nonterminal.AST) = eps',
        '$dynamic_halt_occurrences(pcunit_nonterminal.OCCURRENCES)',
        'S_nonterminal = S[.SOURCES = [($pcsource(0,' + main + ')),pcunit_nonterminal]]',
        '$dynamic_halt_candidate(S_nonterminal,' + child + ',pdeclaration_enter) = ((1,HALT_UNKNOWN))',
        lookup('S_nonterminal') + ' = HALT_UNKNOWN']
    for label, change in [
        ('selection', '.SELECTION = eps'), ('nonce', '.SELECTION = (S.SELECTSEQ)'),
        ('site', '.SITE = (PORIGIN 0 eps)'), ('line', '.LINE = $(pconfigcall_S.LINE + 1)'),
        ('kind', '.KIND = INTRINSIC_DEFINE'), ('index', '.INDEX = 2'),
        ('owner', '.OWNER = (0)'), ('named', '.NAMED = true'),
        ('query', '.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("other"))))]'),
        ('carrier', '.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) (' + KEY + ')))]')]:
        checks += ['pconfigcall_' + label + ' = pconfigcall_S[' + change + ']',
            '~$dynamic_halt_valid(S,pconfigcall_' + label + ')']
    checks += ['S_unselected = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$dynamic_halt_valid(S_unselected,pconfigcall_S)',
        '~$dynamic_halt_literal_defined(S_constant,pconfigcall_S_constant)',
        'pconfigcall_literal_bad = pconfigcall_S_literal[.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("other"))))]]',
        '~$dynamic_halt_valid(S_literal,pconfigcall_literal_bad)']
    return checks


def eval_assertions(main, responses, codes, case, stdout):
    checks = ['S_initial = $php_run(' + main + ',2500,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')']
    previous = 'S_initial'
    for unit, response in enumerate(responses, 1):
        wait, body, context = 'S_wait_' + str(unit), 'S_body_' + str(unit), 'pevalcontext_' + str(unit)
        checks += [wait + ' = $drive_steps($test_running(' + previous + '),2500)',
            wait + '.COMPLETION = SOURCE_PENDING', wait + '.EVALCONTEXTS = ' + context + ' :: pevalcontext_tail_' + str(unit) + '*',
            context + '.UNIT = ' + str(unit), context + '.BYTES = ' + term(codes[unit - 1]),
            context + '.SITE = pevalcontext_1.SITE', context + '.FILE = pevalcontext_1.FILE',
            '$eval_response_valid(' + wait + ',' + response + ')',
            body + ' = $eval_resume(' + wait + ',' + response + ')']
        if unit == 1:
            checks += ['$source_unit(' + body + '.SOURCES,1) = eps',
                '$failed_source_at(' + body + '.FAILEDSOURCES,1) = (pfailedsource)',
                'pfailedsource.KIND = FAILED_PARSE', 'pfailedsource.FILE = pevalcontext_1.FILE']
            previous = body
        else:
            query = 'S_query_' + str(unit)
            checks += reach(query, body, unit, 0)
            lookup = '$dynamic_halt_lookup(' + query + ',pevalcontext_1.FILE,' + query + '.DECLARATIONS)'
            checks += [lookup + (' = HALT_ABSENT' if unit == 2 else ' = HALT_OFFSET 111')]
            checks += step('S_defined_' + str(unit), query, 'PBOOL false' if unit == 2 else 'PBOOL true')
            if unit == 2:
                previous = 'S_defined_2'
            else:
                constant = 'S_constant_' + str(unit)
                checks += reach(constant, 'S_defined_' + str(unit), unit, 1)
                checks += ['$source_unit(' + constant + '.SOURCES,' + str(unit) + ') = (pcunit_' + str(unit) + ')',
                    '$pphalt_offset(pcunit_' + str(unit) + '.AST) = (' + str(111 if unit == 3 else 137) + ')']
                checks += step('S_value_' + str(unit), constant, 'PINT 111')
                previous = 'S_value_' + str(unit)
    checks += ['S_query_4.DECLARATIONS[6] = pdeclaration_first',
        'S_query_4.DECLARATIONS[8] = pdeclaration_second',
        '$dynamic_halt_candidate(S_query_4,pevalcontext_1.FILE,pdeclaration_first) = ((3,HALT_OFFSET 111))',
        '$dynamic_halt_candidate(S_query_4,pevalcontext_1.FILE,pdeclaration_second) = ((4,HALT_OFFSET 137))',
        'S_reverse = S_query_4[.SOURCES = [pcunit_4,pcunit_3]]',
        '$dynamic_halt_lookup(S_reverse,pevalcontext_1.FILE,S_query_4.DECLARATIONS) = HALT_OFFSET 111',
        'pdeclaration_reordered* = S_query_4.DECLARATIONS[0:6] ++ S_query_4.DECLARATIONS[8:2] ++ S_query_4.DECLARATIONS[6:2]',
        '$dynamic_halt_lookup(S_query_4,pevalcontext_1.FILE,pdeclaration_reordered*) = HALT_OFFSET 137',
        '$dynamic_halt_lookup(S_wait_4,pevalcontext_1.FILE,S_wait_4.DECLARATIONS) = HALT_OFFSET 111',
        *final('S_final', previous, stdout)]
    return checks


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
        native = json.loads((sources / 'static-native-v50/report.json').read_text())
        assert native['result'] == 'native_observation' and native['stable_inputs'] and native['target'] == types.PROFILE
        for stage, name in CASES.items():
            case = sources / 'static-native-v50' / name
            row, = [item for item in native['records'] if item['id'] == name]
            assert row['exit'] == 0 and not row['stderr']
            for filename, digest in row['originals'].items():
                assert hashlib.sha256((case / filename).read_bytes()).hexdigest() == digest
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            if stage == 'include':
                parsed_unit = frontend.request({'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
                    'source': b64((case / 'unit.php').read_bytes()),
                    **{key: b64(os.fsencode(case / 'unit.php')) for key in ['requested', 'resolved', 'opened']}})
                assert parsed_unit['accepted']
                unit = adapter.request({'op': 'check', 'ast': parsed_unit['ast'], 'fixture': True})['fixture']
                checks = include_assertions(main, unit, case, row['stdout'])
            else:
                array, = [node for node in nodes(parsed['ast']) if node['node'] == 'Expr_Array']
                codes = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(array) if node['node'] == 'Scalar_String']
                assert len(codes) == 4
                responses = []
                for unit, code in enumerate(codes, 1):
                    parsed_unit = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval',
                        'profile': 'cli-raw-85', 'source': b64(code)})
                    if parsed_unit['accepted']:
                        checked = adapter.request({'op': 'check', 'ast': parsed_unit['ast'], 'fixture': True})['fixture']
                        responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(code) + ' ' + checked)
                    else:
                        assert unit == 1 and parsed_unit['category'] == 'parser_rejection'
                        responses.append('SOURCE_PARSE_REJECT 1 ' + term(code) + ' ' + term(base64.b64decode(parsed_unit['message'])) + ' ' + str(parsed_unit['line']))
                checks = eval_assertions(main, responses, codes, case, row['stdout'])
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources, out = args.sources.resolve(), args.output.resolve()
    suite = sources / 'static-native-v50'
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php',
        ROOT / 'adapter/wire.ml', suite / 'run.py', suite / 'report.json']
    for name in CASES.values():
        case = suite / name
        paths += [*sorted(case.glob('*.php')), *[case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
    if args.phase == 'check':
        for stage in CASES:
            paths += [out / stage / 'protocol.watsup', out / stage / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    assert not (out / (args.phase + '-report.json')).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
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
            for stage in CASES:
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
            report['result'] = 'pass' if len(report['records']) == len(CASES) and all(row['pass'] for row in report['records']) else 'fail'
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
