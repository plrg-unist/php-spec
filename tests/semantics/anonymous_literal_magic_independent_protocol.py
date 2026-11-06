#!/usr/bin/env python3
"""Compiled literal carriers retain their real named table through child ownership."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_literal_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'named-literal-carriers-closure-table-retirement'
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) '
          '-- if S.CURRENT = (pcallcontext) '
          '-- if pcallcontext.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue*')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") '
         '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, RETURN)
PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, CHILD).replace('$factory182_', '$literal201_child_')


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        '$ppmethod_call_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_return_found = $factory182_seek(S_initial,4096)',
        'S_return_found.COMPLETION = BUDGET',
        'S = S_return_found[.COMPLETION = NORMAL]', RETURN,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'n_literal* = $ptascii("BYTE") ++ [128]',
        'pvalue* = [pvalue_string,pvalue_float]',
        'pvalue_string = PSTRING_CARRIER INTERNED_STRING n_literal*',
        'pvalue_float = PFLOAT 4609434218613702656',
        'pmagicmethodcall.ARGUMENTS = [phpType7_first,phpType7_later]',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_first)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_later)',
        '$compiled_read(S,porigin_first) = (PSTRING n_literal*)',
        '$compiled_string_value(S,porigin_first,PSTRING n_literal*) = pvalue_string',
        '$compiled_read(S,porigin_later) = (pvalue_float)',
        '$compiled_effects(S,porigin_first) = eps',
        '$compiled_effects(S,porigin_later) = eps',
        '$string_carrier_valid(S,pvalue_string)',
        'S.STRINGDATA = eps',
        '$value_nodes(pvalue_string) = eps', '$value_nodes(pvalue_float) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN pvalue_float]) = (pvalue*)',
        'n_arguments = n_named',
        'S.FRAMES = pframe :: pframe_tail*',
        '$magic_named_frame(S,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_buffer(S,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_keys(pmagicmethodcall.ARGUMENTS,0,false,eps) = ([KSTRING $ptascii("first"),KSTRING $ptascii("later")])',
        'S.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT pvalue_string),ENTRY (KSTRING $ptascii("later")) (DIRECT pvalue_float)]',
        '$lookup(S.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        '$node_children(S,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_arguments) = 3',
        '$object_body(S.OBJECTS[n_closure]) = REALCLOSURE pfunction_closure.ORIGIN ([DIRECT (PARRAY n_arguments),DIRECT (PSTRING $ptascii("MiSsInG"))]) eps',
        '$node_children(S,HOBJECT n_closure) = [HARRAY n_arguments]',
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        '$closure_scope_at(S.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_base.ORIGIN',
        'pclosurescope.CALLED = pclassdesc_called.ORIGIN',
        'pclosurescope.RECEIVER = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$node_children(S,HCELL n_owner_cell) = eps',
        '$task_nodes(MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue*) = [HARRAY n_named,HOBJECT pmagicmethodcall.OBJECT]',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S.CURRENT) = eps',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$factory182_output(S.EVENTS) = $ptascii("MAGIC;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$closure_state_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        '$magic_method_value(S,PINT 1)',
        '$magic_method_value(S,POBJECT pmagicmethodcall.OBJECT)',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 1),KNOWN pvalue_float]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT pmagicmethodcall.OBJECT),KNOWN pvalue_float]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN (PINT 1)]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN (PFLOAT 4607182418800017408)]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("BAD")),KNOWN pvalue_float]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PSTRING n_literal*),KNOWN pvalue_float]) = eps',
        '$magic_method_collected_values(S[.POOLS = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 1),KNOWN (PINT 2)]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,[phpType7_later,phpType7_first],[KNOWN pvalue_string,KNOWN pvalue_float]) = eps',
        'S_request = S[.STRINGDATA = [n_literal*]]',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING 0) n_literal*',
        '$string_carrier_valid(S_request,pvalue_request)',
        '$magic_method_primitive(S_request,pvalue_request)',
        '$magic_method_collected_values(S_request,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_request,KNOWN pvalue_float]) = eps',
        '~$magic_method_value(S,pvalue_string)',
        '~$magic_method_value(S,pvalue_float)',
        '~$magic_method_flat_array(S,n_arguments)',
        'S_child_found = $literal201_child_seek(S,4096)',
        'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        'S_child.FRAMES = eps',
        '$lookup(S_child.ENV,$ptascii("factory")) = eps',
        '$lookup(S_child.ENV,$ptascii("child")) = (n_child_cell)',
        'S_child.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_child.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$heap_owners($heap_graph(S_child),HOBJECT n_child) = 1',
        '$objectprops_at(S_child.OBJECTPROPS,n_child) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_child,HOBJECT n_child) = [HARRAY n_arguments]',
        '$node_children(S_child,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_child),HARRAY n_arguments) = 1',
        'S_child.ARRAYS[n_arguments] = S.ARRAYS[n_arguments]',
        'S_child.STRINGDATA = eps',
        '~((HOBJECT n_closure) <- S_child.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_child.ALLOCATIONS)',
        '$factory182_output(S_child.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']).rsplit(b'CHILD;', 1)[0], filename),
        '$call_descriptors_valid(S_child)', '$closure_state_valid(S_child)',
        '$class_state_valid(S_child)', '$gc_state_valid(S_child)', '$heap_valid($heap_graph(S_child))',
        'S_split = $drive_steps(S_child,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_child,4098)', 'S_full = S_done',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
