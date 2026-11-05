#!/usr/bin/env python3
"""Keep a computed Generator selection through argument-side rebinding."""
import hashlib
import json
import base64
from pathlib import Path
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_computed_method_review_cases.json')
ROW = json.loads(CATALOG.read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection) '
    '-- if pconfigcall.OWNER = (n_generator) '
    '-- if $lookup(S.ENV, $ptascii("method")) = (n_method_cv) '
    '-- if S.STORE[n_method_cv] = DEFINED (PSTRING $ptascii("throw"))')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
pgeneratormethodselection.SITE = pconfigcall.SITE
pgeneratormethodselection.OBJECT = n_generator
pgeneratormethodselection.NAME = $ptascii("SeNd")
pgeneratormethodselection.LINE = pconfigcall.LINE
pconfigcall.SELECTION = eps
pconfigcall.INDEX = 1
pconfigcall.NAMED
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_token))]
pconfigcall.PACKS = [pconfigpack]
pconfigpack.INDEX = 0
pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (POBJECT n_token))]
~((HARRAY pconfigpack.ARRAY) <- S.ALLOCATIONS)
$lookup(S.ENV, $ptascii("generator")) = (n_generator_cv)
S.STORE[n_generator_cv] = DEFINED (POBJECT n_other)
n_other =/= n_generator
$lookup(S.ENV, $ptascii("other")) = (n_other_cv)
S.STORE[n_other_cv] = DEFINED (POBJECT n_other)
$lookup(S.ENV, $ptascii("methodAlias")) = (n_method_cv)
n_method_cv <- S.REFCELLS
$lookup(S.ENV, $ptascii("pack")) = (n_pack_cv)
S.STORE[n_pack_cv] = DEFINED PNULL
$lookup(S.ENV, $ptascii("cell")) = (n_caller_cell)
S.STORE[n_caller_cell] = DEFINED (POBJECT n_token)
n_caller_cell <- S.REFCELLS
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_FRESH
$object_name(S, n_token) = $ptascii("Token111P")
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_generator_cv)
S.STORE[n_weak_generator_cv] = DEFINED (POBJECT n_weak_generator)
$weakref_get(S, n_weak_generator) = POBJECT n_generator
ptask_tail* = METHOD_RESULT :: (DIM_FETCH z_fetch) :: ptask_after*
$task_nodes(METHOD_RESULT) = eps
$origin_node(S.SOURCES, pconfigcall.SITE) = (NExprNullsafeMethodCall expression_receiver expression_name (SEQUENCE phpType7*) metadata_site)
$property_computed_name(expression_name)
~$generator_source_method(S, pconfigcall.SITE, $ptascii("send"))
(OUTPUT $ptascii("NULL|")) <- S.EVENTS
~((OUTPUT $ptascii("BAD-NAME|")) <- S.EVENTS)
~((OUTPUT $ptascii("BAD-PACK|")) <- S.EVENTS)
$config_nodes(pconfigcall) = [HOBJECT n_generator, HOBJECT n_token]
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HOBJECT n_other) = 2
$call_task_valid(S, CONFIG_INVOKE pconfigcall)
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" eps])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "throw" (pgeneratormethodselection)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.OWNER = (n_other)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.OBJECT = n_other])])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.NAME = $ptascii("throw")])])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.LINE = $(pconfigcall.LINE + 1)])])
$origin_child((pconfigcall.SITE), [PCFIELD 0]) = (porigin_wrong)
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.SITE = porigin_wrong])])
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_normalized
S_normalized.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) :: ptask_tail*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.SITE = pconfigcall.SITE
pgeneratorop.LINE = pconfigcall.LINE
pgeneratorop.SELECTION = (pgeneratormethodselection)
$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) = $config_nodes(pconfigcall)
S_normalized.EVENTS = S.EVENTS
S_normalized.STORE = S.STORE
S_normalized.ALLOCATIONS = S.ALLOCATIONS
$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop[.SELECTION = eps] eps ([KNOWN (POBJECT n_token)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop[.NAME = "throw"] eps ([KNOWN (POBJECT n_token)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop[.OBJECT = n_other] eps ([KNOWN (POBJECT n_token)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop[.BORROWED = true] eps ([KNOWN (POBJECT n_token)]))
$heap_valid($heap_graph(S_normalized))
$call_descriptors_valid(S_normalized)
'''.splitlines() if line.strip()]

# These source views test only the shared site predicate, without asserting
# that the altered source view is a complete executable machine state.
CHECKS.append('pconfigcall.SITE = PORIGIN n_unit pcpath_site')
for label, node, method, first_class, expected in (
        ('bind', 'NExprMethodCall', 'bind', False, True),
        ('bindto', 'NExprNullsafeMethodCall', 'bindTo', False, True),
        ('invoke', 'NExprMethodCall', '__invoke', False, True),
        ('nullinvoke', 'NExprNullsafeMethodCall', '__invoke', False, True),
        ('other', 'NExprMethodCall', 'other', False, False),
        ('nullother', 'NExprNullsafeMethodCall', 'other', False, False),
        ('first', 'NExprMethodCall', '__invoke', True, False),
        ('nullfirst', 'NExprNullsafeMethodCall', '__invoke', True, False)):
    spelling = json.dumps(base64.b64encode(method.encode()).decode())
    arguments = '[(NVariadicPlaceholder metadata_site)]' if first_class else 'eps'
    expression = (f'{node} expression_receiver (NIdentifier (BYTES {spelling}) metadata_site) '
                  f'(SEQUENCE ({arguments})) metadata_site')
    CHECKS += [
        f'S_{label} = S[.SOURCES = [{{ID n_unit, AST PROGRAM eps, OCCURRENCES '
        f'[(PCOCCURRENCE pcpath_site ({expression}))]}}]]',
        ('' if expected else '~') + f'$closure_binding_api_site(S_{label}, pconfigcall.SITE)']

review.CASES = {'i111-peer-computed-selection-normalization-owners': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
