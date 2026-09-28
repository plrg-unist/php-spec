#!/usr/bin/env python3
"""Private slot identity across lexical scopes, saved calls and cloned aliases."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {'external-clone-alias': '<?php class A{private int $x=1;function &ref(){return $this->x;}}class B extends '
                         'A{private string $x="b";}$b=new B;$r=&$b->ref();$c=clone $b;$r="bad";\n',
 'own-private-shadow': '<?php function hold(){}class A{private int $x=1;}class B extends A{private string '
                       '$x="b";}$a=new B;hold();\n',
 'saved-foreach': '<?php function hold(){}class A{private int $x=1;function go(){foreach($this as '
                  '&$v){hold();$v++;}}}class B extends A{}$a=new B;$a->x=7;$a->go();$p=(array)$a;echo '
                  '$p["\\0A\\0x"],$a->x;\n',
 'static-closure': '<?php class A{private $x=4;function make(){return static function($o){return '
                   '$o->x;};}}class B extends A{public $x=9;}$a=new B;$f=$a->make();echo $f($a);\n'}
PREFIX = '\ndec $scope_stage(pstate) : bool\ndef $scope_stage(S) = true -- if STAGE\ndef $scope_stage(S) = false -- otherwise\ndec $scope_seek(pstate,nat) : pstate\ndef $scope_seek(S,n) = S -- if $scope_stage(S)\ndef $scope_seek(S,n) = $scope_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))\n  -- if ~$scope_stage(S) -- if $(n > 0)\ndec $scope_outputs(pevent*) : nat*\ndef $scope_outputs(eps) = eps\ndef $scope_outputs((OUTPUT n*) :: pevent*) = n* ++ $scope_outputs(pevent*)\ndef $scope_outputs((WARNING n* z) :: pevent*) = $scope_outputs(pevent*)\ndef $scope_outputs((DIAGNOSTIC text n* z) :: pevent*) = $scope_outputs(pevent*)\n'
CASES = {'external-clone-alias': ('S.CURRENT = eps -- if $lookup(S.ENV,$ptascii("c")) = (n_clonecell) -- if '
                          'S.STORE[n_clonecell] = DEFINED (POBJECT n_clone) -- if '
                          '$lookup(S.ENV,$ptascii("r")) = (n_cell) -- if $propref_at(S.PROPREFS,n_cell) = '
                          '(ppropref)',
                          ['$lookup(S.ENV,$ptascii("r")) = (n_cell)',
                           'S.PROPREFS = [ppropref]',
                           'ppropref.SOURCES = [pproptypesource,pproptypesource_clone]',
                           'pproptypesource_clone.NAME = [0,65,0,120]',
                           'pproptypesource_clone.DECL = pproptypesource.DECL',
                           'pproptypesource_clone.OBJECT = n_clone',
                           'n_clone =/= pproptypesource.OBJECT',
                           '$propref_descriptor(S,pproptypesource_clone) = (ppropertydesc)',
                           'ppropref.CELL = n_cell',
                           'pproptypesource.OBJECT = n_object',
                           'pproptypesource.NAME = [0,65,0,120]',
                           '$propref_descriptor(S,pproptypesource) = (ppropertydesc)',
                           'ppropertydesc.NAME = [120]',
                           'ppropertydesc.KEY = [0,65,0,120]',
                           '$property_resolve(S,n_object,[120]) = PROPERTY_DENIED ppropertydesc_denied',
                           '$property_resolve(S,n_object,[0,65,0,120]) = PROPERTY_BADNAME',
                           '$property_quiet(S,POBJECT n_object,[120],1).RESULT = KNOWN PNULL',
                           '~$proprefs_valid(S[.PROPREFS = [ppropref[.SOURCES = [pproptypesource[.NAME = '
                           '[120]],pproptypesource_clone]]]])',
                           'S_written = $location_write(S,PROPERTY n_object ([0,65,0,120]),PINT 9)',
                           'S_written.COMPLETION = NORMAL',
                           'S_written.STORE[n_cell] = DEFINED (PINT 9)',
                           '$proprefs_valid(S_written)',
                           'S_done.STORE[n_cell] = DEFINED (PINT 1)',
                           'S_done.COMPLETION = UNCAUGHT n_uncaught_s_done',
                           'S_done.OBJECTS[n_uncaught_s_done] = THROWABLE pthrowable_s_done',
                           'pthrowable_s_done.KIND = "TypeError"',
                           'pthrowable_s_done.MESSAGE = PSTRING $ptascii("Cannot assign string to reference '
                           'held by property A::$x of type int")',
                           'pthrowable_s_done.LINE = 1',
                           'S_done.TRACE = pthrowable_s_done.TRACE',
                           'S_done.ERRORORIGIN = pthrowable_s_done.ORIGIN',
                           '$heap_valid($heap_graph(S_done))',
                           '$($heap_owners($heap_graph(S_done), HOBJECT n_uncaught_s_done) > 0)',
                           'ppropertydesc_denied.KEY = [0,66,0,120]',
                           '$typed_reference_location_source(S,PROPERTY n_object ([0,65,0,120]))',
                           '$typed_reference_location_source(S,PROPERTY n_clone ([0,65,0,120]))']),
 'own-private-shadow': ('S.CURRENT = eps -- if $lookup(S.ENV,$ptascii("a")) = (n_cell) -- if S.STORE[n_cell] '
                        '= DEFINED (POBJECT n_object)',
                        ['S.OBJECTPROPS = [pobjectprops]',
                         'pobjectprops.OBJECT = n_object',
                         'S.OBJECTS[n_object] = INSTANCE porigin_runtime',
                         'pobjectprops.SLOTS = [ppropertyslot_a,ppropertyslot_b]',
                         'ppropertyslot_a.NAME = [0,65,0,120]',
                         'ppropertyslot_b.NAME = [0,66,0,120]',
                         'ppropertyslot_a.DECL =/= ppropertyslot_b.DECL',
                         '~$property_dynamic_name_allowed(S,porigin_runtime,[120])',
                         '$property_resolve(S,n_object,[120]) = PROPERTY_DENIED ppropertydesc',
                         'ppropertydesc.KEY = ppropertyslot_b.NAME',
                         '~$property_dynamic_no_shadow(S,porigin_runtime,pobjectprops.SLOTS ++ '
                         '[ppropertyslot_b[.NAME = [120]][.DECL = eps]])',
                         '~$objectprops_valid(S,[pobjectprops[.SLOTS = [ppropertyslot_a[.NAME = '
                         'ppropertyslot_b.NAME],ppropertyslot_b]]])',
                         '$property_resolve(S,n_object,[0,65,0,120]) = PROPERTY_BADNAME',
                         'S_done.COMPLETION = NORMAL']),
 'saved-foreach': ('S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("hold")',
                   ['S.FRAMES = pframe :: pframe_tail*',
                    'pframe.CONTEXT = (pcallcontext_saved)',
                    'S.ITERATORS = [OBJECTITER n_iterator n_object n_cursor true]',
                    'S.PROPREFS = [ppropref]',
                    'ppropref.SOURCES = [pproptypesource]',
                    'pproptypesource.OBJECT = n_object',
                    'pproptypesource.NAME = [0,65,0,120]',
                    '$property_resolve(S,n_object,[120]) = PROPERTY_ACCESS ([120])',
                    '$property_resolve(S[.CURRENT = pframe.CONTEXT],n_object,[120]) = PROPERTY_ACCESS '
                    '([0,65,0,120])',
                    '$call_saved_context_valid(S,pframe)',
                    '~$call_saved_context_valid(S,pframe[.CONTEXT = (pcallcontext_saved[.LEXICAL_CLASS = '
                    'eps])])',
                    '$($heap_owners($heap_graph(S),HOBJECT n_object) > 0)',
                    '$($heap_owners($heap_graph(S),HCELL ppropref.CELL) > 0)',
                    'S_done.COMPLETION = NORMAL',
                    '$scope_outputs(S_done.EVENTS) = [50,55]',
                    'S_done.ITERATORS = eps',
                    '$property_visible_key(S,n_object,[120])',
                    '~$property_visible_key(S[.CURRENT = pframe.CONTEXT],n_object,[120])',
                    '$property_visible_key(S[.CURRENT = pframe.CONTEXT],n_object,[0,65,0,120])',
                    'S.OBJECTS[n_object] = INSTANCE porigin_runtime',
                    '$property_dynamic_name_allowed(S,porigin_runtime,[120])']),
 'static-closure': ('S.CURRENT = (pcallcontext) -- if pcallcontext.LEXICAL_CLASS =/= eps -- if '
                    'pcallcontext.RECEIVER = eps',
                    ['S.CURRENT = (pcallcontext)',
                     'S.OBJECTPROPS = [pobjectprops]',
                     'pobjectprops.OBJECT = n_object',
                     '$property_resolve(S,n_object,[120]) = PROPERTY_ACCESS ([0,65,0,120])',
                     '$property_resolve(S[.CURRENT = eps],n_object,[120]) = PROPERTY_ACCESS ([120])',
                     '~$call_current_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])])',
                     '~$call_current_valid(S[.CURRENT = (pcallcontext[.RECEIVER = (n_object)])])',
                     'S_done.COMPLETION = NORMAL',
                     '$scope_outputs(S_done.EVENTS) = [52]',
                     '$property_visible_key(S,n_object,[0,65,0,120])',
                     '~$property_visible_key(S,n_object,[120])',
                     '$property_visible_key(S[.CURRENT = eps],n_object,[120])',
                     '~$property_visible_key(S[.CURRENT = eps],n_object,[0,65,0,120])'])}

def run():
    out = Path(tempfile.mkdtemp(prefix='private-property-scope-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = modules + [ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json',
        'frontend/worker.php', 'frontend/FileLexer.php', 'frontend/target.php',
        'tests/semantics/_build/default/numeric_runner.exe', '_build/default/adapter/main.exe',
        '.tools/php/bin/php', '.tools/php-file.so', 'tests/semantics/recorded_worker.py')] + [Path(__file__)]
    def hashes():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    before = hashes()
    rows = []
    for name, (stage, checks) in CASES.items():
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(SOURCES[name])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
        finally:
            try:
                frontend.close()
            finally:
                adapter.close()
        initial = '$php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')'
        common = ['S_initial = ' + initial,
                  'S = $scope_seek(S_initial[.COMPLETION = NORMAL],2000)[.COMPLETION = NORMAL]',
                  '$class_state_valid(S)', '$call_descriptors_valid(S)', '$property_state_valid(S)',
                  '$heap_valid($heap_graph(S))', 'S_done = $drive(S,2000)',
                  'S_done = $drive(S_initial[.COMPLETION = NORMAL],2000)',
                  '$heap_valid($heap_graph(S_done))', 'S_done.FRAMES = eps', 'S_done.TODO = eps']
        fixture = directory / 'fixture.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + check + '\n' for check in common + checks))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, modules), str(fixture)], capture_output=True, timeout=300)
        (directory / 'stdout').write_bytes(result.stdout)
        (directory / 'stderr').write_bytes(result.stderr)
        row = {'name': name, 'assertions': len(common + checks),
               'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'pass': result.returncode == 0 and result.stdout == b'true\n' and not result.stderr}
        rows.append(row)
        print(row, flush=True)
        if not row['pass']:
            print(result.stderr.decode()[-2500:], flush=True)
    stable = before == hashes()
    passed = stable and all(row['pass'] for row in rows)
    (out / 'report.json').write_text(json.dumps({'result': 'pass' if passed else 'fail', 'stable': stable,
        'rows': rows, 'inputs': before}, indent=2) + '\n')
    print(out, flush=True)
    assert passed, 'private scope protocol failed'


if __name__ == '__main__':
    run()
