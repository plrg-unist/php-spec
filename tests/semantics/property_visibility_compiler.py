#!/usr/bin/env python3
"""Protected descriptor admission, exclusions and memoized property write facts."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'protected': ('<?php class A {protected int $x;}', [
        'P.COMPLETION = PPCNORMAL', 'P.CLASSES = [pclassdesc]',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = [120]',
        'ppropertydesc.KEY = [0,42,0,120]', 'ppropertydesc.VISIBILITY = PROPERTY_PROTECTED',
        'ppropertydesc.DEFAULT = PROP_UNINITIALIZED']),
    'widen': ('<?php class A{protected int $x=1;}class B extends A{public int $x=2;}', [
        'P.COMPLETION = PPCNORMAL', 'P.CLASSES = [pclassdesc_a,pclassdesc_b]',
        'pclassdesc_a.PROPERTIES = [ppropertydesc_a]', 'pclassdesc_b.PROPERTIES = [ppropertydesc_b]',
        'ppropertydesc_a.KEY = [0,42,0,120]', 'ppropertydesc_b.KEY = [120]',
        'ppropertydesc_b.VISIBILITY = PROPERTY_PUBLIC']),
    'private-admission': ('<?php class A{private int $x=1;}', ['P.COMPLETION = PPCNORMAL', 'P.CLASSES = [pclassdesc]', 'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.KEY = [0,65,0,120]', 'ppropertydesc.VISIBILITY = PROPERTY_PRIVATE']),
    'static-dependency': ('<?php class A{protected static int $x=1;}', ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "property visibility, static, readonly, or final")']),
    'readonly-dependency': ('<?php class A{protected readonly int $x;}', ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "property visibility, static, readonly, or final")']),
    'asymmetric-dependency': ('<?php class A{public protected(set) int $x=1;}', ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "property visibility, static, readonly, or final")']),
    'hook-dependency': ('<?php class A{protected int $x {get=>1;}}', ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "property attributes, hooks, or members")']),
    'memo-static': ('<?php\n$a->\nx ??=\n4;', [
        'P.COMPLETION = PPCNORMAL', 'P.WRITES = [(([PCINDEX 0,PCFIELD 0,PCFIELD 0]),3)]',
        '(([PCINDEX 0,PCFIELD 0,PCFIELD 0]),PPIS) <- P.ACCESS',
        '(([PCINDEX 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]),PPR) <- P.ACCESS']),
    'memo-computed': ('<?php\n$a->{\nname()\n} ??=\nrhs();', [
        'P.COMPLETION = PPCNORMAL', 'P.WRITES = [(([PCINDEX 0,PCFIELD 0,PCFIELD 0]),3)]',
        '(([PCINDEX 0,PCFIELD 0,PCFIELD 0]),PPIS) <- P.ACCESS',
        '(([PCINDEX 0,PCFIELD 0,PCFIELD 0,PCFIELD 1]),PPR) <- P.ACCESS']),
    'memo-dimension': ('<?php $a->x[0]??=2;', [
        'P.COMPLETION = PPCNORMAL',
        'P.WRITES = [(([PCINDEX 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]),1),(([PCINDEX 0,PCFIELD 0,PCFIELD 0]),1)]']),
}

def main():
    out = Path(tempfile.mkdtemp(prefix='property-visibility-compiler-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records = []
    try:
        for name, (source, checks) in CASES.items():
            original = out / (name + '.php'); original.write_text(source)
            parsed = frontend.request({'op':'parse','source':base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
            lines = ['P = $ppstart(91, ' + checked['fixture'] + ', $ptascii("visibility.php"))', *checks]
            fixture = out / (name + '.watsup')
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in lines))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *map(str,modules), str(fixture)], capture_output=True, text=True, timeout=120)
            (out / (name + '.stdout')).write_text(result.stdout); (out / (name + '.stderr')).write_text(result.stderr)
            (out / (name + '.status.json')).write_text(json.dumps({'exit_status':result.returncode}))
            assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (name,result.stderr[-2200:])
            records.append({'case':name,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'assertions':len(lines)})
            print(name, 'pass', flush=True)
    finally:
        frontend.close(); adapter.close()
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    (out / 'report.json').write_text(json.dumps({'result':'pass','inputs':hashes,'records':records},indent=2)+'\n')
    print(out, len(records), sum(r['assertions'] for r in records))

if __name__ == '__main__':
    main()
