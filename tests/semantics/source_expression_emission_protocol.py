#!/usr/bin/env python3
"""Source compiler certificates select nonconstant ECHO's first emitted work."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

import error_handler_run as recorder
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source-stringable-retirement')
GUARD_FILES = {'cv': 'cv-child.php', 'property': 'property-child.php',
               'call_property': 'call-property-child.php', 'autoglobal': 'emission-autoglobal.php',
               'this': 'emission-this.php', 'dynamic': 'emission-dynamic.php',
               'builtin': 'emission-builtin.php', 'argument': 'emission-argument.php'}
ENTRY_HELPERS = 'dec $emission_review_drop_expr(pcodeexpr*, pcpath) : pcodeexpr*\ndef $emission_review_drop_expr(eps, pcpath) = eps\ndef $emission_review_drop_expr((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath) = $emission_review_drop_expr(pcodeexpr*, pcpath)\ndec $emission_review_expr_at(pcodeexpr, pcpath) : bool\ndef $emission_review_expr_at(CODEEXPR pcpath z b, pcpath) = true\ndef $emission_review_expr_at(pcodeexpr, pcpath) = false -- otherwise\ndef $emission_review_drop_expr(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $emission_review_drop_expr(pcodeexpr_tail*, pcpath)\n  -- if ~$emission_review_expr_at(pcodeexpr, pcpath)\ndec $emission_review_drop_name(pcodename*, pcpath) : pcodename*\ndef $emission_review_drop_name(eps, pcpath) = eps\ndef $emission_review_drop_name((CODENAME pcpath preqbytes preqbytes_fallback?) :: pcodename*, pcpath) = $emission_review_drop_name(pcodename*, pcpath)\ndef $emission_review_drop_name((CODENAME pcpath_other preqbytes preqbytes_fallback?) :: pcodename_tail*, pcpath) = (CODENAME pcpath_other preqbytes preqbytes_fallback?) :: $emission_review_drop_name(pcodename_tail*, pcpath)\n  -- if pcpath_other =/= pcpath\ndec $emission_review_replace_code(pcode*, pcode) : pcode*\ndef $emission_review_replace_code(eps, pcode) = [pcode]\ndef $emission_review_replace_code(pcode_old :: pcode_tail*, pcode) = pcode :: pcode_tail* -- if pcode_old.UNIT = pcode.UNIT\ndef $emission_review_replace_code(pcode_old :: pcode_tail*, pcode) = pcode_old :: $emission_review_replace_code(pcode_tail*, pcode) -- if pcode_old.UNIT =/= pcode.UNIT\n'
ENTRY_PREMISES = ['  -- if regenerated_source_binding',
 '  -- if S_open.COMPLETION = SOURCE_PENDING',
 '  -- if S_open.FILECONTEXTS = pfilecontext_open :: eps',
 '  -- if pfilecontext_open.PHASE = FILE_RESOLVE_WAIT',
 '  -- if regenerated_source_binding',
 '  -- if S_parse.COMPLETION = SOURCE_PENDING',
 '  -- if S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
 '  -- if pfilecontext_parse.UNIT = (n_unit)',
 '  -- if regenerated_source_binding',
 '  -- if S.COMPLETION = NORMAL',
 '  -- if S.TODO = (SOURCE_OPERAND_ENTER psourceoperand n_unit) :: ptask_body*',
 '  -- if $source_unit(S.SOURCES, n_unit) = (pcunit)',
 '  -- if P = $declaration_compiler_state($eval_source_ppstate(S, pcunit))',
 '  -- if P.WORK = (PPCWORK pcpath_fn statement_fn plenv_fn n_fn) :: (PPCWORK pcpath_echo '
 'statement_echo plenv_echo n_echo) :: ppwork_tail*',
 '  -- if statement_echo = (NStmtEcho (SEQUENCE ([expression_property])) metadata_echo)',
 '  -- if expression_property = (NExprPropertyFetch (NExprFuncCall name_call (SEQUENCE eps) '
 'metadata_call) (NIdentifier (BYTES text_property) metadata_property) metadata_fetch)',
 '  -- if pcpath_property = pcpath_echo ++ [PCFIELD 0, PCINDEX 0]',
 '  -- if pcpath_call = pcpath_property ++ [PCFIELD 0]',
 '  -- if porigin_call = PORIGIN n_unit pcpath_call',
 '  -- if $code_at(S.CODE, n_unit) = (pcode)',
 '  -- if S_no_call = S[.CODE = $emission_review_replace_code(S.CODE, pcode[.EXPRESSIONS = '
 '$emission_review_drop_expr(pcode.EXPRESSIONS, pcpath_call)])]',
 '  -- if S_no_name = S[.CODE = $emission_review_replace_code(S.CODE, pcode[.NAMES = '
 '$emission_review_drop_name(pcode.NAMES, pcpath_call)])]',
 '  -- if S_bad_name = S[.CODE = $emission_review_replace_code(S.CODE, pcode[.NAMES = [CODENAME '
 'pcpath_call ($ptascii("forged_emission_314")) eps] ++ $emission_review_drop_name(pcode.NAMES, '
 'pcpath_call)])]',
 '  -- if S_bad_line = S[.CODE = $emission_review_replace_code(S.CODE, pcode[.EXPRESSIONS = '
 '[CODEEXPR pcpath_call 6 false] ++ $emission_review_drop_expr(pcode.EXPRESSIONS, pcpath_call)])]',
 '  -- if $source_operand_enter_valid(S, psourceoperand, n_unit)',
 '  -- if $call_entry_check(S) = S',
 '  -- if $heap_valid($heap_graph(S))',
 '  -- if P.COMPLETION = PPCNORMAL /\\ $compilation_image_valid(S, pcunit, P)',
 '  -- if (PDEXIT n_unit PCSCOMPLETE) <- S.DECLARATIONS',
 '  -- if $source_fast_statement(S, n_unit, pcpath_fn, statement_fn)',
 '  -- if $compiled_read(S, PORIGIN n_unit pcpath_property) = eps',
 '  -- if $code_expression(pcode.EXPRESSIONS, pcpath_call) = ((5, false))',
 '  -- if $code_expression(pcode.EXPRESSIONS, pcpath_property) = ((6, false))',
 '  -- if $code_name(pcode.NAMES, pcpath_call) = (($ptascii("emission_object_314"), eps))',
 '  -- if $source_echo_emission_origin(S, n_unit, pcpath_property, expression_property) = '
 '(porigin_call)',
 '  -- if $source_first_work_origin(S, n_unit, P.WORK) = (porigin_call)',
 '  -- if $source_operand_entry_origin(S, psourceoperand, n_unit) = (porigin_call)',
 '  -- if $property_current_line(S[.ORIGIN = (porigin_call)]) = 5',
 '  -- if $property_current_line(S[.ORIGIN = (PORIGIN n_unit pcpath_property)]) = 6',
 '  -- if S.ORIGIN =/= (porigin_call)',
 '  -- if $source_echo_emission_origin(S_no_call, n_unit, pcpath_property, expression_property) = '
 'eps',
 '  -- if $source_echo_emission_origin(S_no_name, n_unit, pcpath_property, expression_property) = '
 'eps',
 '  -- if $source_echo_emission_origin(S_bad_name, n_unit, pcpath_property, expression_property) = '
 '(porigin_call)',
 '  -- if $source_echo_emission_origin(S_bad_line, n_unit, pcpath_property, expression_property) = '
 'eps',
 '  -- if $heap_graph(S_no_call) = $heap_graph(S)',
 '  -- if $source_operand_entry_origin(S_no_call, psourceoperand, n_unit) = S_no_call.ORIGIN',
 '  -- if $call_entry_check(S_no_call).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"',
 '  -- if $heap_graph(S_no_name) = $heap_graph(S)',
 '  -- if $source_operand_entry_origin(S_no_name, psourceoperand, n_unit) = S_no_name.ORIGIN',
 '  -- if $call_entry_check(S_no_name).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"',
 '  -- if $heap_graph(S_bad_name) = $heap_graph(S)',
 '  -- if $source_operand_entry_origin(S_bad_name, psourceoperand, n_unit) = S_bad_name.ORIGIN',
 '  -- if $call_entry_check(S_bad_name).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"',
 '  -- if $heap_graph(S_bad_line) = $heap_graph(S)',
 '  -- if $source_operand_entry_origin(S_bad_line, psourceoperand, n_unit) = S_bad_line.ORIGIN',
 '  -- if $call_entry_check(S_bad_line).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"',
 '  -- if ~$compilation_image_valid(S_bad_name, pcunit, P)']


GENERATOR_HELPERS = 'dec $expression_comp_review_reached(pstate) : bool\ndef $expression_comp_review_reached(S) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)\n  -- if pdestructorcall.OPERATION = (pdestructionoperation)\n  -- if pdestructionoperation.SOURCE = SOURCE_OPERAND_ENTER psourceoperand n\ndef $expression_comp_review_reached(S) = false -- otherwise\ndec $expression_comp_review_seek(pstate, nat) : pstate\ndef $expression_comp_review_seek(S, n) = S -- if $expression_comp_review_reached(S)\ndef $expression_comp_review_seek(S, n) = S\n  -- if ~$expression_comp_review_reached(S)\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $expression_comp_review_seek(S, 0) = S -- if ~$expression_comp_review_reached(S)\ndef $expression_comp_review_seek(S, n) = $expression_comp_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))\n  -- if ~$expression_comp_review_reached(S)\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $(n > 0)\n' + ENTRY_HELPERS
GENERATOR_PREMISES = ['  -- if regenerated_source_binding',
 '  -- if S_open.COMPLETION = SOURCE_PENDING',
 '  -- if S_open.FILECONTEXTS = pfilecontext_open :: eps',
 '  -- if pfilecontext_open.PHASE = FILE_RESOLVE_WAIT',
 '  -- if regenerated_source_binding',
 '  -- if S_parse.COMPLETION = SOURCE_PENDING',
 '  -- if S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
 '  -- if pfilecontext_parse.UNIT = (n_unit)',
 '  -- if regenerated_source_binding',
 '  -- if S_entry.COMPLETION = NORMAL',
 '  -- if S_entry.TODO = (SOURCE_OPERAND_ENTER psourceoperand n_unit) :: ptask_body*',
 '  -- if S_entry.CURRENT = (pcallcontext_entry)',
 '  -- if $generator_context_operation(S_entry, pcallcontext_entry) = (pgeneratorop_entry)',
 '  -- if $operand_nodes(psourceoperand.INPUT) = [HOBJECT n_operand]',
 '  -- if $source_operand_entry_origin(S_entry, psourceoperand, n_unit) = (porigin_work)',
 '  -- if S_reached = $expression_comp_review_seek(S_entry, 400)',
 '  -- if S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET',
 '  -- if S = S_reached[.COMPLETION = NORMAL]',
 '  -- if S.CURRENT = (pcallcontext)',
 '  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)',
 '  -- if pdestructorcall.OPERATION = (pdestructionoperation)',
 '  -- if pdestructionoperation.SOURCE = SOURCE_OPERAND_ENTER psourceoperand n_unit',
 '  -- if S_owner = $source_string_owner_scope(S, psourceoperand.OWNER)',
 '  -- if S_bad_owner = S_entry[.FILECONTEXTS = [S_entry.FILECONTEXTS[0][.OWNER = '
 '$(psourceoperand.OWNER + 1)]]]',
 '  -- if S_bad_tail = S_entry[.TODO = [SOURCE_OPERAND_ENTER psourceoperand n_unit]]',
 '  -- if $source_unit(S_entry.SOURCES, n_unit) = (pcunit)',
 '  -- if P = $declaration_compiler_state($eval_source_ppstate(S_entry, pcunit))',
 '  -- if $origin_node(S_entry.SOURCES, porigin_work) = (expression_property)',
 '  -- if porigin_work = PORIGIN n_unit pcpath_property',
 '  -- if expression_property = (NExprPropertyFetch (NExprVariable (BYTES text_receiver) '
 'metadata_receiver) (NIdentifier (BYTES text_property) metadata_property) metadata_fetch)',
 '  -- if pcpath_receiver = pcpath_property ++ [PCFIELD 0]',
 '  -- if porigin_receiver = PORIGIN n_unit pcpath_receiver',
 '  -- if $code_at(S_entry.CODE, n_unit) = (pcode)',
 '  -- if S_no_receiver = S_entry[.CODE = $emission_review_replace_code(S_entry.CODE, '
 'pcode[.EXPRESSIONS = $emission_review_drop_expr(pcode.EXPRESSIONS, pcpath_receiver)])]',
 '  -- if S_bad_line = S_entry[.CODE = $emission_review_replace_code(S_entry.CODE, pcode[.EXPRESSIONS = '
 '[CODEEXPR pcpath_property 5 false] ++ $emission_review_drop_expr(pcode.EXPRESSIONS, '
 'pcpath_property)])]',
 '  -- if $call_entry_check(S_entry) = S_entry',
 '  -- if $heap_valid($heap_graph(S_entry))',
 '  -- if $generator_from_state_valid(S_entry)',
 '  -- if $(psourceoperand.OWNER > 0)',
 '  -- if $global_quiet_name(S_entry, $ptascii("mixed_operand_314")).RESULT = KNOWN PNULL',
 '  -- if (HOBJECT n_operand) <- S_entry.ALLOCATIONS',
 '  -- if $source_operand_enter_valid(S_entry, psourceoperand, n_unit)',
 '  -- if $property_current_line(S_entry[.ORIGIN = (porigin_work)]) = 6',
 '  -- if $call_entry_check(S) = S',
 '  -- if $heap_valid($heap_graph(S))',
 '  -- if $destructor_call_live(S, pdestructorcall)',
 '  -- if pdestructionoperation.ORIGIN = (porigin_work)',
 '  -- if pdestructionoperation.CALLER = S_entry.CURRENT /\\ S_owner.CURRENT = S_entry.CURRENT',
 '  -- if $generator_context_operation(S_owner, pcallcontext_entry) = (pgeneratorop_entry)',
 '  -- if $heap_valid($heap_graph(S_bad_owner))',
 '  -- if ~$source_operand_enter_valid(S_bad_owner, psourceoperand, n_unit)',
 '  -- if $call_entry_check(S_bad_owner).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"',
 '  -- if $heap_valid($heap_graph(S_bad_tail))',
 '  -- if ~$source_operand_enter_valid(S_bad_tail, psourceoperand, n_unit)',
 '  -- if $call_entry_check(S_bad_tail).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
 '  -- if P.COMPLETION = PPCNORMAL /\\ $compilation_image_valid(S_entry, pcunit, P)',
 '  -- if $compiled_read(S_entry, porigin_work) = eps',
 '  -- if $source_echo_emission_origin(S_entry, n_unit, pcpath_property, expression_property) = '
 '(porigin_work)',
 '  -- if $code_expression(pcode.EXPRESSIONS, pcpath_receiver) = ((5, false))',
 '  -- if $code_expression(pcode.EXPRESSIONS, pcpath_property) = ((6, false))',
 '  -- if $property_current_line(S_entry[.ORIGIN = (porigin_receiver)]) = 5',
 '  -- if S.EVENTS = S_entry.EVENTS',
 '  -- if $heap_graph(S_no_receiver) = $heap_graph(S_entry)',
 '  -- if $source_operand_entry_origin(S_no_receiver, psourceoperand, n_unit) = S_no_receiver.ORIGIN',
 '  -- if $call_entry_check(S_no_receiver).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"',
 '  -- if $heap_graph(S_bad_line) = $heap_graph(S_entry)',
 '  -- if $source_echo_emission_origin(S_bad_line, n_unit, pcpath_property, expression_property) = '
 '(porigin_work)',
 '  -- if ~$compilation_image_valid(S_bad_line, pcunit, P)',
 '  -- if $source_operand_entry_origin(S_bad_line, psourceoperand, n_unit) = S_bad_line.ORIGIN',
 '  -- if $call_entry_check(S_bad_line).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
COLLECTOR_HELPERS = r'''dec $expression_comp_review_reached(pstate) : bool
def $expression_comp_review_reached(S) = true
  -- if S.TODO = (GC_DTOR_RETURN pgcplan n) :: ptask*
  -- if $object_name(S, n) = $ptascii("DirectCycle301")
def $expression_comp_review_reached(S) = false -- otherwise
dec $expression_comp_review_seek(pstate, nat) : pstate
def $expression_comp_review_seek(S, n) = S -- if $expression_comp_review_reached(S)
def $expression_comp_review_seek(S, n) = S
  -- if ~$expression_comp_review_reached(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $expression_comp_review_seek(S, 0) = S -- if ~$expression_comp_review_reached(S)
def $expression_comp_review_seek(S, n) = $expression_comp_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$expression_comp_review_reached(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''
COLLECTOR_BINDINGS = GENERATOR_PREMISES[:11] + ['  -- if ' + line for line in [
    '$operand_nodes(psourceoperand.INPUT) = [HOBJECT n_operand]',
    '$source_operand_entry_origin(S_entry, psourceoperand, n_unit) = (porigin_work)',
    'S_reached = $expression_comp_review_seek(S_entry, 700)',
    'S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET',
    'S = S_reached[.COMPLETION = NORMAL]',
    'S.TODO = (GC_DTOR_RETURN pgcplan n_cycle) :: ptask_tail*',
    'S.CURRENT = (pcallcontext)',
    '$destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)',
    'pdestructorcall.OPERATION = (pdestructionoperation)',
    'pdestructionoperation.SOURCE = SOURCE_OPERAND_ENTER psourceoperand n_unit',
    'S_owner = $source_string_owner_scope(S, psourceoperand.OWNER)',
    '$global_quiet_name(S, $ptascii("mixed_weak_301")).RESULT = KNOWN (POBJECT n_weak)',
    'pgcplan_bad_caller = pgcplan[.CALL.CALLER = eps]',
    'S_bad_caller = S[.GC.PLAN = (pgcplan_bad_caller)][.GC.ACTIVE = (pgcplan_bad_caller.CALL)][.TODO = (GC_DTOR_RETURN pgcplan_bad_caller n_cycle) :: ptask_tail*]',
    'pgcplan_bad_count = pgcplan[.COUNTED = eps]',
    'S_bad_count = S[.GC.PLAN = (pgcplan_bad_count)][.TODO = (GC_DTOR_RETURN pgcplan_bad_count n_cycle) :: ptask_tail*]',
    'S_duplicate = S[.TODO = (GC_DTOR_RETURN pgcplan n_cycle) :: (GC_DTORS pgcplan) :: ptask_tail*]',
    'S_bad_owner = S_entry[.FILECONTEXTS = [S_entry.FILECONTEXTS[0][.OWNER = $(psourceoperand.OWNER + 1)]]]',
]]
COLLECTOR_CHECKS = ['  -- if ' + line for line in [
    '$property_current_line(S_entry[.ORIGIN = (porigin_work)]) = 6',
    '$source_operand_enter_valid(S_entry, psourceoperand, n_unit)',
    'S_entry.CURRENT = eps /\\ S_owner.CURRENT = eps',
    'pdestructionoperation.ORIGIN = (porigin_work)',
    'pdestructionoperation.CALLER = S_entry.CURRENT /\\ S_owner.CURRENT = S_entry.CURRENT',
    'S.SOURCEPENDING = eps /\\ S.ACTIVEFIBER = eps',
    'pgcplan.CALL.CALLER = S.CURRENT /\\ pgcplan.CALL.PENDING = eps',
    'pgcplan.DTORS = [HOBJECT n_cycle] /\\ pgcplan.COUNTED = [HOBJECT n_cycle]',
    'pgcplan.INDEX = 0 /\\ n_cycle <- S.DESTRUCTION.CALLED',
    '$task_nodes(GC_DTOR_RETURN pgcplan n_cycle) = [HOBJECT n_cycle]',
    '$heap_owners($heap_graph(S), HOBJECT n_cycle) = 2',
    '(HOBJECT n_operand) <- $machine_roots(S)',
    '$weakref_get(S, n_weak) = POBJECT n_cycle',
    '$gc_state_valid(S) /\\ $call_entry_check(S) = S /\\ $heap_valid($heap_graph(S))',
    '$heap_graph(S_bad_caller) = $heap_graph(S)',
    '~$gc_plan_valid(S_bad_caller, pgcplan_bad_caller) /\\ ~$call_descriptors_valid(S_bad_caller)',
    '$heap_graph(S_bad_count) = $heap_graph(S)',
    '~$gc_plan_valid(S_bad_count, pgcplan_bad_count) /\\ ~$call_descriptors_valid(S_bad_count)',
    '$heap_graph(S_duplicate) = $heap_graph(S)',
    '~$gc_plan_valid(S_duplicate, pgcplan) /\\ ~$call_descriptors_valid(S_duplicate)',
    '$heap_graph(S_bad_owner) = $heap_graph(S_entry)',
    '~$source_operand_enter_valid(S_bad_owner, psourceoperand, n_unit)',
    '$call_entry_check(S_bad_owner).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
    'S_paused = $drive(S, 0)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused[.COMPLETION = NORMAL] = S',
    'S_step = $drive_steps(S, 1)',
    'S_step.COMPLETION = BUDGET /\\ $drive_steps(S_paused[.COMPLETION = NORMAL], 1) = S_step',
    'S_next = S_step[.COMPLETION = NORMAL]',
    'S_next.GC.PLAN = (pgcplan_next)',
    'pgcplan_next.INDEX = 1 /\\ pgcplan_next.DONE = [HOBJECT n_cycle]',
    '$heap_owners($heap_graph(S_next), HOBJECT n_cycle) = 1 /\\ $weakref_get(S_next, n_weak) = POBJECT n_cycle',
    '$gc_state_valid(S_next) /\\ $call_descriptors_valid(S_next) /\\ $heap_valid($heap_graph(S_next))',
    'S_done = $drive(S_next, 2500)',
    'S_done.COMPLETION = NORMAL /\\ S_done.GC.ACTIVE = eps /\\ S_done.GC.PLAN = eps /\\ S_done.SOURCEPENDING = eps',
    '~((HOBJECT n_cycle) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_operand) <- S_done.ALLOCATIONS)',
    '$weakref_get(S_done, n_weak) = PNULL',
    '$gc_state_valid(S_done) /\\ $call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]]
COLLECTOR_PREMISES = COLLECTOR_BINDINGS + COLLECTOR_CHECKS

def run_case(case, args):
    recorder.ROOT = ROOT
    semantic = args.semantic_root.resolve()
    files = ([SOURCES / 'expression-call-property.php', SOURCES / 'call-property-child.php']
             if case == 'entry' else [SOURCES / ('expression-cycle-direct.php' if case == 'collector' else 'expression-generator.php'), SOURCES / 'generator-expression-child.php'] if case in ('generator', 'collector') else [SOURCES / name for name in GUARD_FILES.values()])
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    b64 = lambda value: base64.b64encode(value).decode()
    seq = lambda value: '(' + str(list(value)) + ')'
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = dict(json.loads(profile_file.read_bytes()), include_path='.:', error_reporting='30719')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    php, bridge = ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so'
    adapter, frontend = ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php'
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*files, Path(__file__), profile_file, php, bridge, adapter, frontend,
               ROOT / 'frontend/target.php', ROOT / 'spec/schema.json',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/static_types.py',
               ROOT / 'tests/semantics/error_handler_run.py']
    modules = []
    manifest = semantic / 'spec/semantics/modules.json'
    module_names = json.loads(manifest.read_bytes())
    autoglobal = any(Path(name).name == '316-source-autoglobal-emission.watsup' for name in module_names)
    this_fetch = any(Path(name).name == '323-source-this-emission.watsup' for name in module_names)
    watched.append(manifest)
    if not args.prepare_only:
        modules = [semantic / name for name in module_names]
        assert any(path.name == '314-source-expression-emission.watsup' for path in modules)
        watched += [*modules, runner]
    snapshot = lambda: {str(path): sha(path) for path in watched}
    before = snapshot()
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    out = Path(tempfile.mkdtemp(prefix='source-expression-emission-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    counts = {'entry': (24, 33), 'guards': (32, 40), 'generator': (35, 35), 'collector': (len(COLLECTOR_BINDINGS), len(COLLECTOR_CHECKS))}[case]
    report = {'revision': revision, 'working_tree_status': status, 'semantic_root': str(semantic),
              'case': case, 'inputs': before, 'profile': profile, 'mode': 'SL', 'cache': False, 'det': True,
              'compiler_pin': 'da36ac3c434cd291940293a63da64544307730a3',
              'binding_premises': counts[0], 'check_premises': counts[1], 'physical_premises': sum(counts),
              'source_agreements': 0, 'application_evaluations': 0, 'passed': False,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}}
    try:
        parser = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(frontend)], out / 'frontend')
        try:
            parsed = []
            for index, source in enumerate(files):
                request = {'op': 'parse', 'source': b64(source.read_bytes())} if case in ('entry', 'generator', 'collector') and index == 0 else {
                    'op': 'parse-file', 'id': '0', 'mode': 'file', 'profile': 'cli-raw-85',
                    'requested': b64(bytes(source)), 'resolved': b64(bytes(source)),
                    'opened': b64(bytes(source)), 'source': b64(source.read_bytes())}
                parsed.append(parser.request(request))
            assert all(row['accepted'] for row in parsed)
        finally:
            parser.close()
        checker = Worker([str(adapter), str(ROOT)], out / 'adapter')
        try:
            checked = [checker.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for row in parsed]
            assert all(row['ok'] for row in checked)
        finally:
            checker.close()
        (out / 'checked.json').write_text(json.dumps(checked) + '\n')
        if case in ('entry', 'generator', 'collector'):
            source, child = files
            label = 'emission_review' if case == 'entry' else 'expression_comp_review'
            fixture = ('dec $' + label + '_program() : program\ndef $' + label + '_program() = '
                       + checked[0]['fixture'] + '\n')
            fixture += ('dec $' + label + '_child() : program\ndef $' + label + '_child() = '
                        + checked[1]['fixture'] + '\n' + (ENTRY_HELPERS if case == 'entry' else COLLECTOR_HELPERS if case == 'collector' else GENERATOR_HELPERS))
            premises = list(ENTRY_PREMISES if case == 'entry' else COLLECTOR_PREMISES if case == 'collector' else GENERATOR_PREMISES)
            premises[0] = ('  -- if S_open = $php_file_startup_run($' + label + '_program(), 10000, $base64('
                           + json.dumps(b64(bytes(source))) + '), $base64(' + json.dumps(b64(bytes(ROOT)))
                           + '), {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})')
            opened = ('(FILE_OPENED pfilecontext_open.NONCE '
                      + ' '.join(seq(bytes(p)) for p in (source, child, child, child))
                      + ' ' + seq(child.read_bytes()) + ')')
            premises[4] = '  -- if S_parse = $file_open_resume(S_open, ' + opened + ')'
            premises[8] = ('  -- if ' + ('S' if case == 'entry' else 'S_entry') + ' = $file_parse_resume(S_parse, (SOURCE_ACCEPT n_unit '
                           + seq(child.read_bytes()) + ' $' + label + '_child()))')
        else:
            fixture, bindings, checks = '', [], []
            cp = '[PCINDEX 1, PCFIELD 0, PCINDEX 0]'
            for label, source, row in zip(GUARD_FILES, files, checked):
                fixture += ('dec $emission_guard_' + label + '() : program\ndef $emission_guard_'
                            + label + '() = ' + row['fixture'] + '\n')
                bindings += [
                    'P_' + label + ' = $declaration_compiler_state($ppstart(0, $emission_guard_' + label
                    + '(), $base64(' + json.dumps(b64(bytes(source))) + ')))',
                    'S_' + label + ' = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 0 P_'
                    + label + '.LOCATION.FILE]], P_' + label + ')',
                    '$source_unit(S_' + label + '.SOURCES, 0) = (pcunit_' + label + ')',
                    '$origin_node(S_' + label + '.SOURCES, PORIGIN 0 (' + cp + ')) = (expression_' + label + ')']
                expected = ('(PORIGIN 0 (' + (cp[:-1] + ', PCFIELD 0]' if label == 'call_property' else cp)
                            + '))' if label in ('cv', 'property', 'call_property') else 'eps')
                if (label == 'autoglobal' and autoglobal) or (label == 'this' and this_fetch):
                    expected = '(PORIGIN 0 (' + cp[:-1] + ', PCFIELD 0]))'
                checks += [
                    'P_' + label + '.COMPLETION = PPCNORMAL /\\ S_' + label + '.COMPLETION = NORMAL',
                    '$compilation_image_valid(S_' + label + ', pcunit_' + label + ', P_' + label + ')',
                    '$compiled_read(S_' + label + ', PORIGIN 0 (' + cp + ')) = eps',
                    '$source_echo_emission_origin(S_' + label + ', 0, ' + cp + ', expression_' + label
                    + ') = ' + expected,
                    '$source_first_work_origin(S_' + label + ', 0, P_' + label + '.WORK) = ' + expected]
            premises = ['  -- if ' + line for line in bindings + checks]
        assert len(premises) == sum(counts)
        fixture += ('\ndec $main() : bool\ndef $main() = true\n' + '\n'.join(premises)
                    + '\ndef $main() = false -- otherwise\n')
        test = out / 'admission.watsup'
        test.write_text(fixture)
        report.update(frontend_accepted=True, adapter_ok=True, fixture_sha256=sha(test))
        if args.prepare_only:
            report['passed'] = True
        else:
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(test)], out / 'admission', 120 if case == 'collector' else 90)
            stdout, stderr = ((out / ('admission' + suffix)).read_bytes() for suffix in ('.stdout', '.stderr'))
            report['application_evaluations'] = int(process['exit'] == 0 and stdout in (b'true\n', b'false\n'))
            report.update(process=process, observed=stdout.decode(errors='replace'), stderr=stderr.decode(errors='replace'))
            report['passed'] = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
                                and not stderr and stdout == b'true\n')
    finally:
        report['inputs_stable'] = before == snapshot()
        report['head_stable'] = revision == git('rev-parse', 'HEAD')
        report['status_stable'] = status == git('status', '--short')
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return all(report[key] for key in ('passed', 'inputs_stable', 'head_stable', 'status_stable'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('entry', 'guards', 'generator', 'collector'))
    parser.add_argument('--semantic-root', type=Path, default=ROOT)
    args = parser.parse_args()
    return all(run_case(case, args) for case in ((args.case,) if args.case else ('entry', 'guards')))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
