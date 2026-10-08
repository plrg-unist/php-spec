#!/usr/bin/env python3
"""Reached explicitly unset typed reads before the actual release-order visit."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import instance_future_initial_read_protocol as common

base = common.base
sources = common.sources
cross = common.cross
ROOT = common.ROOT
CASES = {
    'dynamic': 'review-instance-future-unset-dynamic-inherited19',
    'pending': 'review-instance-future-unset-pending19',
}
PREFIX = common.PREFIX + r'''
def $initial_read_first(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureUnsetDynamic359") \/ $object_name(S, n) = $ptascii("FutureUnsetPendingFirst359")
def $initial_read_phase(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureUnsetPendingSecond359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|")
def $initial_read_phase(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask*
  -- if pforeachbind.VALUE = POBJECT n
  -- if $object_name(S, n) = $ptascii("FutureUnsetPendingParent359")
dec $unset_replace_class(pclassdesc*, pclassdesc) : pclassdesc*
def $unset_replace_class(eps, pclassdesc) = eps
def $unset_replace_class(pclassdesc_old :: pclassdesc_tail*, pclassdesc) = pclassdesc :: pclassdesc_tail*
  -- if pclassdesc_old.ORIGIN = pclassdesc.ORIGIN
def $unset_replace_class(pclassdesc_old :: pclassdesc_tail*, pclassdesc) = pclassdesc_old :: $unset_replace_class(pclassdesc_tail*, pclassdesc)
  -- if pclassdesc_old.ORIGIN =/= pclassdesc.ORIGIN
'''


def dynamic_assertions(initial, expected):
    return [*common.start(initial, 'FutureUnsetBase359', unset=True),
        '$object_name(S_before, n_parent) = $ptascii("FutureUnsetDerived359")',
        'pinstancestorage.SLOTS = [ppropertyslot_number, ppropertyslot_dynamic]',
        'ppropertyslot_number.DECL =/= eps',
        'ppropertyslot_dynamic.DECL = eps',
        'ppropertyslot_dynamic.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
        '$instance_storage_declared_index(pinstancestorage.SLOTS, ptbytes_key, 0) = (0)',
        'nat_order* = $instance_storage_order(pinstancestorage.SLOTS, true, 0) ++ $instance_storage_order(pinstancestorage.SLOTS, false, 0)',
        'nat_order* = [1, 0]',
        'nat_order*[0:pinstancestorage.NEXT] = [1]',
        '~(0 <- nat_order*[0:pinstancestorage.NEXT])',
        '$instance_storage_initial_desc(S_before, n_parent, ptbytes_key) = eps',
        'S_missing = S_before[.FRAMES = $instance_test_without_frames(S_before.FRAMES)]',
        '$instance_storage_for(S_missing, n_parent) = eps',
        '$instance_storage_unset_desc(S_missing, n_parent, ptbytes_key) = eps',
        '~$call_descriptors_valid(S_missing)',
        'S_duplicate = S_before[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_before.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        '$instance_storage_unset_desc(S_duplicate, n_parent, ptbytes_key) = eps',
        '~$call_descriptors_valid(S_duplicate)',
        # This constructed endpoint has identical unset images; only the
        # actual release prefix distinguishes it from the genuine frontier.
        'pinstancestorage_consumed = pinstancestorage[.NEXT = 2]',
        'S_consumed = S_before[.FRAMES = pframe_owner[.TODO = $initial_replace_stage(pframe_owner.TODO, pinstancestorage_consumed)] :: pframe_tail*]',
        '$instance_storage_state_valid(S_consumed)',
        '$objectprops_at(S_consumed.OBJECTPROPS, n_parent) = (ppropertyslot_live*)',
        '$property_slot_at(ppropertyslot_live*, ptbytes_key) = (ppropertyslot_number)',
        'ppropertyslot_number.STATE = PROP_UNSET',
        '$instance_storage_unset_desc(S_consumed, n_parent, ptbytes_key) = eps',
        '$property_read(S_consumed, POBJECT n_parent, ptbytes_key, z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        'pinstancestorage_bad = pinstancestorage[.NEXT = 3]',
        'S_bad = S_before[.FRAMES = pframe_owner[.TODO = $initial_replace_stage(pframe_owner.TODO, pinstancestorage_bad)] :: pframe_tail*]',
        '~$instance_storage_state_valid(S_bad)',
        '$instance_storage_unset_desc(S_bad, n_parent, ptbytes_key) = eps',
        '$instance_storage_unset_desc(S_before, n_parent, $ptascii("dynamic")) = eps',
        '$property_read(S_before, POBJECT n_parent, $ptascii("dynamic"), z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        '$property_quiet(S_before, POBJECT n_parent, ptbytes_key, z) = S_before[.RESULT = KNOWN PNULL]',
        '$property_reference_fetch_unshared(S_before, n_parent, ptbytes_key, z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        # Guard-only forged method metadata; no getter body is executed.
        'S_before.OBJECTS[n_parent] = INSTANCE porigin_parent',
        '$class_at(S_before.CLASSES, porigin_parent) = (pclassdesc_parent)',
        '$effective_method(S_before, porigin_parent, $ptascii("__get"), |S_before.CLASSES|) = eps',
        '$destructor_method(S_before, n_child) = (pmethoddesc_child)',
        'pmethoddesc_getter = pmethoddesc_child[.NAME = $ptascii("__get")]',
        'S_getter = S_before[.CLASSES = $unset_replace_class(S_before.CLASSES, pclassdesc_parent[.METHODS = pmethoddesc_getter :: pclassdesc_parent.METHODS])]',
        '$instance_storage_state_valid(S_getter)',
        '$effective_method(S_getter, porigin_parent, $ptascii("__get"), |S_getter.CLASSES|) = (pmethoddesc_getter)',
        '$instance_storage_unset_desc(S_getter, n_parent, ptbytes_key) = eps',
        *base.finish('S_throw', expected),
        '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)']


def pending_assertions(initial, expected):
    clauses = common.pending_assertions(initial, expected, unset=True)
    index = clauses.index('$instance_storage_initial_desc(S_second, n_parent, ptbytes_key) = eps')
    clauses[index:index] = [
        '$property_slot_at(pinstancestorage.SLOTS, ptbytes_key) = (ppropertyslot_number)',
        'ppropertyslot_number.STATE = PROP_UNSET',
        '$instance_storage_declared_index(pinstancestorage.SLOTS, ptbytes_key, 0) = (1)',
        'nat_order* = $instance_storage_order(pinstancestorage.SLOTS, true, 0) ++ $instance_storage_order(pinstancestorage.SLOTS, false, 0)',
        '1 <- nat_order*[0:3]',
        '$instance_storage_unset_desc(S_second, n_parent, ptbytes_key) = eps']
    return clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='instance-future-unset-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
              'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
              'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        body = {'dynamic': dynamic_assertions, 'pending': pending_assertions}[args.group](initial, sources.EXPECTED[CASES[args.group]])
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
                          ''.join('  -- if '+clause+'\n' for clause in clauses)+
                          '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture), assertions=len(clauses))
        if not args.prepare_only:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
