#!/usr/bin/env python3
"""Compiler lookup tails preserve exact opaque payloads and first-match order."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNNER = HERE / '_build/default/numeric_runner.exe'
MODULES = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]

# Exact pre-optimization definitions, with function names renamed only.
OLD = '''dec $old_ppconstant_at((pcpath, pvalue)*, pcpath) : pvalue?
def $old_ppconstant_at(eps, pcpath) = eps
def $old_ppconstant_at((pcpath, pvalue) :: (pcpath_tail, pvalue_tail)*, pcpath) = (pvalue)
def $old_ppconstant_at((pcpath_other, pvalue) :: (pcpath_tail, pvalue_tail)*, pcpath) = $old_ppconstant_at((pcpath_tail, pvalue_tail)*, pcpath)
  -- if pcpath_other =/= pcpath
dec $old_pfclass_at((pcpath, pvalueclass)*, pcpath) : pvalueclass?
def $old_pfclass_at(eps, pcpath) = eps
def $old_pfclass_at((pcpath, pvalueclass) :: (pcpath_tail, pvalueclass_tail)*, pcpath) = (pvalueclass)
def $old_pfclass_at((pcpath_other, pvalueclass) :: (pcpath_tail, pvalueclass_tail)*, pcpath) = $old_pfclass_at((pcpath_tail, pvalueclass_tail)*, pcpath)
  -- if pcpath_other =/= pcpath
dec $old_ppput(ppconstants, pcpath, pvalue) : ppconstants
dec $old_ppput_result((pcpath, pvalue)*, pcpath, pvalue, pvalue?) : ppconstants
def $old_ppput(PPCINVALID text, pcpath, pvalue) = PPCINVALID text
def $old_ppput(PPCCONSTANTS (pcpath_old, pvalue_old)*, pcpath, pvalue) = $old_ppput_result((pcpath_old, pvalue_old)*, pcpath, pvalue, $old_ppconstant_at((pcpath_old, pvalue_old)*, pcpath))
def $old_ppput_result((pcpath_old, pvalue_old)*, pcpath, pvalue, pvalue_found?) = PPCCONSTANTS ((pcpath_old, pvalue_old)* ++ [(pcpath, pvalue)])
  -- if pvalue_found? = eps
def $old_ppput_result((pcpath_old, pvalue_old)*, pcpath, pvalue, pvalue_found?) = PPCCONSTANTS (pcpath_old, pvalue_old)*
  -- if pvalue_found? = (pvalue)
def $old_ppput_result((pcpath_old, pvalue_old)*, pcpath, pvalue, pvalue_found?) = PPCINVALID "conflicting constant values for one source occurrence"
  -- if pvalue_found? = (pvalue_existing)
  -- if pvalue_existing =/= pvalue
'''


def table(rows):
    return '[' + ','.join(f'({path},{value})' for path, value in rows) + ']'


def vectors():
    values = ['PNULL', 'PBOOL false', 'PBOOL true', 'PINT $(-7)',
              'PINT 1180591620717411303424', 'PINT $(-1180591620717411303424)',
              'PFLOAT 0', 'PFLOAT 9223372036854775808', 'PFLOAT 9221120237041090561',
              'PFLOAT 1267650600228229401496703205376',
              'PSTRING ([0,255,999])', 'PARRAY 17', 'POBJECT 23']
    classes = ['PVSCALAR', 'PVSTRING true', 'PVSTRING false', 'PVOBJECT',
               'PVCLOSURE 17 (PORIGIN 3 [PCFIELD 9])',
               'PVINSTANCE 19 (PORIGIN 4 [PCINDEX 2])',
               'PVSTDCLASS 23 (PORIGIN 5 eps)', 'PVENUMCASE 29 (PORIGIN 6 [PCFIELD 1])',
               'PVARRAY true ([(KINT $(-3),PVSTRING true),(KSTRING ([0,999]),PVARRAY false ([(KINT 8,PVOBJECT)]))])']
    result = []
    for helper, payloads in [('ppconstant_at', values), ('pfclass_at', classes)]:
        result.append((helper, 'eps', 'eps', 'eps'))
        rows = [(f'[PCFIELD 0,PCINDEX {index}]', value) for index, value in enumerate(payloads)]
        for path, value in rows:
            result.append((helper, table(rows), path, f'({value})'))
        result.append((helper, table(rows), '[PCFIELD 0,PCINDEX 999]', 'eps'))
        prefix = [('eps', payloads[0]), ('[PCFIELD 1]', payloads[1]),
                  ('[PCFIELD 1,PCINDEX 0]', payloads[2]), ('[PCINDEX 1]', payloads[3])]
        for path, value in prefix:
            result.append((helper, table(prefix), path, f'({value})'))
        duplicate = [('[PCFIELD 8]', payloads[0]), ('[PCFIELD 8]', payloads[-1])]
        result.append((helper, table(duplicate), '[PCFIELD 8]', f'({payloads[0]})'))
        duplicate[-1] = duplicate[0]
        result.append((helper, table(duplicate), '[PCFIELD 8]', f'({payloads[0]})'))
        deep = '[' + ','.join(['PCFIELD 2', 'PCINDEX 3'] * 32) + ']'
        result.append((helper, table([(deep, payloads[-1])]), deep, f'({payloads[-1]})'))
        long = [(f'[PCINDEX {index}]', payloads[index % len(payloads)]) for index in range(129)]
        for index in (0, 64, 128):
            result.append((helper, table(long), f'[PCINDEX {index}]', f'({long[index][1]})'))
        result.append((helper, table(long), '[PCINDEX 129]', 'eps'))
    return result


def run(output):
    output = Path(output)
    output.mkdir()
    watched = [*MODULES, ROOT / 'spec/semantics/modules.json', Path(__file__), RUNNER]
    hashes = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = hashes()
    rows, checks = vectors(), []
    for helper, entries, query, expected in rows:
        checks.extend([f'${helper}({entries},{query}) = $old_{helper}({entries},{query})',
                       f'${helper}({entries},{query}) = {expected}'])
    entries = '[([PCFIELD 0],PINT 7),([PCFIELD 0],PINT 8)]'
    for initial, query, value, expected in [
        ('PPCCONSTANTS eps', '[PCFIELD 0]', 'PINT 7', 'PPCCONSTANTS ([([PCFIELD 0],PINT 7)])'),
        (f'PPCCONSTANTS ({entries})', '[PCFIELD 0]', 'PINT 7', f'PPCCONSTANTS ({entries})'),
        (f'PPCCONSTANTS ({entries})', '[PCFIELD 0]', 'PINT 8', 'PPCINVALID "conflicting constant values for one source occurrence"'),
        (f'PPCCONSTANTS ({entries})', '[PCFIELD 1]', 'PARRAY 31', 'PPCCONSTANTS ([([PCFIELD 0],PINT 7),([PCFIELD 0],PINT 8),([PCFIELD 1],PARRAY 31)])'),
        ('PPCINVALID "retained"', 'eps', 'PFLOAT 0', 'PPCINVALID "retained"'),
    ]:
        checks.extend([f'$ppput({initial},{query},{value}) = $old_ppput({initial},{query},{value})',
                       f'$ppput({initial},{query},{value}) = {expected}'])
    fixture = output / 'test.watsup'
    fixture.write_text(OLD + '\ndec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    (output / 'vectors.json').write_text(json.dumps(rows, indent=2) + '\n')
    command = [str(RUNNER), '--sl', *map(str, MODULES), str(fixture)]
    (output / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
    environment = {**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'}
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, timeout=300)
    (output / 'stdout').write_bytes(result.stdout)
    (output / 'stderr').write_bytes(result.stderr)
    after = hashes()
    report = dict(mode='pure compiler lookup SL_mode', module_count=len(MODULES),
                  source_credit=0, native_executions=0, lookup_cases=len(rows), put_cases=5,
                  equalities=len(checks), per_fixture_cap=300, elapsed_seconds=time.monotonic()-start,
                  exit=result.returncode, stable=before == after, inputs_before=before, inputs_after=after,
                  pass_all=before == after and result.returncode == 0 and result.stdout == b'true\n' and not result.stderr)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['pass_all'], output / 'report.json'
    print(json.dumps({key: value for key, value in report.items() if not key.startswith('inputs_')}))


if __name__ == '__main__':
    run(Path(tempfile.mkdtemp(prefix='compiler-lookup-tails-', dir=ROOT / '.tools')) / 'run')
