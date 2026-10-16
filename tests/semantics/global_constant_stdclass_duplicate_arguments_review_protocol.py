#!/usr/bin/env python3
"""Independent rejected array roots, escaped identity and store callbacks."""
import base64
import hashlib
import json
from pathlib import Path

import global_constant_stdclass_duplicate_arguments_protocol as protocol
import global_constant_stdclass_duplicate_arguments_review_sources as sources

packet, std, common = protocol.packet, protocol.std, protocol.common
ROOT, text, term = protocol.ROOT, protocol.text, protocol.term
PREFIX = protocol.PREFIX


def owners(state, escaped=1, last=1):
    return [f'$constant_argument_header({state},pconstantargument)',
        f'{state}.DESTRUCTION.REJECTED = [pconstantargument]',
        f'$heap_owners($heap_graph({state}),HARRAY n_root) = 1',
        f'$heap_owners($heap_graph({state}),HARRAY n_child) = 1',
        f'$heap_owners($heap_graph({state}),HOBJECT n_escaped) = {escaped}',
        f'$heap_owners($heap_graph({state}),HOBJECT n_last) = {last}',
        f'$heap_edge_owners(HARRAY n_child,$heap_graph({state}).EDGES,[HARRAY n_root]) = 1',
        f'$heap_edge_owners(HOBJECT n_escaped,$heap_graph({state}).EDGES,[HARRAY n_child]) = 1',
        f'$heap_edge_owners(HOBJECT n_last,$heap_graph({state}).EDGES,[HARRAY n_child]) = 1']


def property_value(state, value, suffix):
    return [f'$objectprops_at({state}.OBJECTPROPS,n_escaped) = (ppropertyslot_all_{suffix}*)',
        f'$property_slot_at(ppropertyslot_all_{suffix}*,$ptascii("value")) = (ppropertyslot_{suffix})',
        f'ppropertyslot_{suffix}.STATE = PROP_VALUE pitem_{suffix}',
        f'$entry_value({state},pitem_{suffix}) = PINT {value}']


def checks(initial, stdout, retry_response):
    prefix = b'B|prior|E|Named parameter $keep overwrites previous argument|absent|empty|A|'
    assert stdout == prefix + b'escaped:41|last|'
    values = [*initial, *protocol.born('S_initial'),
        *protocol.reach('S_current', 'S_born', 0, 'n_outer'),
        'S_current.TODO = (DEFAULT_NEW_SEND pdefaultnew) :: ptask_current*',
        'pdefaultnew.OBJECT = n_outer', 'pdefaultnew.INDEX = 1',
        'pdefaultnew.VALUES = [POBJECT n_prior]',
        'S_current.RESULT = KNOWN (PARRAY n_root)',
        'S_current.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        'S_current.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_escaped)),ENTRY (KINT 1) (DIRECT (POBJECT n_last))]',
        '$global_new_record(S_current.CONSTANTOBJECTS,n_prior) = (pconstantobject_prior)',
        '$global_new_record(S_current.CONSTANTOBJECTS,n_escaped) = (pconstantobject_escaped)',
        '$global_new_record(S_current.CONSTANTOBJECTS,n_last) = (pconstantobject_last)',
        'S_current.CONSTANTOBJECTS = [pconstantobject_prior,pconstantobject_escaped,pconstantobject_last]',
        '$global_new_completed(S_current,pconstantobject_prior)',
        '$global_new_completed(S_current,pconstantobject_escaped)',
        '$global_new_completed(S_current,pconstantobject_last)',
        'n_escaped =/= n_last', 'n_prior =/= n_escaped', 'n_prior =/= n_last',
        '$global_std_rejected(S_current,pdefaultnew) = (pconstantargument)',
        'pconstantargument.OBJECT = n_outer', 'pconstantargument.INDEX = 1',
        'pconstantargument.VALUE = PARRAY n_root', 'pconstantargument.CONSTANTS = 0',
        '$pvclass_get(pconstantargument.CLASS,KINT 1) = (pvalueclass_child)',
        '$pvclass_get(pvalueclass_child,KINT 0) = (PVINSTANCE n_escaped pconstantobject_escaped.SITE)',
        '$pvclass_get(pvalueclass_child,KINT 1) = (PVINSTANCE n_last pconstantobject_last.SITE)',
        '$constant_arguments_valid(S_current,[pconstantargument])',
        '$constant_argument_roots([pconstantargument]) = [HARRAY n_root]',
        'S_current.DESTRUCTION.REJECTED = eps',
        '$heap_owners($heap_graph(S_current),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_current),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_current),HOBJECT n_escaped) = 2',
        '$heap_owners($heap_graph(S_current),HOBJECT n_last) = 1',
        '$heap_owners($heap_graph(S_current),HOBJECT n_prior) = 1',
        '$heap_owners($heap_graph(S_current),HOBJECT n_outer) = 1',
        *property_value('S_current', 7, 'initial'),
        # Pure invalid headers/capture requests are never driven.
        '~$constant_argument_header(S_current,pconstantargument[.INDEX = 0])',
        '~$constant_argument_header(S_current,pconstantargument[.INDEX = 3])',
        '~$constant_argument_header(S_current,pconstantargument[.CONSTANTS = 1])',
        '~$constant_argument_header(S_current,pconstantargument[.CLASS = PVOBJECT])',
        '~$constant_argument_header(S_current,pconstantargument[.VALUE = POBJECT n_outer])',
        '~$constant_argument_header(S_current[.ALLOCATIONS = $destruction_node_delete(S_current.ALLOCATIONS,HOBJECT n_escaped)],pconstantargument)',
        '~$constant_argument_header(S_current[.CONSTANTOBJECTS = $global_new_record_put(S_current.CONSTANTOBJECTS,pconstantobject_escaped[.COMPLETE = false])],pconstantargument)',
        '~$constant_argument_header(S_current[.CONSTANTSTDOBJECTS = $global_std_record_put(S_current.CONSTANTSTDOBJECTS,pconstantstdobject[.COMPLETE = true])],pconstantargument)',
        '~$constant_arguments_valid(S_current,[pconstantargument,pconstantargument])',
        '$global_std_rejected(S_current[.TODO = eps],pdefaultnew) = eps',
        '$global_std_rejected(S_current[.RESULT = KNOWN PNULL],pdefaultnew) = eps',
        '$global_std_duplicate(S_current[.CONSTCONTEXT = eps],pdefaultnew)',
        '$global_std_rejected(S_current[.CONSTCONTEXT = eps],pdefaultnew) = eps',
        *common.step('S_error', 'S_current'),
        'S_error.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_current*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_outer),DESTRUCTION_VALUE (HOBJECT n_prior)]',
        'pdestructionoperation.SOURCE = DEFAULT_NEW_SEND pdefaultnew',
        'pdestructionoperation.COMPLETION = THROWING n_error',
        'pdestructionoperation.PENDING = (n_error)',
        'S_error.CONSTCONTEXT = S_current.CONSTCONTEXT', *owners('S_error', escaped=2),
        'S_error.ARRAYS[n_root].ITEMS = S_current.ARRAYS[n_root].ITEMS',
        'S_error.ARRAYS[n_child].ITEMS = S_current.ARRAYS[n_child].ITEMS',
        # The faulting SEND is consumed. Eager cleanup releases outer/prior;
        # pending Error search retains its context until the catch restores it.
        *protocol.reach('S_throw', 'S_error', 2, 'n_outer', public=False),
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_current*',
        'S_throw.CONSTCONTEXT = S_current.CONSTCONTEXT',
        'S_throw.DESTRUCTION.REJECTED = S_error.DESTRUCTION.REJECTED',
        *owners('S_throw', escaped=2),
        # The retained array remains owned after all external aliases drop.
        'S_wait2 = $drive_steps(S_throw,5000)', 'S_wait2.COMPLETION = SOURCE_PENDING',
        'S_wait2.CONSTCONTEXT = eps',
        *common.public('S_wait2'), *owners('S_wait2'),
        '$test_outputs(S_wait2.EVENTS) = $ptascii("B|prior|E|Named parameter $keep overwrites previous argument|absent|")',
        '$user_constant_at(S_wait2.USERCONSTANTS,$ptascii("V64_REVIEW_BAD")) = eps',
        'S_wait2.USERCONSTANTS = eps',
        '~((HOBJECT n_outer) <- S_wait2.ALLOCATIONS)',
        '~((HOBJECT n_prior) <- S_wait2.ALLOCATIONS)',
        '(n_prior <- S_wait2.DESTRUCTION.CALLED)',
        '~(n_escaped <- S_wait2.DESTRUCTION.CALLED)', '~(n_last <- S_wait2.DESTRUCTION.CALLED)',
        '$global_std_record(S_wait2.CONSTANTSTDOBJECTS,n_outer) = (pconstantstdobject)',
        '~$constant_value_class_valid(S_wait2,POBJECT n_outer,PVSTDCLASS n_outer porigin_site)',
        'S_wait2.CONSTANTOBJECTS = S_current.CONSTANTOBJECTS',
        *property_value('S_wait2', 41, 'changed'),
        '$eval_response_valid(S_wait2,' + retry_response + ')',
        'S_retry = $test_std_running($eval_resume(S_wait2,' + retry_response + '))',
        *common.reach('S_query', 'S_retry', 0, 'V64_REVIEW_BAD'), *common.public('S_query'),
        '$user_constant_at(S_query.USERCONSTANTS,$ptascii("V64_REVIEW_BAD")) = (puserconstant_retry)',
        'puserconstant_retry.VALUE = POBJECT n_retry',
        'puserconstant_retry.CLASS = PVSTDCLASS n_retry porigin_retry',
        'porigin_retry = PORIGIN 2 pcpath_retry', 'n_retry =/= n_outer',
        '$global_std_record(S_query.CONSTANTSTDOBJECTS,n_retry) = (pconstantstdobject_retry)',
        '$global_std_completed(S_query,pconstantstdobject_retry)',
        'S_query.CONSTANTSTDOBJECTS = [pconstantstdobject,pconstantstdobject_retry]',
        '|S_query.USERCONSTANTS| = 1', *owners('S_query'),
        '$object_table_slots_at(S_query,n_retry) = eps',
        '$heap_owners($heap_graph(S_query),HOBJECT n_retry) = 1',
        *common.step('S_value', 'S_query', 'POBJECT n_retry'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_retry) = 2',
        'S_value.DESTRUCTION.REJECTED = S_query.DESTRUCTION.REJECTED',
        *protocol.reach('S_store_escaped', 'S_value', 1, 'n_escaped'),
        '$test_outputs(S_store_escaped.EVENTS) = ' + term(prefix),
        *owners('S_store_escaped'), *property_value('S_store_escaped', 41, 'store'),
        *std.step('S_selected_escaped', 'S_store_escaped'),
        'S_selected_escaped.TODO = (DESTRUCTOR_ENTER pdestructorcall_escaped) :: ptask_escaped*',
        'pdestructorcall_escaped.OBJECT = n_escaped', 'pdestructorcall_escaped.STORE',
        '$destructor_enter_valid(S_selected_escaped,pdestructorcall_escaped)',
        *owners('S_selected_escaped', escaped=3),
        *protocol.reach('S_store_last', 'S_selected_escaped', 1, 'n_last'),
        '$test_outputs(S_store_last.EVENTS) = ' + term(prefix + b'escaped:41|'),
        '(n_escaped <- S_store_last.DESTRUCTION.CALLED)',
        *owners('S_store_last'),
        *std.step('S_selected_last', 'S_store_last'),
        'S_selected_last.TODO = (DESTRUCTOR_ENTER pdestructorcall_last) :: ptask_last*',
        'pdestructorcall_last.OBJECT = n_last', 'pdestructorcall_last.STORE',
        '$destructor_enter_valid(S_selected_last,pdestructorcall_last)',
        *owners('S_selected_last', last=3),
        *protocol.previous.finish('S_selected_last', stdout),
        'S_final.DESTRUCTION.PHASE = DESTRUCTION_DONE', *owners('S_final'),
        '(n_escaped <- S_final.DESTRUCTION.CALLED)', '(n_last <- S_final.DESTRUCTION.CALLED)',
        'S_final.CONSTANTOBJECTS = S_current.CONSTANTOBJECTS',
        'S_final.CONSTANTSTDOBJECTS = S_query.CONSTANTSTDOBJECTS']
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
            row, = [r for r in native['records'] if r['id'] == name]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['source_sha256']
            assert row['process']['exit'] == 0 and not base64.b64decode(row['stderr'])
            parsed = frontend.request({'op': 'parse', 'source': packet.b64(path.read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            codes = [base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast'])
                if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'const V64_REVIEW_BAD')]
            assert len(codes) == 2
            responses = []
            for unit_id, code in enumerate(codes, 1):
                unit = frontend.request({'op': 'parse-eval', 'id': str(unit_id), 'mode': 'eval',
                    'profile': 'cli-raw-85', 'source': packet.b64(code)})
                assert unit['accepted']
                checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
                responses.append('SOURCE_ACCEPT ' + str(unit_id) + ' ' + term(code) + ' ' + checked)
            initial = ['S_wait = $php_run(' + main + ',5000,' + json.dumps(packet.b64(str(path).encode())) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING', *common.public('S_wait'),
                '$eval_response_valid(S_wait,' + responses[0] + ')',
                'S_initial = $test_std_running($eval_resume(S_wait,' + responses[0] + '))']
            values = checks(initial, base64.b64decode(row['stdout']), responses[1])
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + v + '\n' for v in values))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            frontend.close()


packet.sources, packet.prepare = sources, prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
