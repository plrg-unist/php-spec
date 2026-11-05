#!/usr/bin/env python3
"""Source-reached deferred property setup, cloned arrays and shared statics."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_property_cases.json'
PREFIX = r'''
dec $prop173_front(pstate, nat) : bool
def $prop173_front(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_name(S, porigin) =/= eps
def $prop173_front(S, 1) = true
  -- if S.TODO = (CLASS_CONST_CONSTRUCT ptbytes (eps) false z) :: ptask_tail*
def $prop173_front(S, 2) = true
  -- if S.TODO = (NOCTOR_ARGS pnoctorcall) :: ptask_tail*
  -- if pnoctorcall.ARGUMENTS = eps
def $prop173_front(S, n) = false -- otherwise
dec $prop173_seek(pstate, nat, nat) : pstate
def $prop173_seek(S, n_front, 0) = S
def $prop173_seek(S, n_front, n) = S
  -- if $(n > 0) /\ $prop173_front(S, n_front)
def $prop173_seek(S, n_front, n) = $prop173_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_front, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$prop173_front(S, n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $prop173_seek(S, n_front, n) = S -- otherwise
dec $prop173_output_item(pevent) : ptbytes
def $prop173_output_item(OUTPUT ptbytes) = ptbytes
def $prop173_output_item(pevent) = eps -- otherwise
dec $prop173_output(pevent*) : ptbytes
def $prop173_output(eps) = eps
def $prop173_output(pevent :: pevent_tail*) = $prop173_output_item(pevent) ++ $prop173_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def final_checks(row, state, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [
        state + '.COMPLETION = NORMAL /\\ ' + state + '.TODO = eps',
        '$prop173_output(' + state + '.EVENTS) = ' + term(expected),
        '$class_state_valid(' + state + ') /\\ $property_state_valid(' + state + ')',
        '$declaration_history_valid(' + state + ') /\\ $heap_valid($heap_graph(' + state + '))',
    ]


def checks(row, fixture, filename):
    result = ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
              'S_start.COMPLETION = BUDGET /\\ ~S_start.COMPILESTOP']
    if row['id'] == 'ordinary-property-expression-defaults-cow':
        result += [
            'S_pre = $prop173_seek(S_start,0,100)',
            '$prop173_front(S_pre,0) /\\ S_pre.COMPLETION = BUDGET',
            'S_pre.ORIGIN = (porigin_new)',
            'S_pre.TODO = (EVAL expression_new) :: ptask_tail*',
            '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc)',
            '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
            'S_pre.OBJECTS = eps',
            'pclassdesc.PROPERTIES = [ppropertydesc_a,ppropertydesc_b,ppropertydesc_items,ppropertydesc_label,ppropertydesc_optional]',
            'ppropertydesc_label.VISIBILITY = PROPERTY_PROTECTED /\\ ppropertydesc_optional.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_optional.KEY = [0] ++ pclassdesc.NAME ++ [0] ++ $ptascii("optional")',
            'z_new = $runtime_line(S_pre,eps,expression_new)',
            '$instance_default_tasks(S_pre,pclassdesc.ORIGIN,z_new) =/= eps',
            'S_dispatch = S_pre[.COMPLETION = NORMAL][.TODO = ptask_tail*]',
            'ptask_work* = $class_constant_new_work(S_dispatch,pclassdesc.NAME,z_new)',
            'ptask_marker = $class_constant_constructor_marker(S_dispatch,pclassdesc.NAME,eps,false,z_new)',
            'ptask_marker = CLASS_CONST_CONSTRUCT pclassdesc.NAME (eps) false z_new',
            'S_work = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
            'S_work.COMPLETION = BUDGET /\\ S_work.OBJECTS = eps',
            'S_work.TODO = ptask_work* ++ [ptask_marker] ++ ptask_tail*',
            '$class_constant_constructor_task(S_work,pclassdesc.NAME,eps,false,z_new)',
            'S_ready = $prop173_seek(S_work,1,1000)',
            '$prop173_front(S_ready,1) /\\ S_ready.COMPLETION = BUDGET',
            'S_ready.TODO = ptask_marker :: ptask_tail*',
            'S_ready.OBJECTS = eps',
            '$instance_default_tasks(S_ready,pclassdesc.ORIGIN,z_new) = eps',
            '$static_default_tasks(S_ready,pclassdesc.ORIGIN,z_new) = eps',
            '$call_task_valid(S_ready,ptask_marker)',
            '~$call_task_valid(S_ready,CLASS_CONST_CONSTRUCT $ptascii("Forged173") (eps) false z_new)',
            '~$call_task_valid(S_ready[.ORIGIN = (pclassdesc.ORIGIN)],ptask_marker)',
            '~$call_task_valid(S_ready,CLASS_CONST_CONSTRUCT pclassdesc.NAME (eps) false $(z_new + 1))',
            '$anonymous_new_noctor(S_ready[.COMPLETION = NORMAL],pclassdesc.NAME,z_new) = $new_class(S_ready[.COMPLETION = NORMAL],pclassdesc.NAME,z_new)',
            'S_alloc = $prop173_seek(S_ready,2,100)',
            '$prop173_front(S_alloc,2) /\\ S_alloc.COMPLETION = BUDGET',
            'S_alloc.TODO = (NOCTOR_ARGS pnoctorcall) :: ptask_tail*',
            'pnoctorcall.OBJECT = n_object',
            'S_alloc.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
            '$objectprops_at(S_alloc.OBJECTPROPS,n_object) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*,$ptascii("a")) = (ppropertyslot_a)',
            'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (PINT 9))',
            '$property_slot_at(ppropertyslot*,$ptascii("b")) = (ppropertyslot_b)',
            'ppropertyslot_b.STATE = PROP_VALUE (DIRECT (PINT 12))',
            'S_done = $drive_steps(S_alloc[.COMPLETION = NORMAL],8192)',
            *final_checks(row, 'S_done', filename),
            '$lookup($global_table_view(S_done).ENV,$ptascii("object")) = (n_object_cell)',
            'S_done.STORE[n_object_cell] = DEFINED (POBJECT n_original)',
            '$lookup($global_table_view(S_done).ENV,$ptascii("other")) = (n_other_cell)',
            'S_done.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
            'n_original =/= n_other',
            '$objectprops_at(S_done.OBJECTPROPS,n_original) = (ppropertyslot_original*)',
            '$objectprops_at(S_done.OBJECTPROPS,n_other) = (ppropertyslot_other*)',
            '$property_slot_at(ppropertyslot_original*,$ptascii("items")) = (ppropertyslot_original_items)',
            '$property_slot_at(ppropertyslot_other*,$ptascii("items")) = (ppropertyslot_other_items)',
            'ppropertyslot_original_items.STATE = PROP_VALUE (DIRECT (PARRAY n_original_items))',
            'ppropertyslot_other_items.STATE = PROP_VALUE (DIRECT (PARRAY n_other_items))',
            'n_original_items =/= n_other_items',
            'S_done.ARRAYS[n_original_items].ITEMS = [ENTRY (KSTRING $ptascii("k")) (DIRECT (PINT 3))]',
            'S_done.ARRAYS[n_other_items].ITEMS = [ENTRY (KSTRING $ptascii("k")) (DIRECT (PINT 9))]',
        ]
    else:
        result += [
            'S_done = $drive_steps(S_start[.COMPLETION = NORMAL],8192)',
            *final_checks(row, 'S_done', filename),
            'S_done.CLASSES = [pclassdesc]',
            'pclassdesc.PROPERTIES = [ppropertydesc_count,ppropertydesc_items]',
            'ppropertydesc_count.STATIC /\\ ppropertydesc_items.STATIC',
            'ppropertydesc_count.VISIBILITY = PROPERTY_PRIVATE /\\ ppropertydesc_items.VISIBILITY = PROPERTY_PROTECTED',
            'ppropertydesc_count.KEY = [0] ++ pclassdesc.NAME ++ [0] ++ $ptascii("count")',
            'S_done.CLASSSTATICS = [pclassstatic_count,pclassstatic_items]',
            'pclassstatic_count.DECL = ppropertydesc_count.ORIGIN',
            'pclassstatic_count.STATE = PROP_VALUE (DIRECT (PINT 5))',
            'pclassstatic_items.DECL = ppropertydesc_items.ORIGIN',
            'pclassstatic_items.STATE = PROP_VALUE (DIRECT (PARRAY n_items))',
            'S_done.ARRAYS[n_items].ITEMS = [ENTRY (KSTRING $ptascii("k")) (DIRECT (PINT 4))]',
            '$class_statics_valid(S_done)',
            '$lookup($global_table_view(S_done).ENV,$ptascii("first")) = (n_first_cell)',
            'S_done.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
            '$lookup($global_table_view(S_done).ENV,$ptascii("object")) = (n_last_cell)',
            'S_done.STORE[n_last_cell] = DEFINED (POBJECT n_last)',
            'n_first =/= n_last',
            'S_done.OBJECTS[n_first] = INSTANCE pclassdesc.ORIGIN /\\ S_done.OBJECTS[n_last] = INSTANCE pclassdesc.ORIGIN',
        ]
    return result


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    selected = ['ordinary-property-expression-defaults-cow', 'ordinary-property-static-same-site-sharing']
    rows = json.loads(CATALOGUE.read_text())['cases']
    raw = Path(tempfile.mkdtemp(prefix='anonymous-property-', dir=ROOT / '.tools'))
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
            function = '$prop173_group' + str(index)
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
