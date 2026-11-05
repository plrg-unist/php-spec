#!/usr/bin/env python3
"""Source-reached own constant tables retain types, visibility and name authority."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_own_constant_cases.json'
PREFIX = r'''
dec $own172_front(pstate, nat) : bool
def $own172_front(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_name(S, porigin) =/= eps
def $own172_front(S, 1) = true
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = INSTANCE porigin
def $own172_front(S, n) = false -- otherwise
dec $own172_seek(pstate, nat, nat) : pstate
def $own172_seek(S, n_front, 0) = S
def $own172_seek(S, n_front, n) = S
  -- if $(n > 0) /\ $own172_front(S, n_front)
def $own172_seek(S, n_front, n) = $own172_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_front, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$own172_front(S, n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $own172_seek(S, n_front, n) = S -- otherwise
dec $own172_output_item(pevent) : ptbytes
def $own172_output_item(OUTPUT ptbytes) = ptbytes
def $own172_output_item(pevent) = eps -- otherwise
dec $own172_output(pevent*) : ptbytes
def $own172_output(eps) = eps
def $own172_output(pevent :: pevent_tail*) = $own172_output_item(pevent) ++ $own172_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def checks(row, fixture, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    result = [
        'S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_start.COMPLETION = BUDGET /\\ ~S_start.COMPILESTOP',
        'S_pre = $own172_seek(S_start,0,100)',
        '$own172_front(S_pre,0) /\\ S_pre.COMPLETION = BUDGET',
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc)',
        'pclassdesc.EARLY /\\ pclassdesc.PARENT = eps /\\ pclassdesc.INTERFACES = eps',
        'pclassdesc.NAME = $ptascii("class@anonymous") ++ [0] ++ ' + term(filename) + ' ++ $ptascii(":2$0")',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$class_constant_message_class(S_pre,pclassdesc,pclassdesc.NAME) = pclassdesc.NAME',
        'pclassdesc.NAME =/= $c_string(pclassdesc.NAME)',
        'S_pre.OBJECTS = eps',
        'pclassdesc.CONSTANTS = [pclassconstantdesc_a,pclassconstantdesc_b,pclassconstantdesc_label,pclassconstantdesc_secret,pclassconstantdesc_protected,pclassconstantdesc_null,pclassconstantdesc_map]',
        'pclassconstantdesc_a.ORIGIN =/= pclassconstantdesc_b.ORIGIN',
        'pclassconstantdesc_a.NAME = $ptascii("A") /\\ pclassconstantdesc_b.NAME = $ptascii("B")',
        'pclassconstantdesc_a.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))] /\\ pclassconstantdesc_b.TYPE = pclassconstantdesc_a.TYPE',
        'pclassconstantdesc_a.VISIBILITY = PROPERTY_PUBLIC /\\ pclassconstantdesc_b.VISIBILITY = PROPERTY_PUBLIC',
        'pclassconstantdesc_secret.VISIBILITY = PROPERTY_PRIVATE /\\ pclassconstantdesc_protected.VISIBILITY = PROPERTY_PROTECTED',
        '$typed_exact(pclassconstantdesc_null.TYPE,PNULL) /\\ $typed_exact(pclassconstantdesc_null.TYPE,PINT 1)',
        '~$typed_exact(pclassconstantdesc_null.TYPE,PSTRING eps)',
        'pclassconstantdesc_map.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]',
    ]
    for desc in ['pclassconstantdesc_a', 'pclassconstantdesc_b', 'pclassconstantdesc_label', 'pclassconstantdesc_secret', 'pclassconstantdesc_protected', 'pclassconstantdesc_null', 'pclassconstantdesc_map']:
        result += [
            f'{desc}.OWNER = pclassdesc.ORIGIN /\\ {desc}.OWNERNAME = pclassdesc.NAME',
            f'{desc}.ORIGIN = PORIGIN 0 pcpath_{desc}',
            f'$origin_node(S_pre.SOURCES,{desc}.ORIGIN) = (NConst (NIdentifier (BYTES text_{desc}) metadata_name_{desc}) expression_{desc} metadata_{desc})',
            f'$base64(text_{desc}) = {desc}.NAME',
        ]
    result += [
        'pclassdesc_type = pclassdesc[.CONSTANTS = [pclassconstantdesc_a[.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]],pclassconstantdesc_b,pclassconstantdesc_label,pclassconstantdesc_secret,pclassconstantdesc_protected,pclassconstantdesc_null,pclassconstantdesc_map]]',
        'S_type = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_type)]',
        '$anonymous_new_descriptor(S_type,porigin_new) = eps /\\ ~$declaration_history_valid(S_type)',
        'pclassdesc_duplicate = pclassdesc[.CONSTANTS = pclassdesc.CONSTANTS ++ [pclassconstantdesc_a]]',
        'S_duplicate = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_duplicate)]',
        '$anonymous_new_descriptor(S_duplicate,porigin_new) = eps /\\ ~$declaration_history_valid(S_duplicate)',
        'S_name = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc[.NAME = $c_string(pclassdesc.NAME)])]',
        '$anonymous_new_descriptor(S_name,porigin_new) = eps',
        'S_alloc = $own172_seek(S_pre,1,100)',
        '$own172_front(S_alloc,1) /\\ S_alloc.COMPLETION = BUDGET',
        'S_alloc.RESULT = KNOWN (POBJECT n_object)',
        'S_alloc.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
        'S_alloc.CLASSCONSTANTINIT = eps',
        '$class_constant_compile_value(S_alloc,pclassconstantdesc_a) = ((PINT 7,PVSCALAR))',
        '$class_constant_compile_value(S_alloc,pclassconstantdesc_b) = ((PINT 8,PVSCALAR))',
        '$class_constant_compile_value(S_alloc,pclassconstantdesc_secret) = ((PINT 11,PVSCALAR))',
        '$class_constant_compile_value(S_alloc,pclassconstantdesc_protected) = ((PINT 13,PVSCALAR))',
        '$class_constant_compile_value(S_alloc,pclassconstantdesc_null) = ((PNULL,PVSCALAR))',
        '$class_constant_compile_value(S_alloc,pclassconstantdesc_map) = ((PARRAY n_map,pvalueclass_map))',
        '$constant_value_class_valid(S_alloc,PARRAY n_map,pvalueclass_map)',
        '$class_state_valid(S_alloc[.COMPLETION = NORMAL]) /\\ $heap_valid($heap_graph(S_alloc))',
        'S_done = $drive_steps(S_alloc[.COMPLETION = NORMAL],8192)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps',
        '$own172_output(S_done.EVENTS) = ' + term(expected),
        '$declaration_history_valid(S_done) /\\ $class_constant_state_valid(S_done)',
        '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    ]
    return result


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['id'] == 'own-typed-multiple-constant-table']
    raw = Path(tempfile.mkdtemp(prefix='anonymous-own-constant-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, source, Path(__file__),
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'source_sha256': row['source_sha256'], 'inputs_before': before}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        conditions = checks(row, checked['fixture'], os.fsencode(source))
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in conditions))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), conditions=len(conditions), fixture_sha256=sha(fixture))
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
