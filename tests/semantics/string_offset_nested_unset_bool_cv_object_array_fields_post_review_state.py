#!/usr/bin/env python3
"""Independent DIRECT field arrays, COW, shared cells and outside retirement."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_review_state as prior
import string_offset_nested_unset_bool_cv_object_array_fields_post_cases as cases

INDEX = 0
PRELAW = False
PART = 'all'
FRONT = prior.front
PREFIX = prior.PREFIX

UPDATE_PROGRAM = "(PROGRAM ([(NStmtExpression ((NExprPreInc ((NExprVariable ((BYTES (\"ZmllbGRWYWx1ZQ==\"))) ([(MendFilePos (18)), (MendLine (1)), (MendTokenPos (2)), (MstartFilePos (8)), (MstartLine (1)), (MstartTokenPos (2))]))) ([(MendFilePos (18)), (MendLine (1)), (MendTokenPos (2)), (MstartFilePos (6)), (MstartLine (1)), (MstartTokenPos (1))]))) ([(MendFilePos (19)), (MendLine (1)), (MendTokenPos (3)), (MstartFilePos (6)), (MstartLine (1)), (MstartTokenPos (1))]))]))"
TYPED_PROGRAM = "(PROGRAM ([(NStmtFunction ((SEQUENCE ([]))) ((BOOLEAN (true))) ((NIdentifier ((BYTES (\"YXJyYXlGaWVsZEZsYWdUeXBlZA==\"))) ([(MendFilePos (34)), (MendLine (1)), (MendTokenPos (4)), (MstartFilePos (16)), (MstartLine (1)), (MstartTokenPos (4))]))) ((SEQUENCE ([]))) ((NIdentifier ((BYTES (\"c3RyaW5n\"))) ([(MendFilePos (44)), (MendLine (1)), (MendTokenPos (9)), (MstartFilePos (39)), (MstartLine (1)), (MstartTokenPos (9))]))) ((SEQUENCE ([(NStmtTryCatch ((SEQUENCE ([(NStmtReturn ((NExprVariable ((BYTES (\"ZmllbGRWYWx1ZQ==\"))) ([(MendFilePos (71)), (MendLine (1)), (MendTokenPos (19)), (MstartFilePos (61)), (MstartLine (1)), (MstartTokenPos (19))]))) ([(MendFilePos (72)), (MendLine (1)), (MendTokenPos (20)), (MstartFilePos (54)), (MstartLine (1)), (MstartTokenPos (17))]))]))) ((SEQUENCE ([]))) ((NStmtFinally ((SEQUENCE ([]))) ([(MendFilePos (85)), (MendLine (1)), (MendTokenPos (27)), (MstartFilePos (76)), (MstartLine (1)), (MstartTokenPos (24))]))) ([(MendFilePos (85)), (MendLine (1)), (MendTokenPos (27)), (MstartFilePos (48)), (MstartLine (1)), (MstartTokenPos (13))]))]))) ([(MendFilePos (87)), (MendLine (1)), (MendTokenPos (29)), (MstartFilePos (6)), (MstartLine (1)), (MstartTokenPos (1))]))]))"



def fields(left, right):
    return '[' + ', '.join(prior.slot('$ptascii("' + name + '")', 'PARRAY ' + array)
        for name, array in (('left', left), ('right', right))) + ']'


def items(value):
    return '[ENTRY (KINT 0) (DIRECT (PINT ' + str(value) + ')), ENTRY (KINT 1) (ALIAS n_field)]'


def front(program, path):
    prior.INDEX, prior.cases = INDEX, cases
    checks = FRONT(program, path)
    old = prior.fields(7, 'true', 'old', 4609434218613702656)
    assert sum(check.count(old) for check in checks) == 2
    checks = [check.replace(old, fields('n_payload', 'n_payload')).replace(
        '$node_children(S_R, HOBJECT n_object) = eps',
        '$node_children(S_R, HOBJECT n_object) = [HARRAY n_payload, HARRAY n_payload]').replace(
        '$property_release_nodes(ppropertyslot_before*) = eps',
        '$property_release_nodes(ppropertyslot_before*) = [HARRAY n_payload, HARRAY n_payload]') for check in checks]
    checks += ['$lookup(S_R.ENV, $ptascii("outside")) = (n_outside)',
        'S_R.STORE[n_outside] = DEFINED (PARRAY n_payload)',
        '$(n_payload < |S_R.ARRAYS|)', 'n_payload =/= n_array', 'n_payload =/= n_middle',
        'S_R.ARRAYS[n_payload].ITEMS = ' + items(11),
        '$lookup(S_R.ENV, $ptascii("fieldValue")) = (n_field)',
        'n_field =/= n_outside', 'n_field =/= n_alias', 'n_field =/= n_key',
        'S_R.STORE[n_field] = DEFINED (PINT 7)',
        '$call_reference_operand_valid(S_R, REFERENCE n_field)',
        '$literal_reference_plain_cell(S_R, n_field)',
        '$node_children(S_R, HCELL n_outside) = [HARRAY n_payload]',
        '$node_children(S_R, HARRAY n_payload) = [HCELL n_field]',
        '$node_children(S_R, HCELL n_field) = eps',
        '$heap_member(HCELL n_outside, H_saved.ROOTS)',
        '$heap_member(HARRAY n_payload, $heap_prune(H_saved).NODES)',
        '$heap_member(HCELL n_field, $heap_prune(H_saved).NODES)',
        '$heap_count(HARRAY n_payload, H_saved.ROOTS) = 0',
        '$heap_edge_owners(HARRAY n_payload, H_saved.EDGES, [HOBJECT n_object]) = 2',
        '$heap_edge_owners(HARRAY n_payload, H_saved.EDGES, [HCELL n_outside]) = 1',
        '$heap_owners(H_saved, HARRAY n_payload) = 3',
        '$heap_edge_owners(HCELL n_field, H_saved.EDGES, [HARRAY n_payload]) = 1',
        'n_field_roots = $heap_count(HCELL n_field, H_saved.ROOTS)',
        '$(n_field_roots > 0)', '$heap_owners(H_saved, HCELL n_field) = $(n_field_roots + 1)']
    if PRELAW:
        checks += ['~$string_unset_bool_cv_post_object_fields(S_R, ppropertyslot_before*)',
            '~$string_unset_bool_cv_post_object(S_R, n_object)']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases, prior.front = INDEX, PRELAW, cases, front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = FRONT
    if not PRELAW:
        at = next(i for i, check in enumerate(checks) if check.startswith('S_direct = '))
        checks, derived = checks[:at], 0
        checks.remove('$drive_steps($review_cv_running(S_public), 4000) = S_DONE')
    changed = prior.fields(9, 'true', 'changed', 4609434218613702656)
    rebound = prior.fields(11, 'false', 'new', 4612811918334230528)
    assert sum(check.count(changed) for check in checks) == 1
    assert sum(check.count(rebound) for check in checks) == 2
    checks = [check.replace(changed, fields('n_left', 'n_right')).replace(rebound, 'eps').replace(
        '$node_children(S_B, HOBJECT n_object) = eps',
        '$node_children(S_B, HOBJECT n_object) = [HARRAY n_left, HARRAY n_right]') for check in checks]
    at = checks.index('H_B = $heap_graph(S_B)') + 2
    extra = ['n_left =/= n_right', 'n_left =/= n_payload', 'n_right =/= n_payload',
        '$(n_left < |S_B.ARRAYS|)', '$(n_right < |S_B.ARRAYS|)',
        'S_B.ARRAYS[n_left].ITEMS = ' + items(19),
        'S_B.ARRAYS[n_right].ITEMS = ' + items(11),
        'S_B.ARRAYS[n_payload].ITEMS = ' + items(11),
        'S_B.STORE[n_outside] = DEFINED (PARRAY n_payload)',
        '$lookup(S_B.ENV, $ptascii("fieldValue")) = eps',
        'S_B.STORE[n_field] = DEFINED (PINT 13)',
        '$literal_reference_plain_cell(S_B, n_field)',
        '$heap_count(HCELL n_field, H_B.ROOTS) = 0',
        '$heap_owners(H_B, HCELL n_field) = 3']
    for array in ('n_left', 'n_right', 'n_payload'):
        extra += ['$node_children(S_B, HARRAY ' + array + ') = [HCELL n_field]',
            '$heap_member(HARRAY ' + array + ', $heap_prune(H_B).NODES)',
            '$heap_owners(H_B, HARRAY ' + array + ') = 1',
            '$heap_edge_owners(HCELL n_field, H_B.EDGES, [HARRAY ' + array + ']) = 1']
    checks[at:at] = extra
    derived += len(extra)
    at = checks.index('H_RET = $heap_graph(S_RET)') + 2
    extra = ['~((HARRAY n_left) <- S_RET.ALLOCATIONS)',
        '~((HARRAY n_right) <- S_RET.ALLOCATIONS)',
        '$heap_member(HARRAY n_payload, $heap_prune(H_RET).NODES)',
        '$heap_member(HCELL n_field, $heap_prune(H_RET).NODES)',
        'S_RET.ARRAYS[n_payload].ITEMS = ' + items(11),
        'S_RET.STORE[n_field] = DEFINED (PINT 13)',
        '$heap_owners(H_RET, HARRAY n_payload) = 1',
        '$heap_edge_owners(HARRAY n_payload, H_RET.EDGES, [HCELL n_outside]) = 1',
        '$heap_count(HCELL n_field, H_RET.ROOTS) = 0',
        '$heap_owners(H_RET, HCELL n_field) = 1']
    checks[at:at] = extra
    derived += len(extra)
    name = tuple(cases.CASES)[INDEX]
    output = prior.base.prior.seek.term(cases.OUTSIDE_OUTPUTS[name])
    at = checks.index('S_DONE = $drive_steps(S_RET, 4000)')
    extra = ['S_OUT_found = $review_scalar_fields_seek($drive_steps(S_RET, 1), ' + output + ', true, 4000)',
        '$review_scalar_fields_at(S_OUT_found, ' + output + ', true)',
        'S_OUT = $review_cv_running(S_OUT_found)', 'S_OUT.COMPLETION = NORMAL',
        '$lookup(S_OUT.ENV, $ptascii("outside")) = eps',
        '~((HCELL n_outside) <- S_OUT.ALLOCATIONS)',
        '~((HARRAY n_payload) <- S_OUT.ALLOCATIONS)',
        '~((HCELL n_field) <- S_OUT.ALLOCATIONS)',
        '$weakref_get(S_OUT, n_wrapper) = PNULL',
        '$weakref_get(S_OUT, n_after_wrapper) = POBJECT n_after',
        '$heap_valid($heap_graph(S_OUT))',
        'S_DONE = $drive_steps(S_OUT, 4000)']
    checks[at:at + 1] = extra
    derived += len(extra) - 1
    checks += ['~((HARRAY n_left) <- S_DONE.ALLOCATIONS)',
        '~((HARRAY n_right) <- S_DONE.ALLOCATIONS)',
        '~((HARRAY n_payload) <- S_DONE.ALLOCATIONS)',
        '~((HCELL n_field) <- S_DONE.ALLOCATIONS)']
    if PRELAW:
        return checks, derived + 4
    if PART == 'budget':
        at = next(i for i, check in enumerate(checks) if check.startswith('S_B_found = '))
        checks = checks[:at] + ['S_DONE = $drive_steps(S_P, 3000)',
            r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
            r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
            'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
            '$lookup(S_DONE.ENV, n_key_name*) = eps',
            '$lookup(S_DONE.ENV, $ptascii("objectAlias")) = eps',
            '$lookup(S_DONE.ENV, $ptascii("outside")) = eps',
            '$lookup(S_DONE.ENV, $ptascii("fieldValue")) = eps',
            '~((HCELL n_alias) <- S_DONE.ALLOCATIONS)',
            '~((HOBJECT n_object) <- S_DONE.ALLOCATIONS)',
            '~((HARRAY n_payload) <- S_DONE.ALLOCATIONS)',
            '~((HCELL n_field) <- S_DONE.ALLOCATIONS)',
            '$weakref_get(S_DONE, n_wrapper) = PNULL',
            '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.base.prior.seek.term(cases.OUTPUTS[name]),
            *prior.base.prior.seek.public('S_DONE')]
        if cases.FACTS[name]['throwing']:
            checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
        return checks, 0
    if PART == 'core':
        return checks, 0
    checks += ['$drive_steps(S_P, 3000) = S_DONE']
    reached = len(checks)
    checks += ['$string_unset_bool_cv_post_field_nodes(S_R, $heap_reach([HARRAY n_payload], eps, H_saved.EDGES))',
        '$string_unset_bool_cv_post_array_node(S_R, eps, n_payload)',
        '$string_unset_bool_cv_post_object_cell(S_R, n_alias)',
        '$string_unset_bool_cv_post_nonempty_array(S_R, n_key)']
    legacy = 'n_array' if INDEX else 'n_middle'
    checks += ['S_legacy = S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [' +
        prior.slot('$ptascii("payload")', 'PARRAY ' + legacy) + '])]',
        '~$string_unset_bool_cv_post_object(S_legacy, n_object)']
    for tag, item in (
        ('object', 'DIRECT (POBJECT n_object)'),
        ('alias_object', 'ALIAS n_alias'),
        ('cycle', 'DIRECT (PARRAY n_payload)'),
        ('nul', 'DIRECT (PSTRING_CARRIER INTERNED_STRING ([65, 0, 66]))'),
    ):
        state = 'S_bad_' + tag
        checks += [state + ' = S_R[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (' + item + ')]]',
            '~$string_unset_bool_cv_post_object(' + state + ', n_object)']
    checks += ['S_child_seed = $allocate_array(S_R, $array_insert($array_insert($array_empty(), KINT 0, DIRECT (PINT 5)), KINT 1, ALIAS n_field))',
        'S_child_seed.RESULT = KNOWN (PARRAY n_child)',
        'S_shared = S_child_seed[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)), ENTRY (KINT 1) (DIRECT (PARRAY n_child))]][.RESULT = S_R.RESULT]',
        '$heap_valid($heap_graph(S_shared))',
        '$heap_edge_owners(HARRAY n_child, $heap_graph(S_shared).EDGES, [HARRAY n_payload]) = 2',
        '$string_unset_bool_cv_post_object(S_shared, n_object)',
        'S_alias_array = S_child_seed[.ARRAYS[n_child] = $array_insert($array_empty(), KINT 0, DIRECT (PINT 4))][.STORE[n_field] = DEFINED (PARRAY n_child)][.RESULT = S_R.RESULT]',
        '$heap_valid($heap_graph(S_alias_array))',
        '~$literal_reference_plain_cell(S_alias_array, n_field)',
        '$string_unset_bool_cv_post_object(S_alias_array, n_object)',
        'S_alias_field = S_alias_array[.OBJECTPROPS = $objectprops_set(S_alias_array.OBJECTPROPS, n_object, [' +
        prior.slot('$ptascii("alias")', '', state='PROP_VALUE (ALIAS n_alias)') + '])]',
        '~$string_unset_bool_cv_post_object(S_alias_field, n_object)']
    file = json.dumps(base64.b64encode(b'/derived-array-field-flag.php').decode())
    if INDEX:
        checks += ['S_flag_compile = $php_run(' + TYPED_PROGRAM + ', 0, ' + file + ')',
            'S_flag_compile.COMPLETION = BUDGET',
            'porigin_flag_function = PORIGIN 0 ([PCINDEX 0])',
            '$function_at($all_functions(S_flag_compile), porigin_flag_function) = (pfunction_flag)',
            'pfunction_flag.SIGNATURE.BYREF',
            'porigin_flag = PORIGIN 0 ([PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 0, PCINDEX 0])',
            'pcallcontext_flag = {TARGET porigin_flag_function, CACHE eps, DEFAULTRECEIVE eps, WRAPPER eps, INSTANCE eps, RECEIVER eps, LEXICAL_CLASS eps, CALLED_CLASS eps, FUNCTION porigin_flag_function, NAME $ptascii("arrayFieldFlagTyped"), CALLSITE eps, LINE 1, PARAMS eps, ARGC 0, HOLES eps, EXTRA eps, NAMED eps}',
            'prefstringcv_flag = {SOURCE porigin_flag, LINE 1, CELL n_field, OBJECT n_object}',
            'pvalue_flag = PSTRING_CARRIER INTERNED_STRING ($ptascii("flag"))',
            'S_hidden = S_R[.SOURCES = S_flag_compile.SOURCES][.CODE = S_flag_compile.CODE][.FUNCTIONS = S_flag_compile.FUNCTIONS][.CURRENT = (pcallcontext_flag)][.ORIGIN = (porigin_flag)][.STORE[n_field] = DEFINED (POBJECT n_object)][.TODO = [REF_CV_STRING_COPY prefstringcv_flag pvalue_flag, REF_CV_STRING_TEMP prefstringcv_flag]]',
            '$finally_return_pending(S_hidden)',
            '$reference_return_fetch_valid(S_hidden, 1)',
            '$typed_cv_string_copy_valid(S_hidden, prefstringcv_flag, pvalue_flag)',
            '$typed_cv_string_released_cell(S_hidden, n_field)',
            '~$typed_cv_string_released_cell(S_hidden[.CURRENT = eps], n_field)',
            '~$typed_cv_string_released_cell(S_hidden[.SOURCES = eps], n_field)',
            '~$update_released_cell(S_hidden, n_field)']
    else:
        checks += ['S_flag_compile = $php_run(' + UPDATE_PROGRAM + ', 0, ' + file + ')',
            'S_flag_compile.COMPLETION = BUDGET',
            'porigin_flag = PORIGIN 0 ([PCINDEX 0, PCFIELD 0])',
            'pupdatewarning_flag = {SITE porigin_flag, OP INCREMENT, POST false, NAME $ptascii("fieldValue"), LINE 1, POINTER UPDATE_CELL n_field, INPUT (PBOOL false), PENDING eps}',
            'pupdaterestore_flag = {WARNING pupdatewarning_flag, CELL n_field, WRAPPER eps, VALUE (POBJECT n_object), CALLER S_R.CURRENT, CONSTCONTEXT S_R.CONSTCONTEXT}',
            'S_hidden = S_R[.SOURCES = S_flag_compile.SOURCES][.CODE = S_flag_compile.CODE][.ORIGIN = (porigin_flag)][.STORE[n_field] = DEFINED (POBJECT n_object)][.TODO = [UPDATE_WARNING_COMMIT pupdaterestore_flag]]',
            '$update_warning_source(S_hidden, pupdatewarning_flag)',
            '$update_restore_record_valid(S_hidden, pupdaterestore_flag)',
            '$update_released_cell(S_hidden, n_field)',
            '~$update_released_cell(S_hidden[.CODE = eps], n_field)',
            '~$update_released_cell(S_hidden[.SOURCES = eps], n_field)',
            '~$typed_cv_string_released_cell(S_hidden, n_field)']
    checks += ['$call_reference_operand_valid(S_hidden, REFERENCE n_field)',
        '~$foreach_released_cell(S_hidden, n_field)',
        'S_hidden.STORE[n_field] = DEFINED (POBJECT n_object)',
        '$node_children(S_hidden, HCELL n_field) = eps',
        'H_hidden = $heap_graph(S_hidden)', '$heap_valid(H_hidden)',
        'pnode_hidden* = $heap_reach([HARRAY n_payload], eps, H_hidden.EDGES)',
        '$heap_member(HCELL n_field, pnode_hidden*)',
        '~$heap_member(HOBJECT n_object, pnode_hidden*)',
        '$array_float_key_plain_nodes(pnode_hidden*)',
        '~$string_unset_bool_cv_post_field_nodes(S_hidden, pnode_hidden*)',
        '~$string_unset_bool_cv_post_object(S_hidden, n_object)',
        '~$string_unset_bool_cv_post_nonempty_array(S_hidden, n_key)',
        'S_hidden_child = $allocate_array(S_hidden, $array_insert($array_empty(), KINT 0, ALIAS n_field))',
        'S_hidden_child.RESULT = KNOWN (PARRAY n_hidden_child)',
        'S_hidden_shared = S_hidden_child[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_hidden_child)), ENTRY (KINT 1) (DIRECT (PARRAY n_hidden_child))]][.RESULT = S_hidden.RESULT]',
        'H_hidden_shared = $heap_graph(S_hidden_shared)', '$heap_valid(H_hidden_shared)',
        '$heap_edge_owners(HARRAY n_hidden_child, H_hidden_shared.EDGES, [HARRAY n_payload]) = 2',
        'pnode_hidden_shared* = $heap_reach([HARRAY n_payload], eps, H_hidden_shared.EDGES)',
        '$heap_member(HCELL n_field, pnode_hidden_shared*)',
        '~$heap_member(HOBJECT n_object, pnode_hidden_shared*)',
        '$array_float_key_plain_nodes(pnode_hidden_shared*)',
        '~$string_unset_bool_cv_post_field_nodes(S_hidden_shared, pnode_hidden_shared*)',
        '~$string_unset_bool_cv_post_object(S_hidden_shared, n_object)']
    if PART == 'guards':
        return front(program, path) + checks[reached:], len(checks) - reached
    return checks, derived + 4 + len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    if '--part' in sys.argv:
        at = sys.argv.index('--part')
        PART = sys.argv[at + 1]
        del sys.argv[at:at + 2]
    assert PART in ('all', 'core', 'budget', 'guards') and (not PRELAW or PART == 'all')
    watched = [Path(__file__), Path(prior.__file__), Path(prior.base.__file__),
        Path(prior.base.prior.__file__), Path(prior.base.prior.seek.__file__),
        Path(prior.base.prior.sl.__file__), Path(cases.__file__),
        *[prior.base.prior.runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.base.prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.base.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['part'] = PART
    report['source_bridge_credit'] = int(passed and not PRELAW and PART == 'budget' and cases.FACTS[runner.NAME]['throwing'])
    report['scope'] = ('Independent reached DIRECT arrays and outside owners precede old Unsupported; derived COW, shared-cell and staged-retirement facts source0/native0.' if PRELAW else
        'Independent DIRECT-array field COW, shared scalar cells, outside-owner retirement and full-state/public/budget replay; derived compiler-authenticated marked UPDATE_CELL/protected typed-COPY hidden-parent flags, cycles, shared siblings and ALIAS-array composition remain source0/native0. Same-state valid FOREACH_BIND_COMMIT requires OLD nonREF while ordinary ALIAS authentication requires REF; no marked-foreach witness is claimed.')
    if not PRELAW and PART == 'core':
        report['scope'] = 'Independent checked original prefix through the exact new step, COW, shared cells, B/R/O retirement and final native bytes; the complete budget replay is a separate required cut.'
    if PART == 'budget':
        report['scope'] = 'Independent checked original prefix and exact new step followed by complete drive_steps(S_P,3000), final native bytes and same pending identity; source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
