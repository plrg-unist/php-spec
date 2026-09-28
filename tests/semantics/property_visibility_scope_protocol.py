#!/usr/bin/env python3
"""Protected slot identity across lexical scopes, saved calls and reference binding."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
from recorded_worker import Worker
from throwable_test_support import uncaught_assertions

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'external-alias': '<?php class A{protected int $x=1;function &ref(){return $this->x;}}class B extends A{}$b=new B;$r=&$b->ref();$r="bad";\n',
    'static-closure': '<?php class A{protected $x=4;function make(){return static function($o){return $o->x;};}}$a=new A;$f=$a->make();echo $f($a);\n',
    'saved-foreach': '<?php function hold(){}class A{protected int $x=1;function go(){foreach($this as &$v){hold();$v++;}}}$a=new A;$a->go();$p=(array)$a;echo $p["\\0*\\0x"];\n',
    'binding-atomicity': '<?php class A{public string $x="3";public string $y="4";public int $z=1;}$a=new A;$old=&$a->z;$r=&$a->x;$a->y=&$r;$a->x=&$r;$a->z=&$r;\n',
}
PREFIX = '''
dec $scope_stage(pstate) : bool
def $scope_stage(S) = true -- if STAGE
def $scope_stage(S) = false -- otherwise
dec $scope_seek(pstate,nat) : pstate
def $scope_seek(S,n) = S -- if $scope_stage(S)
def $scope_seek(S,n) = $scope_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$scope_stage(S) -- if $(n > 0)
dec $scope_outputs(pevent*) : nat*
def $scope_outputs(eps) = eps
def $scope_outputs((OUTPUT n*) :: pevent*) = n* ++ $scope_outputs(pevent*)
def $scope_outputs((WARNING n* z) :: pevent*) = $scope_outputs(pevent*)
def $scope_outputs((DIAGNOSTIC text n* z) :: pevent*) = $scope_outputs(pevent*)
'''
CASES = {
    'external-alias': (
        'S.CURRENT = eps -- if $lookup(S.ENV,$ptascii("r")) = (n_cell) -- if $propref_at(S.PROPREFS,n_cell) = (ppropref)',
        [
            '$lookup(S.ENV,$ptascii("r")) = (n_cell)',
            'S.PROPREFS = [ppropref]', 'ppropref.CELL = n_cell',
            'ppropref.SOURCES = [pproptypesource]',
            'pproptypesource.OBJECT = n_object', 'pproptypesource.NAME = [0,42,0,120]',
            '$propref_descriptor(S,pproptypesource) = (ppropertydesc)',
            'ppropertydesc.NAME = [120]', 'ppropertydesc.KEY = [0,42,0,120]',
            '$property_resolve(S,n_object,[120]) = PROPERTY_DENIED ppropertydesc',
            '$property_resolve(S,n_object,[0,42,0,120]) = PROPERTY_BADNAME',
            '$property_quiet(S,POBJECT n_object,[120],1).RESULT = KNOWN PNULL',
            '~$proprefs_valid(S[.PROPREFS = [ppropref[.SOURCES = [pproptypesource[.NAME = [120]]]]]])',
            'S_written = $location_write(S,PROPERTY n_object ([0,42,0,120]),PINT 9)',
            'S_written.COMPLETION = NORMAL', 'S_written.STORE[n_cell] = DEFINED (PINT 9)',
            '$proprefs_valid(S_written)', 'S_done.STORE[n_cell] = DEFINED (PINT 1)',
            *uncaught_assertions('S_done', '"TypeError"', 'ptbytes_error', 'z_error'),
        ]),
    'static-closure': (
        'S.CURRENT = (pcallcontext) -- if pcallcontext.LEXICAL_CLASS =/= eps -- if pcallcontext.RECEIVER = eps',
        [
            'S.CURRENT = (pcallcontext)', 'S.OBJECTPROPS = [pobjectprops]',
            'pobjectprops.OBJECT = n_object',
            '$property_resolve(S,n_object,[120]) = PROPERTY_ACCESS ([0,42,0,120])',
            '$property_resolve(S[.CURRENT = eps],n_object,[120]) = PROPERTY_DENIED ppropertydesc',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.RECEIVER = (n_object)])])',
            'S_done.COMPLETION = NORMAL', '$scope_outputs(S_done.EVENTS) = [52]',
        ]),
    'saved-foreach': (
        'S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("hold")',
        [
            'S.FRAMES = pframe :: pframe_tail*', 'pframe.CONTEXT = (pcallcontext_saved)',
            'S.ITERATORS = [OBJECTITER n_iterator n_object n_cursor true]',
            'S.PROPREFS = [ppropref]', 'ppropref.SOURCES = [pproptypesource]',
            'pproptypesource.OBJECT = n_object', 'pproptypesource.NAME = [0,42,0,120]',
            '$property_resolve(S,n_object,[120]) = PROPERTY_DENIED ppropertydesc',
            '$property_resolve(S[.CURRENT = pframe.CONTEXT],n_object,[120]) = PROPERTY_ACCESS ([0,42,0,120])',
            '$call_saved_context_valid(S,pframe)',
            '~$call_saved_context_valid(S,pframe[.CONTEXT = (pcallcontext_saved[.LEXICAL_CLASS = eps])])',
            '$($heap_owners($heap_graph(S),HOBJECT n_object) > 0)',
            '$($heap_owners($heap_graph(S),HCELL ppropref.CELL) > 0)',
            'S_done.COMPLETION = NORMAL', '$scope_outputs(S_done.EVENTS) = [50]',
            'S_done.ITERATORS = eps',
        ]),
    'binding-atomicity': (
        'S.TODO = (PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) ([122])) n_source* z) :: ptask*',
        [
            'S.TODO = (PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) ([122])) n_source* z) :: ptask*',
            '$lookup(S.ENV,$ptascii("r")) = (n_cell)',
            '$lookup(S.ENV,$ptascii("old")) = (n_old)',
            '$propref_at(S.PROPREFS,n_cell) = (ppropref)',
            'ppropref.SOURCES = [pproptypesource_y,pproptypesource_x]',
            'pproptypesource_y.NAME = [121]', 'pproptypesource_x.NAME = [120]',
            '$propref_at(S.PROPREFS,n_old) = (ppropref_old)',
            'ppropref_old.SOURCES = [pproptypesource_old]', 'pproptypesource_old.NAME = [122]',
            'S_attempt = $assign_property_reference(S,n_object,[122],n_cell,z)',
            'S_attempt.COMPLETION = THROWN "TypeError" ptbytes_error z_error',
            'S_attempt.STORE = S.STORE', 'S_attempt.OBJECTPROPS = S.OBJECTPROPS',
            'S_attempt.PROPREFS = S.PROPREFS', '$proprefs_valid(S_attempt)',
            *uncaught_assertions('S_done', '"TypeError"', 'ptbytes_error', 'z_error'),
            'S_done.STORE[n_cell] = DEFINED (PSTRING ([51]))',
            'S_done.STORE[n_old] = DEFINED (PINT 1)',
            'S_done.PROPREFS = S.PROPREFS',
        ]),
}


def run():
    out = Path(tempfile.mkdtemp(prefix='property-visibility-scope-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = modules + [ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json',
        'frontend/worker.php', 'frontend/FileLexer.php', 'frontend/target.php',
        'tests/semantics/_build/default/numeric_runner.exe', '_build/default/adapter/main.exe',
        '.tools/php/bin/php', '.tools/php-file.so')] + [Path(__file__)]
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
    assert passed, 'visibility scope protocol failed'


if __name__ == '__main__':
    run()
