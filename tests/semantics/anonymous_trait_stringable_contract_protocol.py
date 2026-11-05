#!/usr/bin/env python3
"""Source-reached imported Stringable contract failures before allocation."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from anonymous_trait_adaptations_protocol import PREFIX

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_trait_stringable_cases.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def checks(row, fixture, filename):
    stderr = base64.b64decode(row['stderr_template_base64'])
    message = stderr.split(b'Fatal error: ', 1)[1].split(b' in {FILE} on line 2', 1)[0]
    conditions = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_pre = $class169_seek(S_initial,0,100)',
        'S_pre.COMPLETION = BUDGET /\\ $class169_front(S_pre,0)',
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        'pclassdesc_raw.INTERFACES = eps /\\ ~pclassdesc_raw.EARLY',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        'S_pre.OBJECTS = eps',
        'S_pre.ERRORORIGIN = eps',
        'S_pre.EVENTS = [OUTPUT $ptascii("before;")]',
        '$trait_plan(S_pre,pclassdesc_raw) = ptraitplan',
        '$trait_fetch(S_pre,ptraitplan.TRAITS,eps) = TRAITFETCHED pclassdesc_traits*',
        '$trait_aliases(S_pre,pclassdesc_raw,pclassdesc_traits*,ptraitplan.ALIASES,eps) = TRAITALIASES ptraitalias*',
        '$trait_copy_traits(pclassdesc_raw,pclassdesc_traits*,ptraitalias*,eps,TRAITCOMPOSE S_pre[.COMPLETION = NORMAL] eps eps) = TRAITCOMPOSE S_copy ptraitmethod* ptraitmethod_required*',
        'S_copy.COMPLETION = NORMAL',
        'pmethoddesc_items* = $trait_composed_methods(ptraitmethod*)',
        '$method_named(pmethoddesc_items*,$ptascii("__toString")) = (pmethoddesc_alias)',
        'pmethoddesc_alias.OWNER = pclassdesc_raw.ORIGIN',
        'pmethoddesc_alias.FUNCTION.ORIGIN = TRAIT_ORIGIN pclassdesc_raw.ORIGIN porigin_source $ptascii("__toString")',
        '$origin_node(S_pre.SOURCES,porigin_source) = (NStmtClassMethod phpType14 phpType24 phpType4 (NIdentifier (BYTES text_method) metadata_name) phpType16 phpType18 phpType47 metadata_method)',
        '$base64(text_method) = $ptascii("render")',
        'pmethoddesc_alias.FUNCTION.LINE = 2',
        'pmethoddesc_all* = pclassdesc_raw.METHODS ++ pmethoddesc_items*',
        'pclassdesc_candidate = pclassdesc_raw[.METHODS = pmethoddesc_all*][.INTERFACES = $trait_import_interfaces(pclassdesc_raw,pmethoddesc_all*)]',
        'pclassdesc_candidate.INTERFACES = [$ptascii("Stringable")]',
        '$pil_internal_source_one(S_copy,pclassdesc_candidate,pmethoddesc_alias) = METHOD_FILEISSUE ' + term(message) + ' 2 pmethoddesc_alias.FUNCTION.ORIGIN',
        'S_fatal = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
        'S_fatal.COMPLETION = STATICBYTES ' + term(message) + ' 2',
        'S_fatal.ERRORORIGIN = S_pre.ERRORORIGIN',
        'S_fatal.EVENTS = S_pre.EVENTS',
        'S_fatal.OBJECTS = eps',
        '$class_named(S_fatal.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_fatal.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        '$class_at(S_fatal.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_raw)',
        '$class_link_at(S_fatal.LINKEDPARENTS,pclassdesc_raw.ORIGIN) = eps',
        '$pil_at(S_fatal.LINKEDINTERFACES,pclassdesc_raw.ORIGIN) = eps',
    ]
    if row['id'] == 'aliased-stringable-static-conflict':
        conditions += ['pmethoddesc_alias.STATIC', 'pmethoddesc_alias.VISIBILITY = PROPERTY_PUBLIC']
    elif row['id'] == 'aliased-stringable-private-conflict':
        conditions += ['~pmethoddesc_alias.STATIC', 'pmethoddesc_alias.VISIBILITY = PROPERTY_PRIVATE']
    else:
        conditions += ['~pmethoddesc_alias.STATIC', 'pmethoddesc_alias.VISIBILITY = PROPERTY_PUBLIC',
                       'pmethoddesc_alias.FUNCTION.SIGNATURE.RETURNS = ([(PTBRANCH ([PTBUILTIN "int"]))])']
    return conditions


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    cases = json.loads(CATALOGUE.read_text())['cases']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    for row in [row for row in cases if row['id'].endswith('-conflict')]:
        raw = Path(tempfile.mkdtemp(prefix='anonymous-trait-stringable-contract-', dir=ROOT / '.tools'))
        source = raw / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256']
        watched = [ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/383-anonymous-classes.watsup',
                   ROOT / 'spec/semantics/189-internal-interface-prototypes.watsup',
                   ROOT / 'tests/semantics/anonymous_trait_adaptations_protocol.py',
                   CATALOGUE, source, Path(__file__), ROOT / '_build/default/adapter/main.exe',
                   ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
        before = {str(path): sha(path) for path in watched}
        report = {'passed': False, 'case': row['id'], 'source_sha256': row['source_sha256'],
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
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            fixture = raw / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + condition + '\n' for condition in conditions))
            result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                           '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
            report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                          stderr=result.stderr.decode(errors='replace'),
                          conditions=len(conditions), fixture_sha256=sha(fixture))
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
