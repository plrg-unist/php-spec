"""Independent captured-factory receiver ownership and frozen selection checks."""
from error_handler_protocol import PREFIX


EXTRA = r'''
dec $bound_peer_stage(pstate, nat) : bool
def $bound_peer_stage(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
def $bound_peer_stage(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPENDED
  -- if pconfigcall.OWNER = (n_receiver)
  -- if $fiber_at(S, n_receiver) = (pfiber)
  -- if pfiber.STATUS = FIBER_INIT
def $bound_peer_stage(S, 2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPENDED
  -- if pconfigcall.OWNER = (n_receiver)
  -- if $fiber_at(S, n_receiver) = (pfiber)
  -- if pfiber.STATUS = FIBER_SUSPENDED
def $bound_peer_stage(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPENDED
  -- if pconfigcall.OWNER = (n_receiver)
  -- if $fiber_at(S, n_receiver) = (pfiber)
  -- if pfiber.STATUS = FIBER_TERMINATED
def $bound_peer_stage(S, n) = false -- otherwise
dec $bound_peer_seek(pstate, nat, nat) : pstate
def $bound_peer_seek(S, n_phase, n) = S
  -- if $bound_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bound_peer_seek(S, n_phase, n) = $bound_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$bound_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $bound_peer_seek(S, n_phase, 0) = S
  -- if ~$bound_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bound_peer_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $bound_peer_without(pnode*, pnode) : pnode*
def $bound_peer_without(eps, pnode) = eps
def $bound_peer_without(pnode :: pnode_tail*, pnode) = pnode_tail*
def $bound_peer_without(pnode_other :: pnode_tail*, pnode) = pnode_other :: $bound_peer_without(pnode_tail*, pnode)
  -- if pnode_other =/= pnode
'''


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$class_constant_history_valid({state})',
            f'$fiber_state_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(state, previous, phase):
    return [f'{state}_reached = $bound_peer_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$bound_peer_stage({state}, {phase})']


def render(program, filename, expected):
    checks = [f'S_begin = $php_run({program}, 0, {filename})',
              'S_begin.COMPLETION = BUDGET']
    checks += seek('S_factory', 'S_begin', 0)
    checks += [
        'S_factory.TODO = (CONFIG_INVOKE pconfigcall_factory) :: ptask_factory*',
        'pconfigcall_factory.KIND = INTRINSIC_FROM_CALLABLE_FACTORY',
        'pconfigcall_factory.OWNER = (n_factory)',
        'pconfigcall_factory.SELECTION = eps',
        'pconfigcall_factory.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]',
        'S_factory.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create',
        'porigin_create =/= pconfigcall_factory.SITE',
        '$from_factory_site(S_factory, porigin_create)',
        '$from_factory_call_site(S_factory, pconfigcall_factory.SITE)',
        '$node_children(S_factory, HOBJECT n_factory) = eps',
        '$task_nodes(CONFIG_INVOKE pconfigcall_factory) = [HOBJECT n_factory, HARRAY n_callback]',
        '$lookup(S_factory.ENV, $ptascii("method")) = (n_method_cell)',
        'S_factory.STORE[n_method_cell] = DEFINED pvalue_method',
        '$string_bytes(pvalue_method) = ($ptascii("isSuspended"))',
        'n_method_cell <- S_factory.REFCELLS',
        '$entry_lookup(S_factory.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)',
        'pentry* = $fiber_factory_items(S_factory, PARRAY n_callback)',
        '$entry_lookup(pentry*, KINT 0) = (DIRECT (POBJECT n_receiver))',
        '$entry_lookup(pentry*, KINT 1) = (DIRECT pvalue_method)',
        '$fiber_factory_selection(S_factory, PARRAY n_callback, pentry*) = '
        '((INTRINSIC_FIBER_SUSPENDED, ptbytes_method, (n_receiver)))',
        '$ptlc(ptbytes_method) = $ptascii("issuspended")',
        '$config_invoke_valid(S_factory, pconfigcall_factory)',
        '$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 1',
    ] + guards('S_factory') + [
        'n_capture = |S_factory.OBJECTS|',
        'S_minted_step = $drive_steps(S_factory, 1)',
        'S_minted_step.COMPLETION = BUDGET',
        'S_minted = S_minted_step[.COMPLETION = NORMAL]',
        'S_minted.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
        'pfibercapture.KIND = INTRINSIC_FIBER_SUSPENDED',
        'pfibercapture.INPUT = (n_receiver)',
        'pfibercapture.FACTORY = (pfiberfactory)',
        'pfibercapture.ARRAY = eps',
        'pfiberfactory.CALL = pconfigcall_factory', 'pfiberfactory.ITEMS = pentry*',
        '$node_children(S_minted, HOBJECT n_capture) = [HOBJECT n_receiver]',
        '$fiber_capture_live(S_minted, n_capture)',
    ] + guards('S_minted')
    previous = 'S_minted'
    for phase, label, status, value in [(1, 'initial', 'FIBER_INIT', 'false'),
                                      (2, 'suspended', 'FIBER_SUSPENDED', 'true'),
                                      (3, 'terminated', 'FIBER_TERMINATED', 'false')]:
        state = 'S_' + label
        checks += seek(state, previous, phase)
        checks += [
            f'{state}.TODO = (CONFIG_INVOKE pconfigcall_{label}) :: ptask_release_{label}*',
            f'ptask_release_{label}* = (FIBER_CAPTURE_RELEASE n_capture '
            f'pconfigcall_{label}.SITE) :: ptask_{label}*',
            f'pconfigcall_{label}.OWNER = (n_receiver)',
            f'pconfigcall_{label}.SELECTION = (n_capture)',
            f'pconfigcall_{label}.SENT = eps',
            f'{state}.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            f'{state}.STORE[n_method_cell] = DEFINED pvalue_changed',
            f'$string_bytes(pvalue_changed) = ($ptascii("isTerminated"))',
            'pfibercapture.NAME = $ptascii("isSuspended")',
            f'$fiber_at({state}, n_receiver) = (pfiber_{label})',
            f'pfiber_{label}.STATUS = {status}',
            f'$fiber_capture_source_valid({state}, pfibercapture)',
            f'$fiber_capture_live({state}, n_capture)',
            f'$from_factory_saved({state}, n_factory)',
            f'~$from_factory_live({state}, n_factory)',
            f'~$config_selected_valid({state}, pconfigcall_factory)',
            f'~((HARRAY n_callback) <- {state}.ALLOCATIONS)',
            f'$heap_owners($heap_graph({state}), HOBJECT n_factory) = 0',
            f'$heap_owners($heap_graph({state}), HARRAY n_callback) = 0',
            f'$heap_owners($heap_graph({state}), HOBJECT n_receiver) = 1',
            f'$node_children({state}, HOBJECT n_capture) = [HOBJECT n_receiver]',
            f'$config_nodes(pconfigcall_{label}) = eps',
            f'$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall_{label}.SITE) = [HOBJECT n_capture]',
            f'$config_invoke_valid({state}, pconfigcall_{label})',
            f'S_{label}_value = $config_receive({state}, pconfigcall_{label})',
            f'S_{label}_value.COMPLETION = NORMAL',
            f'S_{label}_value.RESULT = KNOWN (PBOOL {value})',
        ] + guards(state)
        previous = f'$drive_steps({state}, 1)'
    genuine_before_controls = len(checks)
    controls = [
        ('input', 'pfibercapture[.INPUT = eps]'),
        ('kind', 'pfibercapture[.KIND = INTRINSIC_FIBER_TERMINATED]'),
        ('name', 'pfibercapture[.NAME = $ptascii("isTerminated")]'),
        ('history_line', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = '
         'pconfigcall_factory[.LINE = $(pconfigcall_factory.LINE + 1)]])]'),
        ('history_owner', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = '
         'pconfigcall_factory[.OWNER = (n_receiver)]])]'),
    ]
    for label, capture in controls:
        checks += [f'pfibercapture_{label} = {capture}',
                   f'~$fiber_capture_source_valid(S_suspended, pfibercapture_{label})',
                   f'S_bad_{label} = S_suspended[.OBJECTS = '
                   f'$object_set(S_suspended.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_{label})]',
                   f'~$fiber_capture_live(S_bad_{label}, n_capture)',
                   f'~$call_descriptors_valid(S_bad_{label})']
        if label != 'input':
            checks += [f'$heap_graph(S_bad_{label}) = $heap_graph(S_suspended)']
    checks += [
        'n_substitute = |S_suspended.OBJECTS|',
        'S_other = S_suspended[.OBJECTS = S_suspended.OBJECTS ++ [FIBER $fiber_empty()]]'
        '[.ALLOCATIONS = S_suspended.ALLOCATIONS ++ [HOBJECT n_substitute]]',
        '$fiber_at(S_other, n_substitute) =/= eps',
        '$heap_valid($heap_graph(S_other))',
        '$fiber_factory_selection(S_other, PARRAY n_callback, pentry*) = '
        '((INTRINSIC_FIBER_SUSPENDED, ptbytes_method, (n_receiver)))',
        'pfibercapture_substitute = pfibercapture[.INPUT = (n_substitute)]',
        '~$fiber_capture_source_valid(S_other, pfibercapture_substitute)',
        'S_missing = S_suspended[.ALLOCATIONS = '
        '$bound_peer_without(S_suspended.ALLOCATIONS, HOBJECT n_receiver)]',
        '(HOBJECT n_capture) <- S_missing.ALLOCATIONS',
        '~((HOBJECT n_receiver) <- S_missing.ALLOCATIONS)',
        '$fiber_at(S_missing, n_receiver) = eps',
        '~$fiber_capture_source_valid(S_missing, pfibercapture)',
        '~$fiber_capture_live(S_missing, n_capture)',
        '$lookup(S_suspended.ENV, $ptascii("method")) = (n_method_cell)',
        'n_method_cell <- S_suspended.REFCELLS',
        'pentry_alias* = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
        'ENTRY (KINT 1) (ALIAS n_method_cell)]',
        '~$config_pack_items_valid(pentry_alias*)',
        'pfibercapture_alias = pfibercapture[.FACTORY = '
        '(pfiberfactory[.ITEMS = pentry_alias*])]',
        '~$fiber_capture_source_valid(S_suspended, pfibercapture_alias)',
        'S_alias = S_suspended[.OBJECTS = '
        '$object_set(S_suspended.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_alias)]',
        '$heap_graph(S_alias) = $heap_graph(S_suspended)',
        '~$fiber_capture_live(S_alias, n_capture)',
        '~$call_descriptors_valid(S_alias)',
    ]
    constructed = len(checks) - genuine_before_controls
    checks += [
        'S_zero = $drive_steps(S_suspended, 0)',
        'S_zero = S_suspended[.COMPLETION = BUDGET]',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 1000)',
        'S_done = $drive(S_suspended, 1000)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 0',
        '~$fiber_capture_live(S_done, n_capture)',
        '$from_factory_saved(S_done, n_factory)',
        '~$from_factory_live(S_done, n_factory)',
        '$fiber_factory_saved_call(S_done, pconfigcall_factory, INTRINSIC_FIBER_SUSPENDED, (n_receiver))',
        '~$fiber_capture_source_valid(S_done, pfibercapture)',
        f'$outputs(S_done.EVENTS) = $ptascii("{expected}")',
    ] + guards('S_done')
    text = EXTRA + PREFIX.replace('STAGE', '$bound_peer_stage(S, 0)')
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(checks) - constructed, constructed
