#!/usr/bin/env python3
"""User constant compiler phases and original declaration descriptors."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types
import source_compiler as compiler
import source_context as context

ROOT = Path(__file__).resolve().parents[2]
CASES = {'int': '<?php const C=1;', 'quoted-empty': "<?php const C='';", 'quoted-one': "<?php const C='a';", 'quoted-long': "<?php const C='abc';", 'quoted-escaped-one': '<?php const C="\\x61";', 'quoted-binary-one': "<?php const C=b'a';", 'concat': "<?php const C='a'.'b';", 'concat-left-empty': "<?php const C=(~'').' ';", 'bitnot-empty': "<?php const C=~'';", 'bitnot-one': "<?php const C=~'a';", 'bitand-one': "<?php const C='a'&'b';", 'bitand-long': "<?php const C='a'&'bc';", 'empty-array': '<?php const C=[];', 'array-one': "<?php const C=['abc'];", 'array-duplicate': "<?php const C=[0=>'abc',0=>'a'];", 'array-negative': "<?php const C=[-3=>'abc','a'];", 'array-spread-empty': '<?php const C=[...[]];', 'array-spread': "<?php const C=[-3=>'abc',...['a','z'=>'abc']];", 'array-union': '<?php const C=[]+[];', 'cast-null': '<?php const C=(array)null;', 'cast-array': '<?php const C=(array)[];', 'cast-int': '<?php const C=(string)1;', 'cast-float': '<?php const C=(string)1.0;', 'dimension': "<?php const C=['abc'][0];", 'string-dimension': "<?php const C='abc'[0];", 'ternary': "<?php const C=true?'abc':UNKNOWN;", 'coalesce': "<?php const C='abc'??UNKNOWN;", 'heredoc-one': '<?php const C=<<<E\na\nE;', 'heredoc-escaped': '<?php const C=<<<E\n\\x61\nE;', 'nowdoc-empty': "<?php const C=<<<'E'\nE;", 'nowdoc-blank': "<?php const C=<<<'E'\n\nE;", 'nowdoc-one': "<?php const C=<<<'E'\na\nE;", 'magic-file': '<?php const C=__FILE__;', 'magic-dir': '<?php const C=__DIR__;', 'magic-namespace': '<?php const C=__NAMESPACE__;', 'deferred-conditional': "<?php const C=UNKNOWN?'abc':'';", 'deferred-array': "<?php const C=['abc',UNKNOWN];", 'deferred-folded-array': "<?php const C=[['abc'],UNKNOWN];", 'deferred-warning': "<?php const C=1+'2a';", 'deferred-missing-dimension': '<?php const C=[1][9];'}
CONTEXTS = {'int': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSCALAR)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSCALAR)'], 'quoted-empty': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'quoted-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'quoted-long': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'quoted-escaped-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'quoted-binary-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'concat': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'concat-left-empty': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'bitnot-empty': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'bitnot-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'bitand-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'bitand-long': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'empty-array': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY true eps)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY true eps)'], 'array-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY false ([(KINT 0, PVSTRING false)]))', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY false ([(KINT 0, PVSTRING false)]))'], 'array-duplicate': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY false ([(KINT 0, PVSTRING true)]))', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY false ([(KINT 0, PVSTRING true)]))'], 'array-negative': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY false ([(KINT $(-3), PVSTRING false),(KINT $(-2), PVSTRING true)]))', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY false ([(KINT $(-3), PVSTRING false),(KINT $(-2), PVSTRING true)]))'], 'array-spread-empty': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY false eps)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY false eps)'], 'array-spread': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY false ([(KINT $(-3), PVSTRING false),(KINT $(-2), PVSTRING true),(KSTRING ([122]), PVSTRING false)]))', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY false ([(KINT $(-3), PVSTRING false),(KINT $(-2), PVSTRING true),(KSTRING ([122]), PVSTRING false)]))'], 'array-union': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY false eps)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY false eps)'], 'cast-null': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY false eps)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY false eps)'], 'cast-array': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVARRAY true eps)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVARRAY true eps)'], 'cast-int': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'cast-float': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = eps', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value ++ [PCFIELD 0]) = (PVSCALAR)'], 'dimension': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'string-dimension': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'ternary': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'coalesce': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'heredoc-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'heredoc-escaped': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'nowdoc-empty': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'nowdoc-blank': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'nowdoc-one': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'magic-file': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'magic-dir': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING false)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING false)'], 'magic-namespace': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = (PVSTRING true)', '$constant_class_at($export_classes(P.FOLD.CLASSFACTS), pcpath_value) = (PVSTRING true)'], 'deferred-conditional': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = eps', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value ++ [PCFIELD 1]) = (PVSTRING false)'], 'deferred-array': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = eps', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value ++ [PCFIELD 0,PCINDEX 0,PCFIELD 1]) = (PVSTRING false)'], 'deferred-folded-array': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = eps', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value ++ [PCFIELD 0,PCINDEX 0,PCFIELD 1]) = (PVARRAY false ([(KINT 0, PVSTRING false)]))'], 'deferred-warning': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = eps', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value ++ [PCFIELD 1]) = (PVSTRING false)'], 'deferred-missing-dimension': ['pcpath_value = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value) = eps', '$pfclass_at(P.FOLD.CLASSFACTS, pcpath_value ++ [PCFIELD 0]) = (PVARRAY false ([(KINT 0, PVSCALAR)]))']}
PENDING = {}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/user_constant_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='constant-class-compiler-', dir=ROOT / '.tools'))
    print(out, flush=True)

    def run(command, label):
        (out / (label + '.command.json')).write_text(json.dumps(command) + '\n')
        try:
            result = subprocess.run(command, capture_output=True, env=types.ENV, timeout=60)
        except subprocess.TimeoutExpired as error:
            (out / (label + '.stdout')).write_bytes(error.stdout or b'')
            (out / (label + '.stderr')).write_bytes(error.stderr or b'')
            (out / (label + '.status.json')).write_text(json.dumps({'status': 'timeout'}))
            raise
        (out / (label + '.stdout')).write_bytes(result.stdout)
        (out / (label + '.stderr')).write_bytes(result.stderr)
        (out / (label + '.status.json')).write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
        return result

    frontend = types.Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')])
    adapter = types.Worker([str(adapter_path), str(ROOT)])
    records, assertions = [], []
    try:
        for index, (name, source) in enumerate(CASES.items()):
            file = out / (name + '.php')
            file.write_bytes(source.encode())
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            native = run([str(types.PHP), '-n', *types.FLAGS, '-l', str(file)], name)
            assert native.returncode in (0, 255), native
            events = context.events(native)
            record = {'name': name, 'source_base64': base64.b64encode(source.encode()).decode(),
                      'checked': checked, 'lint_exit': native.returncode, 'events': events}
            records.append(record)
            (out / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
            body = f'  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n'
            if name not in PENDING:
                body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if name in PENDING:
                body += '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(PENDING[name])+')\n'
            elif native.returncode == 0:
                body += '  -- if P.COMPLETION = PPCNORMAL\n'
                body += ''.join('  -- if '+condition+'\n' for condition in CONTEXTS.get(name, []))
            assertions.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n' + body)
            (out / (name + '.state.watsup')).write_text(f'dec $main() : ppstate\ndef $main() = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n')
        fixture = out / 'compiler.watsup'
        fixture.write_text(compiler.PREFIX + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout.strip() == b'true' and not result.stderr, result
    finally:
        frontend.close()
        adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Source-backed class descriptor assertions alongside native compiler phases; no native allocation observation or default execution claim.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/constant-class-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
