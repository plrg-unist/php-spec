#!/usr/bin/env python3
"""Check folded capture authority and early static-call warning owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_folded_string_call_cases.json')
INPUT_BYTES = {p:p.read_bytes() for p in (Path(__file__),CATALOG,Path(review.__file__))}
ROWS = {r['id']:r for r in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

API_STAGE = 'S.TODO = (GENERATOR_CREATE porigin_function) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_copy -- if S.FRAMES = pframe_api :: pframe_tail* -- if pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api*'

API = checks(r'''

S.COMPLETION = NORMAL
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake_copy
(HOBJECT n_copy) <- S.ALLOCATIONS
n_source = pboundfake_copy.SOURCE
$(n_source < n_copy)
pboundfake_copy.ORIGINAL = (pclosurescope_original)
pclosurescope_original.OBJECT = n_source
pclosurescope_original.CREATION = eps
pclosurescope_original.RECEIVER = (n_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base96A"))) = (porigin_base)
pboundfake_copy.SCOPE = BIND_CLASS porigin_base
pboundfake_copy.CALLED = BIND_CLASS porigin_base
pboundfake_copy.RECEIVER = (n_maker)
n_old =/= n_maker
S.OBJECTS[n_maker] = INSTANCE porigin_base
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child96A"))) = (porigin_child)
S.OBJECTS[n_old] = INSTANCE porigin_child
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = eps
$closure_call_copy_site(S, pboundfake_copy.SITE)
$closure_call_fake_copy_binding(S, pboundfake_copy)
$bound_fake_valid(S, n_copy)
$closure_call_copy_row(S, n_copy) = (pclosurebinding_copy)
pclosurebinding_copy.OBJECT = n_copy
pclosurebinding_copy.SOURCE = n_source
pclosurebinding_copy.SITE = pboundfake_copy.SITE
pclosurebinding_copy.LEXICAL = (porigin_base)
pclosurebinding_copy.CALLED = (porigin_base)
pclosurebinding_copy.RECEIVER = (n_maker)
~$closure_call_copy_binding(S, pclosurebinding_copy)
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
porigin_function = pfunction.ORIGIN
$class_method_origin(S.CLASSES, porigin_function) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
~pmethoddesc.STATIC
$function_generator(S, pfunction)
$closure_callable(S, n_copy)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
$target_lexical_class(S, CLOSURE_TARGET n_copy) = (porigin_base)
$target_called_class(S, CLOSURE_TARGET n_copy) = (porigin_base)
$target_receiver(S, CLOSURE_TARGET n_copy) = (n_maker)
$call_selected_valid(S, CLOSURE_TARGET n_copy, (pboundfake_copy.SITE))
S.OBJECTS[n_source] = STRINGMETHODCLOSURE pcalltarget_selected pstringselection
$dynamic_fixed_name(S, pstringselection.SITE) =/= eps
$string_site_valid(S, pstringselection, true)
pstringselection.ORIGINAL = $ptascii("Base96A::stream")
pstringselection.REQUESTED = porigin_base
$target_receiver(S, pcalltarget_selected) = (n_old)
$target_function(S, pcalltarget_selected) = (pfunction)
$closure_call_fake_method(S, n_source, pfunction)
~$closure_call_real(S, n_source)
~pfunction.SIGNATURE.BYREF
~$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)
pcallcontext.FUNCTION = porigin_function
pcallcontext.TARGET = CLOSURE_TARGET n_copy
pcallcontext.INSTANCE = (n_copy)
pcallcontext.LEXICAL_CLASS = (porigin_base)
pcallcontext.CALLED_CLASS = (porigin_base)
pcallcontext.RECEIVER = (n_maker)
pcallcontext.CALLSITE = (pboundfake_copy.SITE)
pcallcontext.WRAPPER = eps
pcallcontext.ARGC = 1
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pboundfake_copy.SITE
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pclosurecall.INDEX = 2
pclosurecall.PACKS = eps
pclosurecall.ERROR = eps
$closure_call_copy_required(S, pfunction, pclosurecall)
$closure_call_copy_kind(S, pfunction, pclosurecall, n_maker)
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$task_nodes(CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source]
$call_context_roots((pcallcontext)) = [HOBJECT n_copy]
$call_receiver_roots(pcallcontext) = eps
$call_current_valid(S)
$generator_creation_supported(S, pcallcontext)
S.GLOBALTABLE = (psymboltable_root)
$lookup(psymboltable_root.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$lookup(psymboltable_root.ENV, $ptascii("old")) = (n_old_cell)
S.STORE[n_old_cell] = DEFINED (POBJECT n_old)
$lookup(psymboltable_root.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED (POBJECT n_maker)
$lookup(psymboltable_root.ENV, $ptascii("token")) = (n_token_cell)
S.STORE[n_token_cell] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token96A")
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 2
$heap_owners(H, HOBJECT n_copy) = 2
$heap_owners(H, HOBJECT n_old) = 2
$heap_owners(H, HOBJECT n_maker) = 3
$heap_owners(H, HOBJECT n_token) = 3
$eval_trace_preparser(S, (pcallcontext), pframe_api) = [ptraceframe_api]
ptraceframe_api.FUNCTION = $ptascii("call")
ptraceframe_api.CLASS = ($ptascii("Closure"))
ptraceframe_api.ARGS = [(KINT 0, POBJECT n_maker), (KINT 1, POBJECT n_token)]
pboundfake_bad_scope = pboundfake_copy[.SCOPE = BIND_UNSCOPED]
~$closure_call_fake_copy_binding(S, pboundfake_bad_scope)
pboundfake_bad_called = pboundfake_copy[.CALLED = BIND_UNSCOPED]
~$closure_call_fake_copy_binding(S, pboundfake_bad_called)
pboundfake_old = pboundfake_copy[.CALLED = BIND_CLASS porigin_child][.RECEIVER = (n_old)]
S_old = S[.OBJECTS = $object_set(S.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_old)]
$bound_fake_receiver_valid(S_old, pboundfake_old)
~$closure_call_fake_copy_binding(S_old, pboundfake_old)
~$closure_call_copy_result_valid(S_old, pclosurecall, n_copy)
~$call_current_valid(S_old)
S_dead_source = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_kind(S_dead_source, pfunction, pclosurecall, n_maker)
S_dead_receiver = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_maker)]
~$closure_call_copy_kind(S_dead_receiver, pfunction, pclosurecall, n_maker)
~$closure_call_copy_site(S[.CODE = eps], pboundfake_copy.SITE)
$heap_valid(H)
''')


WARNING_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if S.CURRENT = (pcallcontext_handler) '
    '-- if $error_context_call(S, pcallcontext_handler) = (perrorcall) '
    '-- if perrorcall.RESUME = CLOSURE_CALL_WARNING pclosurecall ptbytes_warning '
    '-- if S.GLOBALTABLE = (psymboltable_root) '
    '-- if $lookup(psymboltable_root.ENV, $ptascii("source")) = (n_source_cell) '
    '-- if S.STORE[n_source_cell] = DEFINED PNULL '
    '-- if $lookup(psymboltable_root.ENV, $ptascii("weakSource")) = (n_weak_cell) '
    '-- if S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak) '
    '-- if pconfigcall.OWNER = (n_weak)')

WARNING = checks(r'''
S.COMPLETION = NORMAL
n_source = pclosurecall.SOURCE
S.OBJECTS[n_source] = STRINGMETHODCLOSURE pcalltarget_selected pstringselection
$dynamic_fixed_name(S, pstringselection.SITE) = eps
$string_site_valid(S, pstringselection, true)
pstringselection.ORIGINAL = $ptascii("Base96B::stream")
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base96B"))) = (porigin_base)
pstringselection.REQUESTED = porigin_base
$target_function(S, CLOSURE_TARGET n_source) = (pfunction)
$function_generator(S, pfunction)
$class_method_origin(S.CLASSES, pfunction.ORIGIN) = (pmethoddesc)
pmethoddesc.STATIC
$target_receiver(S, CLOSURE_TARGET n_source) = eps
$node_children(S, HOBJECT n_source) = eps
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pclosurecall.PACKS = eps
pclosurecall.ERROR = eps
pclosurecall.INDEX = 2
S.OBJECTS[n_maker] = INSTANCE porigin_base
$object_name(S, n_token) = $ptascii("Token96B")
ptbytes_warning = $ptascii("Cannot bind an instance to a static closure, this will be an error in PHP 9")
$closure_call_warning(S, n_source, n_maker) = (ptbytes_warning)
~$closure_call_copy_required(S, pfunction, pclosurecall)
$closure_callable(S, n_source)
$weakref_get(S, n_weak) = POBJECT n_source
$task_nodes(CLOSURE_CALL_WARNING pclosurecall ptbytes_warning) = [HOBJECT n_source, HOBJECT n_maker, HOBJECT n_token]
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_valid(H)
''')

ABRUPT = checks(r'''
S.COMPLETION = NORMAL
n_source = pclosurecall.SOURCE
S.OBJECTS[n_source] = STRINGMETHODCLOSURE pcalltarget_selected pstringselection
$dynamic_fixed_name(S, pstringselection.SITE) = eps
$string_site_valid(S, pstringselection, true)
pstringselection.ORIGINAL = $ptascii("Base96C::stream")
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base96C"))) = (porigin_base)
pstringselection.REQUESTED = porigin_base
$target_function(S, CLOSURE_TARGET n_source) = (pfunction)
$function_generator(S, pfunction)
$class_method_origin(S.CLASSES, pfunction.ORIGIN) = (pmethoddesc)
pmethoddesc.STATIC
$target_receiver(S, CLOSURE_TARGET n_source) = eps
$node_children(S, HOBJECT n_source) = eps
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pclosurecall.PACKS = eps
pclosurecall.ERROR = eps
pclosurecall.INDEX = 2
S.OBJECTS[n_maker] = INSTANCE porigin_base
$object_name(S, n_token) = $ptascii("Token96C")
ptbytes_warning = $ptascii("Cannot bind an instance to a static closure, this will be an error in PHP 9")
$closure_call_warning(S, n_source, n_maker) = (ptbytes_warning)
~$closure_call_copy_required(S, pfunction, pclosurecall)
$closure_callable(S, n_source)
$weakref_get(S, n_weak) = POBJECT n_source
$task_nodes(CLOSURE_CALL_WARNING pclosurecall ptbytes_warning) = [HOBJECT n_source, HOBJECT n_maker, HOBJECT n_token]
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_valid(H)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 2400)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2400)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))

''')

CASES = {
    'i96-folded-copy-api-entry': {'source':ROWS['i96-folded-private-string-call-value-send']['source'],'stage':API_STAGE,'checks':API},
    'i96-static-string-warning-owners': {'source':ROWS['i96-static-string-call-binding-warning-php9']['source'],'stage':WARNING_STAGE,'checks':WARNING},
    'i96-static-string-warning-abrupt-cleanup': {'source':ROWS['i96-static-string-binding-warning-supplied-throw']['source'],'stage':WARNING_STAGE,'checks':ABRUPT},
}

def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected, process_seconds=300)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
