#!/usr/bin/env python3
"""Source-reached static setter denial, previous identity and saved-caller checks."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
from static_set_access import CASES, ROOT, inputs, sha
from typed_static_string_protocol import PREFIX as STRING_PREFIX, initial_checks, valid

STAGES = ['reference-uninitialized-error-chain', 'dimension-null-error-chain',
          'reference-nullable-initialization', 'string-callback-denied',
          'private-string-callback-allowed', 'protected-string-callback-allowed', 'reference-return-denied',
          'receiver-rhs-live-alias', 'receiver-uninitialized-unset', 'receiver-direct-demands',
          'unset-continuation-property', 'unset-continuation-static']
PREFIX = STRING_PREFIX + r'''
dec $set_protocol_phase(pstate,nat) : bool
def $set_protocol_phase(S,0) = true
  -- if S.TODO = (PROPERTY_REF_FETCH z) :: ptask_tail*
  -- if S.BASE = BASE_CLASS_STATIC porigin_requested ptbytes
def $set_protocol_phase(S,1) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_DIM (BASE_CLASS_STATIC porigin_requested ptbytes) poperand_key z_key) z b) :: ptask_tail*
def $set_protocol_phase(S,2) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_CLASS_STATIC porigin_requested ptbytes) z b) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n_object)
def $set_protocol_phase(S,3) = true
  -- if S.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING poperand_class poperand_name) n_cell z) :: ptask_tail*
def $set_protocol_phase(S,4) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase poperand z_receiver) z b) :: ptask_tail*
def $set_protocol_phase(S,5) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_PROPERTY_PENDING pbase poperand z_receiver
def $set_protocol_phase(S,6) = true
  -- if S.TODO = (FOREACH_NEXT n_iterator (HCELL n_cell) statement porigin? z) :: ptask_tail*
def $set_protocol_phase(S,7) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_PROPERTY (POBJECT n_object) ptbytes
def $set_protocol_phase(S,8) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_CLASS_STATIC porigin ptbytes
def $set_protocol_phase(S,n) = false -- otherwise
dec $set_protocol_seek(pstate,nat,nat) : pstate
def $set_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $set_protocol_seek(S,n_phase,n) = S
  -- if $set_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $set_protocol_seek(S,n_phase,0) = S
  -- if ~$set_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $set_protocol_seek(S,n_phase,n) = $set_protocol_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$set_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def before(initial, phase):
    return ['S_initial = ' + initial,
            'S_found = $set_protocol_seek(S_initial,' + str(phase) + ',4096)',
            'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
            'S_before = S_found[.COMPLETION = NORMAL]',
            '$set_protocol_phase(S_before,' + str(phase) + ')',
            'S_before.CLASSSTATICS = [pclassstatic]',
            '$class_static_active_desc(S_before,S_before.CLASSNAMES,pclassstatic.DECL) = (ppropertydesc)',
            'S_before.CLASSES = [pclassdesc_a]',
            'pclassdesc_a.PROPERTIES = [ppropertydesc]',
            '~$class_static_set_allowed(S_before,ppropertydesc)',
            *valid('S_before'),
            '~$class_state_valid(S_before[.CLASSES = [pclassdesc_a[.PROPERTIES = [ppropertydesc[.SETVISIBILITY = (PROPERTY_PROTECTED)]]]]])',
            '~$class_state_valid(S_before[.CLASSES = [pclassdesc_a[.PROPERTIES = [ppropertydesc[.FINAL = false]]]]])',
            'S_after_found = $drive_steps(S_before,1)',
            'S_after_found.COMPLETION = BUDGET',
            'S_after = S_after_found[.COMPLETION = NORMAL]',
            'S_after.TODO = (THROW_SEARCH n_new) :: ptask_tail*',
            'S_after.OBJECTS[n_new] = THROWABLE pthrowable_new',
            'pthrowable_new.KIND = "Error"',
            'pthrowable_new.ORIGIN = S_before.ORIGIN',
            '$throwable_field(S_after,n_new,"line") = PINT 1',
            '$throwable_field(S_after,n_new,"message") = PSTRING $ptascii("Cannot indirectly modify private(set) property A::$p from global scope")',
            *valid('S_after')]


def checks(initial, name):
    if name.startswith('unset-continuation-'):
        phase = 7 if name == 'unset-continuation-property' else 8
        result = ['S_initial = ' + initial,
                  'S_found = $set_protocol_seek(S_initial,' + str(phase) + ',4096)',
                  'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
                  'S_before = S_found[.COMPLETION = NORMAL]',
                  'S_before.TODO = UNSET_ARRAY :: ptask_tail*',
                  *valid('S_before'),
                  'S_after_found = $drive_steps(S_before,1)',
                  'S_after_found.COMPLETION = BUDGET',
                  'S_after = S_after_found[.COMPLETION = NORMAL]',
                  'S_after.CLASSSTATICS = S_before.CLASSSTATICS',
                  'S_after.BASE = BASE_VALUE (KNOWN PNULL)']
        if phase == 7:
            result += ['S_before.BASE = BASE_PROPERTY (POBJECT n_object) $ptascii("x")',
                       'S_after.TODO = ptask_tail*',
                       '$objectprops_record_at(S_after.OBJECTPROPS,n_object) = (pobjectprops)',
                       '$property_slot_at(pobjectprops.SLOTS,$ptascii("x")) = (ppropertyslot)',
                       'ppropertyslot.STATE = PROP_UNSET',
                       'S_after.OBJECTS = S_before.OBJECTS']
        else:
            result += ['S_before.BASE = BASE_CLASS_STATIC porigin_class $ptascii("q")',
                       'S_after.TODO = (THROW_SEARCH n_new) :: ptask_tail*',
                       '$throwable_field(S_after,n_new,"message") = PSTRING $ptascii("Attempt to unset static property A::$q")',
                       '$throwable_field(S_after,n_new,"line") = PINT 1']
        result += [*valid('S_after'),
                   'S_done = $drive_steps(S_after,4096)',
                   'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
                   '$static_protocol_output(S_done.EVENTS) = $ptascii("N|unset|P|Cannot access private property O::$y|S|Attempt to unset static property A::$q|A|Cannot indirectly modify private(set) property A::$p from global scope|1|1")',
                   *valid('S_done')]
        return result, 'S_done'
    if name == 'receiver-direct-demands':
        result = ['S_initial = ' + initial,
                  'S_found = $set_protocol_seek(S_initial,6,4096)',
                  'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
                  'S_before = S_found[.COMPLETION = NORMAL]',
                  'S_before.TODO = (FOREACH_NEXT n_iterator (HCELL n_cell) statement porigin? z) :: ptask_tail*',
                  'S_before.CLASSSTATICS = [pclassstatic]',
                  'pclassstatic.STATE = PROP_VALUE (DIRECT (POBJECT n_object))',
                  '$objectprops_record_at(S_before.OBJECTPROPS,n_object) = (pobjectprops)',
                  '$property_slot_at(pobjectprops.SLOTS,$ptascii("a")) = (ppropertyslot)',
                  'ppropertyslot.STATE = PROP_VALUE (ALIAS n_cell)',
                  'ppropertyslot.DECL = (porigin_decl)',
                  'S_before.STORE[n_cell] = DEFINED (PARRAY n_array)',
                  'n_cell <- S_before.REFCELLS /\\ (HCELL n_cell) <- S_before.ALLOCATIONS',
                  '$propref_at(S_before.PROPREFS,n_cell) = (ppropref)',
                  'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object $ptascii("a") porigin_decl]',
                  'S_before.ITERATORS = [ITERATOR n_iterator n_array true ([(CURSOR n_array 0)])]',
                  '$heap_count(HCELL n_cell,$heap_graph(S_before).ROOTS) = 1',
                  '$heap_owners($heap_graph(S_before),HCELL n_cell) = 2',
                  *valid('S_before'),
                  'S_done = $drive_steps(S_before,4096)',
                  'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.ITERATORS = eps',
                  '$static_protocol_output(S_done.EVENTS) = $ptascii("4|5|7|3|unset")',
                  '$objectprops_record_at(S_done.OBJECTPROPS,n_object) = (pobjectprops_done)',
                  '$property_slot_at(pobjectprops_done.SLOTS,$ptascii("a")) = (ppropertyslot_done)',
                  'ppropertyslot_done.STATE = PROP_VALUE (ALIAS n_cell)',
                  'S_done.STORE[n_cell] = DEFINED (PARRAY n_array)',
                  '$propref_at(S_done.PROPREFS,n_cell) = (ppropref)',
                  '$heap_count(HCELL n_cell,$heap_graph(S_done).ROOTS) = 0',
                  '$heap_owners($heap_graph(S_done),HCELL n_cell) = 1',
                  *valid('S_done')]
        return result, 'S_done'
    if name.startswith('receiver-'):
        phase = 4 if name == 'receiver-rhs-live-alias' else 5
        result = ['S_initial = ' + initial,
                  'S_found = $set_protocol_seek(S_initial,' + str(phase) + ',4096)',
                  'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
                  'S_before = S_found[.COMPLETION = NORMAL]',
                  'S_before.CURRENT = eps /\\ S_before.FRAMES = eps',
                  'S_before.CLASSSTATICS = [pclassstatic]',
                  '$class_static_active_desc(S_before,S_before.CLASSNAMES,pclassstatic.DECL) = (ppropertydesc)',
                  '~$class_static_set_allowed(S_before,ppropertydesc)',
                  *valid('S_before')]
        if phase == 4:
            result += [
                'S_before.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING (BASE_CLASS_STATIC_PENDING poperand_class poperand_static) poperand_name z_receiver) z false) :: ptask_tail*',
                'poperand_class = KNOWN (PSTRING $ptascii("A")) /\\ poperand_static = KNOWN (PSTRING $ptascii("p")) /\\ poperand_name = KNOWN (PSTRING $ptascii("x"))',
                'S_before.RESULT = KNOWN (PINT 3)',
                'pclassstatic.STATE = PROP_VALUE (ALIAS n_cell)',
                'S_before.STORE[n_cell] = DEFINED (POBJECT n_object)',
                '(HCELL n_cell) <- S_before.ALLOCATIONS /\\ (HOBJECT n_object) <- S_before.ALLOCATIONS',
                '~$class_static_raw_object(S_before,pclassstatic.DECL)',
                '$static_protocol_output(S_before.EVENTS) = $ptascii("R")',
                '~$call_descriptors_valid(S_before[.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING (BASE_CLASS_STATIC_PENDING (KNOWN (PSTRING $ptascii("B"))) poperand_static) poperand_name z_receiver) z false) :: ptask_tail*])',
                '~$call_descriptors_valid(S_before[.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING (BASE_CLASS_STATIC_PENDING poperand_class (KNOWN (PSTRING $ptascii("q")))) poperand_name z_receiver) z false) :: ptask_tail*])',
                '~$call_descriptors_valid(S_before[.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING (BASE_CLASS_STATIC_PENDING poperand_class poperand_static) (KNOWN (PSTRING $ptascii("y"))) z_receiver) z false) :: ptask_tail*])',
                '~$call_descriptors_valid(S_before[.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING (BASE_CLASS_STATIC_PENDING poperand_class poperand_static) poperand_name $(z_receiver + 1)) z false) :: ptask_tail*])',
                'S_after_found = $drive_steps(S_before,1)',
                'S_after_found.COMPLETION = BUDGET',
                'S_after = S_after_found[.COMPLETION = NORMAL]',
                'S_after.TODO = (THROW_SEARCH n_new) :: ptask_after*',
                '$throwable_field(S_after,n_new,"message") = PSTRING $ptascii("Cannot indirectly modify private(set) property A::$p from global scope")',
                'S_after.CLASSSTATICS = S_before.CLASSSTATICS',
                '$property_read(S_after,POBJECT n_object,$ptascii("x"),z).RESULT = KNOWN (PINT 1)',
                '(HCELL n_cell) <- S_after.ALLOCATIONS /\\ (HOBJECT n_object) <- S_after.ALLOCATIONS',
                '$static_protocol_output(S_after.EVENTS) = $ptascii("R")',
                *valid('S_after')]
        else:
            result += [
                'S_before.TODO = UNSET_ARRAY :: ptask_tail*',
                'S_before.BASE = BASE_PROPERTY_PENDING (BASE_CLASS_STATIC_PENDING poperand_class poperand_static) poperand_name z_receiver',
                'poperand_class = KNOWN (PSTRING $ptascii("A")) /\\ poperand_static = KNOWN (PSTRING $ptascii("p")) /\\ poperand_name = KNOWN (PSTRING $ptascii("x"))',
                'pclassstatic.STATE = PROP_INITIAL',
                'S_after_found = $drive_steps(S_before,1)',
                'S_after_found.COMPLETION = BUDGET',
                'S_after = S_after_found[.COMPLETION = NORMAL]',
                'S_after.TODO = ptask_tail*',
                'S_after.CLASSSTATICS = S_before.CLASSSTATICS',
                'S_after.OBJECTS = S_before.OBJECTS',
                '$static_protocol_output(S_after.EVENTS) = eps',
                *valid('S_after')]
        return result, 'S_after'
    if name == 'reference-return-denied':
        result = ['S_initial = ' + initial,
                  'S_found = $set_protocol_seek(S_initial,3,4096)',
                  'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
                  'S_before = S_found[.COMPLETION = NORMAL]',
                  'S_before.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING poperand_class poperand_name) n_cell z) :: ptask_tail*',
                  'poperand_class = KNOWN (PSTRING $ptascii("A")) /\\ poperand_name = KNOWN (PSTRING $ptascii("p"))',
                  'S_before.CURRENT = eps /\\ S_before.FRAMES = eps',
                  'S_before.STORE[n_cell] = DEFINED (PINT 2)',
                  'n_cell <- S_before.REFCELLS /\\ (HCELL n_cell) <- S_before.ALLOCATIONS',
                  '$heap_count(HCELL n_cell,$heap_graph(S_before).ROOTS) = 1',
                  '$heap_owners($heap_graph(S_before),HCELL n_cell) = 1',
                  '$static_protocol_output(S_before.EVENTS) = $ptascii("R")',
                  'S_before.CLASSSTATICS = [pclassstatic]',
                  'pclassstatic.STATE = PROP_VALUE (DIRECT (PINT 1))',
                  'S_before.PROPREFS = eps /\\ S_before.REFCOERCIONS = eps',
                  '$class_static_active_desc(S_before,S_before.CLASSNAMES,pclassstatic.DECL) = (ppropertydesc)',
                  '~$class_static_set_allowed(S_before,ppropertydesc)',
                  *valid('S_before'),
                  '~$call_descriptors_valid(S_before[.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING (KNOWN (PSTRING $ptascii("B"))) poperand_name) n_cell z) :: ptask_tail*])',
                  '~$call_descriptors_valid(S_before[.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING poperand_class (KNOWN (PSTRING $ptascii("q")))) n_cell z) :: ptask_tail*])',
                  'S_after_found = $drive_steps(S_before,1)',
                  'S_after_found.COMPLETION = BUDGET',
                  'S_after = S_after_found[.COMPLETION = NORMAL]',
                  'S_after.TODO = (THROW_SEARCH n_new) :: ptask_tail*',
                  '$throwable_field(S_after,n_new,"message") = PSTRING $ptascii("Cannot indirectly modify private(set) property A::$p from global scope")',
                  'S_after.CLASSSTATICS = S_before.CLASSSTATICS',
                  'S_after.PROPREFS = eps /\\ S_after.REFCOERCIONS = eps',
                  '$static_protocol_output(S_after.EVENTS) = $ptascii("R")',
                  '$heap_count(HCELL n_cell,$heap_graph(S_after).ROOTS) = 0',
                  '~((HCELL n_cell) <- S_after.ALLOCATIONS)',
                  *valid('S_after')]
        return result, 'S_after'
    if name.endswith('string-callback-allowed'):
        result = initial_checks(initial) + [
            'S_assign.CURRENT = (pcallcontext_caller)',
            'pcallcontext_caller.LEXICAL_CLASS = (porigin_caller)',
            '$class_at(S_assign.CLASSES,porigin_caller) = (pclassdesc_caller)',
            '$class_static_active_desc(S_assign,S_assign.CLASSNAMES,pstaticstring.DECL) = (ppropertydesc)',
            '$class_static_set_allowed(S_assign,ppropertydesc)',
            'S_entered_found = $static_protocol_seek(S_pending,2,4096)',
            'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
            'S_entered = S_entered_found[.COMPLETION = NORMAL]',
            'S_entered.CURRENT = (pcallcontext_callback)',
            'pcallcontext_callback.LEXICAL_CLASS = (porigin_callback)',
            'porigin_callback =/= porigin_caller',
            'S_entered.FRAMES = pframe :: pframe_tail*',
            'pframe.CONTEXT = (pcallcontext_caller)',
            '$static_string_record_valid(S_entered,pstaticstring)',
            '~$class_static_set_allowed(S_entered,ppropertydesc)',
            '$static_string_task_valid(S_entered[.CURRENT = pframe.CONTEXT][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO],pstaticstring)',
            *valid('S_entered'),
            '~$call_descriptors_valid(S_entered[.FRAMES = pframe[.CONTEXT = (pcallcontext_caller[.LEXICAL_CLASS = (porigin_callback)])] :: pframe_tail*])',
            '~$call_descriptors_valid(S_entered[.CURRENT = (pcallcontext_callback[.LEXICAL_CLASS = (porigin_caller)])])',
            '~$static_string_target_valid(S_assign[.CURRENT = (pcallcontext_caller[.LEXICAL_CLASS = (porigin_callback)])],pstaticstring)',
            'S_entered.CLASSSTATICS = S_assign.CLASSSTATICS',
        ]
        return result, 'S_entered'
    if name == 'string-callback-denied':
        result = ['S_initial = ' + initial,
                  'S_found = $set_protocol_seek(S_initial,2,4096)',
                  'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
                  'S_before = S_found[.COMPLETION = NORMAL]',
                  'S_before.TODO = (ASSIGN_ARRAY pbase z b) :: ptask_tail*',
                  'S_before.RESULT = KNOWN (POBJECT n_original)',
                  '~$static_string_callback_candidate(S_before)',
                  '$static_string_capture(S_before,pbase,z) = eps',
                  *valid('S_before'),
                  'S_after_found = $drive_steps(S_before,1)',
                  'S_after_found.COMPLETION = BUDGET',
                  'S_after = S_after_found[.COMPLETION = NORMAL]',
                  'S_after.TODO = (THROW_SEARCH n_new) :: ptask_tail*',
                  'S_after.CLASSSTATICS = S_before.CLASSSTATICS',
                  '$throwable_field(S_after,n_new,"message") = PSTRING $ptascii("Cannot modify private(set) property A::$p from global scope")',
                  '$static_protocol_output(S_after.EVENTS) = $ptascii("R")',
                  '$heap_count(HOBJECT n_original,$heap_graph(S_after).ROOTS) = 0',
                  *valid('S_after')]
        return result, 'S_after'
    phase = 1 if name.startswith('dimension') else 0
    result = before(initial, phase)
    if name == 'reference-nullable-initialization':
        result += ['pclassstatic.STATE = PROP_INITIAL',
                   'n_new = |S_before.OBJECTS|',
                   '$throwable_previous_id(S_after,n_new) = eps',
                   'n_cell = |S_before.STORE|',
                   'S_after.CLASSSTATICS = [pclassstatic[.STATE = PROP_VALUE (ALIAS n_cell)]]',
                   'S_after.STORE[n_cell] = DEFINED PNULL',
                   'S_after.PROPREFS = [ppropref]',
                   'ppropref.CELL = n_cell',
                   'ppropref.SOURCES = [CLASS_PROP_SOURCE pclassstatic.DECL]',
                   '$heap_count(HCELL n_cell,$heap_graph(S_after).ROOTS) = 1',
                   '~$class_statics_valid(S_after[.PROPREFS = eps])',
                   'S_after.REFCOERCIONS = eps']
    else:
        old_kind = 'TypeError' if phase == 1 else 'Error'
        old_message = ('Cannot auto-initialize an array inside property A::$p of type ?int'
                       if phase == 1 else 'Cannot access uninitialized non-nullable property A::$p by reference')
        result += ['n_old = |S_before.OBJECTS|',
                   'n_new = $(n_old + 1)',
                   'n_new =/= n_old',
                   'S_after.OBJECTS[n_old] = THROWABLE pthrowable_old',
                   'pthrowable_old.KIND = ' + json.dumps(old_kind),
                   'pthrowable_old.ORIGIN = S_before.ORIGIN',
                   '$throwable_previous_id(S_after,n_new) = (n_old)',
                   '$throwable_previous_id(S_after,n_old) = eps',
                   '$throwable_field(S_after,n_old,"message") = PSTRING $ptascii(' + json.dumps(old_message) + ')',
                   '$throwable_field(S_after,n_old,"line") = PINT 1',
                   '$throwable_field(S_after,n_old,"file") = $throwable_field(S_after,n_new,"file")',
                   '$throwable_field(S_after,n_old,"trace") = PARRAY n_trace_old',
                   '$throwable_field(S_after,n_new,"trace") = PARRAY n_trace_new',
                   'S_after.ARRAYS[n_trace_old].ITEMS = eps /\\ S_after.ARRAYS[n_trace_new].ITEMS = eps',
                   '$trace_graph_valid(S_after,n_trace_old) /\\ $trace_graph_valid(S_after,n_trace_new)',
                   '$throwable_chain_valid(S_after,n_new)',
                   '$heap_count(HOBJECT n_new,$heap_graph(S_after).ROOTS) = 1',
                   '$heap_count(HOBJECT n_old,$heap_graph(S_after).ROOTS) = 0',
                   '$heap_owners($heap_graph(S_after),HOBJECT n_old) = 1',
                   'S_after.CLASSSTATICS = S_before.CLASSSTATICS',
                   'S_after.PROPREFS = S_before.PROPREFS',
                   'S_after.STORE = S_before.STORE',
                   'S_after.REFCOERCIONS = eps']
    return result, 'S_after'


def main():
    import typed_static_invoke_set_protocol as driver
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', help='Comma-separated exact stage IDs')
    parser.add_argument('--elaborate-only', action='store_true',
                        help='Check packets and elaborate unused bodies; no source-native or state execution')
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else STAGES
    assert selected and len(selected) == len(set(selected)) and all(name in STAGES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before_inputs = inputs()
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    out = Path(tempfile.mkdtemp(prefix='static-set-access-protocol-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'selected': selected, 'records': [], 'inputs': before_inputs,
              'mode': 'unused-body-elaboration' if args.elaborate_only else 'source-reached-finite',
              'profile': driver.types.PROFILE, 'cwd': str(ROOT),
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'unused_body_assertions': 0, 'state_assertions_evaluated': 0}
    frontend = adapter = None
    unused = []
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in selected:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES['unset-continuation' if name.startswith('unset-continuation-') else name])
            row = {'id': name, 'source_sha256': sha(path), 'completed': False}
            report['records'].append(row)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            initial = '$php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')'
            clauses, _ = checks(initial, name)
            (directory / 'assertions.json').write_text(json.dumps(clauses, indent=2) + '\n')
            body = 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in clauses)
            fixture = directory / 'protocol.watsup'; fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = $body()\n')
            row.update(assertions=len(clauses), fixture_sha256=sha(fixture))
            if args.elaborate_only:
                unused.append(body.replace('$body', '$unused_' + str(len(unused))))
                report['unused_body_assertions'] += len(clauses)
            else:
                result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    *[str(ROOT / module) for module in modules], str(fixture)], directory / 'numeric', 120, ROOT)
                assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                report['state_assertions_evaluated'] += len(clauses)
                row['passed'] = True
            row['completed'] = True
            print(name, 'prepared' if args.elaborate_only else 'pass', len(clauses), flush=True)
        if args.elaborate_only:
            fixture = out / 'all-unused.watsup'
            fixture.write_text(PREFIX + '\n'.join(unused) + '\ndec $main() : bool\ndef $main() = true\n')
            result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                *[str(ROOT / module) for module in modules], str(fixture)], out / 'unused-numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['elaboration'] = {'completed': True, 'state_assertions_evaluated': 0, 'fixture_sha256': sha(fixture)}
        report['result'] = 'prepared' if args.elaborate_only else 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        cleanup = []
        for worker in [adapter, frontend]:
            if worker is not None:
                try:
                    worker.close()
                except BaseException as error:
                    cleanup.append({'type': type(error).__name__, 'message': str(error)})
        report['cleanup_errors'] = cleanup
        report['after_inputs'] = inputs()
        if cleanup or report['after_inputs'] != before_inputs:
            report['result'] = 'fail'
        report['raw_files'] = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'bytes': p.stat().st_size,
            'mode': oct(p.stat().st_mode & 0o7777)} for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)
    assert report['result'] == ('prepared' if args.elaborate_only else 'pass')


if __name__ == '__main__':
    main()
