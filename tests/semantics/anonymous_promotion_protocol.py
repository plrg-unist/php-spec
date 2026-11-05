#!/usr/bin/env python3
"""Actual promotion prologues, value separation and typed reference ownership."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_promotion_cases.json'
PREFIX = r'''
dec $promo175_front(pstate, nat) : bool
def $promo175_front(S, 0) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail*
def $promo175_front(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
def $promo175_front(S, n) = false -- otherwise
dec $promo175_seek(pstate, nat, nat) : pstate
def $promo175_seek(S, n_front, 0) = S
def $promo175_seek(S, n_front, n) = S
  -- if $(n > 0) /\ $promo175_front(S,n_front)
def $promo175_seek(S, n_front, n) = $promo175_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$promo175_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $promo175_seek(S, n_front, n) = S -- otherwise
dec $promo175_output_item(pevent) : ptbytes
def $promo175_output_item(OUTPUT ptbytes) = ptbytes
def $promo175_output_item(pevent) = eps -- otherwise
dec $promo175_output(pevent*) : ptbytes
def $promo175_output(eps) = eps
def $promo175_output(pevent :: pevent_tail*) = $promo175_output_item(pevent) ++ $promo175_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def slot(state, prop, value):
    name = 'ppropertyslot_' + state.lower() + '_' + prop
    return ['$objectprops_at(' + state + '.OBJECTPROPS,n_object) = (ppropertyslot_' + state.lower() + '*)',
            '$property_slot_at(ppropertyslot_' + state.lower() + '*,' + prop + '.KEY) = (' + name + ')',
            name + '.DECL = (' + prop + '.ORIGIN)',
            name + '.STATE = ' + value]


def final_checks(row, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$promo175_output(S_done.EVENTS) = ' + term(expected),
            r'$class_state_valid(S_done) /\ $property_state_valid(S_done)',
            r'$declaration_history_valid(S_done) /\ $heap_valid($heap_graph(S_done))']


def checks(row, fixture, filename):
    out = ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
           r'S_start.COMPLETION = BUDGET /\ ~S_start.COMPILESTOP',
           'S_pre = $promo175_seek(S_start,0,2000)',
           r'$promo175_front(S_pre,0) /\ S_pre.COMPLETION = BUDGET',
           'S_pre.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*',
           'S_pre.ORIGIN = (porigin_ctor)',
           'S_pre.CURRENT = (pcallcontext)',
           'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
           'pcallcontext.RECEIVER = (n_object)',
           'S_pre.CLASSES = [pclassdesc]',
           'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
           '$object_class_origin(S_pre,n_object) = (pclassdesc.ORIGIN)',
           '$receiving_function(S_pre,porigin_ctor) = (pfunction)',
           '$promotion_task_valid(S_pre,porigin_ctor,0)',
           '$call_task_valid(S_pre,PROMOTE_PARAMETER porigin_ctor 0)',
           '~$call_task_valid(S_pre,PROMOTE_PARAMETER porigin_ctor 8)',
           '~$promotion_task_valid(S_pre[.ORIGIN = (pclassdesc.ORIGIN)],porigin_ctor,0)',
           '~$promotion_task_valid(S_pre[.CURRENT = (pcallcontext[.RECEIVER = eps])],porigin_ctor,0)',
           'S_pre.EVENTS = eps']
    if row['id'] == 'promotion-values-defaults-and-local-array-cow':
        out += ['$promotion_descriptor(S_pre,pfunction,0) = (ppropertydesc_value)',
                '$promotion_descriptor(S_pre,pfunction,1) = (ppropertydesc_items)',
                '$promotion_descriptor(S_pre,pfunction,2) = (ppropertydesc_hint)',
                'pclassdesc.PROPERTIES = [ppropertydesc_value,ppropertydesc_items,ppropertydesc_hint]',
                r'ppropertydesc_value.DEFAULT = PROP_UNINITIALIZED /\ ppropertydesc_items.DEFAULT = PROP_UNINITIALIZED /\ ppropertydesc_hint.DEFAULT = PROP_UNINITIALIZED',
                'ppropertydesc_value.KEY = $ptascii("value")',
                'ppropertydesc_items.KEY = [0] ++ pclassdesc.NAME ++ [0] ++ $ptascii("items")',
                'ppropertydesc_hint.KEY = [0,42,0] ++ $ptascii("hint")',
                *slot('S_pre', 'ppropertydesc_value', 'PROP_INITIAL'),
                *slot('S_pre', 'ppropertydesc_items', 'PROP_INITIAL'),
                *slot('S_pre', 'ppropertydesc_hint', 'PROP_INITIAL'),
                '$lookup(S_pre.ENV,$ptascii("value")) = (n_value)',
                'S_pre.STORE[n_value] = DEFINED (PINT 8)',
                '$lookup(S_pre.ENV,$ptascii("items")) = (n_items_cell)',
                'S_pre.STORE[n_items_cell] = DEFINED (PARRAY n_items)',
                '$call_task_valid(S_pre,PROMOTE_PARAMETER porigin_ctor 1)',
                'S_body = $drive_steps(S_pre[.COMPLETION = NORMAL],3)',
                r'S_body.COMPLETION = BUDGET /\ S_body.EVENTS = eps',
                *slot('S_body', 'ppropertydesc_value', 'PROP_VALUE (DIRECT (PINT 8))'),
                *slot('S_body', 'ppropertydesc_items', 'PROP_VALUE (DIRECT (PARRAY n_items))'),
                '$promotion_queued_task_valid(S_body,porigin_ctor,0) = false',
                'S_bad_key = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_value,ppropertydesc_items[.KEY = $c_string(ppropertydesc_items.KEY)],ppropertydesc_hint]]]]',
                '$promotion_descriptor(S_bad_key,pfunction,1) = eps',
                'S_done = $drive_steps(S_body[.COMPLETION = NORMAL],8192)',
                *final_checks(row, filename),
                *slot('S_done', 'ppropertydesc_value', 'PROP_VALUE (DIRECT (PINT 8))'),
                *slot('S_done', 'ppropertydesc_items', 'PROP_VALUE (DIRECT (PARRAY n_items))'),
                'S_done.ARRAYS[n_items].ITEMS = [ENTRY (KSTRING $ptascii("k")) (DIRECT (PINT 3))]']
    else:
        out += ['$promotion_descriptor(S_pre,pfunction,0) = (ppropertydesc)',
                '$promotion_raw(S_pre,pfunction,0) = (psraw)',
                'psraw.BYREF',
                '$lookup(S_pre.ENV,$ptascii("value")) = (n_value)',
                '$lookup($global_table_view(S_pre).ENV,$ptascii("value")) = (n_global)',
                'n_value = n_global',
                'S_pre.STORE[n_value] = DEFINED (PINT 4)',
                *slot('S_pre', 'ppropertydesc', 'PROP_INITIAL'),
                '~$propref_source_present(S_pre.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)']
        if row['id'] == 'promotion-reference-alias-and-type-source':
            out += ['~ppropertydesc.READONLY',
                    'S_body = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
                    r'S_body.COMPLETION = BUDGET /\ S_body.EVENTS = eps',
                    *slot('S_body', 'ppropertydesc', 'PROP_VALUE (ALIAS n_value)'),
                    '$propref_source_present(S_body.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)',
                    '$proprefs_valid(S_body)',
                    '$propref_at(S_body.PROPREFS,n_value) = (ppropref)',
                    'pproptypesource_bad = OBJECT_PROP_SOURCE n_object ppropertydesc.KEY pclassdesc.ORIGIN',
                    'S_bad_source = S_body[.PROPREFS = [ppropref[.SOURCES = [pproptypesource_bad]]]]',
                    '~$proprefs_valid(S_bad_source)',
                    'S_done = $drive_steps(S_body[.COMPLETION = NORMAL],8192)',
                    *final_checks(row, filename),
                    *slot('S_done', 'ppropertydesc', 'PROP_VALUE (ALIAS n_value)'),
                    'S_done.STORE[n_value] = DEFINED (PINT 9)',
                    '$propref_source_present(S_done.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)']
        else:
            out += ['ppropertydesc.READONLY',
                    '$class_static_set_allowed(S_pre,ppropertydesc)',
                    '~$property_readonly_written(S_pre,n_object,$ptascii("value"))',
                    'S_fail = $promo175_seek(S_pre,1,100)',
                    r'$promo175_front(S_fail,1) /\ S_fail.COMPLETION = BUDGET',
                    'S_fail.TODO = (THROW_SEARCH n_error) :: ptask_error*',
                    'S_fail.OBJECTS[n_error] = THROWABLE pthrowable',
                    'pthrowable.KIND = "Error"',
                    '$string_bytes($throwable_field(S_fail,n_error,"message")) = ($ptascii("Cannot indirectly modify readonly property class@anonymous::$value"))',
                    'S_fail.EVENTS = eps',
                    *slot('S_fail', 'ppropertydesc', 'PROP_INITIAL'),
                    '~$propref_source_present(S_fail.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)',
                    'S_done = $drive_steps(S_fail[.COMPLETION = NORMAL],8192)',
                    *final_checks(row, filename),
                    'S_done.STORE[n_value] = DEFINED (PINT 4)']
    return out


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    selected = ['promotion-values-defaults-and-local-array-cow',
                'promotion-reference-alias-and-type-source',
                'promotion-readonly-reference-stops-before-body']
    rows = json.loads(CATALOGUE.read_text())['cases']
    raw = Path(tempfile.mkdtemp(prefix='anonymous-promotion-', dir=ROOT / '.tools'))
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
            function = '$promo175_group' + str(index)
            code += 'dec ' + function + '() : bool\ndef ' + function + '() = true\n' + ''.join('  -- if ' + check + '\n' for check in conditions)
            counts[name] = len(conditions)
            names.append(function + '()')
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + r' /\ '.join(names) + '\n')
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
