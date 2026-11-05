#!/usr/bin/env python3
"""Reached owner Stringable descriptors and source-derived provisional reservation."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_owner_stringable_cases.json'
SELECTED = ['owner-stringable-after-method', 'parented-owner-stringable',
            'nested-stringable-owners']
ABRUPT = 'owner-stringable-invalid-return-after-child'
PREFIX = r'''
dec $owner181_output_one(pevent) : ptbytes
def $owner181_output_one(OUTPUT ptbytes) = ptbytes
def $owner181_output_one(pevent) = eps -- otherwise
dec $owner181_outputs(pevent*) : ptbytes
def $owner181_outputs(eps) = eps
def $owner181_outputs(pevent :: pevent_tail*) = $owner181_output_one(pevent) ++ $owner181_outputs(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def normal(row, fixture, filename):
    name = row['id']
    parented = name == SELECTED[1]
    nested = name == SELECTED[2]
    classes = ('[pclassdesc_base,pclassdesc_owner,pclassdesc_child,pclassdesc_after]' if parented else
               '[pclassdesc_owner,pclassdesc_child,pclassdesc_grand,pclassdesc_after]' if nested else
               '[pclassdesc_owner,pclassdesc_child,pclassdesc_after]')
    count = 4 if nested else 3
    result = ['P = $ppstart(0,' + fixture + ',' + term(filename) + ')',
              'P.COMPLETION = PPCNORMAL /\\ $ppimage_unit(P)',
              '$anonymous_unit(P.FOLD.SOURCE)',
              'P.CLASSES = ' + classes,
              '$anonymous_compiled_class_count(P.FOLD.SOURCE,' + term(filename) + ',P.CLASSES,eps,eps,0) = (' + str(count) + ')',
              'pclassdesc_owner.INTERFACES = [$ptascii("Stringable")] /\\ ~pclassdesc_owner.EARLY',
              '$ppmethod_at(pclassdesc_owner.METHODS,$ptascii("__toString"))',
              '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc_make)',
              'pmethoddesc_make.OWNER = pclassdesc_owner.ORIGIN',
              '$anonymous_class_name(' + term(filename) + ',pclassdesc_child.LINE,1) = (pclassdesc_child.NAME)',
              'S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
              'S_start.COMPLETION = BUDGET /\\ ~S_start.COMPILESTOP',
              '$class_state_valid(S_start) /\\ $declaration_history_valid(S_start)',
              'S_done = $drive_steps(S_start[.COMPLETION = NORMAL],8192)',
              'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
              '$owner181_outputs(S_done.EVENTS) = ' + term(base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)),
              '$class_state_valid(S_done) /\\ $property_state_valid(S_done)',
              '$declaration_history_valid(S_done) /\\ $heap_valid($heap_graph(S_done))']
    if parented:
        result += ['pclassdesc_owner.PARENT = ($ptascii("R181Base"))',
                   '$anonymous_parent_class_name($ptascii("R181Base"),' + term(filename) + ',pclassdesc_owner.LINE,0) = (pclassdesc_owner.NAME)']
    else:
        result += ['$anonymous_class_name(' + term(filename) + ',pclassdesc_owner.LINE,0) = (pclassdesc_owner.NAME)']
    if name == SELECTED[0]:
        result += ['$class_at(P.INSTALLED.CLASSES,pclassdesc_owner.ORIGIN) = (pclassdesc_owner)',
                   '$class_at(P.INSTALLED.CLASSES,pclassdesc_child.ORIGIN) = (pclassdesc_child)']
    if nested:
        result += ['pclassdesc_child.INTERFACES = [$ptascii("Stringable")] /\\ ~pclassdesc_child.EARLY',
                   '$ppmethod_at(pclassdesc_child.METHODS,$ptascii("__toString"))',
                   '$anonymous_class_name(' + term(filename) + ',pclassdesc_grand.LINE,2) = (pclassdesc_grand.NAME)',
                   '$anonymous_class_name(' + term(filename) + ',pclassdesc_after.LINE,3) = (pclassdesc_after.NAME)']
    else:
        result += ['$anonymous_class_name(' + term(filename) + ',pclassdesc_after.LINE,2) = (pclassdesc_after.NAME)']
    return result


def reservation(fixture, filename):
    return ['P_complete = $ppstart(0,' + fixture + ',' + term(filename) + ')',
            'P_complete.COMPLETION = PPCNORMAL',
            'P_complete.CLASSES = [pclassdesc_owner,pclassdesc_child,pclassdesc_after]',
            'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
            '$origin_node([P_complete.FOLD.SOURCE],pclassdesc_owner.ORIGIN) = (NStmtClass (SEQUENCE eps) (INTEGER flags) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata)',
            '$pchlower(NStmtClass (SEQUENCE eps) (INTEGER flags) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata) = PCHRAW pchraw',
            'pchheader = { KIND "class", NAME pclassdesc_owner.NAME, ABSTRACT false, FINAL false, READONLY pclassdesc_owner.READONLY, PARENT eps, INTERFACES eps, BODY pchraw.BODY }',
            'P_before = P_complete[.CLASSES = eps][.EARLY = (pcpath_owner)][.LOCATION = P_complete.LOCATION[.PATH = pcpath_owner][.LINE = pclassdesc_owner.LINE]]',
            '$anonymous_owner_factory_header(P_before,pcpath_owner,pchheader)',
            'P_reserved = $anonymous_owner_reserve(P_before,pcpath_owner,pchheader)',
            'P_reserved.CLASSES = [pclassdesc_provisional]',
            'pclassdesc_provisional.METHODS = eps /\\ pclassdesc_provisional.PROPERTIES = eps',
            'pclassdesc_provisional.INTERFACES = eps /\\ pclassdesc_provisional.EARLY',
            '$anonymous_compiled_class_count(P_complete.FOLD.SOURCE,' + term(filename) + ',P_reserved.CLASSES,eps,eps,0) = (1)',
            'P_finished = $anonymous_owner_finish(P_reserved,pcpath_owner,pchheader,pclassdesc_owner.PROPERTIES,pclassdesc_owner.METHODS)',
            'P_finished.CLASSES = [pclassdesc_owner]',
            'pclassdesc_owner.INTERFACES = [$ptascii("Stringable")] /\\ ~pclassdesc_owner.EARLY']


def abrupt(fixture, filename):
    message = '$ptascii("class@anonymous::__toString(): Return type must be string when declared")'
    return ['P = $ppstart(0,' + fixture + ',' + term(filename) + ')',
            'P.COMPLETION = PPCABRUPT (STATICBYTES ' + message + ' 4)',
            'P.CLASSES = [pclassdesc_owner,pclassdesc_child]',
            'pclassdesc_owner.INTERFACES = eps /\\ pclassdesc_owner.METHODS = eps',
            'P.INSTALLED.CLASSES = eps',
            'P.PUBLICATIONS = [PPCP porigin_child 0 PPCLASS]',
            'porigin_child = pclassdesc_child.ORIGIN',
            'P.DIAGNOSTICS = eps',
            '$anonymous_failed_owner_child_checkpoint(P,pclassdesc_child.ORIGIN)',
            '~$anonymous_failed_owner_child_checkpoint(P,pclassdesc_owner.ORIGIN)',
            'S = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            'S.COMPLETION = STATICBYTES ' + message + ' 4',
            'S.CLASSNAMES = eps']


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
    raw = Path(tempfile.mkdtemp(prefix='class181-protocol-', dir=ROOT / '.tools'))
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
        for index, name in enumerate([*SELECTED, ABRUPT]):
            row = rows[name]
            source = raw / (name + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            checks = abrupt(checked['fixture'], os.fsencode(source)) if name == ABRUPT else normal(row, checked['fixture'], os.fsencode(source))
            if index == 0:
                extra = reservation(checked['fixture'], os.fsencode(source))
                code += 'dec $owner181_reservation() : bool\ndef $owner181_reservation() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in extra)
                groups.append('$owner181_reservation()')
                counts['source_derived_reservation'] = len(extra)
            group = '$owner181_group' + str(index)
            code += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in checks)
            groups.append(group + '()')
            counts[name] = len(checks)
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
