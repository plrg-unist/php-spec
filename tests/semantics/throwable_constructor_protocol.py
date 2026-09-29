#!/usr/bin/env python3
"""Paused finite Throwable constructor provenance, slots, and roots."""
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
    ('selected-new', b'<?php $e=new Exception("M",7);echo $e->getMessage();',
     'S.TODO = (CTOR_ARGS pctorcall) :: ptask*', [
         'pctorcall.MODE = CTOR_NEW',
         'pctorcall.BASE = "Exception"',
         '$call_task_valid(S, CTOR_ARGS pctorcall)',
         '$property_state_valid(S)',
         '$heap_valid($heap_graph(S))',
         '$($heap_owners($heap_graph(S), HOBJECT pctorcall.RECEIVER) > 0)',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.RECEIVER = 999])',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.BASE = "Error"])',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.MODE = CTOR_METHOD])',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.SITE = PORIGIN 999 eps])',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.LINE = 999])',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.INDEX = 1])',
         '$throwable_field(S, pctorcall.RECEIVER, "code") = PINT 0',
         '$throwable_field(S, pctorcall.RECEIVER, "previous") = PNULL',
         '$objectprops_record_at(S.OBJECTPROPS, pctorcall.RECEIVER) = (pobjectprops)',
         'pobjectprops.SLOTS = [ppropertyslot_message, ppropertyslot_string, ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_trace, ppropertyslot_previous]',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pctorcall.RECEIVER, [ppropertyslot_message[.DECL = (INTERNAL_PROPERTY "Error" ([109,101,115,115,97,103,101]))], ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pctorcall.RECEIVER, [ppropertyslot_message, ppropertyslot_code[.STATE = PROP_VALUE (DIRECT (PSTRING eps))], ppropertyslot_file, ppropertyslot_line, ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pctorcall.RECEIVER, [ppropertyslot_message, ppropertyslot_string, ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_trace, ppropertyslot_previous[.STATE = PROP_VALUE (DIRECT (POBJECT 999))]])])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('selected-method', b'<?php try{1/0;}catch(Error $e){}$r=$e->__construct("M");echo $r===null,"|",$e->getMessage();',
     'S.TODO = (CTOR_ARGS pctorcall) :: ptask*', [
         'pctorcall.MODE = CTOR_METHOD',
         'pctorcall.BASE = "Error"',
         '$call_task_valid(S, CTOR_ARGS pctorcall)',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.MODE = CTOR_NEW])',
         '~$call_task_valid(S, CTOR_ARGS pctorcall[.BASE = "Exception"])',
         '$($heap_owners($heap_graph(S), HOBJECT pctorcall.RECEIVER) > 0)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('deferred-send', b'<?php $e=new Exception; $e->__construct($missing);',
     'S.TODO = (CTOR_SEND pctorcall) :: ptask*', [
         '$call_task_valid(S, CTOR_SEND pctorcall)',
         '$ctor_native_result_valid(S)',
         '~$ctor_native_result_valid(S[.RESULT = KNOWN PNULL])',
         '~$call_task_valid(S, CTOR_SEND pctorcall[.RECEIVER = 999])',
         '$($heap_owners($heap_graph(S), HOBJECT pctorcall.RECEIVER) > 0)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('unpack-hole-forgery', b'<?php $e=new Exception(...[1,2]);echo $e->getCode();',
     'S.TODO = (CTOR_UNPACK_NEXT pctorcall poperand 1) :: ptask*', [
         'poperand = KNOWN (PARRAY n_array)',
         'pctorcall.NAMED = false',
         '$call_task_valid(S, CTOR_UNPACK_NEXT pctorcall poperand 1)',
         '$($heap_owners($heap_graph(S), HOBJECT pctorcall.RECEIVER) > 0)',
         '$($heap_owners($heap_graph(S), HARRAY n_array) > 0)',
         '~$call_task_valid(S, CTOR_UNPACK_NEXT pctorcall[.SENT = [NAMED_HOLE, NAMED_SENT (KNOWN (PINT 7))]] poperand 1)',
         '~$call_task_valid(S, CTOR_UNPACK_NEXT pctorcall poperand 999)',
         '~$call_task_valid(S, CTOR_UNPACK_NEXT pctorcall (KNOWN (PARRAY 999)) 1)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('second-unpack-named-mode', b'<?php $e=new Exception(...["code"=>8],...[]);echo $e->getCode();',
     'S.TODO = (CTOR_UNPACK_NEXT pctorcall poperand 0) :: ptask*\n  -- if pctorcall.INDEX = 1', [
         'pctorcall.NAMED = true',
         'pctorcall.SENT = [NAMED_HOLE, NAMED_SENT (KNOWN (PINT 8))]',
         '$call_task_valid(S, CTOR_UNPACK_NEXT pctorcall poperand 0)',
         '~$call_task_valid(S, CTOR_UNPACK_NEXT pctorcall[.NAMED = false] poperand 0)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('sent-object-root', b'<?php $p=new Error("P");function kill(&$x){$x=null;return 0;}$e=new Exception(previous:$p,code:kill($p));echo $e->getPrevious()->getMessage();',
     'S.TODO = (CTOR_INVOKE pctorcall) :: ptask*\n  -- if pctorcall.BASE = "Exception"', [
         'pctorcall.MODE = CTOR_NEW',
         'pctorcall.SENT = [NAMED_HOLE, NAMED_SENT (KNOWN (PINT 0)), NAMED_SENT (KNOWN (POBJECT n_previous))]',
         'n_previous =/= pctorcall.RECEIVER',
         '$call_task_valid(S, CTOR_INVOKE pctorcall)',
         '(HOBJECT n_previous) <- $task_nodes(CTOR_INVOKE pctorcall)',
         '$($heap_owners($heap_graph(S), HOBJECT n_previous) > 0)',
         '~$call_task_valid(S, CTOR_INVOKE pctorcall[.SENT = eps])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('receiver-rebind', b'<?php try{1/0;}catch(Error $e){}echo $e->__construct($e=5)===null;',
     'S.TODO = (CTOR_INVOKE pctorcall) :: ptask*', [
         'pctorcall.MODE = CTOR_METHOD',
         '$call_task_valid(S, CTOR_INVOKE pctorcall)',
         '(HOBJECT pctorcall.RECEIVER) <- $task_nodes(CTOR_INVOKE pctorcall)',
         '$($heap_owners($heap_graph(S), HOBJECT pctorcall.RECEIVER) > 0)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
]


def main():
    out = Path(tempfile.mkdtemp(prefix='throwable-ctor-protocol-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = modules + [ROOT / 'spec/semantics/modules.json', Path(__file__),
                        ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php',
                        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
                        ROOT / 'tests/semantics/profile.json',
                        ROOT / '_build/default/adapter/main.exe',
                        ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
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
    print('PASS Throwable constructor protocol', len(records), out)


if __name__ == '__main__':
    main()
