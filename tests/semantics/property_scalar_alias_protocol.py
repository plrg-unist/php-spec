#!/usr/bin/env python3
"""Source-reached property writes preserve the selected alias and type sources."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'static-success': b'<?php class A{public static string $p="1";}'
                      b'class B{public static int|string $p="1";} B::$p=&A::$p;A::$p=2;',
    'instance-success': b'<?php class A{public string $p="1";public int|string $q="1";}'
                        b'$a=new A;$a->q=&$a->p;$a->p=2;',
    'static-reject': b'<?php class A{public static int|string $p=1;}'
                     b'class B{public static int $p=1;} B::$p=&A::$p;'
                     b'try{A::$p="x";}catch(TypeError $e){}',
    'instance-reject': b'<?php class A{public int|string $p=1;public int $q=1;}'
                       b'$a=new A;$a->q=&$a->p;try{$a->p="x";}catch(TypeError $e){}',
}
PREFIX = '''
dec $scalar_property_head(pstate) : bool
def $scalar_property_head(S) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_CLASS_STATIC porigin ptbytes) z bool) :: ptask*
def $scalar_property_head(S) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY (POBJECT n) ptbytes) z bool) :: ptask*
def $scalar_property_head(S) = false -- otherwise
dec $scalar_property_seek(pstate,nat) : pstate
def $scalar_property_seek(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET
def $scalar_property_seek(S,n) = S
  -- if $scalar_property_head(S) /\\ (S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET)
def $scalar_property_seek(S,0) = S
  -- if ~$scalar_property_head(S) /\\ (S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET)
def $scalar_property_seek(S,n) = $scalar_property_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$scalar_property_head(S) /\\ $(n > 0)
  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(initial, name):
    success = name.endswith('success')
    original = 'PSTRING ([49])' if success else 'PINT 1'
    incoming = 'PINT 2' if success else 'PSTRING ([120])'
    stored = 'PSTRING ([50])' if success else 'PINT 1'
    checks = [
        'S_initial = ' + initial,
        'S_paused = $scalar_property_seek(S_initial,512)',
        'S_paused.COMPLETION = NORMAL \\/ S_paused.COMPLETION = BUDGET',
        'S = S_paused[.COMPLETION = NORMAL]',
        '$scalar_property_head(S)',
        'S.RESULT = KNOWN (' + incoming + ')',
    ]
    if name.startswith('static'):
        checks += [
            'S.TODO = (ASSIGN_ARRAY (BASE_CLASS_STATIC porigin_selected ([112])) z false) :: ptask*',
            'S.CLASSES = [pclassdesc_a,pclassdesc_b]',
            'pclassdesc_a.PROPERTIES = [ppropertydesc_p]',
            'pclassdesc_b.PROPERTIES = [ppropertydesc_q]',
            'porigin_selected = pclassdesc_a.ORIGIN',
            'S.CLASSSTATICS = [pclassstatic_p,pclassstatic_q]',
            'pclassstatic_p.STATE = PROP_VALUE (ALIAS n_cell)',
            'pclassstatic_q.STATE = PROP_VALUE (ALIAS n_cell)',
            'S.PROPREFS = [ppropref]',
            'ppropref.CELL = n_cell',
            'ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertydesc_p.ORIGIN,CLASS_PROP_SOURCE ppropertydesc_q.ORIGIN]',
        ]
        unchanged = ['S_step.CLASSSTATICS = S.CLASSSTATICS',
                     'S_done.CLASSSTATICS = S.CLASSSTATICS']
    else:
        checks += [
            'S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY (POBJECT n_object) ([112])) z false) :: ptask*',
            'S.CLASSES = [pclassdesc_a]',
            'pclassdesc_a.PROPERTIES = [ppropertydesc_p,ppropertydesc_q]',
            '$objectprops_record_at(S.OBJECTPROPS,n_object) = (pobjectprops)',
            'pobjectprops.SLOTS = [ppropertyslot_p,ppropertyslot_q]',
            'ppropertyslot_p.STATE = PROP_VALUE (ALIAS n_cell)',
            'ppropertyslot_q.STATE = PROP_VALUE (ALIAS n_cell)',
            'S.PROPREFS = [ppropref]',
            'ppropref.CELL = n_cell',
            'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object ([112]) ppropertydesc_p.ORIGIN,OBJECT_PROP_SOURCE n_object ([113]) ppropertydesc_q.ORIGIN]',
        ]
        unchanged = ['$objectprops_record_at(S_step.OBJECTPROPS,n_object) = (pobjectprops)',
                     '$objectprops_record_at(S_done.OBJECTPROPS,n_object) = (pobjectprops)']
    checks += [
        'S.STORE[n_cell] = DEFINED (' + original + ')',
        '$class_state_valid(S) /\\ $proprefs_valid(S) /\\ $heap_valid($heap_graph(S))',
        '$call_tasks_valid(S,S.TODO)',
        'S_step = $drive_steps(S,1)',
        'S_step.COMPLETION = BUDGET',
        'S_step.STORE[n_cell] = DEFINED (' + stored + ')',
        'S_step.PROPREFS = S.PROPREFS',
        unchanged[0],
    ]
    if success:
        checks += ['S_step.RESULT = KNOWN (PSTRING ([50]))']
    else:
        checks += ['S_step.TODO = (THROW_SEARCH n_throw) :: ptask_throw*',
                   'S_step.OBJECTS[n_throw] = THROWABLE pthrowable',
                   'pthrowable.KIND = "TypeError"',
                   'HOBJECT n_throw <- S_step.ALLOCATIONS']
    checks += [
        'S_done = $drive(S_step[.COMPLETION = NORMAL],2048)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        'S_done.STORE[n_cell] = DEFINED (' + stored + ')',
        'S_done.PROPREFS = S.PROPREFS',
        unchanged[1],
        '$class_state_valid(S_done) /\\ $proprefs_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'frontend/worker.php',
               'frontend/wire.php', '.tools/php/bin/php', '.tools/php-file.so',
               '_build/default/adapter/main.exe', 'tests/semantics/recorded_worker.py',
               'tests/semantics/_build/default/numeric_runner.exe',
               str(Path(__file__).relative_to(ROOT))]
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='property-scalar-alias-protocol-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    rows = []
    try:
        for name, source in SOURCES.items():
            path = out / (name + '.php')
            path.write_bytes(source)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            initial = '$php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
            checks = assertions(initial, name)
            fixture = out / (name + '.watsup')
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- if ' + x + '\n' for x in checks))
            command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                       *[str(ROOT / p) for p in modules], str(fixture)]
            timed_out = False
            try:
                result = subprocess.run(command, capture_output=True, timeout=180)
                stdout, stderr, exit_status = result.stdout, result.stderr, result.returncode
            except subprocess.TimeoutExpired as error:
                stdout, stderr, exit_status = error.stdout or b'', error.stderr or b'', None
                timed_out = True
            (out / (name + '.stdout')).write_bytes(stdout)
            (out / (name + '.stderr')).write_bytes(stderr)
            passed = exit_status == 0 and stdout == b'true\n' and not stderr
            rows.append({'id': name, 'pass': passed, 'exit_status': exit_status,
                         'timeout': timed_out,
                         'source_sha256': digest(path), 'fixture_sha256': digest(fixture),
                         'assertions': len(checks)})
            print(name, passed, len(checks), flush=True)
            if timed_out:
                break
    finally:
        frontend.close()
        adapter.close()
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed during run'
    outcome = 'timeout' if rows[-1]['timeout'] else 'pass' if all(row['pass'] for row in rows) else 'fail'
    report = {'result': outcome,
              'inputs': before, 'records': rows}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
