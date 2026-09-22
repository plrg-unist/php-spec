#!/usr/bin/env python3
"""Source-authenticated protected keys, alias owners and resumable access."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request
from property_reference_protocol import PREFIX

ROOT = Path(__file__).resolve().parents[2]
SOURCE = b'<?php class A{protected int $x=1;public function go(){$v=2;$this->x=&$v;echo $this->x;unset($this->x);$v="free";echo $v;}}$a=new A;$a->go();unset($a);'


def main():
    out = Path(tempfile.mkdtemp(prefix='property-visibility-protocol-', dir=ROOT / '.tools'))
    paths = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths += [Path(__file__), ROOT / 'tests/semantics/property_reference_protocol.py',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    path = out / 'source.php'; path.write_bytes(SOURCE)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        frontend.close(); adapter.close()
    initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
    checks = [
        'S_initial = ' + initial,
        'S_bind = $ref_seek_bind(S_initial[.COMPLETION = NORMAL], 2048)[.COMPLETION = NORMAL]',
        'S_bind.TODO = (PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) ptbytes_name) n_name_source* z_bind) :: ptask_bind*',
        'ptbytes_name = [120]',
        'S_bind.CLASSES = [pclassdesc]',
        'pclassdesc.PROPERTIES = [ppropertydesc]',
        'ppropertydesc.NAME = [120]',
        'ppropertydesc.KEY = [0,42,0,120]',
        'ppropertydesc.VISIBILITY = PROPERTY_PROTECTED',
        'S_bind.CURRENT = (pcallcontext)',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
        '$call_descriptors_valid(S_bind)',
        '$call_current_valid(S_bind)',
        '$call_tasks_valid(S_bind, S_bind.TODO)',
        '$property_state_valid(S_bind)',
        '~$call_descriptors_valid(S_bind[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.KEY = [120]]]]]])',
        '~$call_descriptors_valid(S_bind[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.VISIBILITY = PROPERTY_PUBLIC]]]]])',
        '~$call_descriptors_valid(S_bind[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.NAME = [121]]]]]])',
        '~$call_descriptors_valid(S_bind[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.DEFAULT = PROP_NULL]]]]])',
        '~$call_descriptors_valid(S_bind[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.ORIGIN = pclassdesc.ORIGIN]]]]])',
        '~$call_current_valid(S_bind[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])])',
        '$objectprops_record_at(S_bind.OBJECTPROPS, n_object) = (pobjectprops)',
        'pobjectprops.SLOTS = [ppropertyslot]',
        'ppropertyslot.NAME = ppropertydesc.KEY',
        '$property_slots_valid(S_bind, [ppropertydesc], [ppropertyslot])',
        '~$property_slots_valid(S_bind, [ppropertydesc], [ppropertyslot[.NAME = [120]]])',
        '~$property_dynamic_no_shadow([ppropertydesc], (pobjectprops.SLOTS ++ [{DECL eps, NAME ([120]), STATE PROP_VALUE (DIRECT (PINT 7))}]))',
        '~$property_state_valid(S_bind[.OBJECTPROPS = [pobjectprops[.MATERIALIZED = true][.SLOTS = pobjectprops.SLOTS ++ [{DECL eps, NAME ([120]), STATE PROP_VALUE (DIRECT (PINT 7))}]]]])',
        '$property_resolve(S_bind, n_object, [120]) = PROPERTY_ACCESS ppropertydesc.KEY',
        '$property_resolve(S_bind[.CURRENT = eps], n_object, [120]) = PROPERTY_DENIED ppropertydesc',
        '$property_resolve(S_bind, n_object, ppropertydesc.KEY) = PROPERTY_BADNAME',
        '$property_quiet(S_bind[.CURRENT = eps], POBJECT n_object, [120], 1).RESULT = KNOWN PNULL',
        '$property_visible_key(S_bind, n_object, ppropertydesc.KEY)',
        '~$property_visible_key(S_bind[.CURRENT = eps], n_object, ppropertydesc.KEY)',
        '$base_acquire(S_bind, BASE_PROPERTY (POBJECT n_object) ([120]), 1).LOCATION = PROPERTY n_object ppropertydesc.KEY',
        '~$call_task_valid(S_bind, PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) ppropertydesc.KEY) n_name_source* z_bind)',
        '$heap_valid($heap_graph(S_bind))',
        '$($heap_owners($heap_graph(S_bind), HOBJECT n_object) > 0)',
        'S_alias = $drive_steps(S_bind, 1)[.COMPLETION = NORMAL]',
        '$property_state_valid(S_alias)',
        '$objectprops_record_at(S_alias.OBJECTPROPS, n_object) = (pobjectprops_alias)',
        'pobjectprops_alias.SLOTS = [ppropertyslot_alias]',
        'ppropertyslot_alias.STATE = PROP_VALUE (ALIAS n_cell)',
        '$propref_at(S_alias.PROPREFS, n_cell) = (ppropref)',
        'ppropref.SOURCES = [{OBJECT n_object, NAME ppropertydesc.KEY, DECL ppropertydesc.ORIGIN}]',
        '~$propref_source_valid(S_alias, n_cell, {OBJECT n_object, NAME ([120]), DECL ppropertydesc.ORIGIN})',
        'S_alias.STORE[n_cell] = DEFINED (PINT 2)',
        '$heap_valid($heap_graph(S_alias))',
        'S_done = $drive(S_alias, 2048)',
        'S_done.COMPLETION = NORMAL',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2048)',
        '$property_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
        '$propref_at(S_done.PROPREFS, n_cell) = eps',
        'S_done.EVENTS = [(OUTPUT ([50])), (OUTPUT ([102,114,101,101]))]',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks))
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)], capture_output=True, text=True, timeout=180)
    (out / 'stdout').write_text(result.stdout); (out / 'stderr').write_text(result.stderr)
    (out / 'status.json').write_text(json.dumps({'exit_status': result.returncode}))
    assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr[-3500:]
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest for p, digest in hashes.items())
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': hashes,
        'source_sha256': hashlib.sha256(SOURCE).hexdigest(), 'assertions': len(checks)}, indent=2) + '\n')
    print('PASS property visibility protocol', len(checks), out)

if __name__ == '__main__':
    main()
