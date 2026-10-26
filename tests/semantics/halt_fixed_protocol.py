#!/usr/bin/env python3
"""Reached direct fixed HALT queries and adjacent admission boundaries."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import halt_absent_sources as selected_sources
import halt_fixed_sources as cases
import halt_lookup_protocol as previous
import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
PREFIX = previous.PREFIX + r'''
dec $test_fixed_front(pstate, nat) : bool
def $test_fixed_front(S, n_unit) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.SELECTION = eps
  -- if $exit_fixed(S,pconfigcall.SITE) = (($ptascii("constant"),eps))
  -- if $dynamic_halt_call(pconfigcall)
def $test_fixed_front(S, n_unit) = false -- otherwise
dec $test_fixed_seek(pstate, nat, nat) : pstate
def $test_fixed_seek(S, n_unit, 0) = S
def $test_fixed_seek(S, n_unit, n) = S
  -- if $(n > 0)
  -- if $test_fixed_front(S,n_unit) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_fixed_seek(S, n_unit, n) = $test_fixed_seek($drive_steps($test_running(S),1),n_unit,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_fixed_front(S,n_unit)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''
MESSAGE = '$ptascii("Undefined constant \\"__COMPILER_HALT_OFFSET__\\"")'
NONLITERAL = b"<?php $name='__COMPILER_HALT_OFFSET__'; try { constant($name); } catch (Error $e) { echo 'M:', $e->getMessage(); } echo '|A';\n"
AUXILIARY = ('nonliteral-state', 'selected-regression', 'defined-regression')
ALL_CASES = ('nonliteral-source', *cases.CASES, *AUXILIARY)


def b64(value):
    return base64.b64encode(value).decode()


def term(value):
    return '$base64(' + json.dumps(b64(value)) + ')'


def checked(adapter, parsed):
    assert parsed['accepted'], parsed
    return adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']


def reach(state, seed, unit):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_fixed_seek(' + seed + ',' + str(unit) + ',2500)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$test_fixed_front(' + state + ',' + str(unit) + ')',
            state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
            '$config_invoke_valid(' + state + ',' + call + ')', *previous.public(state)]


def source_setup(name, directory, main, child, frontend, adapter):
    filename = term(os.fsencode(directory / 'main.php'))
    if name != 'child-present-main-absent' and name != 'main-present-eval-absent':
        return ['S_seed = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(directory / 'main.php'))) + ')',
                'S_seed.COMPLETION = BUDGET'], 0, filename
    if name == 'child-present-main-absent':
        child_name = os.fsencode(directory / 'child.php')
        source = child.read_bytes()
        parsed = frontend.request({'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
            'requested': b64(b'child.php'), 'resolved': b64(child_name), 'opened': b64(child_name),
            'source': b64(source)})
        unit = checked(adapter, parsed)
        response = ('FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER pfilecontext.REQUESTED ' +
                    term(child_name) + ' ' + term(child_name) + ' ' + term(source))
        checks = ['S_open = $php_file_run(' + main + ',2500,' + filename + ',' + term(os.fsencode(directory)) + ')',
                  'S_open.COMPLETION = SOURCE_PENDING', 'S_open.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
                  '$file_open_response_valid(S_open,' + response + ')',
                  'S_parse = $file_open_resume(S_open,' + response + ')',
                  'S_parse.COMPLETION = SOURCE_PENDING',
                  'S_seed = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + term(source) + ' ' + unit + ')',
                  'S_seed.COMPLETION = NORMAL']
        return checks, 1, term(child_name)
    code = b'return constant("__COMPILER_HALT_OFFSET__");'
    parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
        'profile': 'cli-raw-85', 'source': b64(code)})
    unit = checked(adapter, parsed)
    checks = ['S_wait = $php_run(' + main + ',2500,' + json.dumps(b64(os.fsencode(directory / 'main.php'))) + ')',
              'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*',
              'pevalcontext.BYTES = ' + term(code),
              'S_seed = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + term(code) + ' ' + unit + ')',
              'S_seed.COMPLETION = NORMAL']
    return checks, 1, 'pevalcontext.FILE'


def fixed_front(state, unit, sourcefile, offset):
    call = 'pconfigcall_' + state
    budget, resume = state + '_budget', state + '_resume'
    checks = reach(state, 'S_seed', unit)
    checks += ['$dynamic_halt_fixed_constant(' + state + ',' + call + ')',
               '$dynamic_halt_valid(' + state + ',' + call + ')',
               '$exit_fixed(' + state + ',' + call + '.SITE) = (($ptascii("constant"),eps))',
               '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((NScalarString (BYTES text) metadata,false,eps,porigin_arg,z_arg))',
               '$base64(text) = $ptascii("__COMPILER_HALT_OFFSET__")',
               '$call_sourcefile(' + state + '.FILES,' + call + '.SITE) = ' + sourcefile,
               '$dynamic_halt_lookup(' + state + ',' + sourcefile + ',' + state + '.DECLARATIONS) = ' +
                   ('HALT_OFFSET ' + str(offset) if offset is not None else 'HALT_ABSENT'),
               '~$dynamic_halt_valid(' + state + ',' + call + '[.OWNER = (0)])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.NAMED = true])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.SENT = eps])',
               budget + ' = $drive_steps(' + state + ',0)',
               budget + ' = ' + state + '[.COMPLETION = BUDGET]',
               resume + ' = ' + budget + '[.COMPLETION = NORMAL]', resume + ' = ' + state,
               'pconfigcall_' + resume + ' = ' + call]
    return checks


def error_checks(state, sourcefile, expected):
    call = 'pconfigcall_' + state
    resume = state + '_resume'
    checks = ['S_error = $dynamic_halt_receive(' + resume + ',' + call + ')',
              'S_error.COMPLETION = THROWING n_error',
              'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
              'pthrowable.KIND = "Error"', 'pthrowable.ORIGIN = (' + call + '.SITE)',
              '$string_bytes($throwable_field(S_error,n_error,"message")) = ' + MESSAGE,
              '$throwable_field(S_error,n_error,"line") = PINT ' + call + '.LINE',
              '$string_bytes($throwable_field(S_error,n_error,"file")) = (' + sourcefile + ')',
              '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
              'S_error.ARRAYS[n_trace].ITEMS = (ENTRY (KINT 0) (DIRECT (PARRAY n_frame))) :: pentry_trace*',
              '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING $ptascii("constant")',
              '$trace_array_field(S_error,n_frame,$ptascii("file")) = PSTRING (' + sourcefile + ')',
              '$trace_array_field(S_error,n_frame,$ptascii("line")) = PINT ' + call + '.LINE',
              '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
              'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_query)]',
              '$string_bytes(pvalue_query) = $ptascii("__COMPILER_HALT_OFFSET__")',
              *['S_error.' + field + ' = ' + state + '.' + field for field in
                ('SOURCES', 'FILES', 'DECLARATIONS', 'INCLUDEDOPENED', 'FILESEQ', 'FILECONTEXTS', 'EVALCONTEXTS', 'EVENTS')],
              'S_step_found = $drive_steps(' + resume + ',1)',
              'S_step_found.COMPLETION = NORMAL \\/ S_step_found.COMPLETION = BUDGET',
              'S_step = S_step_found[.COMPLETION = NORMAL]',
              'S_step.TODO = (THROW_SEARCH n_error) :: ptask_error*',
              'S_step.OBJECTS[n_error] = S_error.OBJECTS[n_error]',
              *previous.public('S_step'),
              'S_final = $drive_steps(S_step,10000)', 'S_final.COMPLETION = NORMAL',
              'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = ' + term(expected),
              *previous.public('S_final')]
    return checks


def assertions(name, directory, main, child, expected, frontend, adapter):
    checks, unit, sourcefile = source_setup(name, directory, main, child, frontend, adapter)
    offset = 76 if name in ('main-present', 'child-present-main-absent') else None
    if name == 'child-present-main-absent':
        childfile = sourcefile
        checks += fixed_front('S_child', 1, childfile, 76)
        checks += ['pdeclaration_prefix* = [PDENTER 0 eps S_child.REPORTING,PDEXIT 0 PCSCOMPLETE]',
                   'pdeclaration_enter = PDENTER 1 (pfilecontext.SITE) S_child.REPORTING',
                   'S_child.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter,PDEXIT 1 PCSCOMPLETE]',
                   'S_unknown = S_child[.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter]]',
                   '$dynamic_halt_lookup(S_unknown,' + childfile + ',S_unknown.DECLARATIONS) = HALT_UNKNOWN',
                   '$dynamic_halt_valid(S_unknown,pconfigcall_S_child)',
                   '$dynamic_halt_receive(S_unknown,pconfigcall_S_child).COMPLETION = UNSUPPORTED "halt offset constant query"',
                   '$test_outputs(S_child.EVENTS) = $ptascii("I:")']
        checks += previous.step('S_child_value', 'S_child_resume', 'PINT 76')
        checks += reach('S', 'S_child_value', 0)
        checks += fixed_front_checks('S', term(os.fsencode(directory / 'main.php')), None)
        checks += ['$dynamic_halt_lookup(S,' + childfile + ',S.DECLARATIONS) = HALT_OFFSET 76',
                   '$test_outputs(S.EVENTS) = $ptascii("I:76|")']
        checks += error_checks('S', term(os.fsencode(directory / 'main.php')), expected)
    else:
        checks += fixed_front('S', unit, sourcefile, offset)
        if name == 'main-present':
            checks += previous.step('S_value', 'S_resume', 'PINT 76')
            checks += ['S_final = $drive_steps(S_value,10000)', 'S_final.COMPLETION = NORMAL',
                       'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = ' + term(expected),
                       *previous.public('S_final')]
        else:
            if name == 'main-present-eval-absent':
                mainfile = term(os.fsencode(directory / 'main.php'))
                checks += ['$dynamic_halt_lookup(S,' + mainfile + ',S.DECLARATIONS) = HALT_OFFSET z_main']
            checks += error_checks('S', sourcefile, expected)
    return checks


def fixed_front_checks(state, sourcefile, offset):
    call = 'pconfigcall_' + state
    budget, resume = state + '_budget', state + '_resume'
    return ['$dynamic_halt_fixed_constant(' + state + ',' + call + ')',
            '$dynamic_halt_valid(' + state + ',' + call + ')',
            '$call_sourcefile(' + state + '.FILES,' + call + '.SITE) = ' + sourcefile,
            '$dynamic_halt_lookup(' + state + ',' + sourcefile + ',' + state + '.DECLARATIONS) = ' +
                ('HALT_OFFSET ' + str(offset) if offset is not None else 'HALT_ABSENT'),
            budget + ' = $drive_steps(' + state + ',0)',
            budget + ' = ' + state + '[.COMPLETION = BUDGET]',
            resume + ' = ' + budget + '[.COMPLETION = NORMAL]', resume + ' = ' + state,
            'pconfigcall_' + resume + ' = ' + call]


def run_case(name, directory, source, child_source, expected, frontend, adapter):
    assert (directory / 'main.php').read_bytes() == source
    assert child_source is None or (directory / 'child.php').read_bytes() == child_source
    assert (directory / 'native-stdout').read_bytes() == expected
    main = checked(adapter, frontend.request({'op': 'parse', 'source': b64(source)}))
    return assertions(name, directory, main, directory / 'child.php' if child_source is not None else None,
                      expected, frontend, adapter)


def nonliteral_source(out):
    target = out / 'nonliteral-source'
    target.mkdir()
    source = NONLITERAL
    expected = b'M:Undefined constant "__COMPILER_HALT_OFFSET__"|A'
    (target / 'main.php').write_bytes(source)
    native = [str(types.PHP), '-n', *types.FLAGS, str(target / 'main.php')]
    observed = subprocess.run(native, cwd=target, env=types.ENV, capture_output=True, timeout=90)
    (target / 'native-stdout').write_bytes(observed.stdout)
    (target / 'native-stderr').write_bytes(observed.stderr)
    if observed.returncode != 0 or observed.stdout != expected or observed.stderr:
        return {'id': 'nonliteral-source', 'category': 'unsupported-control', 'pass': False,
                'source_sha256': hashlib.sha256(source).hexdigest(), 'native_command': native,
                'native_exit': observed.returncode}
    model = [str(ROOT / 'bin/php-semantics'), str(target / 'main.php'), '--steps', '100000', '--timeout', '60']
    result = subprocess.run(model, cwd=target, env=types.ENV, capture_output=True, timeout=90)
    (target / 'model-stdout').write_bytes(result.stdout)
    (target / 'model-stderr').write_bytes(result.stderr)
    try:
        value = json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        value = {}
    passed = (result.returncode == 1 and not result.stderr and value.get('frontend') == 'accepted' and
              value.get('checked') == 'program' and value.get('status') == 'unsupported' and
              value.get('reason') == 'halt offset constant query')
    print('nonliteral-source', passed, flush=True)
    return {'id': 'nonliteral-source', 'category': 'unsupported-control', 'pass': passed,
            'source_sha256': hashlib.sha256(source).hexdigest(), 'native_command': native,
            'model_command': model, 'native_exit': observed.returncode, 'model_exit': result.returncode}


def auxiliary_checks(name, out, frontend, adapter):
    directory = out / name
    directory.mkdir()
    if name == 'nonliteral-state':
        source = NONLITERAL
    elif name == 'selected-regression':
        source, _, expected = selected_sources.CASES['main-absent']
    else:
        source = b"<?php echo defined('__COMPILER_HALT_OFFSET__') ? 'Y' : 'N'; __halt_compiler();PAYLOAD"
        expected = b'N'
    (directory / 'main.php').write_bytes(source)
    main = checked(adapter, frontend.request({'op': 'parse', 'source': b64(source)}))
    filename = term(os.fsencode(directory / 'main.php'))
    checks = ['S_seed = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(directory / 'main.php'))) + ')',
              'S_seed.COMPLETION = BUDGET']
    if name == 'nonliteral-state':
        checks += reach('S', 'S_seed', 0)
        checks += ['$exit_fixed(S,pconfigcall_S.SITE) = (($ptascii("constant"),eps))',
                   '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((NExprVariable (BYTES text_name) metadata_name, false, eps, porigin_arg, z_arg))',
                   '~$dynamic_halt_fixed_constant(S,pconfigcall_S)',
                   '~$dynamic_halt_valid(S,pconfigcall_S)',
                   '$dynamic_halt_receive(S,pconfigcall_S).COMPLETION = UNSUPPORTED "halt offset constant query"']
    elif name == 'selected-regression':
        checks += previous.reach('S', 'S_seed', 0, 1)
        checks += ['~$dynamic_halt_fixed_constant(S,pconfigcall_S)',
                   '$dynamic_halt_lookup(S,' + filename + ',S.DECLARATIONS) = HALT_ABSENT',
                   '$dynamic_halt_receive(S,pconfigcall_S).COMPLETION = THROWING n_error',
                   'S_final = $drive_steps(S,10000)', 'S_final.COMPLETION = NORMAL',
                   'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = ' + term(expected),
                   *previous.public('S_final')]
    else:
        checks += previous.reach('S', 'S_seed', 0, 2)
        checks += ['$dynamic_halt_literal_defined(S,pconfigcall_S)',
                   '~$dynamic_halt_fixed_constant(S,pconfigcall_S)',
                   '$dynamic_halt_lookup(S,' + filename + ',S.DECLARATIONS) = HALT_OFFSET ' + str(source.index(b'PAYLOAD'))]
        checks += previous.step('S_value', 'S', 'PBOOL false')
        checks += ['S_final = $drive_steps(S_value,10000)', 'S_final.COMPLETION = NORMAL',
                   'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = ' + term(expected),
                   *previous.public('S_final')]
    return checks


def execute(name, checks, out, category='affected'):
    target = out / name
    target.mkdir(exist_ok=True)
    (target / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    fixture = target / 'protocol.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(fixture)]
    result = subprocess.run(command, cwd=ROOT, env=types.ENV, capture_output=True, timeout=150)
    (target / 'stdout').write_bytes(result.stdout)
    (target / 'stderr').write_bytes(result.stderr)
    passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    print(name, passed, len(checks), flush=True)
    return {'id': name, 'category': category, 'pass': passed, 'checks': len(checks), 'exit': result.returncode,
            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(), 'command': command}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    selection = [name for name in ALL_CASES if not args.case or name in args.case]
    assert selection and set(args.case) <= set(selection)
    sources, out = args.sources.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert json.loads((sources / 'native-report.json').read_text())['result'] == 'pass'
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records = []
    try:
        if 'nonliteral-source' in selection:
            records.append(nonliteral_source(out))
        if not records or records[-1]['pass']:
            for name, (source, child, expected) in cases.CASES.items():
                if name not in selection:
                    continue
                checks = run_case(name, sources / name, source, child, expected, frontend, adapter)
                records.append(execute(name, checks, out))
                if not records[-1]['pass']:
                    break
        if not records or all(row['pass'] for row in records):
            for name in AUXILIARY:
                if name not in selection:
                    continue
                checks = auxiliary_checks(name, out, frontend, adapter)
                records.append(execute(name, checks, out, 'unsupported-control' if name == 'nonliteral-state' else 'regression'))
                if not records[-1]['pass']:
                    break
    finally:
        adapter.close()
        frontend.close()
    report = {'result': 'pass' if len(records) == len(selection) and all(r['pass'] for r in records) else 'fail',
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
              'runtime_sha256': hashlib.sha256((ROOT / 'spec/semantics/400-dynamic-constants.watsup').read_bytes()).hexdigest(),
              'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
