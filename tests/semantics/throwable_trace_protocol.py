#!/usr/bin/env python3
"""Paused selected trace methods, seven-slot shape, and captured ownership."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
from throwable_protocol import PREFIX

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('trace-array', b'<?php function f($a){$e=new Exception;$t=$e->getTrace();echo $t[0]["args"][0][0];}f([1]);',
     'S.TODO = (GETTER_INVOKE pgettercall) :: ptask* -- if pgettercall.METHOD = GET_TRACE', [
         '$call_task_valid(S, GETTER_INVOKE pgettercall)',
         '$property_state_valid(S)',
         '$throwable_field(S,pgettercall.RECEIVER,"trace") = PARRAY n_trace',
         '$trace_graph_valid(S,n_trace)',
         'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
         '$trace_array_field(S,n_frame,$ptascii("args")) = PARRAY n_args',
         'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_captured))]',
         '$($heap_owners($heap_graph(S),HARRAY n_captured) > 0)',
         '$objectprops_record_at(S.OBJECTPROPS,pgettercall.RECEIVER) = (pobjectprops)',
         'pobjectprops.SLOTS = [ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace,ppropertyslot_previous]',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,pgettercall.RECEIVER,[ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace[.DECL = (INTERNAL_PROPERTY "Error" $ptascii("trace"))],ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,pgettercall.RECEIVER,[ppropertyslot_message,ppropertyslot_string[.STATE = PROP_VALUE (DIRECT (PINT 1))],ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace,ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,pgettercall.RECEIVER,[ppropertyslot_message,ppropertyslot_string,ppropertyslot_code,ppropertyslot_file,ppropertyslot_line,ppropertyslot_trace[.STATE = PROP_VALUE (DIRECT (PARRAY 999))],ppropertyslot_previous])])',
         'S_bad = S[.ARRAYS = $array_replace(S.ARRAYS,n_frame,$array_insert(S.ARRAYS[n_frame],KSTRING $ptascii("file"),DIRECT (PINT 1)))]',
         '~$property_state_valid(S_bad)',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.METHOD = GET_TO_STRING])',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.RECEIVER = 999])',
         'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
         'S_next.RESULT = KNOWN (PARRAY n_trace)',
         '(HARRAY n_trace) <- $machine_roots(S_next)',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = NORMAL']),
    ('trace-string', b'<?php function f($x){$e=new Exception;echo $e->getTraceAsString();}f(7);',
     'S.TODO = (GETTER_INVOKE pgettercall) :: ptask* -- if pgettercall.METHOD = GET_TRACE_STRING', [
         '$call_task_valid(S, GETTER_INVOKE pgettercall)',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.METHOD = GET_TRACE])',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.BASE = "Error"])',
         'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
         'S_next.RESULT = KNOWN (PSTRING preqbytes_result)',
         '$throwable_field(S,pgettercall.RECEIVER,"trace") = PARRAY n_trace',
         'preqbytes_result = $trace_array_string(S,n_trace)',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = NORMAL']),
    ('to-string-cycle', b'<?php $e=new Exception("M");$e->__construct("M",0,$e);echo $e->__toString();',
     'S.TODO = (GETTER_INVOKE pgettercall) :: ptask* -- if pgettercall.METHOD = GET_TO_STRING', [
         '$call_task_valid(S, GETTER_INVOKE pgettercall)',
         '$throwable_previous_id(S,pgettercall.RECEIVER) = (pgettercall.RECEIVER)',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.METHOD = GET_TRACE_STRING])',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.BASE = "Error"])',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.RECEIVER = 999])',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.SITE = PORIGIN 999 eps])',
         'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
         'S_next.RESULT = KNOWN (PSTRING preqbytes_result)',
         '$throwable_field(S_next,pgettercall.RECEIVER,"string") = PSTRING preqbytes_result',
         '$property_state_valid(S_next)',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = NORMAL']),
    ('generated-frame', b'<?php function f(int $x){}try{f("x");}catch(TypeError $e){$t=$e->getTrace();echo $t[0]["function"];}',
     'S.TODO = (GETTER_INVOKE pgettercall) :: ptask* -- if pgettercall.METHOD = GET_TRACE', [
         '$call_task_valid(S, GETTER_INVOKE pgettercall)',
         'S.OBJECTS[pgettercall.RECEIVER] = THROWABLE pthrowable',
         'pthrowable.KIND = "TypeError"',
         '$throwable_field(S,pgettercall.RECEIVER,"trace") = PARRAY n_trace',
         '$trace_graph_valid(S,n_trace)',
         'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
         '$trace_array_field(S,n_frame,$ptascii("function")) = PSTRING $ptascii("f")',
         'S_next = $drive_steps(S,1)[.COMPLETION = NORMAL]',
         'S_next.RESULT = KNOWN (PARRAY n_trace)',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = NORMAL']),
    ('sent-object-root', b'<?php $e=new Exception;$other=new Error;function kill(&$x){$x=null;return 1;}$e->getTrace($other,kill($other));',
     'S.TODO = (GETTER_INVOKE pgettercall) :: ptask* -- if pgettercall.METHOD = GET_TRACE', [
         'pgettercall.SENT = (KNOWN (POBJECT n_other)) :: poperand_tail*',
         'n_other =/= pgettercall.RECEIVER',
         '$call_task_valid(S, GETTER_INVOKE pgettercall)',
         '(HOBJECT n_other) <- $task_nodes(GETTER_INVOKE pgettercall)',
         '$($heap_owners($heap_graph(S),HOBJECT n_other) > 0)',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.SENT = eps])',
         'S_done = $drive(S,1000)',
         'S_done.COMPLETION = UNCAUGHT n_uncaught']),
]


def main():
    out = Path(tempfile.mkdtemp(prefix='throwable-trace-protocol-', dir=ROOT / '.tools'))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = modules + [ROOT / 'spec/semantics/modules.json', Path(__file__),
                        ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php',
                        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
                        ROOT / 'tests/semantics/profile.json',
                        ROOT / '_build/default/adapter/main.exe',
                        ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    records = []
    for name, source, stage, checks in CASES:
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
                      'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
                      stage] + checks
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + condition + '\n' for condition in conditions))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (name, result.stderr[-3000:])
        records.append({'name': name, 'assertions': len(conditions), 'source_sha256': hashlib.sha256(source).hexdigest()})
        print(name, len(conditions), flush=True)
    assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': hashes, 'cases': records}, indent=2) + '\n')
    print('PASS Throwable trace protocol', len(records), out)


if __name__ == '__main__':
    main()
