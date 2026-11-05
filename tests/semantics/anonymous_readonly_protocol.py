#!/usr/bin/env python3
"""Source-owned readonly headers, implicit fields and initialization boundaries."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_readonly_cases.json'
PREFIX = r'''
dec $ro176_keywordless(metadata) : metadata
def $ro176_keywordless(eps) = eps
def $ro176_keywordless((MclassKeywordLine z) :: metadata_tail*) = $ro176_keywordless(metadata_tail*)
def $ro176_keywordless(metadataEntry :: metadata_tail*) = metadataEntry :: $ro176_keywordless(metadata_tail*)
  -- if $class_keyword_item(metadataEntry) = eps
dec $ro176_assignment(pstate, int) : bool
def $ro176_assignment(S, z) = true
  -- if S.TODO = (EVAL (NExprAssign (NExprPropertyFetch (NExprVariable (BYTES text_object) metadata_object) (NIdentifier (BYTES text_value) metadata_value) metadata_fetch) (NScalarInt (INTEGER z) metadata_int) metadata_assign)) :: ptask_tail*
  -- if $base64(text_object) = $ptascii("object") /\ $base64(text_value) = $ptascii("value")
def $ro176_assignment(S, z) = false -- otherwise
dec $ro176_front(pstate, nat) : bool
def $ro176_front(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 (INTEGER 64) phpType3 phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_name(S,porigin) =/= eps
def $ro176_front(S, 1) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail*
def $ro176_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
def $ro176_front(S, 3) = $ro176_assignment(S,7)
def $ro176_front(S, 4) = $ro176_assignment(S,9)
def $ro176_front(S, n) = false -- otherwise
dec $ro176_seek(pstate, nat, nat) : pstate
def $ro176_seek(S, n_front, 0) = S
def $ro176_seek(S, n_front, n) = S
  -- if $(n > 0) /\ $ro176_front(S,n_front)
def $ro176_seek(S, n_front, n) = $ro176_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ro176_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ro176_seek(S, n_front, n) = S -- otherwise
dec $ro176_output_item(pevent) : ptbytes
def $ro176_output_item(OUTPUT ptbytes) = ptbytes
def $ro176_output_item(pevent) = eps -- otherwise
dec $ro176_output(pevent*) : ptbytes
def $ro176_output(eps) = eps
def $ro176_output(pevent :: pevent_tail*) = $ro176_output_item(pevent) ++ $ro176_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def slots(state, values):
    result = ['$objectprops_at(' + state + '.OBJECTPROPS,n_object) = (ppropertyslot_' + state.lower() + '*)']
    for prop, value in values.items():
        variable = 'ppropertyslot_' + state.lower() + '_' + prop
        result += ['$property_slot_at(ppropertyslot_' + state.lower() + '*,' + prop + '.KEY) = (' + variable + ')',
                   variable + '.DECL = (' + prop + '.ORIGIN)', variable + '.STATE = ' + value]
    return result


def final_checks(row, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$ro176_output(S_done.EVENTS) = ' + term(expected),
            r'$class_state_valid(S_done) /\ $property_state_valid(S_done)',
            r'$declaration_history_valid(S_done) /\ $heap_valid($heap_graph(S_done))']


def checks(row, fixture, filename):
    out = ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
           r'S_start.COMPLETION = BUDGET /\ ~S_start.COMPILESTOP']
    if row['id'] == 'readonly-split-header-implicit-properties-and-promotion':
        out += ['S_new = $ro176_seek(S_start,0,1000)',
                r'$ro176_front(S_new,0) /\ S_new.COMPLETION = BUDGET',
                'S_new.ORIGIN = (porigin_new)',
                '$anonymous_new_descriptor(S_new,porigin_new) = (pclassdesc)',
                'pclassdesc.READONLY',
                'pclassdesc.LINE = 4',
                '$anonymous_class_name(' + term(filename) + ',4,0) = (pclassdesc.NAME)',
                '$origin_node(S_new.SOURCES,pclassdesc.ORIGIN) = (NStmtClass (SEQUENCE eps) (INTEGER 64) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata_class)',
                '$source_line(metadata_class) = 3',
                '$class_keyword_lines(metadata_class) = [4]',
                '$anonymous_class_line(64,metadata_class) = 4',
                'metadata_without = $ro176_keywordless(metadata_class)',
                '$anonymous_class_line(64,metadata_without) = 0',
                '$anonymous_class_line(64,(MclassKeywordLine 4) :: metadata_class) = 0',
                '$anonymous_class_line(64,(MclassKeywordLine 2) :: metadata_without) = 0',
                'z_past = $($source_end_line(metadata_class) + 1)',
                '$anonymous_class_line(64,(MclassKeywordLine z_past) :: metadata_without) = 0',
                '$anonymous_class_line(0,metadata_without) = $source_line(metadata_without)',
                '~$anonymous_class_node(NStmtClass (SEQUENCE eps) (INTEGER 64) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata_without)',
                '$source_unit(S_new.SOURCES,0) = (pcunit)',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',S_new.CLASSES,eps,eps,0) = (1)',
                'S_new.OBJECTS = eps',
                'pclassdesc.PROPERTIES = [ppropertydesc_declared,ppropertydesc_label,ppropertydesc_promoted]',
                r'ppropertydesc_declared.READONLY /\ ppropertydesc_label.READONLY /\ ppropertydesc_promoted.READONLY',
                'ppropertydesc_label.KEY = [0] ++ pclassdesc.NAME ++ [0] ++ $ptascii("label")',
                'pclassdesc_bad = pclassdesc[.READONLY = false][.PROPERTIES = [ppropertydesc_declared[.READONLY = false][.SETVISIBILITY = eps],ppropertydesc_label[.READONLY = false],ppropertydesc_promoted[.READONLY = false][.SETVISIBILITY = eps]]]',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',[pclassdesc_bad],eps,eps,0) = eps',
                'S_bad_header = S_new[.CLASSES = [pclassdesc_bad]]',
                '$anonymous_new_descriptor(S_bad_header,porigin_new) = eps',
                '$anonymous_class_name(' + term(filename) + ',3,0) = (ptbytes_wrong)',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',[pclassdesc[.LINE = 3][.NAME = ptbytes_wrong]],eps,eps,0) = eps',
                'S_promo = $ro176_seek(S_new,1,2000)',
                r'$ro176_front(S_promo,1) /\ S_promo.COMPLETION = BUDGET',
                'S_promo.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*',
                'S_promo.CURRENT = (pcallcontext)',
                'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
                'pcallcontext.RECEIVER = (n_object)',
                '$receiving_function(S_promo,porigin_ctor) = (pfunction)',
                '$promotion_raw(S_promo,pfunction,0) = (psraw)',
                'psraw.FLAGS = 1',
                '$promotion_descriptor(S_promo,pfunction,0) = (ppropertydesc_promoted)',
                '$promotion_task_valid(S_promo,porigin_ctor,0)',
                *slots('S_promo', {p: 'PROP_INITIAL' for p in ['ppropertydesc_declared', 'ppropertydesc_label', 'ppropertydesc_promoted']}),
                'S_body = $drive_steps(S_promo[.COMPLETION = NORMAL],1)',
                r'S_body.COMPLETION = BUDGET /\ S_body.EVENTS = eps',
                *slots('S_body', {'ppropertydesc_declared': 'PROP_INITIAL', 'ppropertydesc_label': 'PROP_INITIAL', 'ppropertydesc_promoted': 'PROP_VALUE (DIRECT (PINT 5))'}),
                'S_done = $drive_steps(S_body[.COMPLETION = NORMAL],8192)',
                *final_checks(row, filename),
                *slots('S_done', {'ppropertydesc_declared': 'PROP_VALUE (DIRECT (PINT 6))', 'ppropertydesc_promoted': 'PROP_VALUE (DIRECT (PINT 5))'})]
    elif row['id'] == 'readonly-implied-reference-promotion-before-body':
        out += ['S_pre = $ro176_seek(S_start,1,2000)',
                r'$ro176_front(S_pre,1) /\ S_pre.COMPLETION = BUDGET',
                'S_pre.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*',
                'S_pre.CURRENT = (pcallcontext)',
                'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
                'pcallcontext.RECEIVER = (n_object)',
                'S_pre.CLASSES = [pclassdesc]', 'pclassdesc.READONLY',
                '$receiving_function(S_pre,porigin_ctor) = (pfunction)',
                '$promotion_raw(S_pre,pfunction,0) = (psraw)',
                r'psraw.FLAGS = 1 /\ psraw.BYREF',
                '$promotion_descriptor(S_pre,pfunction,0) = (ppropertydesc)',
                'ppropertydesc.READONLY',
                '$promotion_task_valid(S_pre,porigin_ctor,0)',
                '$class_static_set_allowed(S_pre,ppropertydesc)',
                '$lookup(S_pre.ENV,$ptascii("value")) = (n_value)',
                *slots('S_pre', {'ppropertydesc': 'PROP_INITIAL'}),
                '~$propref_source_present(S_pre.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)',
                'S_fail = $ro176_seek(S_pre,2,100)',
                r'$ro176_front(S_fail,2) /\ S_fail.COMPLETION = BUDGET',
                'S_fail.TODO = (THROW_SEARCH n_error) :: ptask_error*',
                'S_fail.OBJECTS[n_error] = THROWABLE pthrowable',
                'pthrowable.KIND = "Error"',
                '$string_bytes($throwable_field(S_fail,n_error,"message")) = ($ptascii("Cannot indirectly modify readonly property class@anonymous::$value"))',
                'S_fail.EVENTS = eps',
                *slots('S_fail', {'ppropertydesc': 'PROP_INITIAL'}),
                '~$propref_source_present(S_fail.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)',
                'S_done = $drive_steps(S_fail[.COMPLETION = NORMAL],8192)',
                *final_checks(row, filename),
                'S_done.STORE[n_value] = DEFINED (PINT 4)']
    else:
        out += ['S_first = $ro176_seek(S_start,3,1000)',
                r'$ro176_front(S_first,3) /\ S_first.COMPLETION = BUDGET',
                'S_first.CURRENT = eps', 'S_first.CLASSES = [pclassdesc]',
                'pclassdesc.READONLY', 'pclassdesc.PROPERTIES = [ppropertydesc]',
                'ppropertydesc.READONLY', 'ppropertydesc.SETVISIBILITY = eps',
                '$lookup($global_table_view(S_first).ENV,$ptascii("object")) = (n_object_cell)',
                'S_first.STORE[n_object_cell] = DEFINED (POBJECT n_object)',
                *slots('S_first', {'ppropertydesc': 'PROP_INITIAL'}),
                '$class_static_set_allowed(S_first,ppropertydesc)',
                '~$property_set_denied(S_first,n_object,$ptascii("value"))',
                'S_second = $ro176_seek(S_first,4,1000)',
                r'$ro176_front(S_second,4) /\ S_second.COMPLETION = BUDGET',
                '$property_set_denied(S_second,n_object,$ptascii("value"))',
                *slots('S_second', {'ppropertydesc': 'PROP_VALUE (DIRECT (PINT 7))'}),
                'S_fail = $ro176_seek(S_second,2,100)',
                r'$ro176_front(S_fail,2) /\ S_fail.COMPLETION = BUDGET',
                'S_fail.TODO = (THROW_SEARCH n_error) :: ptask_error*',
                '$string_bytes($throwable_field(S_fail,n_error,"message")) = ($ptascii("Cannot modify readonly property class@anonymous::$value"))',
                'S_done = $drive_steps(S_fail[.COMPLETION = NORMAL],8192)',
                *final_checks(row, filename),
                *slots('S_done', {'ppropertydesc': 'PROP_VALUE (DIRECT (PINT 7))'})]
    return out


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    selected = ['readonly-split-header-implicit-properties-and-promotion',
                'readonly-implied-reference-promotion-before-body',
                'readonly-public-set-first-and-second-store']
    rows = json.loads(CATALOGUE.read_text())['cases']
    raw = Path(tempfile.mkdtemp(prefix='anonymous-readonly-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__),
               ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
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
            function = '$ro176_group' + str(index)
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
