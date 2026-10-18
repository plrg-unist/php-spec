#!/usr/bin/env python3
"""Independent physical reference freezing and nested bucket-reference COW."""
import base64
import hashlib
import json
from pathlib import Path

import define_stdclass_protocol as protocol
import define_stdclass_array_review_sources as sources

packet, std, common = protocol.packet, protocol.std, protocol.common
ROOT, text, term = protocol.ROOT, protocol.text, protocol.term
TARGET = 'V66_REVIEW_TREE'
PREFIX = protocol.PREFIX + r'''
dec $test_define_array_bucket(pstate) : bool
def $test_define_array_bucket(S) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_bucket) metadata_variable])) metadata_unset)) :: ptask_tail*
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_bucket)
  -- if $user_constant_at(S.USERCONSTANTS,$ptascii("V66_REVIEW_RIGHT")) = (puserconstant_right)
  -- if S.STORE[n_bucket] = DEFINED puserconstant_right.VALUE
def $test_define_array_bucket(S) = false -- otherwise
dec $test_define_array_bucket_seek(pstate, nat) : pstate
def $test_define_array_bucket_seek(S,0) = S
def $test_define_array_bucket_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_define_array_bucket(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_array_bucket_seek(S,n) = $test_define_array_bucket_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_array_bucket(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def delivery(state, start):
    after = state + '_value'
    values = [*common.reach(state, start, 0, TARGET), *common.public(state),
        f'{state}.TODO = (CONFIG_INVOKE pconfigcall_{state}) :: ptask_{state}*',
        f'$dynamic_global_constant_valid({state},pconfigcall_{state})',
        f'$dynamic_global_constant_value({state},{text(TARGET)}) = (PARRAY n_root)',
        f'H_{state} = $heap_graph({state})',
        f'n_rootowners_{state} = $heap_owners(H_{state},HARRAY n_root)',
        f'n_leftowners_{state} = $heap_owners(H_{state},HOBJECT n_left)',
        f'n_rightowners_{state} = $heap_owners(H_{state},HOBJECT n_right)',
        *common.step(after, state, 'PARRAY n_root'),
        f'{after}.TODO = ptask_{state}*',
        f'H_{after} = $heap_graph({after})',
        f'H_{after}.NODES = H_{state}.NODES', f'H_{after}.EDGES = H_{state}.EDGES',
        f'$heap_owners(H_{after},HARRAY n_root) = $(n_rootowners_{state} + 1)',
        f'$heap_owners(H_{after},HOBJECT n_left) = n_leftowners_{state}',
        f'$heap_owners(H_{after},HOBJECT n_right) = n_rightowners_{state}']
    values += [f'{after}.{field} = {state}.{field}' for field in
        ['ARRAYS', 'OBJECTS', 'OBJECTTABLES', 'OBJECTPROPS', 'STORE', 'REFCELLS',
         'ALLOCATIONS', 'USERCONSTANTS', 'CONSTANTSTDOBJECTS']]
    return values


def checks(initial, stdout):
    assert stdout == b'B|T|L|R|L|R|31|19|tail|kept|A|'
    head, nested, again = [text(key) for key in ('head', 'nested', 'again')]
    values = [*initial, *protocol.reach('S', 'S_initial', 0, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = ' + text(TARGET),
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$config_nodes(pconfigcall) = [HARRAY n_input]',
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        'puserconstant_left.NAME = $ptascii("V66_REVIEW_LEFT")',
        'puserconstant_left.VALUE = POBJECT n_left',
        'puserconstant_left.CLASS = PVSTDCLASS n_left porigin_left',
        'puserconstant_right.NAME = $ptascii("V66_REVIEW_RIGHT")',
        'puserconstant_right.VALUE = POBJECT n_right',
        'puserconstant_right.CLASS = PVSTDCLASS n_right porigin_right',
        'n_left =/= n_right',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_left) = (pconstantstdobject_left)',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_right) = (pconstantstdobject_right)',
        '$global_std_completed(S,pconstantstdobject_left)',
        '$global_std_completed(S,pconstantstdobject_right)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        'S.STORE[n_cell] = DEFINED (POBJECT n_left)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {head}) (ALIAS n_cell),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_input_child))]',
        f'S.ARRAYS[n_input_child].ITEMS = [ENTRY (KSTRING {again}) (ALIAS n_cell)]',
        '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps',
        'H_before = $heap_graph(S)',
        '$heap_edge_owners(HOBJECT n_left,H_before.EDGES,[HCELL n_cell]) = 1',
        '$heap_edge_owners(HOBJECT n_left,H_before.EDGES,[HARRAY n_input,HARRAY n_input_child]) = 0',
        '$heap_owners(H_before,HOBJECT n_left) = 2',
        '$heap_owners(H_before,HOBJECT n_right) = 1',
        'n_before = |S.ARRAYS|',
        *protocol.property_value('S', 'n_left', 7, 'left_initial'),
        *protocol.property_value('S', 'n_right', 19, 'right_initial'),
        *common.step('S_row', 'S', 'PBOOL true'),
        'S_row.TODO = ptask_tail*',
        '$user_constant_at(S_row.USERCONSTANTS,preqbytes) = (puserconstant)',
        'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant]',
        'puserconstant.NAME = preqbytes', 'puserconstant.ORIGIN = pconfigcall.SITE',
        'puserconstant.VALUE = PARRAY n_root',
        'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
        'n_root =/= n_input', 'n_root = $(n_before + 1)',
        'n_child = n_before', 'n_child =/= n_input_child', 'n_child =/= n_root',
        f'parray_child = $array_insert($array_empty(),KSTRING {again},DIRECT (POBJECT n_left))',
        f'parray_root = $array_insert($array_insert($array_empty(),KSTRING {head},DIRECT (POBJECT n_left)),KSTRING {nested},DIRECT (PARRAY n_child))',
        'S_row.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        f'pvalueclass_child = PVARRAY false ([(KSTRING {again},PVSTDCLASS n_left porigin_left)])',
        f'puserconstant.CLASS = PVARRAY false ([(KSTRING {head},PVSTDCLASS n_left porigin_left),(KSTRING {nested},pvalueclass_child)])',
        '$dynamic_array_value(S_row,PARRAY n_root,eps,false) = ((S_row,PARRAY n_root,puserconstant.CLASS))',
        '$constant_value_class_valid(S_row,PARRAY n_root,puserconstant.CLASS)',
        '$user_constant_roots(S_row.USERCONSTANTS) = $user_constant_roots(S.USERCONSTANTS) ++ [HARRAY n_root]',
        'H_row = $heap_graph(S_row)',
        '$heap_edge_owners(HOBJECT n_left,H_row.EDGES,[HARRAY n_root,HARRAY n_child]) = 2',
        '$heap_edge_owners(HOBJECT n_left,H_row.EDGES,[HCELL n_cell]) = 1',
        '$heap_owners(H_row,HOBJECT n_left) = 4',
        '$heap_owners(H_row,HOBJECT n_right) = 1',
        '$heap_owners(H_row,HARRAY n_input) = 1',
        '$heap_owners(H_row,HARRAY n_root) = 1']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS', 'OBJECTPROPS', 'OBJECTTABLES', 'CONSTANTSTDOBJECTS', 'STORE', 'REFCELLS', 'EVENTS']]
    # Pure authority and canonical-table projections are never driven.
    values += [
        '~$dynamic_array_source(S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0],puserconstant.ORIGIN)',
        'S_no_birth = S_row[.CONSTANTSTDOBJECTS = eps]',
        '$dynamic_array_value(S_no_birth,PARRAY n_root,eps,false) = eps',
        'S_incomplete = S_row[.CONSTANTSTDOBJECTS = $global_std_record_put(S_row.CONSTANTSTDOBJECTS,pconstantstdobject_left[.COMPLETE = false])]',
        '$dynamic_array_value(S_incomplete,PARRAY n_root,eps,false) = eps',
        'S_dead = S_row[.ALLOCATIONS = $destruction_node_delete(S_row.ALLOCATIONS,HOBJECT n_left)]',
        '$dynamic_array_value(S_dead,PARRAY n_root,eps,false) = eps',
        f'pvalueclass_bad = $pvclass_put(puserconstant.CLASS,KSTRING {head},PVOBJECT)',
        'S_bad_tag = S_row[.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant[.CLASS = pvalueclass_bad]]]',
        '~$user_constants_valid(S_bad_tag,S_bad_tag.USERCONSTANTS)',
        f'S_bad_alias = S_row[.ARRAYS[n_root].ITEMS[0] = ENTRY (KSTRING {head}) (ALIAS n_cell)]',
        '$constant_value_class_valid(S_bad_alias,PARRAY n_root,puserconstant.CLASS)',
        '$dynamic_array_value(S_bad_alias,PARRAY n_root,eps,false) = eps',
        '~$user_constants_valid(S_bad_alias,S_bad_alias.USERCONSTANTS)',
        'S_bad_next = S_row[.ARRAYS[n_root].NEXT = 1]',
        '$dynamic_array_value(S_bad_next,PARRAY n_root,eps,false) = eps',
        *delivery('S_first', 'S_row'),
        'n_rootowners_S_first = 1', 'n_leftowners_S_first = 3', 'n_rightowners_S_first = 2',
        'S_first.STORE[n_cell] = DEFINED (POBJECT n_right)',
        'S_first.ARRAYS[n_root] = parray_root', 'S_first.ARRAYS[n_child] = parray_child',
        'S_bucket_found = $test_define_array_bucket_seek(S_first_value,5000)',
        r'S_bucket_found.COMPLETION = NORMAL \/ S_bucket_found.COMPLETION = BUDGET',
        'S_bucket = $test_running(S_bucket_found)', '$test_define_array_bucket(S_bucket)',
        *common.public('S_bucket'),
        '$lookup(S_bucket.ENV,$ptascii("tree")) = (n_tree)',
        'S_bucket.STORE[n_tree] = DEFINED (PARRAY n_copy_root)',
        'n_copy_root =/= n_root',
        f'S_bucket.ARRAYS[n_copy_root].ITEMS = [ENTRY (KSTRING {head}) (DIRECT (POBJECT n_left)),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_copy_child))]',
        'n_copy_child =/= n_child', 'n_copy_child =/= n_input_child',
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_bucket)',
        'n_bucket <- S_bucket.REFCELLS', 'n_bucket =/= n_cell',
        'S_bucket.STORE[n_bucket] = DEFINED (POBJECT n_right)',
        f'S_bucket.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {again}) (ALIAS n_bucket)]',
        'S_bucket.STORE[n_cell] = DEFINED (POBJECT n_right)',
        'S_bucket.ARRAYS[n_root] = parray_root', 'S_bucket.ARRAYS[n_child] = parray_child',
        'S_bucket.USERCONSTANTS = S_row.USERCONSTANTS',
        'H_bucket = $heap_graph(S_bucket)',
        '$heap_edge_owners(HOBJECT n_left,H_bucket.EDGES,[HARRAY n_root,HARRAY n_child,HARRAY n_copy_root]) = 3',
        '$heap_edge_owners(HOBJECT n_right,H_bucket.EDGES,[HCELL n_cell,HCELL n_bucket]) = 2',
        '$heap_edge_owners(HCELL n_bucket,H_bucket.EDGES,[HARRAY n_copy_child]) = 1',
        '$heap_owners(H_bucket,HOBJECT n_left) = 4',
        '$heap_owners(H_bucket,HOBJECT n_right) = 3',
        *protocol.property_value('S_bucket', 'n_left', 31, 'left_bucket'),
        *protocol.property_value('S_bucket', 'n_right', 19, 'right_bucket'),
        *delivery('S_again', 'S_bucket'),
        'n_rootowners_S_again = 1', 'n_leftowners_S_again = 4', 'n_rightowners_S_again = 3',
        'S_again.ARRAYS[n_copy_root] = S_bucket.ARRAYS[n_copy_root]',
        f'$entry_lookup(S_again.ARRAYS[n_copy_child].ITEMS,KSTRING {again}) = (pitem_again)',
        '$entry_value(S_again,pitem_again) = POBJECT n_right',
        '$entry_lookup(S_again.ARRAYS[n_copy_child].ITEMS,KINT 0) = (DIRECT pvalue_tail)',
        '$string_bytes(pvalue_tail) = ($ptascii("tail"))',
        'S_again.ARRAYS[n_root] = parray_root', 'S_again.ARRAYS[n_child] = parray_child',
        *protocol.finish('S_again_value', stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.CONSTANTSTDOBJECTS = S_row.CONSTANTSTDOBJECTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 3',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~((HARRAY n_input) <- S_final.ALLOCATIONS)',
        '~((HARRAY n_input_child) <- S_final.ALLOCATIONS)',
        '~((HARRAY n_copy_root) <- S_final.ALLOCATIONS)',
        '~((HARRAY n_copy_child) <- S_final.ALLOCATIONS)',
        '~((HCELL n_cell) <- S_final.ALLOCATIONS)',
        '~((HCELL n_bucket) <- S_final.ALLOCATIONS)',
        *protocol.property_value('S_final', 'n_left', 31, 'left_final'),
        *protocol.property_value('S_final', 'n_right', 19, 'right_final')]
    return values


def prepare(out, originals):
    native = json.loads((originals / 'native-report.json').read_text())
    assert native['passed'] and native['inputs_stable']
    frontend = packet.Worker([str(packet.types.PHP), '-n', *packet.types.FLAGS,
        '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = packet.Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in sources.family.CASES:
            path = originals / name / 'main.php'
            row, = [row for row in native['records'] if row['id'] == name]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['source_sha256']
            assert row['process']['exit'] == 0 and not base64.b64decode(row['stderr'])
            parsed = frontend.request({'op': 'parse', 'source': packet.b64(path.read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            initial = ['S_initial = $php_run(' + main + ',0,' + json.dumps(packet.b64(str(path).encode())) + ')']
            values = checks(initial, base64.b64decode(row['stdout']))
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + value + '\n' for value in values))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            frontend.close()


packet.sources, packet.prepare = sources, prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
