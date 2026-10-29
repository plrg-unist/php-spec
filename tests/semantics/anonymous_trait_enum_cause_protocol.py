#!/usr/bin/env python3
"""Independent mixed later-unit identity, trait import and first-NEW retry."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_trait_enum_cases.json'
SOURCE_SHA = '98de477d00301e43d6a161a74cb441588f242d48723a5054d72906e6891a64b1'

PREFIX = r"""
dec $review_mix_is_output(pevent) : bool
def $review_mix_is_output(OUTPUT ptbytes) = true
def $review_mix_is_output(pevent) = false -- otherwise
dec $review_mix_output(pevent*) : ptbytes
def $review_mix_output(eps) = eps
def $review_mix_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_mix_output(pevent*)
def $review_mix_output(pevent :: pevent_tail*) = $review_mix_output(pevent_tail*)
  -- if ~$review_mix_is_output(pevent)
dec $review_mix_front(pstate) : bool
def $review_mix_front(S) = true
  -- if S.ORIGIN = (PORIGIN 1 pcpath)
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if $origin_node(S.SOURCES,PORIGIN 1 pcpath) = (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata_class) = 17
def $review_mix_front(S) = false -- otherwise
dec $review_mix_phase(pstate,nat) : bool
def $review_mix_phase(S,0) = $review_mix_front(S)
def $review_mix_phase(S,1) = ($review_mix_output(S.EVENTS) = $ptascii("arg|caught|"))
def $review_mix_phase(S,2) = true
  -- if $review_mix_output(S.EVENTS) = $ptascii("arg|caught|arg|")
  -- if S.CURRENT = (pcallcontext)
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
def $review_mix_phase(S,n) = false -- otherwise
dec $review_mix_seek(pstate,nat,nat) : pstate
def $review_mix_seek(S,n_mode,n) = S -- if $review_mix_phase(S,n_mode)
def $review_mix_seek(S,n_mode,0) = S -- if ~$review_mix_phase(S,n_mode)
def $review_mix_seek(S,n_mode,n) = $review_mix_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$review_mix_phase(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $review_mix_seek(S,n_mode,n) = S -- otherwise
dec $review_mix_receipt(pdeclaration,porigin) : bool
def $review_mix_receipt(PDRCLASS porigin pdeclcause,porigin) = true
def $review_mix_receipt(pdeclaration,porigin) = false -- otherwise
dec $review_mix_bit(bool) : nat
def $review_mix_bit(true) = 1
def $review_mix_bit(false) = 0
dec $review_mix_count(pdeclaration*,porigin) : nat
def $review_mix_count(eps,porigin) = 0
def $review_mix_count(pdeclaration :: pdeclaration_tail*,porigin) = $($review_mix_bit($review_mix_receipt(pdeclaration,porigin)) + $review_mix_count(pdeclaration_tail*,porigin))
dec $review_mix_function(pfunction*,ptbytes) : porigin?
def $review_mix_function(eps,ptbytes) = eps
def $review_mix_function(pfunction :: pfunction_tail*,ptbytes) = (pfunction.ORIGIN)
  -- if pfunction.NAME = ptbytes
def $review_mix_function(pfunction :: pfunction_tail*,ptbytes) = $review_mix_function(pfunction_tail*,ptbytes)
  -- if pfunction.NAME =/= ptbytes
dec $review_mix_first_function(pdeclcalls) : porigin
def $review_mix_first_function((porigin_function,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail) = porigin_function
dec $review_mix_wrong_function(pdeclcalls,porigin) : pdeclcalls
def $review_mix_wrong_function((porigin_function,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail,porigin_wrong) = (porigin_wrong,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail
dec $review_mix_replace(pclassdesc*,pclassdesc) : pclassdesc*
def $review_mix_replace(eps,pclassdesc_new) = eps
def $review_mix_replace(pclassdesc :: pclassdesc_tail*,pclassdesc_new) = pclassdesc_new :: pclassdesc_tail*
  -- if pclassdesc.ORIGIN = pclassdesc_new.ORIGIN
def $review_mix_replace(pclassdesc :: pclassdesc_tail*,pclassdesc_new) = pclassdesc :: $review_mix_replace(pclassdesc_tail*,pclassdesc_new)
  -- if pclassdesc.ORIGIN =/= pclassdesc_new.ORIGIN
dec $review_mix_cache_item(pclassconstantevent,porigin) : bool
def $review_mix_cache_item(CCCACHE porigin porigin_trigger n,porigin) = true
def $review_mix_cache_item(pclassconstantevent,porigin) = false -- otherwise
dec $review_mix_cached(pclassconstantevent*,porigin) : bool
def $review_mix_cached(eps,porigin) = false
def $review_mix_cached(pclassconstantevent :: pclassconstantevent_tail*,porigin) = ($review_mix_cache_item(pclassconstantevent,porigin) \/ $review_mix_cached(pclassconstantevent_tail*,porigin))
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    mixed_file = filename + b"(8) : eval()'d code"
    tail_file = filename + b"(31) : eval()'d code"
    name = b'Later150Review\\Parent150Review@anonymous\0' + mixed_file + b':17$2'
    tail_name = b'class@anonymous\0' + tail_file + b':1$3'
    base = term(b'Root150Review\\Base150Review')
    mix = term(b'Later150Review\\Mix150Review')
    enum = term(b'Later150Review\\Choice150Review')
    parent = term(b'Later150Review\\Parent150Review')
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait.EVALCONTEXTS,1) = (pevalcontext)',
        'pevalcontext.BYTES = ' + term(codes[0]),
        'pevalcontext.FILE = ' + term(mixed_file),
        '$eval_response_valid(S_wait,' + responses[0] + ')',
        'S_body = $eval_resume(S_wait,' + responses[0] + ')',
        'S_body.COMPLETION = NORMAL',
        'S_front_raw = $review_mix_seek(S_body,0,4096)',
        r'S_front_raw.COMPLETION = NORMAL \/ S_front_raw.COMPLETION = BUDGET',
        'S_front = S_front_raw[.COMPLETION = NORMAL]',
        '$review_mix_front(S_front)',
        'S_front.ORIGIN = (PORIGIN 1 pcpath_new)',
        '$anonymous_new_pending(S_front,PORIGIN 1 pcpath_new) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN 1 (pcpath_new ++ [PCFIELD 0])',
        'pclassdesc.NAME = ' + term(name),
        '~pclassdesc.EARLY',
        '$anonymous_history_seed(S_front,1) = (0)',
        '$source_unit(S_front.SOURCES,1) = (pcunit_mixed)',
        '$class_constant_compile_entry(S_front,1) = (S_entry)',
        '$class_named(S_entry.CLASSNAMES,$ptlc(' + base + ')) = (porigin_base)',
        '$class_named(S_entry.CLASSNAMES,$ptlc(' + mix + ')) = eps',
        '$class_named(S_entry.CLASSNAMES,$ptlc(' + enum + ')) = eps',
        '$class_named(S_front.CLASSNAMES,$ptlc(' + mix + ')) = (porigin_mix)',
        '$class_named(S_front.CLASSNAMES,$ptlc(' + enum + ')) = (porigin_enum)',
        '$class_named(S_front.CLASSNAMES,$ptlc(' + parent + ')) = (porigin_parent)',
        '$class_at(S_front.CLASSES,porigin_mix) = (pclassdesc_mix)',
        'pclassdesc_mix.KIND = "trait"',
        'pclassdesc_mix.EARLY',
        'pclassdesc_mix.INTERFACES = eps',
        '$class_at(S_front.CLASSES,porigin_enum) = (pclassdesc_enum)',
        'pclassdesc_enum.KIND = "enum"',
        '~pclassdesc_enum.EARLY',
        'pclassdesc_enum.INTERFACES = [$ptascii("UnitEnum"),$ptascii("BackedEnum")]',
        '$class_at(S_front.CLASSES,porigin_parent) = (pclassdesc_parent)',
        '~pclassdesc_parent.EARLY',
        '$class_link_at(S_front.LINKEDPARENTS,porigin_parent) = (SOURCE_PARENT porigin_base)',
        '$method_named(pclassdesc_mix.METHODS,$ptascii("read")) = (pmethoddesc_source)',
        '$effective_method(S_front,porigin_parent,$ptascii("read"),64) = (pmethoddesc_read)',
        'pmethoddesc_read.OWNER = porigin_parent',
        'pmethoddesc_read.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_parent pmethoddesc_source.FUNCTION.ORIGIN ($ptascii("read"))',
        '$compilation_projection(S_front,pcunit_mixed) = (ppinstalled_mixed)',
        '$anonymous_compiled_class_count(pcunit_mixed,' + term(mixed_file) + ',ppinstalled_mixed.CLASSES,eps,(S_entry),0) = (3)',
        '$anonymous_compiled_class_count(pcunit_mixed,' + term(mixed_file) + ',$review_mix_replace(ppinstalled_mixed.CLASSES,pclassdesc_mix[.EARLY = false]),eps,(S_entry),0) = eps',
        '$anonymous_compiled_class_count(pcunit_mixed,' + term(mixed_file) + ',$review_mix_replace(ppinstalled_mixed.CLASSES,pclassdesc_enum[.EARLY = true]),eps,(S_entry),0) = eps',
        '$anonymous_compiled_class_count(pcunit_mixed,' + term(mixed_file) + ',$review_mix_replace(ppinstalled_mixed.CLASSES,pclassdesc_enum[.KIND = "interface"][.INTERFACES = eps]),eps,(S_entry),0) = eps',
        '$anonymous_compiled_class_count(pcunit_mixed,' + term(mixed_file) + ',$review_mix_replace(ppinstalled_mixed.CLASSES,pclassdesc_enum[.INTERFACES = [$ptascii("UnitEnum")]]),eps,(S_entry),0) = eps',
        '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$review_mix_count(S_front.DECLARATIONS,pclassdesc.ORIGIN) = 0',
        'S_front.CURRENT = (pcallcontext_factory)',
        'pcallcontext_factory.FUNCTION = PORIGIN 1 pcpath_factory',
        'pcallcontext_factory.LEXICAL_CLASS = eps',
        'pcallcontext_factory.CALLED_CLASS = eps',
        '$call_descriptors_valid(S_front)',
        '$class_state_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
        'pdeclcause = $declaration_cause(S_front)',
        'pdeclcause.UNIT = 1',
        'pdeclcause.AUTOLOAD = eps',
        '|pdeclcause.CALLS| = 1',
        '$review_mix_first_function(pdeclcause.CALLS) = pcallcontext_factory.FUNCTION',
        '$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause)',
        '~$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause[.UNIT = 0])',
        '$review_mix_function($all_functions(S_front),' + term(b'Later150Review\\argument150Review') + ') = (porigin_wrong)',
        '$function_at($all_functions(S_front),porigin_wrong) = (pfunction_wrong)',
        '$declaration_callable_available(S_front,pfunction_wrong,|S_front.DECLARATIONS|)',
        '~$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause[.CALLS = $review_mix_wrong_function(pdeclcause.CALLS,porigin_wrong)])',
        'S_linked_raw = $drive_steps(S_front,1)',
        r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
        'S_linked = S_linked_raw[.COMPLETION = NORMAL]',
        'S_linked.ORIGIN = S_front.ORIGIN',
        'S_linked.TODO = S_front.TODO',
        'S_linked.EVENTS = S_front.EVENTS',
        'S_linked.OBJECTS = S_front.OBJECTS',
        'S_linked.OBJECTPROPS = S_front.OBJECTPROPS',
        'S_linked.ALLOCATIONS = S_front.ALLOCATIONS',
        'S_linked.DECLARATIONS = S_front.DECLARATIONS ++ [PDRCLASS pclassdesc.ORIGIN pdeclcause]',
        '$class_named(S_linked.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$class_link_at(S_linked.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_parent)',
        '$anonymous_new_pending(S_linked,PORIGIN 1 pcpath_new) = eps',
        'S_caught_raw = $review_mix_seek(S_linked,1,4096)',
        r'S_caught_raw.COMPLETION = NORMAL \/ S_caught_raw.COMPLETION = BUDGET',
        'S_caught = S_caught_raw[.COMPLETION = NORMAL]',
        '$review_mix_phase(S_caught,1)',
        'S_caught.DECLARATIONS = S_linked.DECLARATIONS',
        '$class_named(S_caught.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$enum_case_origins(S_caught,pclassdesc_enum.CONSTANTS) = [porigin_case]',
        '$default_cache_at(S_caught.CLASSCONSTANTCACHE,porigin_case) = eps',
        'S_retry_raw = $review_mix_seek(S_caught,0,4096)',
        r'S_retry_raw.COMPLETION = NORMAL \/ S_retry_raw.COMPLETION = BUDGET',
        'S_retry = S_retry_raw[.COMPLETION = NORMAL]',
        'S_retry.ORIGIN = (PORIGIN 1 pcpath_new)',
        '$anonymous_new_name(S_retry,PORIGIN 1 pcpath_new) = (pclassdesc.NAME)',
        '$anonymous_new_pending(S_retry,PORIGIN 1 pcpath_new) = eps',
        'S_retry.DECLARATIONS = S_linked.DECLARATIONS',
        'S_ctor_raw = $review_mix_seek(S_retry,2,4096)',
        r'S_ctor_raw.COMPLETION = NORMAL \/ S_ctor_raw.COMPLETION = BUDGET',
        'S_ctor = S_ctor_raw[.COMPLETION = NORMAL]',
        '$review_mix_phase(S_ctor,2)',
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'pcallcontext_ctor.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_ctor.CALLED_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext_ctor.CALLSITE = (PORIGIN 1 pcpath_new)',
        'S_cached = $drive_steps(S_ctor,4096)',
        'S_cached.COMPLETION = SOURCE_PENDING',
        '$default_cache_at(S_cached.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
        'pdefaultcache_case.VALUE = POBJECT n_case',
        '$review_mix_cached(S_cached.CLASSCONSTANTHISTORY,porigin_case)',
        '$location_slot(S_cached,PROPERTY n_case $ptascii("value")) = DEFINED (PINT 11)',
        '$eval_context_at(S_cached.EVALCONTEXTS,2) = (pevalcontext_tail)',
        'pevalcontext_tail.BYTES = ' + term(codes[1]),
        'pevalcontext_tail.FILE = ' + term(tail_file),
        '$eval_response_valid(S_cached,' + responses[1] + ')',
        'S_tail = $eval_resume(S_cached,' + responses[1] + ')',
        'S_tail.COMPLETION = NORMAL',
        '$anonymous_history_seed(S_tail,2) = (3)',
        '$class_constant_compile_entry(S_tail,2) = (S_entry_tail)',
        '$default_cache_at(S_entry_tail.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
        '$class_named(S_entry_tail.CLASSNAMES,$ptlc(' + term(tail_name) + ')) = eps',
        '$class_named(S_tail.CLASSNAMES,$ptlc(' + term(tail_name) + ')) = (porigin_tail)',
        '$class_at(S_tail.CLASSES,porigin_tail) = (pclassdesc_tail)',
        'pclassdesc_tail.EARLY',
        '$declaration_unit_complete(S_tail.DECLARATIONS,1)',
        '$declaration_unit_complete(S_tail.DECLARATIONS,2)',
        'S_done = $drive_steps(S_tail,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$review_mix_output(S_done.EVENTS) = ' + term(stdout),
        '$review_mix_count(S_done.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$review_mix_count(S_done.DECLARATIONS,porigin_tail) = 0',
        '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-trait-enum-cause-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row['stdout_template_base64'] if 'stdout_template_base64' in row else row['stdout_base64']).replace(b'{FILE}', os.fsencode(source))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__), source,
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'source_sha256': SOURCE_SHA, 'inputs_before': before, 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        codes, responses = [], []
        for unit, prefix in [(1, b'namespace Later150Review;'), (2, b'$tail = new class {};')]:
            code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                     if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(prefix)]
            codes.append(code)
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval',
                                            'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
            assert parsed_eval['accepted'] is True
            checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
            assert checked_eval['ok'] is True
            responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(code) + ' ' + checked_eval['fixture'])
        checks = assertions(checked['fixture'], os.fsencode(source), stdout, codes, responses)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), fixture_sha256=sha(fixture))
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
