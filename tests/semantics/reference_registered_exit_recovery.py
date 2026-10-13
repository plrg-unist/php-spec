"""Derive one parked Fiber operation-exit integrity check from a reached case."""
import base64
import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARCHIVE = Path('/home/user/workspace/php-spec/.tools/calls-fiber-current-14/.tools/fiber-state-review-9zgmnvth/cached-callback-parks-real-handler-operation-and-cleanup')
SOURCE_SHA = '2906d3d4679332e406c046e607dff6ccf443eef216d063284458348eca274508'
FIXTURE_SHA = '0bf9f16a6537137f02ecaf1af0cc26199a126738321e0e60b4b31c10d4a30b46'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(ARCHIVE / 'source.php') == SOURCE_SHA
assert sha(ARCHIVE / 'test.watsup') == FIXTURE_SHA
source = HERE / 'parked-exit-source.php'
source.write_bytes((ARCHIVE / 'source.php').read_bytes())
archived = (ARCHIVE / 'test.watsup').read_text()
prefix, main = archived.split('dec $main() : bool\n', 1)
initial = next(line for line in main.splitlines() if line.startswith('  -- if S_initial = '))
old_path = '"' + base64.b64encode(str(ARCHIVE / 'source.php').encode()).decode() + '"'
new_path = '"' + base64.b64encode(str(source).encode()).decode() + '"'
assert initial.count(old_path) == 1
initial = initial.replace(old_path, new_path)
helpers = r'''
dec $parked_drop_exit_tasks(ptask*, pdestructionoperation) : ptask*
def $parked_drop_exit_tasks(eps, pdestructionoperation) = eps
def $parked_drop_exit_tasks((DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*, pdestructionoperation) = $parked_drop_exit_tasks(ptask_tail*, pdestructionoperation)
def $parked_drop_exit_tasks(ptask :: ptask_tail*, pdestructionoperation) = ptask :: $parked_drop_exit_tasks(ptask_tail*, pdestructionoperation)
  -- if ptask =/= DESTRUCTOR_OPERATION_EXIT pdestructionoperation
dec $parked_drop_exit_frames(pframe*, pdestructionoperation) : pframe*
def $parked_drop_exit_frames(eps, pdestructionoperation) = eps
def $parked_drop_exit_frames(pframe :: pframe_tail*, pdestructionoperation) = pframe[.TODO = $parked_drop_exit_tasks(pframe.TODO, pdestructionoperation)] :: $parked_drop_exit_frames(pframe_tail*, pdestructionoperation)
'''
checks = r'''
  -- if S_reached = $seek(S_initial[.COMPLETION = NORMAL], 4000)
  -- if S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET
  -- if S = S_reached[.COMPLETION = NORMAL]
  -- if $stage(S)
  -- if S.FIBERCLOSERS = [pfiberclose]
  -- if pfiberclose.VM.DESTRUCTOROPERATIONS = [pdestructionoperation]
  -- if pfiberclose.VM.DESTRUCTORCLEANUPS = [pdestructioncleanup]
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if S_view = $fiber_vm_restore(S, pfiberclose.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]
  -- if $destructor_operation_exits_valid(S_view, [pdestructionoperation])
  -- if $fiber_vm_valid(S, pfiberclose.VM, eps, eps)
  -- if $call_descriptors_valid(S)
  -- if $heap_valid($heap_graph(S))
  -- if pfibervm_bad = pfiberclose.VM[.TODO = $parked_drop_exit_tasks(pfiberclose.VM.TODO, pdestructionoperation)][.FRAMES = $parked_drop_exit_frames(pfiberclose.VM.FRAMES, pdestructionoperation)]
  -- if pfibervm_bad.DESTRUCTOROPERATIONS = [pdestructionoperation]
  -- if pfibervm_bad.DESTRUCTORCLEANUPS = [pdestructioncleanup]
  -- if S_view_bad = $fiber_vm_restore(S, pfibervm_bad)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]
  -- if ~$destructor_operation_exits_valid(S_view_bad, [pdestructionoperation])
  -- if S_bad = S[.FIBERCLOSERS = [pfiberclose[.VM = pfibervm_bad]]]
  -- if $heap_valid($heap_graph(S_bad))
  -- if ~$fiber_vm_valid(S, pfibervm_bad, eps, eps)
  -- if ~$call_descriptors_valid(S_bad)
'''
fixture = prefix + helpers + '\ndec $main() : bool\ndef $main() = true\n' + initial + '\n' + checks.lstrip('\n')
path = HERE / 'parked-exit-public.watsup'
path.write_text(fixture)
print(path, sha(path), len(checks.splitlines()))
