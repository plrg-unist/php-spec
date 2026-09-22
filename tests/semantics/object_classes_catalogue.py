#!/usr/bin/env python3
"""Check the pinned internal class-name occupancy against the local PHP CLI."""
from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CODE = '''
$rows=[];
foreach (["class"=>get_declared_classes(), "interface"=>get_declared_interfaces(), "trait"=>get_declared_traits()] as $kind=>$names) {
  foreach ($names as $name) {
    $actual=$kind==="class" && (new ReflectionClass($name))->isEnum()?"enum":$kind;
    $rows[]=["name"=>$name,"kind"=>$actual];
  }
}
usort($rows, static fn($a,$b)=>strcmp(strtolower($a["name"]),strtolower($b["name"])));
echo json_encode($rows, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
'''

raw = subprocess.run([str(ROOT / '.tools/php/bin/php'), '-n', '-r', CODE],
                     cwd=ROOT, capture_output=True, check=True)
assert not raw.stderr, raw.stderr
oracle = json.loads(raw.stdout)
catalogue = []
for line in (ROOT / 'spec/semantics/126-class-compiler.watsup').read_text().splitlines():
    if not line.startswith('  INTERNAL '):
        continue
    expressions = re.findall(r'\((\$ptascii\("[^"]+"\)(?: \+\+ \[92\] \+\+ \$ptascii\("[^"]+"\))*)\)', line)
    assert len(expressions) == 2, line
    key, name = ['\\'.join(re.findall(r'\$ptascii\("([^"]+)"\)', expr)) for expr in expressions]
    kind = re.search(r'"(class|interface|trait|enum)"[,]?$', line).group(1)
    assert key == name.lower(), line
    catalogue.append({'name': name, 'kind': kind})
assert len(oracle) == len(catalogue) == 166
assert catalogue == oracle, [(a, b) for a, b in zip(catalogue, oracle) if a != b]
print('PASS internal class occupancy: 166 exact names and kinds')
