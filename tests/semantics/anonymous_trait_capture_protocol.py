#!/usr/bin/env python3
"""Source-reached parented anonymous trait publication and capture boundary."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_trait_capture_cases.json'
CASE = 'parented-anonymous-trait-first-capture'
PREFIX = r'''
dec $class166_single_trait(statement) : bool
def $class166_single_trait(NStmtTraitUse (SEQUENCE (name_trait :: eps)) (SEQUENCE eps) metadata_use) = true
  -- if ~$anonymous_member(NStmtTraitUse (SEQUENCE (name_trait :: name_trait :: eps)) (SEQUENCE eps) metadata_use)
def $class166_single_trait(statement) = false -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def checks(fixture, filename):
    return [
        'program_source = ' + fixture,
        'S = $php_run(program_source,12,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S.COMPLETION = BUDGET', '~S.COMPILESTOP',
        'S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE statement*) metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*',
        'statement* = [statement_use]',
        '$class166_single_trait(statement_use)',
        '$anonymous_member(statement_use)',
        '$anonymous_trait_use_count(statement*) = 1',
        '$anonymous_trait_use_count(statement_use :: statement_use :: eps) = 2',
        '$anonymous_class_node(NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE statement*) metadata_class)',
        '~$anonymous_class_node(NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE (statement_use :: statement_use :: eps)) metadata_class)',
        '~$anonymous_class_node(NStmtClass phpType14 phpType24 phpType3 ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata_class)',
        'S.ORIGIN = (PORIGIN 0 pcpath)',
        '$source_unit(S.SOURCES,0) = (pcunit)',
        '$compilation_projection(S,pcunit) = (ppinstalled)',
        '$class_at(ppinstalled.CLASSES,PORIGIN 0 (pcpath ++ [PCFIELD 0])) = (pclassdesc_raw)',
        '$class_at(S.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        'pclassdesc_live[.PROPERTIES = $trait_notice_own_properties(pclassdesc_live.PROPERTIES)][.CONSTANTS = $trait_notice_own_constants(pclassdesc_live.CONSTANTS)][.METHODS = $trait_notice_own_methods(pclassdesc_live.METHODS,pclassdesc_live.ORIGIN)] = pclassdesc_raw',
        '$anonymous_class_prefix(pcunit,' + term(filename) + ',ppinstalled.CLASSES,0)',
        'pclassdesc_live.NAME = $ptascii("Base166@anonymous") ++ [0] ++ ' + term(filename) + ' ++ [58] ++ $ntunsigned(pclassdesc_live.LINE) ++ [36,48]',
        'pclassdesc_live.LINE = 9',
        'pclassdesc_live.PARENT = ($ptascii("Base166"))',
        '$class_named(S.CLASSNAMES,$ptascii("base166")) = (porigin_base)',
        '$class_link_at(S.LINKEDPARENTS,pclassdesc_live.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_live.NAME)) = (pclassdesc_live.ORIGIN)',
        '$anonymous_runtime_declaration(S.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$declaration_history_valid(S)',
        '$anonymous_new_descriptor(S,PORIGIN 0 pcpath) = (pclassdesc_live)',
        '$anonymous_new_name(S,PORIGIN 0 pcpath) = (pclassdesc_live.NAME)',
        '$anonymous_new_pending(S,PORIGIN 0 pcpath) = eps',
        '$anonymous_new_available(S,pclassdesc_live)',
        'pclassdesc_live.METHODS = pmethoddesc_imported :: pmethoddesc_tail*',
        '$trait_imported_origin(pmethoddesc_imported.FUNCTION.ORIGIN)',
        'pclassdesc_forged = pclassdesc_live[.METHODS = pclassdesc_live.METHODS ++ [pmethoddesc_imported]]',
        'pclassdesc_forged[.PROPERTIES = $trait_notice_own_properties(pclassdesc_forged.PROPERTIES)][.CONSTANTS = $trait_notice_own_constants(pclassdesc_forged.CONSTANTS)][.METHODS = $trait_notice_own_methods(pclassdesc_forged.METHODS,pclassdesc_forged.ORIGIN)] = pclassdesc_raw',
        'S_forged = S[.CLASSES = $trait_class_set(S.CLASSES,pclassdesc_forged)]',
        '~$declaration_history_valid(S_forged)',
        '$anonymous_new_descriptor(S_forged,PORIGIN 0 pcpath) = eps',
        'S_one = $drive_steps(S[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.RESULT = KNOWN (POBJECT n_object)',
        'S_one.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        '(HOBJECT n_object) <- S_one.ALLOCATIONS',
        'S_one.EVENTS = S.EVENTS',
        '$class_state_valid(S_one[.COMPLETION = NORMAL])',
        '$heap_valid($heap_graph(S_one))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['id'] == CASE]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-trait-capture-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/383-anonymous-classes.watsup',
               CATALOGUE, source, Path(__file__), ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'case': CASE, 'source_sha256': row['source_sha256'],
              'inputs_before': before, 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        conditions = checks(checked['fixture'], os.fsencode(source))
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + condition + '\n' for condition in conditions))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(conditions), fixture_sha256=sha(fixture))
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
