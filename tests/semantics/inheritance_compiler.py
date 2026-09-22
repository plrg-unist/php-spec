#!/usr/bin/env python3
"""Focused class-parent lowering, early-link phase and keyword-line controls."""
from pathlib import Path
import base64
import copy
import json
import subprocess
import sys
import tempfile
from recorded_worker import Worker


ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'early': b'<?php\nclass A {}\nclass B extends A {}\n',
    'forward': b'<?php\nclass B extends A {}\nclass A {}\n',
    'conditional': b'<?php\nif (true) { class A {} }\nclass B extends A {}\n',
    'stdclass': b'<?php\nclass B extends stdClass {}\n',
    'abstract': b'<?php\nabstract class A {}\nclass B extends A {}\n',
    'missing': b'<?php\nclass B extends Missing {}\n',
    'final_early': b'<?php\nfinal class A {}\nclass B extends A {}\n',
    'final_forward': b'<?php\nclass B extends A {}\nfinal class A {}\n',
    'readonly_early': b'<?php\nclass A {}\nreadonly\nclass B extends A {}\n',
    'readonly_forward': b'<?php\nreadonly\nclass B extends A {}\nclass A {}\n',
    'interface': b'<?php\nclass B extends Iterator {}\n',
    'enum': b'<?php\nclass B extends RoundingMode {}\n',
    'closure': b'<?php\nclass B extends Closure {}\n',
    'engine_final': b'<?php\nclass B extends Random\\Engine\\Xoshiro256StarStar {}\n',
    'internal_other': b'<?php\nclass B extends DateTime {}\n',
    'duplicate': b'<?php\nclass B {}\nclass B extends Iterator {}\n',
    'split_keyword': b'<?php\nclass A {}\nreadonly\nclass\nB extends A {}\n',
}


def main():
    out = Path(tempfile.mkdtemp(prefix='inherit-compiler-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        fixtures = {}
        asts = {}
        for name, source in SOURCES.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            fixtures[name] = checked['fixture']
            asts[name] = parsed['ast']
        for name, changed in [('missing_fact', None), ('bad_fact', 99)]:
            ast = copy.deepcopy(asts['split_keyword'])
            node = ast['program'][1]
            assert node['node'] == 'Stmt_Class'
            if changed is None:
                del node['meta']['classKeywordLine']
            else:
                node['meta']['classKeywordLine'] = {'int': str(changed)}
            checked = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})
            assert checked['ok'], (name, checked)
            fixtures[name] = checked['fixture']
        fact = '(MclassKeywordLine (4))'
        assert fixtures['split_keyword'].count(fact) == 1
        fixtures['duplicate_fact'] = fixtures['split_keyword'].replace(fact, fact + ', ' + fact)
        filename = '[' + ','.join(map(str, str(out / 'source.php').encode())) + ']'
        checks_by_case = {name: [] for name in fixtures}
        normal = ['early', 'forward', 'conditional', 'stdclass', 'abstract',
                  'missing', 'final_forward', 'readonly_forward', 'duplicate']
        for name in normal:
            checks_by_case[name] += [f'P_{name} = $ppstart(91, {fixtures[name]}, n_file*)',
                                     f'P_{name}.COMPLETION = PPCNORMAL']
        extra = [
            'P_early.CLASSES = [pclassdesc_a,pclassdesc_early]',
            'pclassdesc_early.PARENT = ($ptascii("A"))',
            'pclassdesc_early.EARLY',
            'pclassdesc_early.LINE = 3',
            'P_forward.CLASSES = [pclassdesc_forward,pclassdesc_forward_a]',
            'pclassdesc_forward.PARENT = ($ptascii("A"))',
            '~pclassdesc_forward.EARLY',
            'P_conditional.CLASSES = [pclassdesc_conditional_a,pclassdesc_conditional]',
            '~pclassdesc_conditional.EARLY',
            'P_stdclass.CLASSES = [pclassdesc_stdclass]',
            'pclassdesc_stdclass.PARENT = ($ptascii("stdClass"))',
            'pclassdesc_stdclass.EARLY',
            'P_abstract.CLASSES = [pclassdesc_abstract_parent,pclassdesc_abstract_child]',
            'pclassdesc_abstract_parent.ABSTRACT',
            '~pclassdesc_abstract_child.ABSTRACT',
            'pclassdesc_abstract_child.EARLY',
            'P_missing.CLASSES = [pclassdesc_missing]',
            '~pclassdesc_missing.EARLY',
            '~$class_internal_final($ptascii("DateTime"))',
            '$class_internal_final($ptascii("Closure"))',
            '$class_internal_final($ptascii("Random") ++ [92] ++ $ptascii("Engine") ++ [92] ++ $ptascii("Xoshiro256StarStar"))',
        ]
        for check in extra:
            for name in normal:
                if f'P_{name}.' in check or f'pclassdesc_{name}' in check:
                    checks_by_case[name].append(check)
                    break
            else:
                checks_by_case['early'].append(check)
        errors = {
            'final_early': ('Class B cannot extend final class A', 3),
            'readonly_early': ('Readonly class B cannot extend non-readonly class A', 4),
            'split_keyword': ('Readonly class B cannot extend non-readonly class A', 4),
            'interface': ('Class B cannot extend interface Iterator', 2),
            'enum': ('Class B cannot extend enum RoundingMode', 2),
            'closure': ('Class B cannot extend final class Closure', 2),
            'engine_final': ('Class B cannot extend final class Random\\Engine\\Xoshiro256StarStar', 2),
        }
        for name, (message, line) in errors.items():
            checks_by_case[name] += [f'P_{name} = $ppstart(91, {fixtures[name]}, n_file*)',
                                     f'P_{name}.COMPLETION = PPCABRUPT (STATICBYTES $ptascii("{message.replace(chr(92), chr(92) * 2)}") {line})']
        checks_by_case['internal_other'] += [f'P_internal_other = $ppstart(91, {fixtures["internal_other"]}, n_file*)',
                                             'P_internal_other.COMPLETION = PPCABRUPT (UNSUPPORTED "internal class inheritance")']
        for name in ('missing_fact', 'bad_fact', 'duplicate_fact'):
            checks_by_case[name] += [f'P_{name} = $ppstart(91, {fixtures[name]}, n_file*)',
                                     f'P_{name}.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")']
        modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        count = 0
        for name, assertions in checks_by_case.items():
            if len(sys.argv) > 1 and name not in sys.argv[1:]:
                continue
            fixture = out / f'{name}.watsup'
            checks = [f'n_file* = {filename}', *assertions]
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + check + '\n' for check in checks))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *modules, str(fixture)], capture_output=True, text=True, timeout=120)
            (out / f'{name}.stdout').write_text(result.stdout)
            (out / f'{name}.stderr').write_text(result.stderr)
            assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (name, result.stderr)
            count += len(checks)
        print(f'PASS inheritance compiler: {count} assertions', out)
    finally:
        frontend.close()
        adapter.close()


if __name__ == '__main__':
    main()
