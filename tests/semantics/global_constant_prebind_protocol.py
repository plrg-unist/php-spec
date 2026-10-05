#!/usr/bin/env python3
"""Source-derived per-child global constant lookup, retry and owner guards."""
import argparse,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import global_constant_callable_protocol as global_protocol
base=global_protocol.base
SOURCES={'global-constant-prebind-mixed-lookup': '<?php\n'
                                         'namespace {\n'
                                         '    const PREBIND_SEED = static function () { '
                                         "return 'global'; };\n"
                                         '}\n'
                                         'namespace GlobalPreBindMixedScope {\n'
                                         '    set_error_handler(function ($level) {\n'
                                         "        echo $level, ':';\n"
                                         '        eval("namespace GlobalPreBindMixedScope; '
                                         'const PREBIND_SEED = static function () { return '
                                         '\'late\'; };");\n'
                                         '        return true;\n'
                                         '    });\n'
                                         '    const VALUE = [PREBIND_SEED, E_STRICT + 0, '
                                         'PREBIND_SEED];\n'
                                         '    restore_error_handler();\n'
                                         '    $values = VALUE;\n'
                                         '    $before = $values[0];\n'
                                         '    $after = $values[2];\n'
                                         "    echo $before(), ':', $after(), ':',\n"
                                         "        ($before === $after ? '1' : '0'), ':',\n"
                                         "        ($before === \\PREBIND_SEED ? '1' : "
                                         "'0'), ':', $values[1];\n"
                                         '}\n',
 'global-constant-prebind-throw-retry': '<?php\n'
                                        'namespace {\n'
                                        '    const PREBIND_SEED = static function () { '
                                        "return 'global'; };\n"
                                        '}\n'
                                        'namespace GlobalPreBindRetryScope {\n'
                                        '    set_error_handler(function ($level) {\n'
                                        "        echo $level, ':';\n"
                                        '        eval("namespace GlobalPreBindRetryScope; '
                                        'const PREBIND_SEED = static function () { return '
                                        '\'late\'; };");\n'
                                        "        throw new \\Error('stop');\n"
                                        '    });\n'
                                        '    try {\n'
                                        '        eval("namespace GlobalPreBindRetryScope; '
                                        'const VALUE = [PREBIND_SEED, static function () { '
                                        "return 'candidate'; }, E_STRICT + 0, "
                                        'PREBIND_SEED];");\n'
                                        '    } catch (\\Error $e) {\n'
                                        "        echo 'F:';\n"
                                        '    }\n'
                                        '    restore_error_handler();\n'
                                        '    try { $failed = VALUE; } catch (\\Error $e) { '
                                        "echo 'U:'; }\n"
                                        '    set_error_handler(function ($level) { echo '
                                        "$level, ':'; return true; });\n"
                                        '    eval("namespace GlobalPreBindRetryScope; '
                                        'const VALUE = [PREBIND_SEED, static function () { '
                                        "return 'candidate'; }, E_STRICT + 0, "
                                        'PREBIND_SEED];");\n'
                                        '    restore_error_handler();\n'
                                        '    $values = VALUE;\n'
                                        '    $before = $values[0];\n'
                                        '    $candidate = $values[1];\n'
                                        '    $after = $values[3];\n'
                                        "    echo $before(), ':', $candidate(), ':', "
                                        "$after(), ':',\n"
                                        "        ($before === $after ? '1' : '0'), ':', "
                                        '$values[2];\n'
                                        '}\n'}
FILES={}
EVALS={
 'global-constant-prebind-mixed-lookup': ["namespace GlobalPreBindMixedScope; const PREBIND_SEED = static function () { return 'late'; };"],
 'global-constant-prebind-throw-retry': [
  "namespace GlobalPreBindRetryScope; const VALUE = [PREBIND_SEED, static function () { return 'candidate'; }, E_STRICT + 0, PREBIND_SEED];",
  "namespace GlobalPreBindRetryScope; const PREBIND_SEED = static function () { return 'late'; };",
 ],
}
PREFIX=global_protocol.PREFIX+r'''
def $global_test_stage(S, ptbytes, 9) = true
  -- if S.TODO = (CONSTANT_OBSERVE porigin_site) :: ptask_tail*
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
  -- if $global_constant_alias(S, S.USERCONSTANTS, porigin_site) = (puserconstant)
  -- if ~$constant_callable_foldable(puserconstant.CLASS)
'''
CHECKS={}
premises=global_protocol.premises
CHECKS['global-constant-prebind-mixed-lookup']=premises(r'''
ptbytes_value = $user_constant_key($ptascii("GlobalPreBindMixedScope") ++ [92] ++ $ptascii("VALUE"))
ptbytes_seed = $ptascii("PREBIND_SEED")
ptbytes_late = $user_constant_key($ptascii("GlobalPreBindMixedScope") ++ [92] ++ ptbytes_seed)
S_before = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_value, 9, 2000)
S_before.TODO = (CONSTANT_OBSERVE porigin_before) :: ptask_before*
S_before.CONSTCONTEXT = (pconstantcontext_before)
porigin_decl = pconstantcontext_before.ORIGIN
S_before.USERCONSTANTS = [puserconstant_global]
puserconstant_global.NAME = ptbytes_seed
puserconstant_global.VALUE = POBJECT n_global
S_before.RESULT = KNOWN (POBJECT n_global)
n_before = |S_before.USERCONSTANTS|
$constant_class(S_before, porigin_before) = puserconstant_global.CLASS
$global_constant_observation_lookup(S_before, porigin_before, POBJECT n_global, puserconstant_global.CLASS) = (pconstantlookup_before)
pconstantlookup_before = {ORIGIN porigin_decl, SITE porigin_before, DECL puserconstant_global.ORIGIN, PREFIX n_before}
$constant_context_valid(S_before)
$global_constant_observation_lookup(S_before[.RESULT = KNOWN PNULL], porigin_before, POBJECT n_global, puserconstant_global.CLASS) = eps
$global_constant_observation_lookup(S_before[.DECLARATIONS = eps], porigin_before, POBJECT n_global, puserconstant_global.CLASS) = eps
$global_constant_observation_lookup(S_before[.TODO = eps], porigin_before, POBJECT n_global, puserconstant_global.CLASS) = eps
$global_constant_observation_lookup(S_before[.CONSTCONTEXT = (pconstantcontext_before[.ORIGIN = puserconstant_global.ORIGIN])], porigin_before, POBJECT n_global, puserconstant_global.CLASS) = eps
S_warning = $global_test_find(S_before, ptbytes_value, 6, 1200)
S_warning.CONSTCONTEXT = (pconstantcontext_warning)
$constant_fact_at(pconstantcontext_warning.FACTS, porigin_before) = (pconstantfact_before)
pconstantfact_before.LOOKUP = (pconstantlookup_before)
pconstantfact_before.CLASS = puserconstant_global.CLASS
$global_constant_reads(S_warning, porigin_decl) = [pconstantfact_before]
$constant_context_valid(S_warning)
S_after = $global_test_find(S_warning, ptbytes_value, 9, 2400)
S_after.TODO = (CONSTANT_OBSERVE porigin_after) :: ptask_after*
porigin_after =/= porigin_before
S_after.USERCONSTANTS = [puserconstant_global, puserconstant_late]
puserconstant_late.NAME = ptbytes_late
puserconstant_late.VALUE = POBJECT n_late
n_late =/= n_global
S_after.RESULT = KNOWN (POBJECT n_late)
n_after = |S_after.USERCONSTANTS|
$(n_before < n_after)
$global_constant_observation_lookup(S_after, porigin_after, POBJECT n_late, puserconstant_late.CLASS) = (pconstantlookup_after)
pconstantlookup_after = {ORIGIN porigin_decl, SITE porigin_after, DECL puserconstant_late.ORIGIN, PREFIX n_after}
$constant_context_valid(S_after)
$global_constant_observation_lookup(S_after, porigin_after, POBJECT n_global, puserconstant_global.CLASS) = eps
S_bind = $global_test_find(S_after, ptbytes_value, 1, 1200)
S_bind.TODO = (CONSTANT_BIND porigin_decl) :: ptask_bind*
S_bind.CONSTCONTEXT = (pconstantcontext_bind)
$constant_fact_at(pconstantcontext_bind.FACTS, porigin_after) = (pconstantfact_after)
pconstantfact_after.LOOKUP = (pconstantlookup_after)
$global_constant_reads(S_bind, porigin_decl) = [pconstantfact_before, pconstantfact_after]
pvalueclass_value = $constant_received_class(S_bind, porigin_decl)
pvalueclass_value = PVARRAY false [(KINT 0, puserconstant_global.CLASS), (KINT 1, PVSCALAR), (KINT 2, puserconstant_late.CLASS)]
S_bind.RESULT = KNOWN (PARRAY n_array)
S_bind.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_global)), ENTRY (KINT 1) (DIRECT (PINT 2048)), ENTRY (KINT 2) (DIRECT (POBJECT n_late))]
$constant_value_class_valid(S_bind, PARRAY n_array, pvalueclass_value)
$global_constant_transfer_valid(S_bind, porigin_decl, pvalueclass_value, S_bind.USERCONSTANTS)
$constant_context_valid(S_bind)
$call_descriptors_valid(S_bind)
~$global_constant_transfer_reads_valid(S_bind, porigin_decl, pvalueclass_value, S_bind.USERCONSTANTS, eps)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_before[.LOOKUP = (pconstantlookup_after)], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_after[.LOOKUP = (pconstantlookup_before)], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_before[.LOOKUP = (pconstantlookup_before[.PREFIX = n_after])], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_before[.LOOKUP = (pconstantlookup_before[.DECL = puserconstant_late.ORIGIN])], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_before[.LOOKUP = (pconstantlookup_before[.ORIGIN = puserconstant_late.ORIGIN])], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_before[.LOOKUP = (pconstantlookup_before[.SITE = porigin_after])], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_before[.LOOKUP = (pconstantlookup_before[.PREFIX = 0])], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_before[.CLASS = puserconstant_late.CLASS], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, puserconstant_global.ORIGIN, pconstantfact_before, S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_decl, pconstantfact_after, S_bind.USERCONSTANTS[0:n_before])
~$global_constant_reads_valid(S_bind, porigin_decl, [pconstantfact_before, pconstantfact_before, pconstantfact_after], S_bind.USERCONSTANTS)
~$constant_facts_valid(S_bind, porigin_decl, $constant_fact_put(pconstantcontext_bind.FACTS, pconstantfact_before[.LOOKUP = eps]))
S_done = $global_test_finish(S_bind, 3000)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("8192:global:late:0:1:2048")
$user_constant_at(S_done.USERCONSTANTS, ptbytes_value) = (puserconstant_value)
puserconstant_value.VALUE = PARRAY n_array
puserconstant_value.READS = [pconstantfact_before, pconstantfact_after]
S_done.CONSTCONTEXT = eps
$user_constants_valid(S_done, S_done.USERCONSTANTS)
$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)
~$global_constant_user_valid(S_done, puserconstant_value[.READS = eps])
n_done = |S_done.USERCONSTANTS|
pconstantfact_future = pconstantfact_after[.LOOKUP = (pconstantlookup_after[.PREFIX = n_done])]
$global_constant_lookup_valid(S_done, porigin_decl, pconstantfact_future, S_done.USERCONSTANTS)
~$global_constant_user_valid(S_done, puserconstant_value[.READS = [pconstantfact_before, pconstantfact_future]])
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HARRAY n_array) <- S_roots.ALLOCATIONS
(HOBJECT n_global) <- S_roots.ALLOCATIONS
(HOBJECT n_late) <- S_roots.ALLOCATIONS
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
$task_nodes(GLOBAL_CONSTANT_DUPLICATE porigin_decl PNULL PVSCALAR n_done [pconstantfact_before, pconstantfact_after] 1) = eps
''')
CHECKS['global-constant-prebind-throw-retry']=premises(r'''
ptbytes_value = $user_constant_key($ptascii("GlobalPreBindRetryScope") ++ [92] ++ $ptascii("VALUE"))
ptbytes_seed = $ptascii("PREBIND_SEED")
ptbytes_late = $user_constant_key($ptascii("GlobalPreBindRetryScope") ++ [92] ++ ptbytes_seed)
S_warning = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_value, 6, 2400)
S_warning.CONSTCONTEXT = (pconstantcontext_failed)
porigin_failed = pconstantcontext_failed.ORIGIN
porigin_failed = PORIGIN n_failed pcpath_failed
S_warning.USERCONSTANTS = [puserconstant_global]
puserconstant_global.VALUE = POBJECT n_global
porigin_before_failed = $constant_child(porigin_failed, [PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1])
porigin_candidate_failed = $constant_child(porigin_failed, [PCFIELD 1, PCFIELD 0, PCINDEX 1, PCFIELD 1])
$constant_fact_at(pconstantcontext_failed.FACTS, porigin_before_failed) = (pconstantfact_failed)
pconstantfact_failed.LOOKUP = (pconstantlookup_failed)
pconstantlookup_failed.DECL = puserconstant_global.ORIGIN
pconstantlookup_failed.ORIGIN = porigin_failed
$constant_fact_at(pconstantcontext_failed.FACTS, porigin_candidate_failed) = (pconstantfact_candidate_failed)
pconstantfact_candidate_failed.CLASS = PVCLOSURE n_discarded porigin_candidate_failed
pconstantfact_candidate_failed.LOOKUP = eps
$constant_callable_record(S_warning.CONSTANTCLOSURES, n_discarded) = (pconstantclosure_discarded)
pconstantclosure_discarded.DECL = porigin_failed
$constant_context_valid(S_warning)
(HOBJECT n_discarded) <- $prune_allocations(S_warning).ALLOCATIONS
S_caught = $global_test_find(S_warning, $ptascii("8192:F:"), 7, 2600)
S_caught.CONSTCONTEXT = eps
$user_constant_at(S_caught.USERCONSTANTS, ptbytes_value) = eps
$user_constant_at(S_caught.USERCONSTANTS, ptbytes_late) = (puserconstant_late)
puserconstant_late.VALUE = POBJECT n_late
n_late =/= n_global
S_failed_roots = $prune_allocations(S_caught)
~((HOBJECT n_discarded) <- S_failed_roots.ALLOCATIONS)
$constant_callable_record(S_failed_roots.CONSTANTCLOSURES, n_discarded) = (pconstantclosure_discarded)
$constant_callable_record_valid(S_failed_roots, pconstantclosure_discarded)
$user_constants_valid(S_failed_roots, S_failed_roots.USERCONSTANTS)
S_retry = $global_test_find(S_caught, ptbytes_value, 9, 2600)
S_retry.TODO = (CONSTANT_OBSERVE porigin_before_retry) :: ptask_retry*
S_retry.CONSTCONTEXT = (pconstantcontext_retry)
porigin_retry = pconstantcontext_retry.ORIGIN
porigin_retry = PORIGIN n_retry pcpath_retry
n_retry =/= n_failed
porigin_retry =/= porigin_failed
pconstantcontext_retry.FACTS = eps
S_retry.RESULT = KNOWN (POBJECT n_late)
$global_constant_observation_lookup(S_retry, porigin_before_retry, POBJECT n_late, puserconstant_late.CLASS) = (pconstantlookup_retry)
pconstantlookup_retry.ORIGIN = porigin_retry
pconstantlookup_retry.SITE = porigin_before_retry
pconstantlookup_retry.DECL = puserconstant_late.ORIGIN
pconstantlookup_retry.PREFIX = |S_retry.USERCONSTANTS|
$global_constant_observation_lookup(S_retry, porigin_before_retry, POBJECT n_global, puserconstant_global.CLASS) = eps
S_bind = $global_test_find(S_retry, ptbytes_value, 1, 2800)
S_bind.CONSTCONTEXT = (pconstantcontext_bind)
porigin_after_retry = $constant_child(porigin_retry, [PCFIELD 1, PCFIELD 0, PCINDEX 3, PCFIELD 1])
porigin_candidate_retry = $constant_child(porigin_retry, [PCFIELD 1, PCFIELD 0, PCINDEX 1, PCFIELD 1])
$constant_fact_at(pconstantcontext_bind.FACTS, porigin_before_retry) = (pconstantfact_before)
$constant_fact_at(pconstantcontext_bind.FACTS, porigin_after_retry) = (pconstantfact_after)
pconstantfact_before.LOOKUP = (pconstantlookup_retry)
pconstantfact_after.LOOKUP = (pconstantlookup_after)
pconstantlookup_after.ORIGIN = porigin_retry
pconstantlookup_after.SITE = porigin_after_retry
pconstantlookup_after.DECL = puserconstant_late.ORIGIN
pconstantlookup_after.PREFIX = pconstantlookup_retry.PREFIX
pconstantfact_before.CLASS = puserconstant_late.CLASS
pconstantfact_after.CLASS = puserconstant_late.CLASS
$constant_fact_at(pconstantcontext_bind.FACTS, porigin_candidate_retry) = (pconstantfact_candidate)
pconstantfact_candidate.CLASS = PVCLOSURE n_kept porigin_candidate_retry
n_kept =/= n_discarded
pconstantfact_candidate.LOOKUP = eps
S_bind.RESULT = KNOWN (PARRAY n_array)
pvalueclass_value = $constant_received_class(S_bind, porigin_retry)
$constant_value_class_valid(S_bind, PARRAY n_array, pvalueclass_value)
$global_constant_transfer_valid(S_bind, porigin_retry, pvalueclass_value, S_bind.USERCONSTANTS)
$constant_context_valid(S_bind)
~$global_constant_lookup_valid(S_bind, porigin_retry, pconstantfact_before[.LOOKUP = (pconstantlookup_failed)], S_bind.USERCONSTANTS)
~$global_constant_lookup_valid(S_bind, porigin_retry, pconstantfact_before[.LOOKUP = (pconstantlookup_after)], S_bind.USERCONSTANTS)
~$constant_facts_valid(S_bind, porigin_retry, $constant_fact_put(pconstantcontext_bind.FACTS, pconstantfact_before[.LOOKUP = (pconstantlookup_failed)]))
S_done = $global_test_finish(S_bind, 3200)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("8192:F:U:8192:late:candidate:late:1:2048")
$user_constant_at(S_done.USERCONSTANTS, ptbytes_value) = (puserconstant_value)
puserconstant_value.ORIGIN = porigin_retry
puserconstant_value.VALUE = PARRAY n_array
puserconstant_value.READS = [pconstantfact_before, pconstantfact_after]
S_done.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_late)), ENTRY (KINT 1) (DIRECT (POBJECT n_kept)), ENTRY (KINT 2) (DIRECT (PINT 2048)), ENTRY (KINT 3) (DIRECT (POBJECT n_late))]
$user_constants_valid(S_done, S_done.USERCONSTANTS)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_discarded) <- S_roots.ALLOCATIONS)
(HOBJECT n_kept) <- S_roots.ALLOCATIONS
(HOBJECT n_late) <- S_roots.ALLOCATIONS
(HOBJECT n_global) <- S_roots.ALLOCATIONS
(HARRAY n_array) <- S_roots.ALLOCATIONS
$constant_callable_record_valid(S_roots, pconstantclosure_discarded)
$constant_callable_records_valid(S_roots, S_roots.CONSTANTCLOSURES)
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')

def prepare(out):
    names=('SOURCES','FILES','EVALS','PREFIX','CHECKS')
    saved={name:getattr(global_protocol,name) for name in names}
    try:
        for name in names:setattr(global_protocol,name,globals()[name])
        return global_protocol.prepare(out)
    finally:
        for name,value in saved.items():setattr(global_protocol,name,value)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only');parser.add_argument('--output')
    arguments=parser.parse_args()
    out=Path(arguments.prepare_only or arguments.output or str(Path(tempfile.mkdtemp(prefix='global-constant-prebind-',dir=ROOT/'.tools'))/'prepared'))
    if arguments.prepare_only:
        prepare(out)
    else:
        watched=[Path(__file__),Path(global_protocol.__file__)]
        before={str(p):base.sha(p) for p in watched}
        original=base.prepare
        try:
            base.prepare=prepare;base.run(out)
        finally:
            base.prepare=original
        report=json.loads((out/'report.json').read_text())
        report.update(protocol_inputs=before,protocols_unchanged=before=={str(p):base.sha(p) for p in watched})
        if not report['protocols_unchanged']:report['result']='failed'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        assert report['protocols_unchanged'],'protocol changed'
    print(out)

if __name__=='__main__':
    main()
