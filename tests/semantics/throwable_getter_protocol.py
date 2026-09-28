#!/usr/bin/env python3
"""Paused native Throwable getter identity, storage, and argument ownership."""
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
    ('selected', b'<?php try{1/0;}catch(Error $e){echo $e->getMessage();}',
     'S.TODO = (GETTER_ARGS pgettercall) :: ptask*', [
         '$call_task_valid(S, GETTER_ARGS pgettercall)',
         '$property_state_valid(S)',
         '$heap_valid($heap_graph(S))',
         '$($heap_owners($heap_graph(S), HOBJECT pgettercall.RECEIVER) > 0)',
         '~$call_task_valid(S, GETTER_ARGS pgettercall[.RECEIVER = 999])',
         '~$call_task_valid(S, GETTER_ARGS pgettercall[.BASE = "Exception"])',
         '~$call_task_valid(S, GETTER_ARGS pgettercall[.METHOD = GET_CODE])',
         '~$call_task_valid(S, GETTER_ARGS pgettercall[.SITE = PORIGIN 999 eps])',
         '~$call_task_valid(S, GETTER_ARGS pgettercall[.LINE = 999])',
         '~$call_task_valid(S, GETTER_ARGS pgettercall[.INDEX = 1])',
         '$objectprops_record_at(S.OBJECTPROPS, pgettercall.RECEIVER) = (pobjectprops)',
         'pobjectprops.SLOTS = [ppropertyslot_message, ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_previous]',
         'ppropertyslot_message.DECL = (INTERNAL_PROPERTY "Error" ([109,101,115,115,97,103,101]))',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pgettercall.RECEIVER, [ppropertyslot_message[.DECL = (INTERNAL_PROPERTY "Exception" ([109,101,115,115,97,103,101]))], ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pgettercall.RECEIVER, [ppropertyslot_message[.DECL = (INTERNAL_PROPERTY "Error" ([120]))], ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pgettercall.RECEIVER, [ppropertyslot_message[.NAME = ([109,101,115,115,97,103,101])], ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pgettercall.RECEIVER, [ppropertyslot_message, ppropertyslot_code, ppropertyslot_file[.STATE = PROP_VALUE (DIRECT (PINT 1))], ppropertyslot_line, ppropertyslot_previous])])',
         '~$property_state_valid(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, pgettercall.RECEIVER, [ppropertyslot_message, ppropertyslot_code, ppropertyslot_file, ppropertyslot_line, ppropertyslot_previous[.STATE = PROP_VALUE (DIRECT (POBJECT 999))]])])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('deferred-send', b'<?php try{1/0;}catch(Error $e){try{$e->getMessage($missing);}catch(Throwable $x){echo 1;}}',
     'S.TODO = (GETTER_SEND pgettercall) :: ptask*', [
         '$call_task_valid(S, GETTER_SEND pgettercall)',
         '$getter_result_valid(S)',
         '~$getter_result_valid(S[.RESULT = KNOWN PNULL])',
         '~$call_task_valid(S, GETTER_SEND pgettercall[.RECEIVER = 999])',
         '$($heap_owners($heap_graph(S), HOBJECT pgettercall.RECEIVER) > 0)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('unpack-root', b'<?php try{1/0;}catch(Error $e){try{$e->getMessage(...[1]);}catch(Throwable $x){echo 1;}}',
     'S.TODO = (GETTER_UNPACK_NEXT pgettercall poperand n_cursor) :: ptask*', [
         'poperand = KNOWN (PARRAY n_array)',
         '$call_task_valid(S, GETTER_UNPACK_NEXT pgettercall poperand n_cursor)',
         '$($heap_owners($heap_graph(S), HOBJECT pgettercall.RECEIVER) > 0)',
         '$($heap_owners($heap_graph(S), HARRAY n_array) > 0)',
         '~$call_task_valid(S, GETTER_UNPACK_NEXT pgettercall poperand 999)',
         '~$call_task_valid(S, GETTER_UNPACK_NEXT pgettercall (KNOWN (PARRAY 999)) n_cursor)',
         '~$call_task_valid(S, GETTER_UNPACK_NEXT pgettercall[.RECEIVER = 999] poperand n_cursor)',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = NORMAL']),
    ('sent-object-root', b'<?php try{1/0;}catch(Error $e){} try{2/0;}catch(Error $other){} function kill(&$x){$x=null;return 1;} $e->getMessage($other,kill($other));',
     'S.TODO = (GETTER_INVOKE pgettercall) :: ptask*', [
         'pgettercall.SENT = (KNOWN (POBJECT n_other)) :: poperand_tail*',
         'n_other =/= pgettercall.RECEIVER',
         '$call_task_valid(S, GETTER_INVOKE pgettercall)',
         '(HOBJECT n_other) <- $task_nodes(GETTER_INVOKE pgettercall)',
         '$($heap_owners($heap_graph(S), HOBJECT n_other) > 0)',
         '~$call_task_valid(S, GETTER_INVOKE pgettercall[.SENT = eps])',
         '$call_descriptors_valid(S)',
         'S_done = $drive(S, 1000)',
         'S_done.COMPLETION = UNCAUGHT n_uncaught']),
]


def main():
    out = Path(tempfile.mkdtemp(prefix='throwable-getter-protocol-', dir=ROOT / '.tools'))
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
    assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': hashes, 'cases': records}, indent=2) + '\n')
    print('PASS Throwable getter protocol', len(records), out)


if __name__ == '__main__':
    main()
