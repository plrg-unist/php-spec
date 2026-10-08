"""New 326 consumer checks from the exact maintained checked originals."""

from error_handler_protocol import PREFIX


CASES = [
    ('named-row-promotion', 'named-reference-argument-captured-returned-row'),
    ('named-duplicate-before-promotion', 'named-reference-duplicate-check-after-get-before-promotion'),
    ('update-copy-and-embedded-alias', 'nested-updates-preserve-copy-and-shared-embedded-alias'),
]


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$gc_state_valid({state})']


def captured(task):
    return f'''
S.TODO = (KEY_WRITE_FINISH pkeywriter) :: ptask_tail*
pkeywriter.TASK = {task}
pkeywriter.BASE = BASE_PLACE pkeywriter.TARGET (ELEMENT n pkey)
pkey = KINT 0
S.ORIGIN = (pkeywriter.SITE)
S.LOCATION = ELEMENT n pkey
(HARRAY n) <- S.ALLOCATIONS
$(n < |S.ARRAYS|)
$($heap_owners($heap_prune($heap_graph(S)), HARRAY n) > 0)
$access_original_writer(S, pkeywriter) = (pkeywriter_original)
pkeywriter_original.BASE = pkeywriter.BASE
~$access_has_returned(pkeywriter.BASE)
$access_captured_consumer(pkeywriter.TASK)
$key_writer_valid(S, pkeywriter, ptask_tail*)
$outputs(S.EVENTS) = $ptascii("G;")
'''.strip().splitlines() + guards('S')


def forged(task):
    return f'''
pkeywriter_site = pkeywriter[.SITE = PORIGIN 0 eps]
S_site = S[.TODO = (KEY_WRITE_FINISH pkeywriter_site) :: ptask_tail*]
$heap_graph(S_site) = $heap_graph(S)
~$key_writer_valid(S_site, pkeywriter_site, ptask_tail*)
pkeywriter_task = pkeywriter[.TASK = {task}]
S_task = S[.TODO = (KEY_WRITE_FINISH pkeywriter_task) :: ptask_tail*]
~$key_writer_valid(S_task, pkeywriter_task, ptask_tail*)
pkeywriter_base = pkeywriter[.BASE = BASE_PLACE (PORIGIN 0 eps) (ELEMENT n pkey)]
~$key_writer_valid(S, pkeywriter_base, ptask_tail*)
$lookup(S.ENV, $ptascii("box")) = (n_box)
pkeywriter_root = pkeywriter[.BASE = BASE_PLACE pkeywriter.TARGET (ROOT n_box)]
~$key_writer_valid(S, pkeywriter_root, ptask_tail*)
pkeywriter_missing = pkeywriter[.BASE = BASE_PLACE pkeywriter.TARGET (ELEMENT n (KINT 19))]
~$key_writer_valid(S, pkeywriter_missing, ptask_tail*)
'''.strip().splitlines()


def named(duplicate):
    task = 'NAMED_SEND pcalltarget phpType7* n_arg pnamedargs porigin_call? z'
    stage = ('S.TODO = (KEY_WRITE_FINISH pkeywriter) :: ptask_tail* '
             '-- if pkeywriter.TASK = ' + task)
    checks = captured(task) + [
        '$entry_lookup(S.ARRAYS[n].ITEMS, pkey) = (DIRECT (PINT 7))',
        '$call_task_valid(S, pkeywriter.TASK)',
    ] + forged('NAMED_SEND pcalltarget phpType7* n_arg pnamedargs porigin_call? $(z + 1)')
    if duplicate:
        checks += '''
n_arg = 1
$named_slot_at(pnamedargs.SLOTS, 0) = NAMED_SENT (REFERENCE n_given)
S.STORE[n_given] = DEFINED (PINT 5)
z_error = $named_line(S, porigin_call?, n_arg)
PhpStep: S ~> S_sent
S_sent.COMPLETION = THROWN "Error" $ptascii("Named parameter $row overwrites previous argument") z_error
S_sent.STORE = S.STORE
S_sent.ARRAYS = S.ARRAYS
S_sent.REFCELLS = S.REFCELLS
S_sent.ALLOCATIONS = S.ALLOCATIONS
S_sent.GC = S.GC
S_sent.HELD = S.HELD
'''.strip().splitlines()
    else:
        checks += '''
n_arg = 0
PhpStep: S ~> S_sent
S_sent.COMPLETION = NORMAL
S_sent.TODO = (NAMED_ARGS pcalltarget phpType7* $(n_arg + 1) pnamedargs_sent porigin_call? z) :: ptask_tail*
S_sent.RESULT = KNOWN PNULL
$named_slot_at(pnamedargs_sent.SLOTS, 0) = NAMED_SENT (REFERENCE n_ref)
n_ref = |S.STORE|
S_sent.STORE[n_ref] = DEFINED (PINT 7)
n_ref <- S_sent.REFCELLS
S_sent.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_ref]
$entry_lookup(S_sent.ARRAYS[n].ITEMS, pkey) = (ALIAS n_ref)
S_sent.GC = S.GC
S_sent.HELD = S.HELD
'''.strip().splitlines()
    return stage, checks + guards('S_sent'), not duplicate


def update():
    task = 'UPDATE_PREP INCREMENT true z'
    stage = ('S.TODO = (KEY_WRITE_FINISH pkeywriter) :: ptask_tail* '
             '-- if pkeywriter.TASK = ' + task)
    checks = captured(task) + forged('UPDATE_PREP INCREMENT false z')
    checks += '''
$lookup(S.ENV, $ptascii("back18")) = (n_back)
S.STORE[n_back] = DEFINED (PARRAY n)
n_back <- S.REFCELLS
$lookup(S.ENV, $ptascii("alias18")) = (n_alias)
n_alias <- S.REFCELLS
S.STORE[n_alias] = DEFINED (PINT 7)
$entry_lookup(S.ARRAYS[n].ITEMS, pkey) = (ALIAS n_alias)
$lookup(S.ENV, $ptascii("copy18")) = (n_copy_cell)
S.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)
$entry_lookup(S.ARRAYS[n_copy].ITEMS, pkey) = (DIRECT (PINT 7))
$lookup(S.ENV, $ptascii("withAlias18")) = (n_with_cell)
S.STORE[n_with_cell] = DEFINED (PARRAY n_with)
$entry_lookup(S.ARRAYS[n_with].ITEMS, pkey) = (ALIAS n_alias)
n =/= n_copy
n =/= n_with
$($heap_owners($heap_prune($heap_graph(S)), HCELL n_alias) > 1)
PhpStep: S ~> S_post
S_post.COMPLETION = NORMAL
S_post.TODO = ptask_tail*
S_post.RESULT = KNOWN (PINT 7)
S_post.STORE[n_alias] = DEFINED (PINT 8)
S_post.ARRAYS = S.ARRAYS
S_post.REFCELLS = S.REFCELLS
S_post.ALLOCATIONS = S.ALLOCATIONS
S_post.GC = S.GC
S_post.HELD = S.HELD
'''.strip().splitlines()
    return stage, checks + guards('S_post'), True


def render(name, fixture, filename, expected):
    if name == 'named-row-promotion':
        stage, checks, one = named(False)
    elif name == 'named-duplicate-before-promotion':
        stage, checks, one = named(True)
    elif name == 'update-copy-and-embedded-alias':
        stage, checks, one = update()
    else:
        raise ValueError(name)
    checks = [f'S_initial = $php_run({fixture}, 0, {filename})',
              'S_initial.COMPLETION = BUDGET',
              'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
              r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
              'S = S_reached[.COMPLETION = NORMAL]'] + checks
    checks += ['S_zero = $drive_steps(S, 0)', 'S_zero = S[.COMPLETION = BUDGET]']
    if one:
        checks += ['S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET'] + guards('S_one')
        resumed = 'S_one'
    else:
        resumed = 'S_zero'
    checks += [f'S_done = $drive({resumed}[.COMPLETION = NORMAL], 1500)',
               'S_direct = $drive(S, 1500)', 'S_done = S_direct',
               'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               '$outputs(S_done.EVENTS) = $ptascii("' + expected + '")'] + guards('S_done')
    text = PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- ' + ('' if c.startswith('PhpStep: ') else 'if ') + c + '\n' for c in checks)
    return text, checks
