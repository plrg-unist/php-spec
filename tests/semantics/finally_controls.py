#!/usr/bin/env python3
"""Stage A transfer admission controls; not native semantic agreements."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = {'value-return': '<?php echo "BAD";function f(){try{return 1;}finally{echo "F";}}', 'reference-return': '<?php echo "BAD";function &f(){$x=1;try{return $x;}finally{$x=2;}}', 'break-through': '<?php echo "BAD";while(true){try{break;}finally{echo "F";}}', 'continue-through': '<?php echo "BAD";for($i=0;$i<1;$i++){try{continue;}finally{echo "F";}}', 'goto-into-catch': '<?php echo "BAD";goto L;try{}catch(Throwable){L:;}finally{}', 'goto-local-finalizer': '<?php echo "BAD";try{}finally{goto L;L:;}'}

def main():
    out = Path(tempfile.mkdtemp(prefix='finally-controls-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, Path(__file__), ROOT / '_build/default/adapter/main.exe', ROOT / 'bin/php-semantics', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / 'frontend/worker.php', ROOT / 'spec/semantics/modules.json']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    rows = []
    for name, source in CASES.items():
        path = out / (name + '.php')
        path.write_bytes(source.encode())
        command = [str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '45']
        process = subprocess.run(command, capture_output=True, env=types.ENV, timeout=55)
        (out / (name + '.stdout')).write_bytes(process.stdout)
        (out / (name + '.stderr')).write_bytes(process.stderr)
        actual = json.loads(process.stdout)
        assert process.returncode != 0 and actual['status'] == 'unsupported', (name, actual)
        assert actual['reason'] == 'finally return and jump unwinding' and actual['stdout'] == '', (name, actual)
        rows.append({'name': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'command': command, 'exit_status': process.returncode, 'actual': actual})
    assert before == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'rows': rows, 'inputs': before}, indent=2) + '\n')
    print(out, '6 temporary source-admission controls pass')


if __name__ == '__main__':
    main()
