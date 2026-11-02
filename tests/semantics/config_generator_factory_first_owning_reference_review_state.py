#!/usr/bin/env python3
"""A BYVAL factory returns a BYREF Generator whose first ARRAY copy survives real storage."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_factory_first_owning_reference_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-factory-first-owning-reference-array-cow-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a91_peer_echo(pstate, ptbytes) : bool
def $a91_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a91_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 9100) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 9101) = $a91_peer_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 9102) = $a91_peer_echo(S, $ptascii("W:"))
def $list_warning_frontier(S, 9103) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 9104) = $a91_peer_echo(S, $ptascii("T:"))
def $list_warning_frontier(S, 9105) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 9106) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 9107) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 9108) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 9109) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 9110) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 9111) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 9112) = $a91_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 9113) = $a91_peer_echo(S, $ptascii("L:"))
def $list_warning_frontier(S, 9114) = $a91_peer_echo(S, $ptascii("R:"))
'''


def row(state, array, value, marker):
    return (f'{state}.ARRAYS[{array}].ITEMS = '
            f'[ENTRY (KINT 0) (DIRECT (PINT {value})), '
            f'ENTRY (KINT 1) (DIRECT (POBJECT {marker}))]')


def watch(state, name, cell_id, watch_id, value):
    return [f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({cell_id})',
            f'{state}.STORE[{cell_id}] = DEFINED (POBJECT {watch_id})',
            f'$weakref_get({state},{watch_id}) = {value}']


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 9100, 'S_first') + [
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_first*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        'pconfiggenerator.CALL.KIND = INTRINSIC_INI_SET',
        '$config_generator_owning_input(pconfiggenerator)',
        '$config_generator_input_nodes(pconfiggenerator) = [HOBJECT n_generator]',
        '$heap_count(HOBJECT n_generator,$config_generator_nodes(pconfiggenerator,"ready")) = 2',
        '$intrinsic_argument(S_first,pconfiggenerator.CALL.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath,z))',
        '$source_emission_noarg_call(S_first,n_source,pcpath,expression) = (z_call)',
        '$code_at(S_first.CODE,n_source) = (pcode)',
        '$source_unit(S_first.SOURCES,n_source) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath) = (UNPACK_VAR)',
        '$code_name(pcode.NAMES,pcpath) = ((ptbytes_name,eps))',
        '$call_target(S_first,ptbytes_name,eps) = (pfunction_factory)',
        'pfunction_factory.SIGNATURE.PARAMETERS = eps',
        '~pfunction_factory.SIGNATURE.BYREF',
        '~$function_generator(S_first,pfunction_factory)',
        'S_first.OBJECTS[n_generator] = GENERATOR pgenerator_first',
        '$function_at($all_functions(S_first),pgenerator_first.FUNCTION) = (pfunction_generator)',
        'pfunction_generator.SIGNATURE.PARAMETERS = eps',
        'pfunction_generator.SIGNATURE.BYREF',
        '$function_generator(S_first,pfunction_generator)',
        'pfunction_generator =/= pfunction_factory',
        '~$config_generator_temporary_reference_input(S_first,pconfiggenerator)',
        '$config_generator_factory_reference_input(S_first,pconfiggenerator)',
        '~$config_generator_reference_owning_source(S_first,pconfiggenerator)',
        '$config_generator_history(S_first,pconfiggenerator)',
        'S_first.CURRENT = eps',
        'S_first.FRAMES = eps',
        'pgenerator_first.VALUE = eps',
        'pgenerator_first.REFCELL = (n_payloadref)',
        'pgenerator_first.KEY = (PINT 0)',
        '$ordinary_reference_value(S_first,n_payloadref) = (PARRAY n_old)',
        row('S_first', 'n_old', 13, 'n_oldmarker'),
        '$config_generator_value(S_first,pconfiggenerator) = (PARRAY n_old)',
        '$config_iterator_argument(S_first,PARRAY n_old)',
        owners('S_first', 'HOBJECT n_generator', 2),
        owners('S_first', 'HARRAY n_old', 1),
    ] + watch('S_first', 'genWatch', 'n_genwatch_cell', 'n_genwatch',
              'POBJECT n_generator') + watch('S_first', 'oldWatch', 'n_oldwatch_cell', 'n_oldwatch',
              'POBJECT n_oldmarker') + [
        '$lookup($global_table_view(S_first).ENV,$ptascii("result")) = (n_result_cell)',
        'S_first.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_debt = S_first[.LITERALREFDEBTS = [n_payloadref]]',
        '$config_generator_value(S_debt,pconfiggenerator) = eps',
        'PhpStep: S_first ~> S_sent_first',
        'S_sent_first.TODO = (CONFIG_GENERATOR pconfiggenerator_one "next") :: ptask_first*',
        'pconfiggenerator_one = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old))]]',
        '$config_generator_temporary_reference_owning_first_items(S_sent_first,pconfiggenerator_one)',
        '$config_generator_factory_reference_input(S_sent_first,pconfiggenerator_one)',
        '$config_generator_history(S_sent_first,pconfiggenerator_one)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_one "next") = [HOBJECT n_generator,HOBJECT n_generator,HARRAY n_old]',
        owners('S_sent_first', 'HARRAY n_old', 2),
        '$weakref_get(S_sent_first,n_genwatch) = POBJECT n_generator',
    ] + public('S_first') + public('S_sent_first') + seek('S_sent_first', 9101, 'S_cow') + [
        '$ordinary_reference_value(S_cow,n_payloadref) = (PARRAY n_new)',
        'n_new =/= n_old',
        row('S_cow', 'n_old', 13, 'n_oldmarker'),
        row('S_cow', 'n_new', 31, 'n_newmarker'),
        '$node_children(S_cow,HCELL n_payloadref) = [HARRAY n_new]',
        owners('S_cow', 'HARRAY n_old', 1),
        owners('S_cow', 'HARRAY n_new', 1),
        owners('S_cow', 'HOBJECT n_oldmarker', 1),
        owners('S_cow', 'HOBJECT n_newmarker', 1),
        '$weakref_get(S_cow,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_cow,n_oldwatch) = POBJECT n_oldmarker',
    ] + watch('S_cow', 'newWatch', 'n_newwatch_cell', 'n_newwatch',
              'POBJECT n_newmarker') + public('S_cow') + seek('S_cow', 9102, 'S_overwrite') + [
        '$ordinary_reference_value(S_overwrite,n_payloadref) = (PINT 9)',
        '$weakref_get(S_overwrite,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_overwrite,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_overwrite,n_newwatch) = PNULL',
        '~((HARRAY n_new) <- S_overwrite.ALLOCATIONS)',
        '~((HOBJECT n_newmarker) <- S_overwrite.ALLOCATIONS)',
        owners('S_overwrite', 'HARRAY n_old', 1),
    ] + public('S_overwrite') + seek('S_overwrite', 9103, 'S_second') + [
        'S_second.TODO = (CONFIG_GENERATOR pconfiggenerator_one "ready") :: ptask_second*',
        'S_second.OBJECTS[n_generator] = GENERATOR pgenerator_second',
        'pgenerator_second.VALUE = eps',
        'pgenerator_second.REFCELL = (n_valueref)',
        'pgenerator_second.KEY = (PINT 1)',
        'n_valueref =/= n_payloadref',
        '$ordinary_reference_value(S_second,n_valueref) = (PINT 7)',
        '$config_generator_value(S_second,pconfiggenerator_one) = (PINT 7)',
        '$config_generator_temporary_reference_owning_first_items(S_second,pconfiggenerator_one)',
        '$config_generator_factory_reference_input(S_second,pconfiggenerator_one)',
        '$weakref_get(S_second,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_second,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_second,n_newwatch) = PNULL',
        owners('S_second', 'HOBJECT n_generator', 2),
        owners('S_second', 'HARRAY n_old', 1),
        'PhpStep: S_second ~> S_sent_second',
        'S_sent_second.TODO = (CONFIG_GENERATOR pconfiggenerator_two "next") :: ptask_second*',
        'pconfiggenerator_two = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old)),ENTRY (KINT 1) (DIRECT (PINT 7))]]',
        '$config_generator_temporary_reference_owning_first_completed(S_sent_second,pconfiggenerator_two)',
        '$config_generator_history(S_sent_second,pconfiggenerator_two)',
        '$weakref_get(S_sent_second,n_genwatch) = POBJECT n_generator',
    ] + public('S_second') + public('S_sent_second') + seek('S_sent_second', 9104, 'S_terminal') + [
        '$ordinary_reference_value(S_terminal,n_valueref) = (PINT 8)',
        'S_terminal.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_terminal,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_terminal,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_terminal,n_newwatch) = PNULL',
    ] + public('S_terminal') + seek('S_terminal', 9105, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_two "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_valueref)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_finish,n_valueref) = (PINT 8)',
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_valueref]',
        row('S_finish', 'n_old', 13, 'n_oldmarker'),
        '$config_generator_temporary_reference_owning_first_completed(S_finish,pconfiggenerator_two)',
        '$config_generator_factory_reference_input(S_finish,pconfiggenerator_two)',
        '$config_generator_reference_history(S_finish,pconfiggenerator_two)',
        '$config_generator_reference_storage(S_finish,pconfiggenerator_two)',
        '$config_generator_storage_child(S_finish,pconfiggenerator_two)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_two)',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_valueref', 1),
        owners('S_finish', 'HARRAY n_old', 1),
        'S_finish.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_finish,n_genwatch) = POBJECT n_generator',
    ] + public('S_finish') + budget('S_finish', 'S_data_budget') + seek('S_finish', 9106, 'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator_two "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator_two,"input-release")',
        '$config_generator_nodes(pconfiggenerator_two,"input-release") = [HOBJECT n_generator,HARRAY n_old]',
        '$ordinary_reference_value(S_input,n_valueref) = (PINT 8)',
        '$config_generator_temporary_reference_owning_first_completed(S_input,pconfiggenerator_two)',
        '$config_generator_reference_storage(S_input,pconfiggenerator_two)',
        '$config_generator_last_input_allowed(S_input,pconfiggenerator_two)',
        '~$config_generator_finish_allowed(S_input,pconfiggenerator_two)',
        owners('S_input', 'HOBJECT n_generator', 1),
        owners('S_input', 'HCELL n_valueref', 1),
        owners('S_input', 'HARRAY n_old', 1),
        '$weakref_get(S_input,n_genwatch) = POBJECT n_generator',
        'S_input_debt = S_input[.LITERALREFDEBTS = [n_valueref]]',
        '~$config_generator_reference_storage(S_input_debt,pconfiggenerator_two)',
        '~$config_generator_last_input_allowed(S_input_debt,pconfiggenerator_two)',
    ] + public('S_input') + budget('S_input', 'S_input_budget') + seek('S_input', 9107, 'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$ordinary_reference_value(S_slot1,n_valueref) = (PINT 8)',
        '$config_generator_reference_history(S_slot1,pconfiggenerator_two)',
        '$weakref_get(S_slot1,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_slot1,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_slot1,n_newwatch) = PNULL',
        owners('S_slot1', 'HOBJECT n_generator', 1),
        owners('S_slot1', 'HCELL n_valueref', 1),
        owners('S_slot1', 'HARRAY n_old', 1),
    ] + public('S_slot1') + seek('S_slot1', 9108, 'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        '~((HCELL n_valueref) <- S_slot2.ALLOCATIONS)',
        '$node_children(S_slot2,HOBJECT n_generator) = eps',
        '(HOBJECT n_generator) <- S_slot2.ALLOCATIONS',
        '(HARRAY n_old) <- S_slot2.ALLOCATIONS',
        '$weakref_get(S_slot2,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_slot2,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_slot2,n_newwatch) = PNULL',
        owners('S_slot2', 'HOBJECT n_generator', 1),
        owners('S_slot2', 'HARRAY n_old', 1),
    ] + public('S_slot2') + seek('S_slot2', 9109, 'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator_two "storage-released") :: ptask_retired*',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '~((HCELL n_valueref) <- S_retired.ALLOCATIONS)',
        '(HARRAY n_old) <- S_retired.ALLOCATIONS',
        '$weakref_get(S_retired,n_genwatch) = PNULL',
        '$weakref_get(S_retired,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_retired,n_newwatch) = PNULL',
        '$config_generator_factory_reference_input(S_retired,pconfiggenerator_two)',
        '$config_generator_reference_history(S_retired,pconfiggenerator_two)',
        '$config_generator_temporary_reference_owning_first_completed(S_retired,pconfiggenerator_two)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator_two)',
        '$config_generator_valid(S_retired,pconfiggenerator_two,"storage-released")',
        '~$config_generator_reference_storage(S_retired,pconfiggenerator_two)',
    ] + public('S_retired') + seek('S_retired', 9110, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_two "invoke") :: ptask_invoke*',
        '$config_generator_valid(S_invoke,pconfiggenerator_two,"invoke")',
        '$config_pack_prefix(pconfiggenerator_two.CALL,pconfiggenerator_two.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall_prefix.SENT = [NAMED_SENT (KNOWN (PARRAY n_old)),NAMED_SENT (KNOWN (PINT 7))]',
        '$weakref_get(S_invoke,n_genwatch) = PNULL',
        '$weakref_get(S_invoke,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_invoke,n_newwatch) = PNULL',
        '~((HOBJECT n_generator) <- S_invoke.ALLOCATIONS)',
        '~((HCELL n_valueref) <- S_invoke.ALLOCATIONS)',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old)),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        row('S_error', 'n_old', 13, 'n_oldmarker'),
        '$weakref_get(S_error,n_genwatch) = PNULL',
        '$weakref_get(S_error,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_error,n_newwatch) = PNULL',
    ] + public('S_invoke') + seek('S_invoke', 9111, 'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator_two "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_temporary_reference_owning_first_completed(S_popped,pconfiggenerator_two)',
        '$config_generator_retired_scope(S_popped,pconfiggenerator_two)',
        '~$config_generator_reference_storage(S_popped,pconfiggenerator_two)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_two)',
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_two,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '$weakref_get(S_raw,n_genwatch) = PNULL',
        '$weakref_get(S_raw,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_raw,n_newwatch) = PNULL',
    ] + public('S_throw') + public('S_raw') + seek('S_raw', 9112, 'S_catch') + [
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        '$weakref_get(S_catch,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_catch,n_newwatch) = PNULL',
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        '~((HCELL n_valueref) <- S_catch.ALLOCATIONS)',
    ] + public('S_catch') + seek('S_catch', 9113, 'S_later') + [
        '$weakref_get(S_later,n_genwatch) = PNULL',
        '$weakref_get(S_later,n_oldwatch) = PNULL',
        '$weakref_get(S_later,n_newwatch) = PNULL',
        '~((HARRAY n_old) <- S_later.ALLOCATIONS)',
        '~((HOBJECT n_oldmarker) <- S_later.ALLOCATIONS)',
    ] + public('S_later') + seek('S_later', 9114, 'S_recovery') + [
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout, [
        'HOBJECT n_generator', 'HCELL n_payloadref', 'HCELL n_valueref',
        'HARRAY n_old', 'HARRAY n_new',
        'HOBJECT n_oldmarker', 'HOBJECT n_newmarker', 'HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
