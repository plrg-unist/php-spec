#!/usr/bin/env python3
"""Reached anonymous-owner factory classes and source-derived reservation checks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_owner_factory_cases.json'
SELECTED = ['owner-method-reuse-order', 'owner-nested-depth', 'owner-inherited-protected-ctor']
ABRUPT = 'owner-child-warning-before-later-static'
PREFIX = r'''
dec $owner180_output_one(pevent) : ptbytes
def $owner180_output_one(OUTPUT ptbytes) = ptbytes
def $owner180_output_one(pevent) = eps -- otherwise
dec $owner180_outputs(pevent*) : ptbytes
def $owner180_outputs(eps) = eps
def $owner180_outputs(pevent :: pevent_tail*) = $owner180_output_one(pevent) ++ $owner180_outputs(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def reached(row, fixture, filename):
    name = row['id']
    parented = name == SELECTED[2]
    nested = name == SELECTED[1]
    classes = '[pclassdesc_base,pclassdesc_owner,pclassdesc_child]' if parented else (
        '[pclassdesc_owner,pclassdesc_child,pclassdesc_grand,pclassdesc_after]' if nested else
        '[pclassdesc_owner,pclassdesc_child,pclassdesc_after]')
    count = 2 if parented else 4 if nested else 3
    out = ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
           r'S_start.COMPLETION = BUDGET /\ ~S_start.COMPILESTOP',
           '$source_unit(S_start.SOURCES,0) = (pcunit)',
           '$anonymous_unit(pcunit)',
           'S_start.CLASSES = ' + classes,
           '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',S_start.CLASSES,eps,eps,0) = (' + str(count) + ')',
           'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
           'pclassdesc_child.ORIGIN = PORIGIN 0 pcpath_child',
           '$origin_node(S_start.SOURCES,pclassdesc_owner.ORIGIN) = (pcnode_owner)',
           '$anonymous_owner_factory_node(pcnode_owner)',
           '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc_make)',
           'pmethoddesc_make.OWNER = pclassdesc_owner.ORIGIN',
           'pmethoddesc_make.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
           'pcpath_body = pcpath_method ++ [PCFIELD 6]',
           r'$(|pcpath_body| < |pcpath_child|)',
           'pcpath_child[0:|pcpath_body|] = pcpath_body',
           '$origin_node(S_start.SOURCES,pmethoddesc_make.FUNCTION.ORIGIN) = (pcnode_method)',
           '$anonymous_method_factory_node(pcnode_method)',
           '$class_state_valid(S_start) /\\ $declaration_history_valid(S_start)',
           'S_done = $drive_steps(S_start[.COMPLETION = NORMAL],8192)',
           r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
           '$owner180_outputs(S_done.EVENTS) = ' + term(base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)),
           r'$class_state_valid(S_done) /\ $property_state_valid(S_done)',
           r'$declaration_history_valid(S_done) /\ $heap_valid($heap_graph(S_done))']
    if parented:
        out += ['$anonymous_parent_class_name($ptascii("R180Base"),' + term(filename) + ',3,0) = (pclassdesc_owner.NAME)',
                '$anonymous_parent_class_name($ptascii("R180Base"),' + term(filename) + ',5,1) = (pclassdesc_child.NAME)',
                'pclassdesc_owner.PARENT = ($ptascii("R180Base"))',
                'pclassdesc_child.PARENT = ($ptascii("R180Base"))',
                '~pclassdesc_owner.EARLY /\\ ~pclassdesc_child.EARLY']
    else:
        child_line = 3
        out += ['$anonymous_class_name(' + term(filename) + ',2,0) = (pclassdesc_owner.NAME)',
                '$anonymous_class_name(' + term(filename) + ',' + str(child_line) + ',1) = (pclassdesc_child.NAME)',
                'pclassdesc_owner.EARLY /\\ pclassdesc_child.EARLY',
                'pcpath_new = pcpath_child[0:$nabs($(|pcpath_child| - 1))]',
                '$anonymous_new_descriptor(S_start,PORIGIN 0 pcpath_new) = (pclassdesc_child)']
        if nested:
            out += ['$anonymous_class_name(' + term(filename) + ',4,2) = (pclassdesc_grand.NAME)',
                    '$anonymous_class_name(' + term(filename) + ',7,3) = (pclassdesc_after.NAME)',
                    'pclassdesc_grand.EARLY /\\ pclassdesc_after.EARLY']
        else:
            out += ['$anonymous_class_name(' + term(filename) + ',5,2) = (pclassdesc_after.NAME)',
                    'pclassdesc_after.EARLY']
    return out


def reservation(fixture, filename):
    return ['P_complete = $ppstart(0,' + fixture + ',' + term(filename) + ')',
            r'P_complete.COMPLETION = PPCNORMAL /\ $ppimage_unit(P_complete)',
            'P_complete.CLASSES = [pclassdesc_owner,pclassdesc_child,pclassdesc_after]',
            '$source_unit([P_complete.FOLD.SOURCE],0) = (pcunit)',
            'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
            '$origin_node([pcunit],pclassdesc_owner.ORIGIN) = (NStmtClass (SEQUENCE eps) (INTEGER flags) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata)',
            '$pchlower(NStmtClass (SEQUENCE eps) (INTEGER flags) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata) = PCHRAW pchraw',
            'pchheader = { KIND "class", NAME pclassdesc_owner.NAME, ABSTRACT false, FINAL false, READONLY pclassdesc_owner.READONLY, PARENT eps, INTERFACES eps, BODY pchraw.BODY }',
            'P_before = P_complete[.CLASSES = eps][.EARLY = (pcpath_owner)][.LOCATION = P_complete.LOCATION[.PATH = pcpath_owner][.LINE = pclassdesc_owner.LINE]]',
            '$anonymous_owner_factory_header(P_before,pcpath_owner,pchheader)',
            'P_reserved = $anonymous_owner_reserve(P_before,pcpath_owner,pchheader)',
            'P_reserved.CLASSES = [pclassdesc_provisional]',
            'pclassdesc_provisional.ORIGIN = pclassdesc_owner.ORIGIN',
            'pclassdesc_provisional.NAME = pclassdesc_owner.NAME',
            'pclassdesc_provisional.METHODS = eps /\\ pclassdesc_provisional.PROPERTIES = eps',
            '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',P_reserved.CLASSES,eps,eps,0) = (1)',
            'P_finished = $anonymous_owner_finish(P_reserved,pcpath_owner,pchheader,pclassdesc_owner.PROPERTIES,pclassdesc_owner.METHODS)',
            'P_finished.CLASSES = [pclassdesc_owner]',
            '~$anonymous_owner_factory_header(P_before[.EARLY = eps],pcpath_owner,pchheader)',
            '~$anonymous_owner_factory_header(P_before[.LOCATION = P_before.LOCATION[.LINE = 999]],pcpath_owner,pchheader)']


def abrupt(fixture, filename):
    message = '$ptascii("Method class@anonymous::__construct() cannot be static")'
    return ['P = $ppstart(0,' + fixture + ',' + term(filename) + ')',
            'P.COMPLETION = PPCABRUPT (STATICBYTES ' + message + ' 4)',
            'P.CLASSES = [pclassdesc_owner,pclassdesc_child]',
            'P.INSTALLED.CLASSES = eps',
            'P.PUBLICATIONS = [PPCP porigin_published 1 PPCLASS]',
            'porigin_published = pclassdesc_child.ORIGIN',
            '|P.DIAGNOSTICS| = 1',
            '$anonymous_failed_owner_child_checkpoint(P,pclassdesc_child.ORIGIN)',
            '~$anonymous_failed_owner_child_checkpoint(P,pclassdesc_owner.ORIGIN)',
            'P_installed = P[.INSTALLED = P.INSTALLED[.CLASSES = [pclassdesc_child]]]',
            '~$anonymous_failed_owner_child_checkpoint(P_installed,pclassdesc_child.ORIGIN)',
            'S = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            'S.COMPLETION = STATICBYTES ' + message + ' 4',
            'S.CLASSNAMES = eps']


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
    raw = Path(tempfile.mkdtemp(prefix='class180-protocol-', dir=ROOT / '.tools'))
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
        code, groups, counts = PREFIX, [], {}
        for index, name in enumerate(SELECTED):
            row = rows[name]
            source = raw / (name + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            conditions = reached(row, checked['fixture'], os.fsencode(source))
            group = '$owner180_group' + str(index)
            code += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in conditions)
            groups.append(group + '()')
            counts[name] = len(conditions)
            if index == 0:
                conditions = reservation(checked['fixture'], os.fsencode(source))
                code += 'dec $owner180_reservation() : bool\ndef $owner180_reservation() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in conditions)
                groups.append('$owner180_reservation()')
                counts['source_derived_reservation'] = len(conditions)
        row = rows[ABRUPT]
        source = raw / (ABRUPT + '.php')
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256']
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        conditions = abrupt(checked['fixture'], os.fsencode(source))
        code += 'dec $owner180_abrupt() : bool\ndef $owner180_abrupt() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in conditions)
        groups.append('$owner180_abrupt()')
        counts[ABRUPT + '_replay'] = len(conditions)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + r' /\ '.join(groups) + '\n')
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 600, ROOT)
        report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), conditions=counts, fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter: adapter.close()
        finally:
            if frontend: frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and before == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
