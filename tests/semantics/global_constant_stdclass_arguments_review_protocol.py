#!/usr/bin/env python3
"""Independent ignored named values, real destructors and abrupt cutoff."""
import base64
import hashlib
import json
from pathlib import Path

import global_constant_stdclass_arguments_protocol as protocol
import global_constant_stdclass_arguments_review_sources as sources

packet, std, common = protocol.packet, protocol.std, protocol.common
ROOT, text, term = protocol.ROOT, protocol.text, protocol.term
CASE = 'named-value-destructors-and-argument-error-cutoff'
PREFIX = protocol.PREFIX + r'''
def $test_stdargs_front(S,4) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.INDEX = 1
  -- if $global_std_pending(S,pdefaultnew)
def $test_stdargs_front(S,5) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if S.OBJECTS[pinstancestorage.OBJECT] = STDINSTANCE
  -- if $global_std_record(S.CONSTANTSTDOBJECTS,pinstancestorage.OBJECT) = (pconstantstdobject)
  -- if ~pconstantstdobject.COMPLETE
'''


def born(label, start, unit, argc):
    before, after = 'S_' + label, 'S_' + label + '_born'
    return [*protocol.reach(before, start, 0),
        f'{before}.ORIGIN = (porigin_{label})',
        f'porigin_{label} = PORIGIN {unit} pcpath_{label}',
        f'{before}.CONSTCONTEXT = (pconstantcontext_{label})',
        f'porigin_decl_{label} = pconstantcontext_{label}.ORIGIN',
        f'$origin_node({before}.SOURCES,porigin_{label}) = (NExprNew name_{label} (SEQUENCE phpType7_{label}*) metadata_{label})',
        f'|phpType7_{label}*| = {argc}',
        f'$parameter_new_prefix(phpType7_{label}*)',
        f'$default_new_unique(phpType7_{label}*)',
        f'$global_std_source({before},porigin_{label},porigin_decl_{label},|{before}.DECLARATIONS|)',
        *std.step(after, before),
        f'{after}.TODO = (DEFAULT_NEW_ARGS pdefaultnew_{label}) :: ptask_{label}*',
        f'n_{label} = |{before}.OBJECTS|', f'pdefaultnew_{label}.OBJECT = n_{label}',
        f'pdefaultnew_{label}.SITE = porigin_{label}',
        f'pdefaultnew_{label}.ARGUMENTS = phpType7_{label}*',
        f'pdefaultnew_{label}.INDEX = 0', f'pdefaultnew_{label}.VALUES = eps',
        f'{after}.OBJECTS = {before}.OBJECTS ++ [STDINSTANCE]',
        f'{after}.ALLOCATIONS = {before}.ALLOCATIONS ++ [HOBJECT n_{label}]',
        f'n_prefix_{label} = |{before}.DECLARATIONS|',
        f'$global_std_record({after}.CONSTANTSTDOBJECTS,n_{label}) = (pconstantstdobject_{label})',
        f'pconstantstdobject_{label} = {{OBJECT n_{label}, SITE porigin_{label}, DECL porigin_decl_{label}, PREFIX n_prefix_{label}, COMPLETE false}}',
        f'{after}.CONSTANTSTDOBJECTS = {before}.CONSTANTSTDOBJECTS ++ [pconstantstdobject_{label}]',
        f'$global_std_pending({after},pdefaultnew_{label})',
        f'$default_new_valid({after},pdefaultnew_{label})',
        f'~$global_std_completed({after},pconstantstdobject_{label})',
        f'$heap_owners($heap_graph({after}),HOBJECT n_{label}) = 1']


def argument(state, obj, suffix):
    record = 'pconstantobject_' + suffix
    return [f'$global_new_record({state}.CONSTANTOBJECTS,{obj}) = ({record})',
        f'{state}.OBJECTS[{obj}] = INSTANCE {record}.CLASS',
        f'$global_new_completed({state},{record})',
        f'(HOBJECT {obj}) <- {state}.ALLOCATIONS',
        f'$heap_owners($heap_graph({state}),HOBJECT {obj}) = 1']


def checks(initial, stdout, response):
    values = [*initial, *born('good', 'S_initial', 0, 2),
        'S_good.CONSTANTSTDOBJECTS = eps',
        'phpType7_good* = [phpType7_first,phpType7_spare]',
        'phpType7_first = NArg (NIdentifier (BYTES "Zmlyc3Q=") metadata_first_name) expression_first (BOOLEAN false) (BOOLEAN false) metadata_first',
        '~$default_new_unique([phpType7_first,phpType7_first])',
        '~$global_std_pending(S_good_born,pdefaultnew_good[.ARGUMENTS = eps])',
        '~$global_std_pending(S_good_born,pdefaultnew_good[.INDEX = 3])',
        '~$global_std_pending(S_good_born,pdefaultnew_good[.VALUES = [PNULL]])',
        '~$global_std_pending(S_good_born[.CONSTANTSTDOBJECTS = eps],pdefaultnew_good)',
        *protocol.reach('S_values', 'S_good_born', 1),
        'S_values.TODO = (DEFAULT_NEW_ARGS pdefaultnew_values) :: ptask_values*',
        'pdefaultnew_values.OBJECT = n_good', 'pdefaultnew_values.INDEX = 2',
        'pdefaultnew_values.VALUES = [POBJECT n_first,POBJECT n_second]',
        'n_first =/= n_second', 'n_good =/= n_first', 'n_good =/= n_second',
        *argument('S_values', 'n_first', 'first'),
        *argument('S_values', 'n_second', 'second'),
        'S_values.CONSTANTOBJECTS = [pconstantobject_first,pconstantobject_second]',
        '$global_std_record(S_values.CONSTANTSTDOBJECTS,n_good) = (pconstantstdobject_good)',
        '~$constant_value_class_valid(S_values,POBJECT n_good,PVSTDCLASS n_good porigin_good)',
        '$global_new_complete_phase(S_values,pdefaultnew_values)',
        '~$new_has_ctor(S_values,pdefaultnew_values.CLASS)',
        '$test_outputs(S_values.EVENTS) = $ptascii("B|")',
        *std.step('S_done', 'S_values'),
        '$global_std_record(S_done.CONSTANTSTDOBJECTS,n_good) = (pconstantstdobject_good_done)',
        'pconstantstdobject_good_done = pconstantstdobject_good[.COMPLETE = true]',
        '$global_std_completed(S_done,pconstantstdobject_good_done)',
        '(HOBJECT n_good) <- S_done.ALLOCATIONS',
        *protocol.query('first', 'S_done', 'V63_REVIEW_GOOD', 'n_good', 'porigin_good'),
        'n_owners_first = 1', '$object_table_slots_at(S_first,n_good) = eps',
        '$test_outputs(S_first.EVENTS) = $ptascii("B|first|second|ready|")',
        '(n_first <- S_first.DESTRUCTION.CALLED)', '(n_second <- S_first.DESTRUCTION.CALLED)',
        '~(n_good <- S_first.DESTRUCTION.CALLED)',
        '~((HOBJECT n_first) <- S_first.ALLOCATIONS)',
        '~((HOBJECT n_second) <- S_first.ALLOCATIONS)',
        'S_wait = $drive_steps(S_first_value,5000)', 'S_wait.COMPLETION = SOURCE_PENDING',
        *common.public('S_wait'), '$eval_response_valid(S_wait,' + response + ')',
        'S_eval = $test_std_running($eval_resume(S_wait,' + response + '))',
        *born('bad', 'S_eval', 1, 3),
        'n_good =/= n_bad', 'porigin_good =/= porigin_bad',
        *protocol.reach('S_prior', 'S_bad_born', 4),
        'S_prior.TODO = (DEFAULT_NEW_ARGS pdefaultnew_prior) :: ptask_prior*',
        'pdefaultnew_prior.OBJECT = n_bad', 'pdefaultnew_prior.INDEX = 1',
        'pdefaultnew_prior.VALUES = [POBJECT n_bad_first]',
        *argument('S_prior', 'n_bad_first', 'bad_first'),
        'S_prior.CONSTANTOBJECTS = [pconstantobject_first,pconstantobject_second,pconstantobject_bad_first]',
        '$test_outputs(S_prior.EVENTS) = $ptascii("B|first|second|ready|41|")',
        *protocol.reach('S_throw', 'S_prior', 3, public=False),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (DEFAULT_NEW_SEND pdefaultnew_throw) :: ptask_throw*',
        'S_throw.CONSTCONTEXT = eps', 'pdefaultnew_throw = pdefaultnew_prior',
        '$constant_bindings(S_throw,S_throw.TODO) = [porigin_decl_bad]',
        '$global_new_argument_owned(S_throw,pdefaultnew_throw)',
        '~$global_new_argument_owned(S_throw[.TODO = eps],pdefaultnew_throw)',
        '~$global_new_argument_owned(S_throw,pdefaultnew_throw[.ARGUMENTS = eps])',
        '~$global_new_argument_owned(S_throw,pdefaultnew_throw[.VALUES = eps])',
        '~$global_new_argument_owned(S_throw[.CONSTANTSTDOBJECTS = $global_std_record_put(S_throw.CONSTANTSTDOBJECTS,pconstantstdobject_bad[.COMPLETE = true])],pdefaultnew_throw)',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = (' + text('Undefined constant "V63_REVIEW_MISSING"') + ')',
        '~(n_bad <- S_throw.DESTRUCTION.CALLED)',
        # These are real abandoned throw phases; their default-context validator
        # is not used after throwable_begin has cleared CONSTCONTEXT.
        'S_discarded_found = $drive_steps(S_throw,1)',
        r'S_discarded_found.COMPLETION = NORMAL \/ S_discarded_found.COMPLETION = BUDGET',
        'S_discarded = $test_std_running(S_discarded_found)',
        'S_discarded.CONSTANTSTDOBJECTS = S_throw.CONSTANTSTDOBJECTS',
        '~(n_bad <- S_discarded.DESTRUCTION.CALLED)',
        # Normal free_obj storage retirement also marks CALLED. Reach that
        # actual physical pin separately from constructor-failed discard.
        *protocol.reach('S_storage', 'S_discarded', 5, public=False),
        'S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_storage*',
        'pinstancestorage.OBJECT = n_bad', 'pinstancestorage.SLOTS = eps',
        '(n_bad <- S_storage.DESTRUCTION.CALLED)',
        '(HOBJECT n_bad) <- S_storage.ALLOCATIONS',
        '$heap_owners($heap_graph(S_storage),HOBJECT n_bad) = 1',
        '$global_std_record(S_storage.CONSTANTSTDOBJECTS,n_bad) = (pconstantstdobject_bad)',
        *protocol.query('again', 'S_storage', 'V63_REVIEW_GOOD', 'n_good', 'porigin_good'),
        'n_owners_again = 2',
        '$user_constant_at(S_again.USERCONSTANTS,$ptascii("V63_REVIEW_BAD")) = eps',
        'S_again.CONSTANTSTDOBJECTS = [pconstantstdobject_good_done,pconstantstdobject_bad]',
        'S_again.CONSTANTOBJECTS = S_prior.CONSTANTOBJECTS',
        '$global_std_records_valid(S_again,S_again.CONSTANTSTDOBJECTS)',
        '~$global_std_completed(S_again,pconstantstdobject_bad)',
        '~$constant_value_class_valid(S_again,POBJECT n_bad,PVSTDCLASS n_bad porigin_bad)',
        '$global_new_completed(S_again,pconstantobject_bad_first)',
        '~$constant_value_class_valid(S_again,POBJECT n_bad_first,PVINSTANCE n_bad_first pconstantobject_bad_first.SITE)',
        '(n_bad <- S_again.DESTRUCTION.CALLED)',
        '(n_bad_first <- S_again.DESTRUCTION.CALLED)',
        '~((HOBJECT n_bad) <- S_again.ALLOCATIONS)',
        '~((HOBJECT n_bad_first) <- S_again.ALLOCATIONS)',
        '$test_outputs(S_again.EVENTS) = $ptascii("B|first|second|ready|41|first|Undefined constant \\"V63_REVIEW_MISSING\\"|absent|")',
        *std.property_value('S_again', 'n_good', 41, 'good'),
        *protocol.query('last', 'S_again_value', 'V63_REVIEW_GOOD', 'n_good', 'porigin_good'),
        'n_owners_last = 1',
        *protocol.finish('S_last_value', stdout),
        '$heap_owners($heap_graph(S_final),HOBJECT n_good) = 2',
        'S_final.CONSTANTSTDOBJECTS = S_again.CONSTANTSTDOBJECTS',
        'S_final.CONSTANTOBJECTS = S_again.CONSTANTOBJECTS']
    return values


def prepare(out, originals):
    native = json.loads((originals / 'native-report.json').read_text())
    assert native['passed'] and native['inputs_stable']
    frontend = packet.Worker([str(packet.types.PHP), '-n', *packet.types.FLAGS,
        '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
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
            code, = [base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast'])
                if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'const V63_REVIEW_BAD')]
            unit = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                'profile': 'cli-raw-85', 'source': packet.b64(code)})
            assert unit['accepted']
            checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
            response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked
            initial = ['S_initial = $php_run(' + main + ',0,' + json.dumps(packet.b64(str(path).encode())) + ')',
                'S_initial.COMPLETION = BUDGET']
            values = checks(initial, base64.b64decode(row['stdout']), response)
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
    sources.family.CASES = {CASE: sources.family.CASES[CASE]}
    raise SystemExit(0 if packet.main() else 1)
