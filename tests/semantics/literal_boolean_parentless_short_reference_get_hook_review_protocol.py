#!/usr/bin/env python3
"""Check strict literal Boolean aliases, failed acquisition and quiet removal."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('literal_boolean_parentless_short_reference_get_hook_review')
PREFIX = r'''
var U : program
dec $lbr_output(pevent*) : ptbytes
def $lbr_output(eps) = eps
def $lbr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $lbr_output(pevent*)
dec $lbr_phase(pstate,int) : bool
def $lbr_phase(S,0) = ($property_hook_ref_plan(S) =/= eps)
def $lbr_phase(S,-1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*
def $lbr_phase(S,-2) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $lbr_phase(S,-3) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("box302peer")
def $lbr_phase(S,-4) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("f302peer") \/ $base64(text_name) = $ptascii("probe302peer")
def $lbr_phase(S,z) = true
  -- if $(z > 0)
  -- if S.TODO = (EVAL (NExprAssign expression_left expression_right metadata)) :: ptask*
  -- if $source_line(metadata) = z
def $lbr_phase(S,z) = false -- otherwise
dec $lbr_seek(pstate,int,nat) : pstate
def $lbr_seek(S,z,n) = S[.COMPLETION = NORMAL]
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $lbr_phase(S,z) \/ n = 0
def $lbr_seek(S,z,n) = $lbr_seek($drive_steps(S[.COMPLETION = NORMAL],1),z,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps /\ ~$lbr_phase(S,z) /\ $(n > 0)
def $lbr_seek(S,z,n) = S -- otherwise
dec $lbr_noarrow(pcodeexpr*,pcpath) : pcodeexpr*
def $lbr_noarrow(eps,pcpath) = eps
def $lbr_noarrow((CODEARROW pcpath z) :: pcodeexpr_tail*,pcpath) = $lbr_noarrow(pcodeexpr_tail*,pcpath)
def $lbr_noarrow(pcodeexpr :: pcodeexpr_tail*,pcpath) = pcodeexpr :: $lbr_noarrow(pcodeexpr_tail*,pcpath)
  -- if $arrow_line_entry(pcodeexpr,pcpath) = eps
'''


def fields(fixture, source, form):
    nullable = form == 'nullable'
    abrupt = form == 'uninitialized'
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')',
        'S_front = $lbr_seek(S_start,0,30000)', '$lbr_phase(S_front,0)', 'S_front.COMPLETION = NORMAL',
        '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box302peer")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps',
        '$trait_plan(S_front,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_f]' if abrupt else 'pclassdesc_root.PROPERTIES = [ppropertydesc_f,ppropertydesc_t]',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = (ppropertyslot_front*)',
    ]
    for name, kind, line in [('f', 'false', 4)] + ([] if abrupt else [('t', 'true', 5)]):
        desc = 'ppropertydesc_' + name
        normalized = '[(PTBRANCH ([PTBUILTIN "' + kind + '"]))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')
        header = 'NIdentifier (BYTES text_type_' + name + ') metadata_type_' + name
        if nullable:
            header = 'NNullableType (' + header + ') metadata_nullable_' + name
        checks += [
            desc + '.NAME = $ptascii("' + name + '")', desc + '.TYPE = ' + normalized,
            '$property_hook_reference_decl(S_front,' + desc + ')',
            desc + '.ORIGIN = PORIGIN n_source pcpath_' + name,
            'pcpath_group_' + name + ' = pcpath_' + name + '[0:$nabs($( |pcpath_' + name + '| - 2))]',
            'pcpath_' + name + ' = pcpath_group_' + name + ' ++ [PCFIELD 3,PCINDEX 0]',
            '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group_' + name + ') = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18_' + name + ' (SEQUENCE ([NPropertyItem phpType40_' + name + ' phpType5_' + name + ' metadata_item_' + name + '])) (SEQUENCE ([phpType38_' + name + '])) metadata_group_' + name + ')',
            'phpType18_' + name + ' = ' + header, '$base64(text_type_' + name + ') = $ptascii("' + kind + '")',
            '$hook_short_reference_header(phpType18_' + name + ',' + desc + '.TYPE)',
            '~$hook_short_reference_header(phpType18_' + name + ',[(PTBRANCH ([PTBUILTIN "bool"]))])',
            '$pttypename(' + desc + '.TYPE) = $ptascii("' + ('?' if nullable else '') + kind + '")',
            '$property_hook_origin(S_front,' + desc + ') = (porigin_hook_' + name + ')',
            '$function_at($all_functions(S_front),porigin_hook_' + name + ') = (pfunction_' + name + ')',
            'pfunction_' + name + '.SIGNATURE = {PARAMETERS eps, RETURNS ' + desc + '.TYPE, BYREF true}',
            'pfunction_' + name + '.CODE.STRICT',
            'pfunction_' + name + '.BODY = pcpath_group_' + name + ' ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
            'phpType38_' + name + ' = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_' + name + ' (SEQUENCE eps) expression_' + name + ' metadata_hook_' + name,
            '$hook_parameter_facts(metadata_hook_' + name + ') = [false]',
            'expression_' + name + ' = NExprPropertyFetch (NExprVariable (BYTES text_this_' + name + ') metadata_this_' + name + ') (NScalarString (BYTES text_field_' + name + ') metadata_field_' + name + ') metadata_expression_' + name,
            '$base64(text_this_' + name + ') = $ptascii("this")', '$base64(text_field_' + name + ') = $ptascii("' + name + '")',
            '$source_line(metadata_expression_' + name + ') = ' + str(line),
            '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction_' + name + '.BODY) = (expression_' + name + ')',
            '$code_expression(pfunction_' + name + '.CODE.EXPRESSIONS,pfunction_' + name + '.BODY) = ((' + str(line) + ',false))',
            '$arrow_line(pfunction_' + name + '.CODE.EXPRESSIONS,pfunction_' + name + '.BODY) = (' + str(line) + ')',
            '$property_slot_at(ppropertyslot_front*,$ptascii("' + name + '")) = (ppropertyslot_' + name + ')',
            'ppropertyslot_' + name + '.STATE = ' + ('PROP_INITIAL' if nullable or abrupt else 'PROP_VALUE (DIRECT (PBOOL ' + kind + '))'),
        ]
        if nullable or abrupt:
            checks += ['phpType5_' + name + ' = ABSENT']
        for strict in ('false', 'true'):
            checks += [
                '$propref_class(S_front,' + desc + '.TYPE,PBOOL ' + kind + ',' + strict + ') = PROP_EXACT',
                '$propref_class(S_front,' + desc + '.TYPE,PBOOL ' + ('true' if kind == 'false' else 'false') + ',' + strict + ') = PROP_IMPOSSIBLE',
                '$propref_class(S_front,' + desc + '.TYPE,PINT 0,' + strict + ') = PROP_IMPOSSIBLE',
                '$propref_class(S_front,' + desc + '.TYPE,PINT 1,' + strict + ') = PROP_IMPOSSIBLE',
                '$propref_class(S_front,' + desc + '.TYPE,PNULL,' + strict + ') = ' + ('PROP_EXACT' if nullable else 'PROP_IMPOSSIBLE'),
            ]
    checks += [
        'ppropertyhook.PROPERTY = ppropertydesc_f.ORIGIN', 'ppropertyhook.HOOK = porigin_hook_f',
        'S_return = $lbr_seek(S_front,-1,30000)', '$lbr_phase(S_return,-1)', 'S_return.COMPLETION = NORMAL',
        'S_return.TODO = (RETURN_REF_FETCH 4) :: ptask_return*',
        '$reference_return_source(S_return,4)', '$reference_return_fetch_valid(S_return,4)', '$reference_verifies(S_return)',
        '$property_current_line(S_return) = 4', '$property_current_line($hold_task_inputs(S_return)) = 4',
        '~$reference_return_source(S_return,5)', '~$call_task_valid(S_return,RETURN_REF_FETCH 5)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction_f[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction_f.CODE.EXPRESSIONS,pfunction_f.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,4)', '$property_current_line(S_noarrow) = 0',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction_f[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"]))]]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,4)', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH 4)',
        '~$hook_short_reference_header(NIdentifier (BYTES "Ym9vbA==") eps,ppropertydesc_f.TYPE)',
        '~$hook_short_reference_header(NIdentifier (BYTES "dHJ1ZQ==") eps,[(PTBRANCH ([PTBUILTIN "false"]))])',
        '$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "ZmFsc2U=") eps,NIdentifier (BYTES "bnVsbA==") eps])) eps,[(PTBRANCH ([PTBUILTIN "false"])),(PTBRANCH ([PTBUILTIN "null"]))])',
        '$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "bnVsbA==") eps,NIdentifier (BYTES "dHJ1ZQ==") eps])) eps,[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "true"]))])',
    ]
    if form == 'canonical':
        checks += [
            '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
            'statement_badraw = NStmtProperty (SEQUENCE eps) (INTEGER 1) (NIdentifier (BYTES "Ym9vbA==") metadata_type_f) (SEQUENCE ([NPropertyItem phpType40_f phpType5_f metadata_item_f])) (SEQUENCE ([phpType38_f])) metadata_group_f',
            'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group_f statement_badraw) :: pcunit.OCCURRENCES]]]',
            '~$property_hook_reference_decl(S_badraw,ppropertydesc_f)',
            '$property_hook_reference_expression_return(S_badraw,ppropertyhook.HOOK,4) = eps',
            '$property_current_line(S_badraw) = 0',
        ]
    if abrupt:
        message = '$base64(' + peer.quoted('Cannot access uninitialized non-nullable property LiteralBoolean302UninitPeerBox::$f by reference') + ')'
        checks += [
            '$lookup(S_front.ENV,$ptascii("old302peer")) = (n_old)',
            '$lookup(S_front.ENV,$ptascii("probe302peer")) = (n_old)',
            '$lookup(S_front.ENV,$ptascii("shadow302peer")) = (n_old)',
            'S_front.STORE[n_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
            '$heap_owners($heap_graph(S_front),HCELL n_old) = 3',
            'S_error = $reference_return_fetch($hold_task_inputs(S_return),S_return.BASE,4)',
            'S_error.COMPLETION = THROWN "Error" (' + message + ') 4',
            'S_error.STORE = S_return.STORE', 'S_error.REFCELLS = S_return.REFCELLS',
            'S_error.OBJECTPROPS = S_return.OBJECTPROPS', 'S_error.PROPREFS = S_return.PROPREFS',
            'S_failed = $lbr_seek(S_return,15,30000)', '$lbr_phase(S_failed,15)',
            '$lbr_output(S_failed.EVENTS) = $ptascii("U|P|")',
            'S_failed.STORE[n_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
            '$objectprops_at(S_failed.OBJECTPROPS,n_root) = (ppropertyslot_front*)',
            'S_oldwrite = $lbr_seek(S_failed,17,30000)', '$lbr_phase(S_oldwrite,17)',
            '$lbr_output(S_oldwrite.EVENTS) = $ptascii("U|P|W|")', 'S_oldwrite.STORE[n_old] = DEFINED (PINT 37)',
            '$objectprops_at(S_oldwrite.OBJECTPROPS,n_root) = (ppropertyslot_front*)',
            'S_initialized = $lbr_seek(S_oldwrite,0,30000)', '$lbr_phase(S_initialized,0)',
            '$objectprops_at(S_initialized.OBJECTPROPS,n_root) = (ppropertyslot_afterinit*)',
            '$property_slot_at(ppropertyslot_afterinit*,$ptascii("f")) = (ppropertyslot_initialized)',
            'ppropertyslot_initialized.STATE = PROP_VALUE (DIRECT (PBOOL false))',
            'S_goodreturn = $lbr_seek(S_initialized,-1,30000)', '$lbr_phase(S_goodreturn,-1)',
            'S_fetch = $lbr_seek(S_goodreturn,-2,30000)', '$lbr_phase(S_fetch,-2)',
            'S_fetch.RESULT = REFERENCE n_f', 'n_f =/= n_old', 'S_fetch.STORE[n_f] = DEFINED (PBOOL false)',
            'S_rebound = $lbr_seek(S_fetch,20,30000)', '$lbr_phase(S_rebound,20)',
            '$lbr_output(S_rebound.EVENTS) = $ptascii("U|P|W|A|")',
            '$lookup(S_rebound.ENV,$ptascii("probe302peer")) = (n_f)',
            'S_rebound.STORE[n_f] = DEFINED (PBOOL false)', 'S_rebound.STORE[n_old] = DEFINED (PINT 37)',
            '$heap_owners($heap_graph(S_rebound),HCELL n_f) = 2',
        ]
        for state in ('S_failed', 'S_oldwrite', 'S_initialized'):
            for name in ('old', 'probe', 'shadow'):
                checks += ['$lookup(' + state + '.ENV,$ptascii("' + name + '302peer")) = (n_old)']
            checks += ['$heap_owners($heap_graph(' + state + '),HCELL n_old) = 3',
                       '$propref_at(' + state + '.PROPREFS,n_old) = eps']
        for name in ('old', 'shadow'):
            checks += ['$lookup(S_rebound.ENV,$ptascii("' + name + '302peer")) = (n_old)']
        checks += ['$heap_owners($heap_graph(S_rebound),HCELL n_old) = 2']
        active = 'S_rebound'
        detached_line = 25
        alias_names = [('f', 'probe302peer', 'PBOOL false', 2, 1)]
    else:
        checks += [
            'S_fetch = $lbr_seek(S_return,-2,30000)', '$lbr_phase(S_fetch,-2)',
            'S_fetch.RESULT = REFERENCE n_f', 'S_fetch.STORE[n_f] = DEFINED (' + ('PNULL' if nullable else 'PBOOL false') + ')',
            '$propref_at(S_fetch.PROPREFS,n_f) = (ppropref_fetch)',
            'ppropref_fetch.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("f")) ppropertydesc_f.ORIGIN]',
            '$heap_owners($heap_graph(S_fetch),HCELL n_f) = 2',
            'S_copies = $lbr_seek(S_fetch,' + ('17' if nullable else '14') + ',30000)',
            '$lbr_phase(S_copies,' + ('17' if nullable else '14') + ')',
            '$lookup(S_copies.ENV,$ptascii("f302peer")) = (n_f)',
            '$lookup(S_copies.ENV,$ptascii("aliasf302peer")) = (n_f)',
            '$lookup(S_copies.ENV,$ptascii("t302peer")) = (n_t)',
        ]
        for name, kind in (('f', 'false'), ('t', 'true')):
            checks += [
                'S_copies.STORE[n_' + name + '] = DEFINED (PBOOL ' + kind + ')',
                '$lookup(S_copies.ENV,$ptascii("copy' + name + '302peer")) = (n_copy_' + name + ')',
                'n_copy_' + name + ' =/= n_' + name,
                'S_copies.STORE[n_copy_' + name + '] = DEFINED (PBOOL ' + kind + ')',
                '$propref_at(S_copies.PROPREFS,n_copy_' + name + ') = eps',
                '$heap_owners($heap_graph(S_copies),HCELL n_copy_' + name + ') = 1',
            ]
        if nullable:
            checks += ['S_reset = $lbr_seek(S_copies,36,30000)', '$lbr_phase(S_reset,36)',
                       'S_reset.STORE[n_f] = DEFINED PNULL', 'S_reset.STORE[n_t] = DEFINED PNULL',
                       '$lbr_output(S_reset.EVENTS) = $ptascii("N|V|F|T|I|J|Q|")']
        active = 'S_copies'
        detached_line = 41 if nullable else 37
        alias_names = [('f', 'f302peer', 'PBOOL false', 3, 2), ('t', 't302peer', 'PBOOL true', 2, 1)]
    for name, alias, value, before, after in alias_names:
        checks += [
            '$propref_at(' + active + '.PROPREFS,n_' + name + ') = (ppropref_' + name + ')',
            'ppropref_' + name + '.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("' + name + '")) ppropertydesc_' + name + '.ORIGIN]',
            '$heap_owners($heap_graph(' + active + '),HCELL n_' + name + ') = ' + str(before),
        ]
    checks += [
        'S_missing = ' + active + '[.PROPREFS = $propref_detach(' + active + '.PROPREFS,n_f,OBJECT_PROP_SOURCE n_root ($ptascii("f")) ppropertydesc_f.ORIGIN)]',
        '~$property_state_valid(S_missing)',
        'S_before = $lbr_seek(' + active + ',-3,30000)', '$lbr_phase(S_before,-3)',
        'S_before.COMPLETION = NORMAL', 'S_before.CURRENT = eps', 'S_before.FRAMES = eps',
        'S_detached = $lbr_seek(S_before,' + str(detached_line) + ',30000)', '$lbr_phase(S_detached,' + str(detached_line) + ')',
        'S_detached.COMPLETION = NORMAL', '~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
        'S_written = $lbr_seek(S_detached,-4,30000)', '$lbr_phase(S_written,-4)',
        'S_end = $drive_steps(S_written,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $ptascii("' + json.loads((SOURCES/'cases.json').read_text())[form]['stdout'] + '")',
    ]
    for name, alias, value, before, after in alias_names:
        checks += [
            'S_before.STORE[n_' + name + '] = DEFINED (' + value + ')',
            '$propref_at(S_before.PROPREFS,n_' + name + ') = (ppropref_' + name + ')',
            '$heap_owners($heap_graph(S_before),HCELL n_' + name + ') = ' + str(before),
            'S_detached.STORE[n_' + name + '] = DEFINED (' + value + ')',
            '$lookup(S_detached.ENV,$ptascii("' + alias + '")) = (n_' + name + ')',
            '$propref_at(S_detached.PROPREFS,n_' + name + ') = eps',
            '$heap_owners($heap_graph(S_detached),HCELL n_' + name + ') = ' + str(after),
            '~((HCELL n_' + name + ') <- S_end.ALLOCATIONS)',
        ]
    if abrupt:
        checks += ['S_written.STORE[n_f] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("free")))',
                   'S_written.STORE[n_old] = DEFINED (PINT 37)',
                   '$heap_owners($heap_graph(S_written),HCELL n_old) = 2',
                   '~((HCELL n_old) <- S_end.ALLOCATIONS)']
    else:
        checks += ['S_written.STORE[n_f] = DEFINED (PINT 0)', 'S_written.STORE[n_t] = DEFINED (PINT 1)']
        for name, kind in (('f', 'false'), ('t', 'true')):
            checks += ['S_written.STORE[n_copy_' + name + '] = DEFINED (PBOOL ' + kind + ')',
                       '~((HCELL n_copy_' + name + ') <- S_end.ALLOCATIONS)']
    for state in ('S_return', active, 'S_before', 'S_detached', 'S_written', 'S_end'):
        checks += ['$call_descriptors_valid(' + state + ')', '$property_state_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)']
    checks += ['S_cleanup_one.COMPLETION = BUDGET',
               '$drive_steps(S_cleanup_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['canonical', 'nullable', 'uninitialized'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    cases = json.loads((SOURCES/'cases.json').read_text())
    source = SOURCES/cases[args.form]['source']
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(peer.__file__), source, SOURCES/'cases.json', SOURCES/'hashes.json', *modules, *(ROOT/p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'),
                           str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form)
        report['premises'] = len(checks)
        (out/'assertions.json').write_text(json.dumps(checks, indent=2)+'\n')
        (out/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'
                                         + ''.join('  -- if '+check+'\n' for check in checks))
        report['process'] = recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 240)
        report['stdout'] = (out/'check.stdout').read_text(); report['stderr'] = (out/'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__':
    main()
