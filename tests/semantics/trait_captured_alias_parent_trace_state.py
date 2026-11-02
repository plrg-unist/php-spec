#!/usr/bin/env python3
"""Reach the two failed copied-alias trace scopes from their PHP originals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/trait_captured_alias_parent_cases.json'
CASES = (
    ('failed-first-alias-parent-shutdown', 'U', 'BaseA165Failure', b'PRE;SHUT;A:'),
    ('failed-first-post-fixup-alias-parent-shutdown', 'C', 'BaseB165Fixed',
     b'PRE;SHUT;A:T:C:E;B:'),
)
PREFIX = r'''
dec $tc165_stage(pstate,ptbytes,ptbytes) : bool
def $tc165_stage(S,ptbytes_lexical,ptbytes_argument) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $closure_scope_at(S.CLOSURESCOPES,n) = (pclosurescope)
  -- if $class_at(S.CLASSES,pclosurescope.LEXICAL) = (pclassdesc_lexical)
  -- if pclassdesc_lexical.NAME = ptbytes_lexical
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if pfunction.SIGNATURE.PARAMETERS = [psparam]
  -- if $lookup(S.ENV,psparam.NAME) = (n_value)
  -- if S.STORE[n_value] = DEFINED (POBJECT n_argument)
  -- if S.OBJECTS[n_argument] = INSTANCE porigin_argument
  -- if $class_at(S.CLASSES,porigin_argument) = (pclassdesc_argument)
  -- if pclassdesc_argument.NAME = ptbytes_argument
def $tc165_stage(S,ptbytes_lexical,ptbytes_argument) = false -- otherwise
dec $tc165_seek(pstate,ptbytes,ptbytes,nat) : pstate
def $tc165_seek(S,ptbytes_lexical,ptbytes_argument,n) = S
  -- if $tc165_stage(S,ptbytes_lexical,ptbytes_argument)
def $tc165_seek(S,ptbytes_lexical,ptbytes_argument,0) = S
  -- if ~$tc165_stage(S,ptbytes_lexical,ptbytes_argument)
def $tc165_seek(S,ptbytes_lexical,ptbytes_argument,n) = $tc165_seek(S_next,ptbytes_lexical,ptbytes_argument,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$tc165_stage(S,ptbytes_lexical,ptbytes_argument)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $tc165_seek(S,ptbytes_lexical,ptbytes_argument,n) = S -- otherwise
dec $tc165_output_item(pevent) : ptbytes
def $tc165_output_item(OUTPUT ptbytes) = ptbytes
def $tc165_output_item(pevent) = eps -- otherwise
dec $tc165_output(pevent*) : ptbytes
def $tc165_output(eps) = eps
def $tc165_output(pevent :: pevent_tail*) = $tc165_output_item(pevent) ++ $tc165_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quoted(text):
    return '$ptascii(' + json.dumps(text) + ')'


def checks(fixture, filename, lexical, argument, output):
    lexical_name = quoted(lexical)
    return [
        'S_initial = $php_run(' + fixture + ',0,' +
        json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_raw = $tc165_seek(S_initial[.COMPLETION = NORMAL],' + lexical_name +
        ',' + quoted(argument) + ',16384)',
        r'S_raw.COMPLETION = NORMAL \/ S_raw.COMPLETION = BUDGET',
        'S = S_raw[.COMPLETION = NORMAL]',
        '$tc165_stage(S,' + lexical_name + ',' + quoted(argument) + ')',
        'S.TODO = [TYPE_RECEIVE porigin 0]',
        'S.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n',
        'pcallcontext.INSTANCE = (n)',
        'pcallcontext.FUNCTION = porigin_method',
        'pcallcontext.NAME = ' + quoted('C::q'),
        '$object_body(S.OBJECTS[n]) = METHODCLOSURE porigin_method porigin_site porigin_owner eps',
        '$class_method_origin(S.CLASSES,porigin_method) = eps',
        '$closure_method_origin(S,porigin_method) = (pmethoddesc)',
        'pmethoddesc.NAME = ' + quoted('q'),
        'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$closure_scope_at(S.CLOSURESCOPES,n) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_lexical',
        '$class_at(S.CLASSES,porigin_lexical) = (pclassdesc_lexical)',
        'pclassdesc_lexical.NAME = ' + lexical_name,
        '$class_at(S.CLASSES,pclosurescope.CALLED) = (pclassdesc_called)',
        'pclassdesc_called.NAME = ' + quoted('E'),
        '$trait_fcc_failed_header(S,porigin_site) = ((pconstantclosure,porigin_first,pmethoddesc_first))',
        '$trait_fcc_scope_owner(S,pmethoddesc,porigin_site,porigin_owner,pclosurescope) = (porigin_owner)',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$trace_context_function(S,pcallcontext) = ' + quoted('q'),
        '$trace_context_class(S,pcallcontext) = (' + lexical_name + ')',
        '$trace_context_type(S,pcallcontext) = (' + quoted('::') + ')',
        '$trace_context(S,S.ENV,(pcallcontext)) = ptraceframe :: ptraceframe_tail*',
        'ptraceframe.FUNCTION = ' + quoted('q'),
        'ptraceframe.CLASS = (' + lexical_name + ')',
        'ptraceframe.TYPE = (' + quoted('::') + ')',
        '$trace_context_function(S,pcallcontext[.INSTANCE = eps]) = pcallcontext.NAME',
        '$tc165_output(S.EVENTS) = $base64(' +
        json.dumps(base64.b64encode(output).decode()) + ')',
        'S_next = $drive_steps(S,1)',
        '$tc165_output(S_next.EVENTS) = $tc165_output(S.EVENTS)',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    data = json.loads(CATALOGUE.read_text())
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    for case, lexical, argument, output in CASES:
        row, = [r for r in data['cases'] if r['id'] == case]
        raw = Path(tempfile.mkdtemp(prefix='trait-captured-alias-parent-trace-',
                                    dir=ROOT / '.tools'))
        source = raw / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256']
        watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE,
                   source, Path(__file__), ROOT / '_build/default/adapter/main.exe',
                   ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
        before = {str(path): sha(path) for path in watched}
        report = {'passed': False, 'case': case, 'source_sha256': row['source_sha256'],
                  'inputs_before': before, 'raw': str(raw)}
        frontend = adapter = None
        try:
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                               '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], raw / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                             raw / 'adapter')
            parsed = frontend.request({'op': 'parse',
                                       'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            conditions = checks(checked['fixture'], os.fsencode(source), lexical,
                                argument, output)
            fixture = raw / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + condition + '\n'
                                       for condition in conditions))
            result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                           '--sl', *map(str, modules), str(fixture)],
                                          raw / 'numeric', 1200, ROOT)
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
