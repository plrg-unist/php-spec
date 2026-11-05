#!/usr/bin/env python3
"""Source-reached setter permission, readonly initialization and final storage."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_property_modifier_cases.json'
PREFIX = r'''
dec $prop174_assign(pstate, ptbytes, ptbytes, int) : bool
def $prop174_assign(S, ptbytes_receiver, ptbytes_member, z) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprPropertyFetch (NExprVariable (BYTES text_receiver) metadata_receiver) (NIdentifier (BYTES text_member) metadata_member) metadata_fetch) (NScalarInt (INTEGER z) metadata_value) metadata_assign)) :: ptask_tail*
  -- if $base64(text_receiver) = ptbytes_receiver /\ $base64(text_member) = ptbytes_member
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprAssign (NExprPropertyFetch (NExprVariable (BYTES text_receiver) metadata_receiver) (NIdentifier (BYTES text_member) metadata_member) metadata_fetch) (NScalarInt (INTEGER z) metadata_value) metadata_assign)
def $prop174_assign(S, ptbytes_receiver, ptbytes_member, z) = false -- otherwise
dec $prop174_front(pstate, nat) : bool
def $prop174_front(S, 0) = $prop174_assign(S,$ptascii("this"),$ptascii("secret"),7)
def $prop174_front(S, 1) = $prop174_assign(S,$ptascii("object"),$ptascii("value"),9)
def $prop174_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
def $prop174_front(S, 3) = $prop174_assign(S,$ptascii("object"),$ptascii("value"),7)
def $prop174_front(S, n) = false -- otherwise
dec $prop174_seek(pstate, nat, nat) : pstate
def $prop174_seek(S, n_front, 0) = S
def $prop174_seek(S, n_front, n) = S
  -- if $(n > 0) /\ $prop174_front(S,n_front)
def $prop174_seek(S, n_front, n) = $prop174_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$prop174_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $prop174_seek(S, n_front, n) = S -- otherwise
dec $prop174_output_item(pevent) : ptbytes
def $prop174_output_item(OUTPUT ptbytes) = ptbytes
def $prop174_output_item(pevent) = eps -- otherwise
dec $prop174_output(pevent*) : ptbytes
def $prop174_output(eps) = eps
def $prop174_output(pevent :: pevent_tail*) = $prop174_output_item(pevent) ++ $prop174_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def slots(state, obj, values):
    result = ['$objectprops_at(' + state + '.OBJECTPROPS,' + obj + ') = (ppropertyslot_' + state.lower() + '*)']
    for name, value in values.items():
        variable = 'ppropertyslot_' + state.lower() + '_' + name
        result += ['$property_slot_at(ppropertyslot_' + state.lower() + '*,$ptascii("' + name + '")) = (' + variable + ')',
                   variable + '.STATE = ' + value]
    return result


def final_checks(row, state, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [state + '.COMPLETION = NORMAL /\\ ' + state + '.TODO = eps',
            '$prop174_output(' + state + '.EVENTS) = ' + term(expected),
            '$class_state_valid(' + state + ') /\\ $property_state_valid(' + state + ')',
            '$declaration_history_valid(' + state + ') /\\ $heap_valid($heap_graph(' + state + '))']


def global_object(state):
    return ['$lookup($global_table_view(' + state + ').ENV,$ptascii("object")) = (n_object_cell)',
            state + '.STORE[n_object_cell] = DEFINED (POBJECT n_object)']


def checks(row, fixture, filename):
    out = ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
           'S_start.COMPLETION = BUDGET /\\ ~S_start.COMPILESTOP']
    if row['id'] == 'asymmetric-instance-setter-storage-and-denials':
        out += ['S_local = $prop174_seek(S_start,0,1000)',
                '$prop174_front(S_local,0) /\\ S_local.COMPLETION = BUDGET',
                'S_local.CLASSES = [pclassdesc]',
                'pclassdesc.PROPERTIES = [ppropertydesc_value,ppropertydesc_secret]',
                'ppropertydesc_value.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ ~ppropertydesc_value.FINAL',
                'ppropertydesc_secret.SETVISIBILITY = (PROPERTY_PRIVATE) /\\ ppropertydesc_secret.FINAL',
                'ppropertydesc_value.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc_secret.VISIBILITY = PROPERTY_PUBLIC',
                'ppropertydesc_value.KEY = $ptascii("value") /\\ ppropertydesc_secret.KEY = $ptascii("secret")',
                'S_local.CURRENT = (pcallcontext)',
                'pcallcontext.INSTANCE = (n_object)',
                'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
                '$class_static_set_allowed(S_local,ppropertydesc_secret)',
                '~$property_set_denied(S_local,n_object,$ptascii("secret"))',
                *slots('S_local', 'n_object', {'value': 'PROP_VALUE (DIRECT (PINT 5))', 'secret': 'PROP_VALUE (DIRECT (PINT 4))'}),
                'S_global = $prop174_seek(S_local,1,1000)',
                '$prop174_front(S_global,1) /\\ S_global.COMPLETION = BUDGET',
                'S_global.CURRENT = eps',
                '$property_set_denied(S_global,n_object,$ptascii("value")) /\\ $property_set_denied(S_global,n_object,$ptascii("secret"))',
                '~$class_static_set_allowed(S_global,ppropertydesc_value) /\\ ~$class_static_set_allowed(S_global,ppropertydesc_secret)',
                *slots('S_global', 'n_object', {'value': 'PROP_VALUE (DIRECT (PINT 5))', 'secret': 'PROP_VALUE (DIRECT (PINT 7))'}),
                'S_throw = $prop174_seek(S_global,2,100)',
                '$prop174_front(S_throw,2) /\\ S_throw.COMPLETION = BUDGET',
                'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
                'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
                '$throwable_field(S_throw,n_error,"message") = PSTRING $ptascii("Cannot modify protected(set) property class@anonymous::$value from global scope")',
                '$throwable_field(S_throw,n_error,"line") = PINT 8',
                *slots('S_throw', 'n_object', {'value': 'PROP_VALUE (DIRECT (PINT 5))', 'secret': 'PROP_VALUE (DIRECT (PINT 7))'}),
                'S_bad_final = S_global[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_value,ppropertydesc_secret[.FINAL = false]]]]]',
                '~$declaration_history_valid(S_bad_final)',
                'S_bad_set = S_global[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_value,ppropertydesc_secret[.SETVISIBILITY = (PROPERTY_PROTECTED)]]]]]',
                '~$declaration_history_valid(S_bad_set)',
                'S_done = $drive_steps(S_throw[.COMPLETION = NORMAL],8192)',
                *final_checks(row, 'S_done', filename),
                *slots('S_done', 'n_object', {'value': 'PROP_VALUE (DIRECT (PINT 5))', 'secret': 'PROP_VALUE (DIRECT (PINT 7))'})]
    elif row['id'] == 'asymmetric-explicit-public-set-readonly-initialization':
        out += ['S_first = $prop174_seek(S_start,3,1000)',
                '$prop174_front(S_first,3) /\\ S_first.COMPLETION = BUDGET',
                'S_first.CURRENT = eps', 'S_first.CLASSES = [pclassdesc]',
                'pclassdesc.PROPERTIES = [ppropertydesc]',
                'ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
                'ppropertydesc.SETVISIBILITY = eps /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC',
                *global_object('S_first'),
                *slots('S_first', 'n_object', {'value': 'PROP_INITIAL'}),
                '$class_static_set_allowed(S_first,ppropertydesc)',
                '~$property_set_denied(S_first,n_object,$ptascii("value"))',
                'S_second = $prop174_seek(S_first,1,1000)',
                '$prop174_front(S_second,1) /\\ S_second.COMPLETION = BUDGET',
                '$property_readonly_written(S_second,n_object,$ptascii("value"))',
                '$property_set_denied(S_second,n_object,$ptascii("value"))',
                *slots('S_second', 'n_object', {'value': 'PROP_VALUE (DIRECT (PINT 7))'}),
                'S_throw = $prop174_seek(S_second,2,100)',
                '$prop174_front(S_throw,2) /\\ S_throw.COMPLETION = BUDGET',
                'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
                'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
                '$throwable_field(S_throw,n_error,"message") = PSTRING $ptascii("Cannot modify readonly property class@anonymous::$value")',
                '$throwable_field(S_throw,n_error,"line") = PINT 5',
                'S_done = $drive_steps(S_throw[.COMPLETION = NORMAL],8192)',
                *final_checks(row, 'S_done', filename),
                *slots('S_done', 'n_object', {'value': 'PROP_VALUE (DIRECT (PINT 7))'})]
    else:
        out += ['S_write = $prop174_seek(S_start,1,1000)',
                '$prop174_front(S_write,1) /\\ S_write.COMPLETION = BUDGET',
                'S_write.CLASSES = [pclassdesc]',
                'pclassdesc.PROPERTIES = [ppropertydesc_value,ppropertydesc_count]',
                'ppropertydesc_value.FINAL /\\ ppropertydesc_count.FINAL',
                '~ppropertydesc_value.READONLY /\\ ~ppropertydesc_count.READONLY',
                'ppropertydesc_value.SETVISIBILITY = eps /\\ ppropertydesc_count.SETVISIBILITY = eps',
                '~ppropertydesc_value.STATIC /\\ ppropertydesc_count.STATIC',
                *global_object('S_write'),
                '~$property_set_denied(S_write,n_object,$ptascii("value"))',
                '$class_static_set_allowed(S_write,ppropertydesc_count)',
                'S_done = $drive_steps(S_write[.COMPLETION = NORMAL],8192)',
                *final_checks(row, 'S_done', filename),
                *slots('S_done', 'n_object', {'value': 'PROP_VALUE (DIRECT (PINT 9))'}),
                'S_done.CLASSSTATICS = [{DECL ppropertydesc_count.ORIGIN, STATE PROP_VALUE (DIRECT (PINT 2))}]',
                '$class_statics_valid(S_done)',
                'S_bad_final = S_done[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_value[.FINAL = false],ppropertydesc_count]]]]',
                '~$declaration_history_valid(S_bad_final)']
    return out


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    selected = ['asymmetric-instance-setter-storage-and-denials',
                'asymmetric-explicit-public-set-readonly-initialization',
                'final-instance-and-static-properties-remain-writable']
    rows = json.loads(CATALOGUE.read_text())['cases']
    raw = Path(tempfile.mkdtemp(prefix='anonymous-property-modifier-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__),
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        code, counts, names = PREFIX, {}, []
        for index, name in enumerate(selected):
            row, = [r for r in rows if r['id'] == name]
            source = raw / (name + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            function = '$prop174_group' + str(index)
            code += 'dec ' + function + '() : bool\ndef ' + function + '() = true\n' + ''.join('  -- if ' + check + '\n' for check in conditions)
            counts[name] = len(conditions)
            names.append(function + '()')
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + ' /\\ '.join(names) + '\n')
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), conditions=counts, fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and before == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
