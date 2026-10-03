#!/usr/bin/env python3
"""Synthetic backing-value controls; the reference-return producer is absent."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php class O {} class C { public O $p; } class A { public static O $p; } '
          b'function &f($a): string { return $a; } '
          b'$a=new O; $c=new C; $c->p=&$a; A::$p=&$a; '
          b'$b="7"; $spare=&$b; $plain="7";')
MUTATION_SOURCE = (b'<?php class O {} '
          b'class C { public O $p; public int $i=1; } class A { public static O $p; } '
          b'function &f($a): string { return $a; } '
          b'$a=new O; $c=new C; $c->p=&$a; A::$p=&$a; $good=new O;')
CATCH_SOURCE = (b'<?php class O extends Exception {} '
          b'class C { public O $p; } class A { public static O $p; } '
          b'function &f($a): string { return $a; } '
          b'$a=new O; $c=new C; $c->p=&$a; A::$p=&$a; $good=new O; $e=new Exception;')
CAPABILITY_SOURCE = (b'<?php interface I {} '
          b'function &f($a): string { return $a; } function byvalue($a): string { return $a; } '
          b'function &objects($a): object|string { return $a; } '
          b'function &mixedvalue($a): mixed { return $a; } '
          b'function &accepted($a): Stringable|string { return $a; } '
          b'function &intersection($a): (Stringable&I)|string { return $a; } '
          b'function &integer($a): int { return $a; } '
          b'function &outer($a): string { function inner($a): string { return $a; } return $a; } '
          b'$arrow=static fn &($a): string => $a;')
STRICT_SOURCE = (b'<?php declare(strict_types=1); '
                 b'function &f($a): string { return $a; } '
                 b'$arrow=static fn &($a): string => $a;')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initialized(initial):
    return [
        'S_initial = ' + initial,
        'S = $drive(S_initial[.COMPLETION = NORMAL],4096)',
        'S.COMPLETION = NORMAL /\\ S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps',
        'S.REFCOERCIONS = eps',
    ]



def row_cost(initial):
    # Separate one row/source predicate from drive and full property validity.
    return initialized(initial) + [
        '$lookup(S.ENV,$ptascii("a")) = (n_cell)',
        '$call_target(S,$ptascii("f"),eps) = (pfunction)',
        'porigin_site = PORIGIN pfunction.CODE.UNIT (pfunction.BODY ++ [PCINDEX 0])',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY ++ [PCINDEX 0]) = ((z_line,false))',
        'prefcoercion = {CELL n_cell,SITE porigin_site,LINE z_line,VALUE ([55])}',
        'S_injected = S[.STORE = $set_cell(S.STORE,n_cell,DEFINED (PSTRING ([55])))][.REFCOERCIONS = [prefcoercion]]',
        '$reference_coercion_row_valid(S_injected,prefcoercion)',
    ]


def common(initial):
    return initialized(initial) + [
        '$lookup(S.ENV,$ptascii("a")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_original)',
        '$lookup(S.ENV,$ptascii("c")) = (n_c)',
        'S.STORE[n_c] = DEFINED (POBJECT n_object)',
        '$call_target(S,$ptascii("f"),eps) = (pfunction)',
        'porigin_site = PORIGIN pfunction.CODE.UNIT (pfunction.BODY ++ [PCINDEX 0])',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY ++ [PCINDEX 0]) = ((z_line,false))',
        '$reference_coercion_source(S,porigin_site,z_line)',
        'prefcoercion = {CELL n_cell,SITE porigin_site,LINE z_line,VALUE ([55])}',
        'S_missing = $prune_allocations(S[.STORE = $set_cell(S.STORE,n_cell,DEFINED (PSTRING ([55])))])',
        'S_witness = S_missing[.REFCOERCIONS = [prefcoercion]]',
        '$reference_coercions_valid(S_witness) /\\ $reference_coercion_value(S_witness,n_cell,PSTRING ([55]))',
        'S_witness.CURRENT = eps /\\ S_witness.FRAMES = eps',
        'S_witness.PROPREFS = S.PROPREFS /\\ S_witness.CLASSSTATICS = S.CLASSSTATICS',
        '$machine_roots(S_witness) = $machine_roots(S_missing)',
    ]


def validity():
    return [
        '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $heap_valid($heap_graph(S))',
        '~$property_state_valid(S_missing) /\\ ~$proprefs_valid(S_missing) /\\ ~$class_statics_valid(S_missing)',
        '$call_descriptors_valid(S_witness) /\\ $class_state_valid(S_witness) /\\ $heap_valid($heap_graph(S_witness))',
        '~((HOBJECT n_original) <- S_witness.ALLOCATIONS)',
    ]


def stages(initial, mutation_initial, catch_initial, capability_initial, strict_initial):
    metadata = common(initial) + validity() + [
        '$lookup(S.ENV,$ptascii("b")) = (n_spare)',
        'n_spare <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("plain")) = (n_plain)',
        '~(n_plain <- S.REFCELLS)',
        '~$reference_coercion_value(S_witness,n_cell,PSTRING ([56]))',
        '~$reference_coercion_value(S_witness,n_cell,PINT 7)',
        '~$reference_coercion_row_valid(S_witness,prefcoercion[.CELL = n_c])',
        '~$reference_coercion_row_valid(S_witness,prefcoercion[.CELL = n_plain])',
        '~$reference_coercion_row_valid(S_witness,prefcoercion[.CELL = $(|S_witness.STORE| + 1)])',
        '~$reference_coercion_row_valid(S_witness[.ALLOCATIONS = $call_remove_owner(S_witness.ALLOCATIONS,HCELL n_cell)],prefcoercion)',
        '~$reference_coercion_row_valid(S_witness,prefcoercion[.VALUE = [56]])',
        '~$reference_coercion_row_valid(S_witness,prefcoercion[.LINE = $(z_line + 1)])',
        '~$reference_coercion_source(S_witness,pfunction.ORIGIN,z_line)',
        '~$reference_coercion_source(S_witness,PORIGIN $(pfunction.CODE.UNIT + 1) (pfunction.BODY ++ [PCINDEX 0]),z_line)',
        '~$reference_coercions_valid(S_witness[.REFCOERCIONS = [prefcoercion,prefcoercion]])',
        '~$property_state_valid(S_witness[.REFCOERCIONS = [prefcoercion,prefcoercion]])',
        'prefcoercion_spare = prefcoercion[.CELL = n_spare]',
        '$propref_at(S_witness.PROPREFS,n_spare) = eps',
        '$reference_coercion_row_valid(S_witness,prefcoercion_spare)',
        '~$property_state_valid(S_witness[.REFCOERCIONS = [prefcoercion,prefcoercion_spare,prefcoercion_spare]])',
        '~$reference_coercion_producer(S_witness,n_cell,porigin_site,z_line)',
        'S_admission = $reference_coercion_write(S_witness[.RESULT = KNOWN (PSTRING ([55]))],n_cell,porigin_site,z_line,[55])',
        'S_admission.COMPLETION = UNSUPPORTED "invalid reference coercion producer"',
        'S_admission.STORE = S_witness.STORE /\\ S_admission.PROPREFS = S_witness.PROPREFS /\\ S_admission.REFCOERCIONS = S_witness.REFCOERCIONS',
    ]
    capability = [
        'S_initial = ' + capability_initial,
        'S = $drive(S_initial[.COMPLETION = NORMAL],2048)',
        'S.COMPLETION = NORMAL /\\ S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps',
        'S.REFCOERCIONS = eps /\\ $call_descriptors_valid(S)',
        '$call_target(S,$ptascii("f"),eps) = (pfunction)',
        '$reference_coercion_function(pfunction)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY ++ [PCINDEX 0]) = ((z_line,false))',
        '$reference_coercion_source(S,PORIGIN pfunction.CODE.UNIT (pfunction.BODY ++ [PCINDEX 0]),z_line)',
        '$call_target(S,$ptascii("byvalue"),eps) = (pfunction_byvalue)',
        '~$reference_coercion_function(pfunction_byvalue)',
        '~$reference_coercion_source(S,PORIGIN pfunction_byvalue.CODE.UNIT (pfunction_byvalue.BODY ++ [PCINDEX 0]),z_line)',
        '$call_target(S,$ptascii("objects"),eps) = (pfunction_objects)',
        '~$reference_coercion_function(pfunction_objects)',
        '$call_target(S,$ptascii("mixedvalue"),eps) = (pfunction_mixed)',
        '~$reference_coercion_function(pfunction_mixed)',
        '$call_target(S,$ptascii("accepted"),eps) = (pfunction_accepted)',
        '~$reference_coercion_function(pfunction_accepted)',
        '$call_target(S,$ptascii("integer"),eps) = (pfunction_integer)',
        '~$reference_coercion_function(pfunction_integer)',
        '$call_target(S,$ptascii("intersection"),eps) = (pfunction_intersection)',
        '$reference_coercion_function(pfunction_intersection)',
        '$call_target(S,$ptascii("outer"),eps) = (pfunction_outer)',
        '$reference_coercion_function(pfunction_outer)',
        '$function_at($all_functions(S),PORIGIN pfunction_outer.CODE.UNIT (pfunction_outer.BODY ++ [PCINDEX 0])) = (pfunction_inner)',
        'pcpath_inner = pfunction_inner.BODY ++ [PCINDEX 0]',
        '$goto_source_owner($all_functions(S),pfunction_inner.CODE.UNIT,pcpath_inner) = (pfunction_inner)',
        '$code_expression(pfunction_inner.CODE.EXPRESSIONS,pcpath_inner) = ((z_inner,false))',
        '~$reference_coercion_source(S,PORIGIN pfunction_inner.CODE.UNIT pcpath_inner,z_inner)',
        'S.CLOSURETEMPLATES = [pfunction_arrow]',
        '$arrow_line(pfunction_arrow.CODE.EXPRESSIONS,pfunction_arrow.BODY) = (z_arrow)',
        '$reference_coercion_source(S,pfunction_arrow.ORIGIN,z_arrow)',
        '~$reference_coercion_source(S,pfunction_arrow.ORIGIN,$(z_arrow + 1))',
        '$lookup(S.ENV,$ptascii("arrow")) = (n_arrow_cell)',
        'S.STORE[n_arrow_cell] = DEFINED (POBJECT n_arrow)',
        'S_arrow_gone = $prune_allocations($unset_name(S,$ptascii("arrow")))',
        '~((HOBJECT n_arrow) <- S_arrow_gone.ALLOCATIONS)',
        'S_arrow_gone.CURRENT = eps /\\ S_arrow_gone.FRAMES = eps /\\ $call_descriptors_valid(S_arrow_gone)',
        '$reference_coercion_source(S_arrow_gone,pfunction_arrow.ORIGIN,z_arrow)',
    ]
    mutation = common(mutation_initial) + validity() + [
        '$lookup(S.ENV,$ptascii("good")) = (n_good_cell)',
        'S.STORE[n_good_cell] = DEFINED (POBJECT n_good)',
        'S_object_fetch = $property_reference_fetch(S_witness,n_object,$ptascii("p"),1)',
        'S_object_fetch.RESULT = REFERENCE n_cell /\\ S_object_fetch.COMPLETION = NORMAL',
        'S_object_fetch.STORE = S_witness.STORE /\\ S_object_fetch.PROPREFS = S_witness.PROPREFS /\\ S_object_fetch.REFCOERCIONS = S_witness.REFCOERCIONS',
        'S_witness.CLASSSTATICS = [pclassstatic_alias]',
        'S_static_fetch = $class_static_reference_fetch(S_witness,pclassstatic_alias.DECL,1)',
        'S_static_fetch.RESULT = REFERENCE n_cell /\\ S_static_fetch.COMPLETION = NORMAL',
        'S_static_fetch.STORE = S_witness.STORE /\\ S_static_fetch.PROPREFS = S_witness.PROPREFS /\\ S_static_fetch.REFCOERCIONS = S_witness.REFCOERCIONS',
        'S_reject = $write_cell_checked(S_witness,n_cell,PSTRING ([55]),1)',
        'S_reject.COMPLETION = THROWN "TypeError" ptbytes_error z_error',
        'S_reject.STORE[n_cell] = S_witness.STORE[n_cell] /\\ S_reject.REFCOERCIONS = S_witness.REFCOERCIONS',
        '$class_state_valid(S_reject)',
        'S.OBJECTS[n_object] = INSTANCE porigin_c',
        '$property_desc_at($property_layout(S_witness,porigin_c,|S_witness.CLASSES|),$ptascii("p")) = (ppropertydesc_p)',
        'S_bind_reject = $property_bind_type(S_witness,ppropertydesc_p,n_cell,PSTRING ([55]),1)',
        'S_bind_reject.COMPLETION = THROWN "TypeError" ptbytes_bind_error z_bind_error',
        'S_bind_reject.STORE[n_cell] = S_witness.STORE[n_cell] /\\ S_bind_reject.REFCOERCIONS = S_witness.REFCOERCIONS',
        'S_write_accept = $write_cell_checked(S_witness,n_cell,POBJECT n_good,1)',
        'S_write_accept.COMPLETION = NORMAL /\\ S_write_accept.STORE[n_cell] = DEFINED (POBJECT n_good)',
        'S_write_accept.REFCOERCIONS = eps /\\ S_write_accept.PROPREFS = S_witness.PROPREFS',
        '$class_state_valid(S_write_accept)',
        '$class_named(S_witness.CLASSNAMES,$ptascii("a")) = (porigin_a)',
        '$class_static_info(S_witness,porigin_a,$ptascii("p")) = (ppropertydesc_static)',
        'S_unset = $property_unset(S_witness,POBJECT n_object,$ptascii("p"),1)',
        'S_detached = $assign_class_static_reference(S_unset,ppropertydesc_static.ORIGIN,n_good_cell,1)',
        'S_detached.COMPLETION = NORMAL /\\ $propref_at(S_detached.PROPREFS,n_cell) = eps',
        'S_detached.REFCOERCIONS = S_witness.REFCOERCIONS /\\ S_detached.STORE[n_cell] = DEFINED (PSTRING ([55]))',
        '$class_state_valid(S_detached)',
        'S_identical = $write_cell_checked(S_detached,n_cell,PSTRING ([55]),1)',
        'S_identical.COMPLETION = NORMAL /\\ S_identical.STORE[n_cell] = S_detached.STORE[n_cell] /\\ S_identical.REFCOERCIONS = eps',
        '$class_state_valid(S_identical)',
        'S_bind_convert = $assign_property_reference(S_detached,n_object,$ptascii("i"),n_cell,1)',
        'S_bind_convert.COMPLETION = NORMAL /\\ S_bind_convert.STORE[n_cell] = DEFINED (PINT 7) /\\ S_bind_convert.REFCOERCIONS = eps',
        '$class_state_valid(S_bind_convert)',
        'S_retired = $prune_allocations($unset_name(S_detached,$ptascii("a"))[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
        '~((HCELL n_cell) <- S_retired.ALLOCATIONS)',
        'S_retired.REFCOERCIONS = eps /\\ $class_state_valid(S_retired)',
        'S_fresh = $ensure(S_retired,$ptascii("fresh"))',
        'S_fresh.CELL = |S_retired.STORE| /\\ S_fresh.CELL =/= n_cell /\\ S_fresh.REFCOERCIONS = eps',
    ]
    catch = common(catch_initial) + validity() + [
        '$lookup(S.ENV,$ptascii("good")) = (n_good_cell)',
        'S.STORE[n_good_cell] = DEFINED (POBJECT n_good)',
        '$lookup(S.ENV,$ptascii("e")) = (n_e_cell)',
        'S.STORE[n_e_cell] = DEFINED (POBJECT n_e)',
        'S_catch_reject = $throwable_bind_cell(S_witness,n_cell,n_e,1)',
        'S_catch_reject.COMPLETION = THROWN "TypeError" ptbytes_catch_error z_catch_error',
        'S_catch_reject.STORE[n_cell] = S_witness.STORE[n_cell] /\\ S_catch_reject.REFCOERCIONS = S_witness.REFCOERCIONS',
        '$class_state_valid(S_catch_reject)',
        'S_catch_accept = $throwable_bind_cell(S_witness,n_cell,n_good,1)',
        'S_catch_accept.COMPLETION = NORMAL /\\ S_catch_accept.STORE[n_cell] = DEFINED (POBJECT n_good)',
        'S_catch_accept.REFCOERCIONS = eps /\\ S_catch_accept.PROPREFS = S_witness.PROPREFS',
        '$class_state_valid(S_catch_accept)',
    ]
    strict = [
        'S_initial = ' + strict_initial,
        'S = $drive(S_initial[.COMPLETION = NORMAL],2048)',
        'S.COMPLETION = NORMAL /\\ S.REFCOERCIONS = eps',
        '$call_descriptors_valid(S)',
        '$call_target(S,$ptascii("f"),eps) = (pfunction)',
        'pfunction.CODE.STRICT /\\ pfunction.SIGNATURE.BYREF',
        '~$reference_coercion_function(pfunction)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY ++ [PCINDEX 0]) = ((z_line,false))',
        '~$reference_coercion_source(S,PORIGIN pfunction.CODE.UNIT (pfunction.BODY ++ [PCINDEX 0]),z_line)',
        'S.CLOSURETEMPLATES = [pfunction_arrow]',
        'pfunction_arrow.CODE.STRICT /\\ pfunction_arrow.SIGNATURE.BYREF',
        '$arrow_line(pfunction_arrow.CODE.EXPRESSIONS,pfunction_arrow.BODY) = (z_arrow)',
        '~$reference_coercion_source(S,pfunction_arrow.ORIGIN,z_arrow)',
    ]
    return [('minimal-drive', initialized(initial)), ('row-and-source', row_cost(initial)),
            ('backing-validity', common(initial) + validity()),
            ('metadata', metadata), ('ordinary-mutation', mutation),
            ('catch-drive', initialized(catch_initial)), ('catch-assignment', catch),
            ('weak-source-capability', capability), ('strict-source', strict)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnose', action='store_true',
                        help='Measure drive, row/source and backing validity before lifecycle controls.')
    parser.add_argument('--stage', action='append',
                        choices=['metadata', 'ordinary-mutation', 'catch-drive', 'catch-assignment',
                                 'weak-source-capability', 'strict-source'],
                        help='Run selected remaining controls without repeating accepted stages.')
    args = parser.parse_args()
    if args.diagnose and args.stage:
        parser.error('--diagnose and --stage are separate selections')
    out = Path(tempfile.mkdtemp(prefix='reference-coercion-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'spec/semantics/modules.json',
                         ROOT / 'tests/semantics/recorded_worker.py',
                         ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so',
                         ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php', ROOT / '.tools/php/bin/php']
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    initials = []
    try:
        for name, source in [('backing', SOURCE), ('mutation', MUTATION_SOURCE),
                             ('catch', CATCH_SOURCE),
                             ('capability', CAPABILITY_SOURCE),
                             ('strict', STRICT_SOURCE)]:
            path = out / (name + '.php')
            path.write_bytes(source)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            initials.append('$php_run(' + checked['fixture'] + ',0,'
                            + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')')
    finally:
        frontend.close()
        adapter.close()
    records = []
    suites = stages(*initials)
    if args.diagnose:
        suites = suites[:3]
    else:
        suites = suites[3:]
        if args.stage:
            suites = [row for row in suites if row[0] in args.stage]
        else:
            suites = [row for row in suites if row[0] != 'catch-drive']
    for name, checks in suites:
        fixture = out / (name + '.watsup')
        fixture.write_text('dec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + check + '\n' for check in checks))
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                   *map(str, modules), str(fixture)]
        started = time.monotonic()
        try:
            result = subprocess.run(command, capture_output=True, timeout=180)
            stdout, stderr, code, timed_out = result.stdout, result.stderr, result.returncode, False
        except subprocess.TimeoutExpired as error:
            stdout, stderr, code, timed_out = error.stdout or b'', error.stderr or b'', None, True
        (out / (name + '.stdout')).write_bytes(stdout)
        (out / (name + '.stderr')).write_bytes(stderr)
        records.append({'id': name, 'assertions': len(checks), 'fixture_sha256': digest(fixture),
                        'seconds': time.monotonic() - started,
                        'timeout': timed_out, 'returncode': code,
                        'pass': code == 0 and stdout == b'true\n' and not stderr})
        print(name, records[-1]['pass'], len(checks), 'timeout' if timed_out else '', flush=True)
        if not records[-1]['pass']:
            break
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in watched}, 'inputs changed during run'
    outcome = ('timeout' if any(row['timeout'] for row in records)
               else 'pass' if all(row['pass'] for row in records) else 'fail')
    report = {'result': outcome, 'inputs': before,
              'selection': [name for name, _ in suites],
              'scope': 'Synthetic state consistency and ordinary mutation controls; producer default-false, not native callback agreement.',
              'source_sha256': hashlib.sha256(SOURCE).hexdigest(),
              'mutation_source_sha256': hashlib.sha256(MUTATION_SOURCE).hexdigest(),
              'catch_source_sha256': hashlib.sha256(CATCH_SOURCE).hexdigest(),
              'capability_source_sha256': hashlib.sha256(CAPABILITY_SOURCE).hexdigest(),
              'strict_source_sha256': hashlib.sha256(STRICT_SOURCE).hexdigest(), 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
