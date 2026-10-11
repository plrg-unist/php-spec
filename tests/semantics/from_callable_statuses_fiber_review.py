"""Remaining captured Fiber statuses at five authentic phases and final release."""
from error_handler_protocol import PREFIX
from from_callable_bound_fiber_review import guards


EXTRA = r'''
dec $statuses_peer_stage(pstate, pintrinsic, nat) : bool
def $statuses_peer_stage(S, pintrinsic, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
def $statuses_peer_stage(S, pintrinsic, n_phase) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = pintrinsic
  -- if pconfigcall.OWNER = (n_receiver)
  -- if $fiber_at(S, n_receiver) = (pfiber)
  -- if (n_phase = 1 /\ pfiber.STATUS = FIBER_INIT) \/
        ((n_phase = 2 \/ n_phase = 4) /\ pfiber.STATUS = FIBER_RUNNING) \/
        (n_phase = 3 /\ pfiber.STATUS = FIBER_SUSPENDED) \/
        (n_phase = 5 /\ pfiber.STATUS = FIBER_TERMINATED)
def $statuses_peer_stage(S, pintrinsic, 6) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("status")
  -- if S.RESULT = KNOWN PNULL
def $statuses_peer_stage(S, pintrinsic, 7) = true
  -- if S.ACTIVEFIBER = eps
  -- if $lookup(S.ENV, $ptascii("status")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED PNULL
  -- if S.RESULT = KNOWN PNULL
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.TODO =/= eps
def $statuses_peer_stage(S, pintrinsic, n) = false -- otherwise
dec $statuses_peer_seek(pstate, pintrinsic, nat, nat) : pstate
def $statuses_peer_seek(S, pintrinsic, n_phase, n) = S
  -- if $statuses_peer_stage(S, pintrinsic, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $statuses_peer_seek(S, pintrinsic, n_phase, n) = $statuses_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pintrinsic, n_phase, $nabs($(n - 1)))
  -- if ~$statuses_peer_stage(S, pintrinsic, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $statuses_peer_seek(S, pintrinsic, n_phase, 0) = S
  -- if ~$statuses_peer_stage(S, pintrinsic, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $statuses_peer_seek(S, pintrinsic, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $statuses_marker_done(pstate, ptask*) : bool
def $statuses_marker_done(S, ptask*) = true
  -- if S.TODO = ptask*
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
def $statuses_marker_done(S, ptask*) = false -- otherwise
dec $statuses_marker_seek(pstate, ptask*, nat) : pstate
def $statuses_marker_seek(S, ptask*, n) = S
  -- if $statuses_marker_done(S, ptask*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $statuses_marker_seek(S, ptask*, n) = $statuses_marker_seek($drive_steps(S[.COMPLETION = NORMAL], 1), ptask*, $nabs($(n - 1)))
  -- if ~$statuses_marker_done(S, ptask*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $statuses_marker_seek(S, ptask*, 0) = S
  -- if ~$statuses_marker_done(S, ptask*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $statuses_marker_seek(S, ptask*, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''

METHODS = {
    'isStarted': ('INTRINSIC_FIBER_STARTED', 'isTerminated', ('false', 'true', 'true', 'true', 'true')),
    'isRunning': ('INTRINSIC_FIBER_RUNNING', 'isStarted', ('false', 'true', 'false', 'true', 'false')),
    'isTerminated': ('INTRINSIC_FIBER_TERMINATED', 'isStarted', ('false', 'false', 'false', 'false', 'true')),
}


def seek(state, previous, intrinsic, phase):
    return [f'{state}_reached = $statuses_peer_seek({previous}, {intrinsic}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$statuses_peer_stage({state}, {intrinsic}, {phase})']


def render(program, filename, expected, method, entry='main', shared=True):
    intrinsic, changed, values = METHODS[method]
    shared_release = method == 'isStarted'
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_factory', 'S_begin', intrinsic, 0)
    genuine += [
        'S_factory.TODO = (CONFIG_INVOKE pconfigcall_factory) :: ptask_factory*',
        'pconfigcall_factory.OWNER = (n_factory)', 'pconfigcall_factory.SELECTION = eps',
        'pconfigcall_factory.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]',
        'S_factory.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create',
        '$from_factory_site(S_factory, porigin_create)',
        '$from_factory_call_site(S_factory, pconfigcall_factory.SITE)',
        '$config_invoke_valid(S_factory, pconfigcall_factory)',
        '$lookup(S_factory.ENV, $ptascii("method")) = (n_method)',
        'S_factory.STORE[n_method] = DEFINED pvalue_method',
        f'$string_bytes(pvalue_method) = ($ptascii("{method}"))',
        '~(n_method <- S_factory.REFCELLS)',
        'pentry* = $fiber_factory_items(S_factory, PARRAY n_callback)',
        '$entry_lookup(pentry*, KINT 0) = (DIRECT (POBJECT n_receiver))',
        '$entry_lookup(pentry*, KINT 1) = (DIRECT pvalue_method)',
        f'$fiber_factory_selection(S_factory, PARRAY n_callback, pentry*) = (({intrinsic}, ptbytes_method, (n_receiver)))',
        '$fiber_factory_statuses(S_factory, pconfigcall_factory, PARRAY n_callback)',
        '~$fiber_factory_suspended(S_factory, pconfigcall_factory, PARRAY n_callback)',
        '$fiber_at(S_factory, n_receiver) = (pfiber_factory)',
        'pfiber_factory.STATUS = FIBER_INIT',
        'pfiber_factory.RAW = POBJECT n_body',
        '$node_children(S_factory, HOBJECT n_body) = eps',
        '$node_children(S_factory, HOBJECT n_factory) = eps',
        '$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 1',
    ] + guards('S_factory') + [
        'n_capture = |S_factory.OBJECTS|',
        'S_minted_step = $drive_steps(S_factory, 1)', 'S_minted_step.COMPLETION = BUDGET',
        'S_minted = S_minted_step[.COMPLETION = NORMAL]',
        'S_minted.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
        f'pfibercapture.KIND = {intrinsic}', f'pfibercapture.NAME = $ptascii("{method}")',
        'pfibercapture.INPUT = (n_receiver)', 'pfibercapture.ARRAY = eps',
        'pfibercapture.FACTORY = (pfiberfactory)',
        'pfiberfactory.CALL = pconfigcall_factory', 'pfiberfactory.ITEMS = pentry*',
        '$node_children(S_minted, HOBJECT n_capture) = [HOBJECT n_receiver]',
        '$fiber_capture_live(S_minted, n_capture)',
    ] + guards('S_minted')
    previous = 'S_minted'
    phases = [(1, 'initial', 'FIBER_INIT', 'I:'),
              (2, 'running_before', 'FIBER_RUNNING', 'B:'),
              (3, 'suspended', 'FIBER_SUSPENDED', 'S:'),
              (4, 'running_after', 'FIBER_RUNNING', 'R:'),
              (5, 'terminated', 'FIBER_TERMINATED', 'T:')]
    for (phase, label, status, marker), value in zip(phases, values):
        state = 'S_' + label
        result = state + '_result'
        config = 'pconfigcall_' + label
        tail = 'ptask_' + label + '*'
        prefix = expected.split(marker)[0] + marker
        genuine += seek(state, previous, intrinsic, phase) + [
            f'{state}.TODO = (CONFIG_INVOKE {config}) :: ptask_release_{label}*',
            f'ptask_release_{label}* = (FIBER_CAPTURE_RELEASE n_capture {config}.SITE) :: {tail}',
            f'{config}.KIND = {intrinsic}', f'{config}.OWNER = (n_receiver)',
            f'{config}.SELECTION = (n_capture)', f'{config}.SENT = eps',
            f'{state}.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            f'$fiber_at({state}, n_receiver) = (pfiber_{label})',
            f'pfiber_{label}.STATUS = {status}',
            f'{state}.STORE[n_method] = DEFINED pvalue_changed',
            f'$string_bytes(pvalue_changed) = ($ptascii("{changed}"))',
            f'psymboltable_{label} = $fiber_globals({state})',
            f'$lookup(psymboltable_{label}.ENV, $ptascii("status")) = (n_status)',
            f'{state}.STORE[n_status] = DEFINED (POBJECT n_capture)',
            f'$node_children({state}, HCELL n_status) = [HOBJECT n_capture]',
            f'$heap_owners($heap_graph({state}), HOBJECT n_capture) = 2',
            f'$heap_owners($heap_graph({state}), HOBJECT n_receiver) = {3 if status == "FIBER_RUNNING" else 1}',
            f'$node_children({state}, HOBJECT n_capture) = [HOBJECT n_receiver]',
            f'~((HOBJECT n_factory) <- {state}.ALLOCATIONS)',
            f'~((HARRAY n_callback) <- {state}.ALLOCATIONS)',
            f'$from_factory_saved({state}, n_factory)', f'~$from_factory_live({state}, n_factory)',
            f'$config_nodes({config}) = eps',
            f'$config_invoke_valid({state}, {config})',
            f'{state}.DESTRUCTION.OPERATIONS = eps', f'{state}.DESTRUCTION.RELEASES = eps',
            f'$outputs({state}.EVENTS) = $ptascii("{prefix}")',
        ]
        if status == 'FIBER_RUNNING':
            genuine += [f'{state}.ACTIVEFIBER = (n_receiver)',
                        f'{state}.FIBERCALLERS = [pfibercaller_{label}]',
                        f'pfibercaller_{label}.OBJECT = n_receiver',
                        f'pfibercaller_{label}.PREVIOUS = eps',
                        f'pfibercaller_{label}.VM.GLOBAL',
                        f'pfibercaller_{label}.VM.TABLE = $empty_table()',
                        f'pfibercaller_{label}.API.OBJECT = n_receiver',
                        f'$fiber_caller_api_nodes(pfibercaller_{label}) = [HOBJECT n_receiver]',
                        f'$lookup({state}.ENV, $ptascii("status")) = (n_status)',
                        f'$lookup(psymboltable_{label}.ENV, $ptascii("active")) = (n_active)',
                        f'{state}.STORE[n_active] = DEFINED (POBJECT n_receiver)']
        else:
            genuine += [f'{state}.ACTIVEFIBER = eps', f'{state}.FIBERCALLERS = eps']
        genuine += guards(state) + [
            f'{result}_step = $drive_steps({state}, 1)', f'{result}_step.COMPLETION = BUDGET',
            f'{result} = {result}_step[.COMPLETION = NORMAL]',
            f'{result}.TODO = (FIBER_CAPTURE_RESULT n_capture {config} false) :: {tail}',
            f'{result}.RESULT = KNOWN (PBOOL {value})',
            f'$fiber_capture_result_valid({result}, n_capture, {config}, false)',
            f'{result}.ACTIVEFIBER = {state}.ACTIVEFIBER',
            f'{result}.FIBERCALLERS = {state}.FIBERCALLERS',
            f'{result}.GLOBALTABLE = {state}.GLOBALTABLE',
            f'{result}.CURRENT = {state}.CURRENT', f'{result}.FRAMES = {state}.FRAMES',
            f'{result}.ARRAYS = {state}.ARRAYS', f'{result}.OBJECTS = {state}.OBJECTS',
            f'{result}.EVENTS = {state}.EVENTS',
            f'$heap_owners($heap_graph({result}), HOBJECT n_capture) = 2',
        ] + (guards(result) if shared_release else [
            f'$heap_graph({result}) = $heap_graph({state})'])
        previous = result
    genuine += ['pconfigcall_running_before.SITE =/= pconfigcall_running_after.SITE']
    controls = []
    if shared_release:
        genuine += [
            'S_marker_step = $drive_steps(S_suspended_result, 1)', 'S_marker_step.COMPLETION = BUDGET',
            'S_marker = S_marker_step[.COMPLETION = NORMAL]',
            'S_marker.DESTRUCTION.OPERATIONS = pdestructionoperation_marker :: pdestructionoperation_marker_tail*',
            'pdestructionoperation_marker_tail* = eps',
            'pdestructionoperation_marker.SOURCE = FIBER_CAPTURE_RESULT n_capture pconfigcall_suspended false',
            f'pdestructionoperation_marker.VALUE = KNOWN (PBOOL {values[2]})',
            'pdestructionoperation_marker.PENDING = eps',
            '$destructor_operation_live(S_marker, pdestructionoperation_marker)',
            '$heap_owners($heap_graph(S_marker), HOBJECT n_capture) = 2',
            'S_marker_done_reached = $statuses_marker_seek(S_marker, ptask_suspended*, 1000)',
            r'S_marker_done_reached.COMPLETION = NORMAL \/ S_marker_done_reached.COMPLETION = BUDGET',
            'S_marker_done = S_marker_done_reached[.COMPLETION = NORMAL]',
            '$statuses_marker_done(S_marker_done, ptask_suspended*)',
            f'S_marker_done.RESULT = KNOWN (PBOOL {values[2]})',
            '$heap_owners($heap_graph(S_marker_done), HOBJECT n_capture) = 1',
            '$heap_owners($heap_graph(S_marker_done), HOBJECT n_receiver) = 1',
            'S_marker_done.EVENTS = S_suspended.EVENTS',
        ] + guards('S_marker') + guards('S_marker_done')
        genuine += seek('S_clear_before', 'S_terminated_result', intrinsic, 6) + [
            'S_clear_before.TODO = (WRITE_NAME $ptascii("status") z_clear) :: ptask_clear_tail*',
            'S_clear_before.STORE[n_status] = DEFINED (POBJECT n_capture)',
            'S_clear_before.RESULT = KNOWN PNULL',
            '$heap_owners($heap_graph(S_clear_before), HOBJECT n_capture) = 1',
            '$heap_owners($heap_graph(S_clear_before), HOBJECT n_receiver) = 1',
            'S_clear_before.STORE[n_active] = DEFINED PNULL',
            '~((HOBJECT n_body) <- S_clear_before.ALLOCATIONS)',
            '$lookup(S_clear_before.ENV, $ptascii("weakStatus")) = (n_weak_capture_cell)',
            'S_clear_before.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)',
            '$lookup(S_clear_before.ENV, $ptascii("weak")) = (n_weak_receiver_cell)',
            'S_clear_before.STORE[n_weak_receiver_cell] = DEFINED (POBJECT n_weak_receiver)',
            '$weakref_get(S_clear_before, n_weak_capture) = POBJECT n_capture',
            '$weakref_get(S_clear_before, n_weak_receiver) = POBJECT n_receiver',
            f'$outputs(S_clear_before.EVENTS) = $ptascii("{expected.split("C:")[0]}")',
            'S_clear_step = $drive_steps(S_clear_before, 1)', 'S_clear_step.COMPLETION = BUDGET',
            'S_clear = S_clear_step[.COMPLETION = NORMAL]',
            'S_clear.STORE[n_status] = DEFINED PNULL',
            'S_clear.DESTRUCTION.OPERATIONS = pdestructionoperation_clear :: pdestructionoperation_clear_tail*',
            'pdestructionoperation_clear_tail* = eps',
            'pdestructionoperation_clear.SOURCE = $eager_operation_source(S_clear_before, WRITE_NAME $ptascii("status") z_clear)',
            'pdestructionoperation_clear.VALUE = KNOWN PNULL', 'pdestructionoperation_clear.PENDING = eps',
            '$destructor_operation_live(S_clear, pdestructionoperation_clear)',
        ] + guards('S_clear_before') + guards('S_clear')
        genuine += seek('S_pruned', 'S_clear', intrinsic, 7) + [
            'S_pruned.STORE[n_status] = DEFINED PNULL',
            '~((HOBJECT n_capture) <- S_pruned.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_pruned.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_pruned), HOBJECT n_capture) = 0',
            '$heap_owners($heap_graph(S_pruned), HOBJECT n_receiver) = 0',
            '$weakref_get(S_pruned, n_weak_capture) = PNULL', '$weakref_get(S_pruned, n_weak_receiver) = PNULL',
            'S_pruned.EVENTS = S_clear_before.EVENTS',
        ] + guards('S_pruned')
        for label, capture in [
            ('input', 'pfibercapture[.INPUT = eps]'),
            ('kind', 'pfibercapture[.KIND = INTRINSIC_FIBER_SUSPENDED]'),
            ('family_kind', f'pfibercapture[.KIND = {METHODS[changed][0]}]'),
            ('family_running_kind', 'pfibercapture[.KIND = INTRINSIC_FIBER_RUNNING]'),
            ('name', f'pfibercapture[.NAME = $ptascii("{changed}")]'),
            ('history_line', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.LINE = $(pconfigcall_factory.LINE + 1)]])]'),
            ('history_owner', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.OWNER = (n_receiver)]])]'),
            ('history_site', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.SITE = PORIGIN 999 eps]])]'),
        ]:
            controls += [f'pfibercapture_{label} = {capture}',
                         f'~$fiber_capture_source_valid(S_suspended, pfibercapture_{label})',
                         f'S_bad_{label} = S_suspended[.OBJECTS = $object_set(S_suspended.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_{label})]',
                         f'~$fiber_capture_live(S_bad_{label}, n_capture)',
                         f'~$call_descriptors_valid(S_bad_{label})']
            if label != 'input':
                controls += [f'$heap_graph(S_bad_{label}) = $heap_graph(S_suspended)']
        controls += [
            'pentry_static* = [ENTRY (KINT 0) (DIRECT (PSTRING $ptascii("Fiber"))), ENTRY (KINT 1) (DIRECT pvalue_method)]',
            '$fiber_factory_selection(S_factory, PARRAY n_callback, pentry_static*) = eps',
            'pentry_alias* = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (ALIAS n_method)]',
            '~$config_pack_items_valid(pentry_alias*)',
            'pfibercapture_alias = pfibercapture[.FACTORY = (pfiberfactory[.ITEMS = pentry_alias*])]',
            '~$fiber_capture_source_valid(S_suspended, pfibercapture_alias)',
            '~$fiber_capture_result_valid(S_suspended_result, n_capture, pconfigcall_suspended, true)',
            '~$fiber_capture_result_valid(S_suspended_result, n_capture, pconfigcall_suspended[.SITE = PORIGIN 999 eps], false)',
            f'~$fiber_factory_saved_call(S_suspended, pconfigcall_factory, {intrinsic}, eps)',
            '~$fiber_factory_saved_call(S_suspended, pconfigcall_factory, INTRINSIC_FIBER_RETURN, eps)',
        ]
    genuine += [
        'S_zero = $drive_steps(S_suspended, 0)', 'S_zero = S_suspended[.COMPLETION = BUDGET]',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 1000)',
        'S_done = $drive(S_suspended, 1000)',
        *(['S_done = $drive(S_pruned, 1000)'] if shared_release else []),
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.ACTIVEFIBER = eps', 'S_done.FIBERCALLERS = eps', 'S_done.FIBERCLOSERS = eps',
        '$from_factory_saved(S_done, n_factory)', '~$from_factory_live(S_done, n_factory)',
        f'$fiber_factory_saved_call(S_done, pconfigcall_factory, {intrinsic}, (n_receiver))',
        '~$fiber_capture_source_valid(S_done, pfibercapture)',
        f'$outputs(S_done.EVENTS) = $ptascii("{expected}")',
    ] + guards('S_done')
    checks = genuine + controls
    text = EXTRA + PREFIX[PREFIX.index('dec $outputs'):] if shared else ''
    text += f'\ndec ${entry}() : bool\ndef ${entry}() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
