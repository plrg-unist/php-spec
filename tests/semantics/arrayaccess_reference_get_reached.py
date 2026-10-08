"""Bounded 319 checks reached from the exact maintained original programs."""

from error_handler_protocol import PREFIX


CASES = [
    ('discarded-get-demand', 'mixed-get-quiet-copy-and-unused-demand'),
    ('sole-w-reference-move', 'sole-reference-false-w-fetch-unwraps'),
    ('shared-w-reference-preserved', 'shared-reference-false-w-fetch-preserved'),
    ('raw-compound-carrier-and-throw', 'compound-rebound-reference-retires-before-catch'),
    ('nested-reference-acquisition-row', 'shared-get-copy-and-nested-alias'),
    ('unset-retired-parent-source', 'unset-keeps-captured-child-after-parent-retirement'),
]


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$gc_state_valid({state})']


def demand():
    stage = ('S.TODO = (RETURN_REF_FETCH z) :: ptask_tail* '
             '-- if S.CURRENT = (pcallcontext) '
             '-- if S.FRAMES = pframe :: pframe_tail* '
             '-- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved* '
             '-- if paccess.MODE = ACCESS_READ KEY_R '
             '-- if paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")')
    checks = '''
S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*
S.CURRENT = (pcallcontext)
S.FRAMES = pframe :: pframe_tail*
pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
paccess.MODE = ACCESS_READ KEY_R
paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
pcallcontext.CALLSITE = (paccess.SITE)
$access_frame(S, pcallcontext, pframe)
$target_function(S, $context_target(pcallcontext)) = (pfunction)
pfunction.SIGNATURE.BYREF
"mixed" <- $ptmasks(pfunction.SIGNATURE.RETURNS)
$access_reference_signature(pfunction.SIGNATURE)
$access_reference_signature(pfunction.SIGNATURE[.RETURNS = eps])
~$access_reference_signature(pfunction.SIGNATURE[.RETURNS = ([(PTBRANCH ([PTBUILTIN "int"]))])])
~$reference_verifies(S)
~$reference_call_used(S, paccess.SITE)
$reference_callback_used(S, pcallcontext) = (true)
$reference_return_used(S)
$outputs(S.EVENTS) = $ptascii("G;")
pframe_bad = pframe[.TODO = (ACCESS_RESULT paccess[.LINE = $(paccess.LINE + 1)]) :: ptask_saved*]
S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]
$heap_graph(S_bad) = $heap_graph(S)
~$access_frame(S_bad, pcallcontext, pframe_bad)
$reference_callback_used(S_bad, pcallcontext) = eps
~$call_frames_valid(S_bad, S_bad.FRAMES)
'''.strip().splitlines()
    return stage, checks + guards('S') + budget()


def budget():
    return ['S_zero = $drive_steps(S, 0)',
            'S_zero = S[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = BUDGET'] + guards('S_one')


def fetch(shared):
    stage = ('S.TODO = (ACCESS_RESULT paccess) :: ptask_tail* '
             '-- if paccess.MODE = ACCESS_FETCH b_unset b_rw '
             '-- if paccess.PHASE = ACCESS_CALL $ptascii("offsetGet") '
             '-- if S.RESULT = REFERENCE n')
    checks = '''
S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*
paccess.MODE = ACCESS_FETCH false false
paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
S.RESULT = REFERENCE n
n <- S.REFCELLS
(HCELL n) <- S.ALLOCATIONS
S.STORE[n] = DEFINED (PBOOL false)
$access_valid(S, paccess)
$access_reference_get(S, paccess)
$access_reference_result_pending(S)
$call_reference_operand_valid(S, S.RESULT)
n_count = $heap_owners($heap_prune($heap_graph(S)), HCELL n)
'''.strip().splitlines()
    checks += ['$(n_count > 1)' if shared else 'n_count = 1'] + guards('S')
    checks += '''
PhpStep: S ~> S_moved
S_moved.COMPLETION = NORMAL
S_moved.LOCATION = ROOT n
S_moved.RESULT = KNOWN PNULL
S_moved.STORE = S.STORE
S_moved.ALLOCATIONS = S.ALLOCATIONS
S_moved.GC = S.GC
S_moved.DESTRUCTION = S.DESTRUCTION
$access_parent_tasks(S_moved.TODO, paccess.TARGET) = (n)
$access_returned_valid(S_moved, n)
$heap_owners($heap_prune($heap_graph(S_moved)), HCELL n) = n_count
'''.strip().splitlines()
    checks += (['S_moved.REFCELLS = S.REFCELLS'] if shared
               else ['~(n <- S_moved.REFCELLS)',
                     'S_moved.REFCELLS = $access_reference_unwrap(S.REFCELLS, n)'])
    return stage, checks + guards('S_moved') + budget()


def compound(expected):
    stage = ('S.TODO = (ACCESS_RESULT paccess) :: ptask_tail* '
             '-- if paccess.MODE = ACCESS_COMPOUND CONCAT PNULL '
             '-- if paccess.PHASE = ACCESS_CALL $ptascii("offsetGet") '
             '-- if S.RESULT = REFERENCE n')
    checks = '''
S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*
paccess.MODE = ACCESS_COMPOUND CONCAT PNULL
paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
S.RESULT = REFERENCE n
S.STORE[n] = DEFINED (PARRAY n_array)
$access_valid(S, paccess)
$access_reference_get(S, paccess)
$access_reference_result_pending(S)
$call_reference_operand_valid(S, S.RESULT)
$outputs(S.EVENTS) = $ptascii("G;")
'''.strip().splitlines() + guards('S')
    checks += '''
PhpStep: S ~> S_set
S_set.COMPLETION = NORMAL
S_set.TODO = (CALL_ARGS pcalltarget eps n_args poperand* (porigin) z) :: (ACCESS_RESULT paccess_set) :: ptask_set*
paccess_set.MODE = ACCESS_REFERENCE_COMPOUND CONCAT n
paccess_set.PHASE = ACCESS_CALL $ptascii("offsetSet")
paccess_set.VALUE = PSTRING $ptascii("Arrayb")
paccess_set.SITE = porigin
$access_extra_roots(paccess_set) = [HCELL n]
S_set.STORE = S.STORE
S_set.HELD = S.HELD
$access_valid(S_set, paccess_set)
$access_source(S_set, paccess_set)
$call_reference_operand_valid(S_set, REFERENCE n)
'''.strip().splitlines() + guards('S_set')
    checks += '''
paccess_line = paccess_set[.LINE = $(paccess_set.LINE + 1)]
S_line = S_set[.TODO = (CALL_ARGS pcalltarget eps n_args poperand* (porigin) z) :: (ACCESS_RESULT paccess_line) :: ptask_set*]
$heap_graph(S_line) = $heap_graph(S_set)
~$access_source(S_line, paccess_line)
~$call_descriptors_valid(S_line)
$lookup(S_set.ENV, $ptascii("box")) = (n_plain)
(HCELL n_plain) <- S_set.ALLOCATIONS
~(n_plain <- S_set.REFCELLS)
paccess_plain = paccess_set[.MODE = ACCESS_REFERENCE_COMPOUND CONCAT n_plain]
S_plain = S_set[.TODO = (CALL_ARGS pcalltarget eps n_args poperand* (porigin) z) :: (ACCESS_RESULT paccess_plain) :: ptask_set*]
$heap_valid($heap_graph(S_plain))
~$call_reference_operand_valid(S_plain, REFERENCE n_plain)
~$access_source(S_plain, paccess_plain)
~$call_descriptors_valid(S_plain)
S_rejected = $call_entry_check(S_plain)
S_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
S_rejected.TODO = eps
S_rejected.STORE = S_plain.STORE
n_out = |S_set.STORE|
~$access_source(S_set, paccess_set[.MODE = ACCESS_REFERENCE_COMPOUND CONCAT n_out])
'''.strip().splitlines()
    checks += budget()
    checks += ['S_done = $drive(S_one[.COMPLETION = NORMAL], 1500)',
               'S_direct = $drive(S, 1500)',
               'S_done = S_direct',
               'S_done.COMPLETION = NORMAL',
               'S_done.TODO = eps', 'S_done.CURRENT = eps',
               'S_done.FRAMES = eps',
               '$outputs(S_done.EVENTS) = $ptascii("' + expected + '")']
    return stage, checks + guards('S_done')


def acquire():
    stage = ('S.TODO = (KEY_WRITE_FINISH pkeywriter) :: ptask_tail* '
             '-- if pkeywriter.TASK = ACQUIRE_ARRAY z')
    checks = '''
S.TODO = (KEY_WRITE_FINISH pkeywriter) :: ptask_tail*
pkeywriter.TASK = ACQUIRE_ARRAY z
pkeywriter.BASE = BASE_PLACE pkeywriter.TARGET (ELEMENT n pkey)
pkey = KSTRING $ptascii("x")
S.ORIGIN = (pkeywriter.SITE)
S.LOCATION = ELEMENT n pkey
(HARRAY n) <- S.ALLOCATIONS
$entry_lookup(S.ARRAYS[n].ITEMS, pkey) = (DIRECT (PINT 2))
$lookup(S.ENV, $ptascii("data18")) = (n_back)
S.STORE[n_back] = DEFINED (PARRAY n)
n_back <- S.REFCELLS
$access_original_writer(S, pkeywriter) = (pkeywriter_original)
pkeywriter_original.BASE = pkeywriter.BASE
~$access_has_returned(pkeywriter.BASE)
~$access_reference_temporary(S, pkeywriter)
$key_writer_valid(S, pkeywriter, ptask_tail*)
$outputs(S.EVENTS) = $ptascii("G;G;R:1:2;G;G;")
PhpStep: S ~> S_ref
S_ref.COMPLETION = NORMAL
S_ref.TODO = ptask_tail*
S_ref.RESULT = REFERENCE n_ref
S_ref.CELL = n_ref
n_ref = |S.STORE|
S_ref.STORE[n_ref] = DEFINED (PINT 2)
n_ref <- S_ref.REFCELLS
S_ref.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_ref]
$entry_lookup(S_ref.ARRAYS[n].ITEMS, pkey) = (ALIAS n_ref)
$call_reference_operand_valid(S_ref, S_ref.RESULT)
S_ref.GC = S.GC
S_ref.HELD = S.HELD
pkeywriter_site = pkeywriter[.SITE = PORIGIN 0 eps]
S_site = S[.TODO = (KEY_WRITE_FINISH pkeywriter_site) :: ptask_tail*]
$heap_graph(S_site) = $heap_graph(S)
~$key_writer_valid(S_site, pkeywriter_site, ptask_tail*)
pkeywriter_line = pkeywriter[.TASK = ACQUIRE_ARRAY $(z + 1)]
S_line = S[.TODO = (KEY_WRITE_FINISH pkeywriter_line) :: ptask_tail*]
$heap_graph(S_line) = $heap_graph(S)
~$key_writer_valid(S_line, pkeywriter_line, ptask_tail*)
pkeywriter_base = pkeywriter[.BASE = BASE_PLACE (PORIGIN 0 eps) (ELEMENT n pkey)]
S_base = S[.TODO = (KEY_WRITE_FINISH pkeywriter_base) :: ptask_tail*]
$heap_graph(S_base) = $heap_graph(S)
~$key_writer_valid(S_base, pkeywriter_base, ptask_tail*)
pkeywriter_root = pkeywriter[.BASE = BASE_PLACE pkeywriter.TARGET (ROOT n_back)]
~$key_writer_valid(S, pkeywriter_root, ptask_tail*)
pkeywriter_missing = pkeywriter[.BASE = BASE_PLACE pkeywriter.TARGET (ELEMENT n (KSTRING $ptascii("absent")))]
~$key_writer_valid(S, pkeywriter_missing, ptask_tail*)
'''.strip().splitlines()
    return stage, checks + guards('S') + guards('S_ref') + budget()


def unset_retired():
    stage = ('S.TODO = (KEY_UNSET_RESULT pkeyread) :: ptask_tail* '
             '-- if $key_float_phase(pkeyread.PHASE) '
             '-- if $lookup(S.ENV, $ptascii("back18")) = eps')
    checks = '''
S.TODO = (KEY_UNSET_RESULT pkeyread) :: ptask_tail*
ptask_tail* = (KEY_UNSET_FINISH pkeyread.SITE pbase) :: ptask_after*
pbase = BASE_DIM (BASE_PLACE porigin_prefix (ELEMENT n_parent (KSTRING $ptascii("a")))) poperand z
S.ORIGIN = (pkeyread.SITE)
pkeyread.MODE = KEY_R
pkeyread.PHASE = KEY_FLOAT PRECISIONLOSS eps
pkeyread.BASE = PARRAY n_child
pkeyread.VALUE = PFLOAT n_bits
pkeyread.INPUT = KNOWN (PFLOAT n_bits)
pkeyread.KEY = KINT 1
$lookup(S.ENV, $ptascii("back18")) = eps
$lookup(S.ENV, $ptascii("child18")) = (n_alias)
S.STORE[n_alias] = DEFINED (PARRAY n_child)
n_alias <- S.REFCELLS
$heap_owners($heap_prune($heap_graph(S)), HARRAY n_parent) = 0
$heap_owners($heap_prune($heap_graph(S)), HARRAY n_child) = 2
$task_nodes(KEY_UNSET_RESULT pkeyread) = [HARRAY n_child]
$task_nodes(KEY_UNSET_FINISH pkeyread.SITE pbase) = eps
$entry_lookup(S.ARRAYS[n_child].ITEMS, KINT 1) = (DIRECT (PINT 7))
$entry_lookup(S.ARRAYS[n_child].ITEMS, KINT 2) = (DIRECT (PINT 9))
~$key_tail_chain(pbase)
$access_unset_captured(pbase)
$key_unset_source(S, pkeyread.SITE, pbase)
$key_unset_valid(S, pkeyread)
$key_unset_live(S, pkeyread)
$outputs(S.EVENTS) = $ptascii("G;H:8192;")
pbase_bad = BASE_DIM (BASE_PLACE (PORIGIN 0 eps) (ELEMENT n_parent (KSTRING $ptascii("a")))) poperand z
S_bad = S[.TODO = (KEY_UNSET_RESULT pkeyread) :: (KEY_UNSET_FINISH pkeyread.SITE pbase_bad) :: ptask_after*]
$heap_graph(S_bad) = $heap_graph(S)
~$key_unset_source(S_bad, pkeyread.SITE, pbase_bad)
~$key_unset_valid(S_bad, pkeyread)
~$call_descriptors_valid(S_bad)
~$key_unset_source(S, PORIGIN 0 eps, pbase)
~$key_unset_valid(S, pkeyread[.LINE = $(pkeyread.LINE + 1)])
~$key_unset_valid(S, pkeyread[.KEY = KINT 2])
~$key_unset_valid(S, pkeyread[.MODE = KEY_IS])
PhpStep: S ~> S_deleted
S_deleted.COMPLETION = NORMAL
S_deleted.TODO = ptask_tail*
S_deleted.RESULT = KNOWN PNULL
S_deleted.LOCATION = NOWHERE
S_deleted.STORE = S.STORE
S_deleted.HELD = S.HELD
S_deleted.GC = S.GC
$entry_lookup(S_deleted.ARRAYS[n_child].ITEMS, KINT 1) = eps
$entry_lookup(S_deleted.ARRAYS[n_child].ITEMS, KINT 2) = (DIRECT (PINT 9))
$heap_owners($heap_prune($heap_graph(S_deleted)), HARRAY n_child) = 1
$key_unset_source(S_deleted, pkeyread.SITE, pbase)
PhpStep: S_deleted ~> S_finished
S_finished.COMPLETION = NORMAL
S_finished.TODO = ptask_after*
S_finished.STORE = S_deleted.STORE
S_finished.ARRAYS = S_deleted.ARRAYS
'''.strip().splitlines()
    return (stage, checks + guards('S') + guards('S_deleted')
            + guards('S_finished') + budget())


def render(name, fixture, filename, expected):
    if name == 'discarded-get-demand':
        stage, checks = demand()
    elif name == 'sole-w-reference-move':
        stage, checks = fetch(False)
    elif name == 'shared-w-reference-preserved':
        stage, checks = fetch(True)
    elif name == 'raw-compound-carrier-and-throw':
        stage, checks = compound(expected)
    elif name == 'nested-reference-acquisition-row':
        stage, checks = acquire()
    elif name == 'unset-retired-parent-source':
        stage, checks = unset_retired()
    else:
        raise ValueError(name)
    checks = [f'S_initial = $php_run({fixture}, 0, {filename})',
              'S_initial.COMPLETION = BUDGET',
              'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
              r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
              'S = S_reached[.COMPLETION = NORMAL]'] + checks
    text = PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep: ') else 'if ')
                    + check + '\n' for check in checks)
    return text, checks
