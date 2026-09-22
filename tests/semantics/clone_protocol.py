#!/usr/bin/env python3
"""Clone paused ownership, typed references and closure static copies."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('typed-shared', b'<?php class C{public int $x=1;} $a=new C;$r=&$a->x;$b=clone $a;$r=2;echo $a->x,$b->x;',
     'S.TODO = (CLONE_RESULT porigin z) :: ptask*', [
        'S.TODO = (CLONE_RESULT porigin z) :: ptask*',
        '$clone_task_valid(S, porigin, z)',
        '$call_tasks_valid(S, S.TODO)',
        '~$clone_task_valid(S, porigin, 999)',
        '~$clone_task_valid(S[.ORIGIN = eps], porigin, z)',
        '~$clone_task_valid(S[.SOURCES = eps], porigin, z)',
        '~$clone_task_valid(S[.CODE = eps], porigin, z)',
        'S_bad = $drive(S[.TODO = (CLONE_RESULT porigin 999) :: ptask*],1000)',
        'S_bad.COMPLETION = UNSUPPORTED text',
        'S_read = $resolve(S, S.RESULT)',
        'S_read.RESULT = KNOWN (POBJECT n_old)',
        '$objectprops_record_at(S.OBJECTPROPS, n_old) = (pobjectprops)',
        'ppropertyslot = pobjectprops.SLOTS[0]',
        'ppropertyslot.STATE = PROP_VALUE (ALIAS n_cell)',
        'S_copy = $drive_steps(S,1)[.COMPLETION = NORMAL]',
        'S_copy.RESULT = KNOWN (POBJECT n_new)',
        'n_new =/= n_old',
        '$objectprops_record_at(S_copy.OBJECTPROPS, n_new) = (pobjectprops_new)',
        'pobjectprops_new.SLOTS[0].STATE = PROP_VALUE (ALIAS n_cell)',
        '$propref_at(S_copy.PROPREFS, n_cell) = (ppropref)',
        '|ppropref.SOURCES| = 2',
        '$heap_valid($heap_graph(S_copy))',
        '$call_descriptors_valid(S_copy)',
        'S_done = $drive(S_copy,1000)',
        '$outputs(S_done.EVENTS) = [50,50]',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
     ]),
    ('closure-cold', b'<?php $f=function(){static $x=0;return ++$x;};echo $f();$g=clone $f;echo $f(),$g();',
     'S.TODO = (CLONE_RESULT porigin z) :: ptask*', [
        'S_read = $resolve(S,S.RESULT)',
        'S_read.RESULT = KNOWN (POBJECT n_old)',
        'S.OBJECTS[n_old] = REALCLOSURE porigin_template pitem* ([pstaticcell])',
        'S_copy = $drive_steps(S,1)[.COMPLETION = NORMAL]',
        'S_copy.RESULT = KNOWN (POBJECT n_new)',
        'S_copy.OBJECTS[n_new] = REALCLOSURE porigin_template pitem* ([pstaticcell_new])',
        'pstaticcell.CELL =/= pstaticcell_new.CELL',
        'pstaticcell.ORIGIN = pstaticcell_new.ORIGIN',
        '$closure_state_valid(S_copy)',
        '$heap_valid($heap_graph(S_copy))',
        '~$clone_statics_compatible([pstaticcell, pstaticcell[.ORIGIN = PORIGIN 99 eps]])',
        'S_done = $drive(S_copy,1000)',
        '$outputs(S_done.EVENTS) = [49,50,50]',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
     ]),
    ('closure-live', b'<?php $g=null;$f=function()use(&$f,&$g){static $x=0;if(!$g){$g=clone $f;}return ++$x;};echo $f(),$g();',
     'S.TODO = (CLONE_RESULT porigin z) :: ptask*', [
        'S_read = $resolve(S,S.RESULT)',
        'S_read.RESULT = KNOWN (POBJECT n_old)',
        'S.OBJECTS[n_old] = REALCLOSURE porigin_template pitem* ([pstaticcell])',
        'S_copy = $drive_steps(S,1)[.COMPLETION = NORMAL]',
        'S_copy.RESULT = KNOWN (POBJECT n_new)',
        'S_copy.OBJECTS[n_new] = REALCLOSURE porigin_template pitem* ([pstaticcell])',
        '$closure_state_valid(S_copy)',
        '$heap_valid($heap_graph(S_copy))',
        '$call_descriptors_valid(S_copy)',
        'S_done = $drive(S_copy,1000)',
        '$outputs(S_done.EVENTS) = [49,50]',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
     ]),
]

CASES += [('weak-update',
  b'<?php declare(strict_types=1);class C{public int $x=1;}$a=new C;$r=&$a->x;$b=clone($a,["x"=>'
  b'"3"]);echo $r,$b->x;',
  'S.TODO = (CLONE_UPDATE pclonecall n_object n_array 0) :: ptask*',
  ['S.TODO = (CLONE_UPDATE pclonecall n_object n_array 0) :: ptask*',
   '$clone_update_valid(S,pclonecall,n_object,n_array,0)',
   '$call_tasks_valid(S,S.TODO)',
   '~$property_strict(S)',
   '$property_strict(S[.TODO = (NAME_READ 1) :: S.TODO])',
   '~$clone_update_valid(S,pclonecall[.LINE = 999],n_object,n_array,0)',
   '~$clone_update_valid(S[.ORIGIN = eps],pclonecall,n_object,n_array,0)',
   '~$clone_update_valid(S[.SOURCES = eps],pclonecall,n_object,n_array,0)',
   '~$clone_update_valid(S[.CODE = eps],pclonecall,n_object,n_array,0)',
   '~$clone_update_valid(S,pclonecall,n_object,n_array,2)',
   '~$clone_update_valid(S[.OBJECTS = '
   '$object_set(S.OBJECTS,n_object,STDINSTANCE)],pclonecall,n_object,n_array,0)',
   'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
   '$clone_update_valid(S_next,pclonecall,n_object,n_array,1)',
   '$call_descriptors_valid(S_next)',
   'S_done = $drive(S_next,1000)',
   '$outputs(S_done.EVENTS) = [51,51]',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)']),
 ('update-abrupt-cleanup',
  b'<?php class C{public int $x=1;}$a=new C;$r=&$a->x;$b=clone($a,["x"=>2,"bad"=>&$r]);',
  'S.TODO = (CLONE_UPDATE pclonecall n_object n_array 0) :: ptask*',
  ['S.TODO = (CLONE_UPDATE pclonecall n_object n_array 0) :: ptask*',
   '$objectprops_record_at(S.OBJECTPROPS,n_object) = (pobjectprops)',
   'pobjectprops.SLOTS[0].STATE = PROP_VALUE (ALIAS n_cell)',
   '$propref_at(S.PROPREFS,n_cell) = (ppropref)',
   '|ppropref.SOURCES| = 2',
   '~$clone_update_valid(S,pclonecall,n_object,n_array,2)',
   'S_bad = $drive(S[.TODO = (CLONE_UPDATE pclonecall n_object n_array 2) :: ptask*],1000)',
   'S_bad.COMPLETION = UNSUPPORTED text',
   'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
   'S_next.STORE[n_cell] = DEFINED (PINT 2)',
   '$clone_update_valid(S_next,pclonecall,n_object,n_array,1)',
   'S_done = $drive(S_next,1000)',
   'S_done.COMPLETION = THROWN text_error preqbytes z',
   '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
   '$propref_at(S_done.PROPREFS,n_cell) = (ppropref_done)',
   '|ppropref_done.SOURCES| = 1',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)']),
 ('unpack-unknown',
  b'<?php $a=new stdClass;clone(...["object"=>$a,"other"=>1]);',
  'S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
  ['S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
   '$clone_unpack_valid(S,pclonecall,poperand,0)',
   '$call_tasks_valid(S,S.TODO)',
   '~$clone_unpack_valid(S,pclonecall,poperand,2)',
   'S_bad = $drive(S[.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 2) :: ptask*],1000)',
   'S_bad.COMPLETION = UNSUPPORTED text',
   'S_done = $drive(S,1000)',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)']),
 ('unpack-duplicate',
  b'<?php $a=new stdClass;clone($a,...["object"=>$a]);',
  'S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
  ['S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
   '$clone_unpack_valid(S,pclonecall,poperand,0)',
   '$call_tasks_valid(S,S.TODO)',
   '~$clone_unpack_valid(S,pclonecall,poperand,1)',
   'S_bad = $drive(S[.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 1) :: ptask*],1000)',
   'S_bad.COMPLETION = UNSUPPORTED text',
   'S_done = $drive(S,1000)',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)']),
 ('unpack-order',
  b'<?php $a=new stdClass;clone(...["object"=>$a,[]]);',
  'S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
  ['S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
   '$clone_unpack_valid(S,pclonecall,poperand,0)',
   '$call_tasks_valid(S,S.TODO)',
   '~$clone_unpack_valid(S,pclonecall,poperand,2)',
   'S_bad = $drive(S[.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 2) :: ptask*],1000)',
   'S_bad.COMPLETION = UNSUPPORTED text',
   'S_done = $drive(S,1000)',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)']),
 ('unpack-success',
  b'<?php $a=new stdClass;$b=clone(...[$a,["x"=>2]]);echo $b->x;',
  'S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
  ['S.TODO = (CLONE_UNPACK_NEXT pclonecall poperand 0) :: ptask*',
   '$clone_unpack_valid(S,pclonecall,poperand,0)',
   '$call_tasks_valid(S,S.TODO)',
   '$clone_unpack_valid(S,pclonecall,poperand,2)',
   'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
   '$clone_unpack_valid(S_next,pclonecall,poperand,1)',
   '$call_descriptors_valid(S_next)',
   'S_done = $drive(S,1000)',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)'])]

CASES += [('intrinsic-kind',
  b'<?php $a=new stdClass;$f="clone";$b=$f($a);',
  'S.TODO = (CLONE_INVOKE pclonecall) :: ptask*',
  ['S.TODO = (CLONE_INVOKE pclonecall) :: ptask*',
   '$clone_invoke_valid(S,pclonecall)',
   'pclonecall.SENT = [NAMED_SENT poperand]',
   'pexitcall = {SITE pclonecall.SITE, KIND INTRINSIC_CLONE, INDEX pclonecall.INDEX, SENT '
   '([poperand]), NAMED pclonecall.NAMED, OWNER pclonecall.OWNER, LINE pclonecall.LINE}',
   '~$exit_call_valid(S,pexitcall)',
   'S_bad = $drive(S[.TODO = (EXIT_INVOKE pexitcall) :: ptask*],1000)',
   'S_bad.COMPLETION = UNSUPPORTED text',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = NORMAL',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)'])]

CASES += [('bound-receiver',
  b'<?php class C{public int $x=1;function make(){return function(){return ++$this->x;};}}'
  b'$o=new C;$f=$o->make();$g=clone $f;unset($o,$f);echo $g(),$g();unset($g);',
  'S.TODO = (CLONE_RESULT porigin z) :: ptask*',
  ['S_read = $resolve(S,S.RESULT)',
   'S_read.RESULT = KNOWN (POBJECT n_old)',
   '$closure_scope_at(S.CLOSURESCOPES,n_old) = (pclosurescope)',
   'pclosurescope.RECEIVER = (n_receiver)',
   'S_copy = $drive_steps(S,1)[.COMPLETION = NORMAL]',
   'S_copy.RESULT = KNOWN (POBJECT n_new)',
   'n_new =/= n_old',
   '$closure_scope_at(S_copy.CLOSURESCOPES,n_new) = (pclosurescope[.OBJECT = n_new])',
   '(HOBJECT n_receiver) <- $node_children(S_copy,HOBJECT n_new)',
   '$closure_state_valid(S_copy)',
   '$heap_valid($heap_graph(S_copy))',
   '$call_descriptors_valid(S_copy)',
   '~$closure_state_valid(S_copy[.CLOSURESCOPES = S.CLOSURESCOPES])',
   'S_done = $drive(S_copy,1000)',
   '$outputs(S_done.EVENTS) = [50,51]',
   '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
   '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
   'S_done.CLOSURESCOPES = eps',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)'])]

CASES += [('wrapper-missing-object',
  b'<?php (clone(...))->__invoke(withProperties:[]);',
  'S.TODO = (CLONE_INVOKE pclonecall) :: ptask*',
  ['S.TODO = (CLONE_INVOKE pclonecall) :: ptask*',
   'pclonecall.SENT = [NAMED_HOLE,NAMED_SENT poperand]',
   'pclonecall.OWNER = (n_owner)',
   '(HOBJECT n_owner) <- $task_nodes(CLONE_INVOKE pclonecall)',
   '$clone_invoke_valid(S,pclonecall)',
   'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
   'S_next.TRACE = [ptraceframe]',
   'ptraceframe.NAME = $ptascii("Closure->__invoke")',
   'S_done = $drive(S_next,1000)',
   'S_done.COMPLETION = THROWN "ArgumentCountError" '
   '$ptascii("Closure::__invoke(): Argument #1 ($object) not passed") 1',
   '~((HOBJECT n_owner) <- S_done.ALLOCATIONS)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)']),
 ('wrapper-clone-receive',
  b'<?php (clone(...))->__invoke(1);',
  'S.TODO = (CLONE_INVOKE pclonecall) :: ptask*',
  ['S.TODO = (CLONE_INVOKE pclonecall) :: ptask*',
   'pclonecall.OWNER = (n_owner)',
   '(HOBJECT n_owner) <- $task_nodes(CLONE_INVOKE pclonecall)',
   '$clone_invoke_valid(S,pclonecall)',
   'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
   'S_next.TRACE = [ptraceframe,ptraceframe_wrapper]',
   'ptraceframe.NAME = $ptascii("clone")',
   'ptraceframe_wrapper.NAME = $ptascii("Closure->__invoke")',
   'S_done = $drive(S_next,1000)',
   'S_done.COMPLETION = THROWN "TypeError" preqbytes 1',
   '~((HOBJECT n_owner) <- S_done.ALLOCATIONS)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)'])]

PREFIX = '''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''


def main(match=""):
    out = Path(tempfile.mkdtemp(prefix='clone-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    results = []
    for name, source, stage, checks in CASES:
        if match not in name:
            continue
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
        conditions = ['S_initial = ' + initial,
                      'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]'] + checks
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + line + '\n' for line in conditions))
        process = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                  *modules, str(fixture)], capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(process.stdout)
        (directory / 'stderr').write_text(process.stderr)
        assert process.returncode == 0 and process.stdout == 'true\n' and not process.stderr, (name, process.stderr[-2400:])
        results.append({'name': name, 'assertions': len(conditions),
                        'source_sha256': hashlib.sha256(source).hexdigest()})
        print(name, len(conditions), flush=True)
    assert before == request.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'assertions': sum(r['assertions'] for r in results),
              'cases': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    main(parser.parse_args().match)
