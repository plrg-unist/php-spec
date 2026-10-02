#!/usr/bin/env python3
"""Finite-context source comparisons for include_path mutation."""
import base64
import errno
import hashlib
import json
import locale
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / 'tests/semantics/profile.json'
locale.setlocale(locale.LC_ALL, 'C')
CASES = {
    'set-restore': b"<?php echo include 'one.php'; echo set_include_path('__SUB__'); echo include 'one.php'; ini_restore('include_path'); echo include 'one.php';",
    'ini-set': b"<?php echo ini_set('include_path','__SUB__'); echo include 'one.php';",
    'ini-case': b"<?php echo ini_set('INCLUDE_PATH','__SUB__')?'Y':'N'; echo include 'one.php';",
    'named-error': b"<?php function a(){echo 'A';return 'sub';} function b(){echo 'B';return 7;} try{set_include_path(include_path:a(),bad:b());}catch(Error $e){echo '|',$e->getMessage(),'|';} echo include 'one.php';",
    'first-class': b"<?php $f=set_include_path(...); echo $f('__SUB__'); echo include 'one.php';",
    'dynamic-restore': b"<?php set_include_path('sub'); $f='ini_restore'; $f('include_path'); echo set_include_path('z');",
    'dynamic-ini-set': b"<?php $f='ini_set'; echo $f(option:'include_path',value:'sub');",
    'dynamic-mutated-callee': b'<?php $f="set_include_path"; function mutate(){global $f; $f="ini_restore"; return "sub";} echo $f(mutate()),"|",set_include_path("end");',
    'dynamic-ref-finally': b"<?php function &r($tmp):string{$x='sub';try{if($tmp)return 'sub';return $x;}finally{echo 'R';}} function arg(){global $f;r(false);r(true);$f='ini_restore';return 'sub';} $f='set_include_path'; echo $f(arg()),'|',set_include_path('end');",
    'dynamic-caught-reentry': b'<?php function g($x){$f="set_include_path"; return $f($x ? throw new Exception("boom") : "sub");} try{g(true);}catch(Throwable $e){} echo g(false);',
    'dynamic-pipe': b'<?php $f="set_include_path"; echo "sub" |> $f;',
    'fixed-pipe': b'<?php echo "sub" |> set_include_path(...);',
    'dynamic-chdir': b"<?php $f='chdir'; $f('__SUB__'); echo include 'one.php';",
    'named': b"<?php echo ini_set(value:'__SUB__',option:'include_path'); echo include 'one.php';",
    'unpack': b"<?php echo set_include_path(...['include_path'=>'__SUB__']); echo include 'one.php';",
    'empty': b"<?php echo set_include_path('')?'Y':'N'; echo include 'one.php';",
    'null': b"<?php echo set_include_path(null)?'Y':'N'; echo include 'one.php';",
    'ini-false': b"<?php echo ini_set('include_path',false)?'Y':'N'; echo include 'one.php';",
    'ini-null': b"<?php echo ini_set('include_path',null)?'Y':'N'; echo include 'one.php';",
    'strict-ini-int': b"<?php declare(strict_types=1); echo ini_set('include_path',123);",
    'strict-set-int': b"<?php declare(strict_types=1); try{set_include_path(123);}catch(TypeError $e){echo $e->getMessage();} echo include 'one.php';",
    'set-nul': b"<?php try{set_include_path(\"a\\0b\");}catch(ValueError $e){echo $e->getMessage();} echo include 'one.php';",
    'chdir-success': b"<?php echo include 'one.php'; echo chdir('__SUB__')?'T':'F'; echo include 'one.php';",
    'chdir-relative': b"<?php echo include 'one.php'; echo chdir('sub')?'T':'F'; echo include 'one.php';",
    'chdir-function': b"<?php function f(){return chdir('__SUB__');} echo include 'one.php'; f(); echo include 'one.php';",
    'chdir-once': b"<?php echo include_once 'one.php'; chdir('__SUB__'); echo include_once 'one.php';",
    'chdir-failure': b"<?php echo chdir('missing')?'T':'F'; echo include 'one.php';",
    'chdir-empty': b"<?php echo chdir('')?'T':'F'; echo include 'one.php';",
    'chdir-nul': b"<?php try{chdir(\"a\\0b\");}catch(ValueError $e){echo $e->getMessage();} echo include 'one.php';",
    'chdir-null': b"<?php echo chdir(null)?'T':'F'; echo include 'one.php';",
    'chdir-weak-int': b"<?php echo chdir(123)?'T':'F'; echo include 'one.php';",
    'chdir-strict-int': b"<?php declare(strict_types=1); try{chdir(123);}catch(TypeError $e){echo $e->getMessage();} echo include 'one.php';",
    'chdir-named': b"<?php chdir(directory:'__SUB__'); echo include 'one.php';",
    'chdir-unpack': b"<?php chdir(...['directory'=>'__SUB__']); echo include 'one.php';",
    'chdir-first-class': b"<?php $f=chdir(...); $f('__SUB__'); echo include 'one.php';",
    'included-function-chdir': b"<?php include 'mutate.php'; echo include 'one.php';",
    'chdir-stringable-weak': b"<?php class O { function __toString(): string { echo 'S'; return '__SUB__'; } } echo chdir(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-throw-lines': b'<?php\nclass O { function __toString(): string { throw new Exception("X"); } }\nchdir(\n  new O\n);\n',
    'chdir-stringable-nul': b'<?php class O { function __toString(): string { echo "S"; return "a\\0b"; } } try { chdir(new O); } catch (ValueError $e) { echo "V"; } echo include "one.php";',
    'chdir-stringable-nul-uncaught': b'<?php class O { function __toString(): string { return "a\\0b"; } } chdir(new O);',
    'chdir-stringable-invoke-nul': b'<?php class O { function __toString(): string { return "a\\0b"; } } $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-invoke-throw': b'<?php class O { function __toString(): string { throw new Exception("X"); } } $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-invoke-nested-throw': b'<?php class O { function __toString(): string { $this->g(); return "sub"; } function g(): void { throw new Exception("X"); } } $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-inherited-invoke-throw': b'<?php class P {function __toString():string {throw new Exception("X");}} class O extends P {} $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-inherited-case-invoke-throw': b'<?php class P {function __ToStRiNg():string {throw new Exception("X");}} class O extends P {} $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-strict': b'<?php declare(strict_types=1); class O { function __toString(): string { echo "S"; return "sub"; } } try { chdir(new O); } catch (TypeError $e) { echo "T"; } echo include "one.php";',
    'chdir-object-nonstringable': b'<?php class O {} try { chdir(new O); } catch (TypeError $e) { echo "T"; } echo include "one.php";',
    'chdir-stringable-dynamic': b"<?php class O { function __toString(): string { echo 'S'; return '__SUB__'; } } $f='chdir'; echo $f(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-first-class': b"<?php class O { function __toString(): string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-nested-throw': b'<?php class O { function __toString(): string { $this->g(); return "sub"; } function g(): void { throw new Exception("X"); } } chdir(new O);',
    'chdir-stringable-mutate-cwd': b"<?php class O { function __toString(): string { chdir('__SUB__'); return '..'; } } echo chdir(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-nested-conversion': b"<?php class P { function __toString():string { echo 'P'; return '__SUB__'; } } class O { function __toString():string { echo 'O'; $g='chdir'; $g(new P); return '..'; } } $f='chdir'; echo $f(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-selection': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } function swap($v){global $f; echo 'A'; $f='ini_restore'; return new O;} $f='chdir'; echo $f(directory:swap($f))?'T':'F'; echo include 'one.php'; echo '|',$f;",
    'chdir-stringable-named-first-class': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-invoke': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f->__invoke(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-mutate-cwd': b"<?php class O { function __toString():string { echo 'S'; chdir('__SUB__'); return '..'; } } echo chdir(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } chdir(directory:new O);',
    'chdir-stringable-named-invoke-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(directory:new O);',
    'chdir-stringable-named-inherited-case-throw': b'<?php class P { function __ToStRiNg():string { throw new Exception("X"); } } class O extends P {} $f=chdir(...); $f->__invoke(directory:new O);',
    'chdir-stringable-named-strict': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } chdir(directory:new O);',
    'chdir-stringable-named-strict-first-class': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } $f=chdir(...); $f(directory:new O);',
    'chdir-stringable-named-strict-invoke': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(directory:new O);',
    'chdir-object-named-nonstringable': b'<?php class O {} chdir(directory:new O);',
    'chdir-object-named-unknown': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a(){echo "A"; return new O;} $f=chdir(...); $f->__invoke(bad:a());',
    'chdir-object-named-case': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a(){echo "A"; return new O;} chdir(Directory:a());',
    'chdir-object-named-duplicate': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(a("A"),directory:a("B"));',
    'chdir-object-named-count': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(a("A"),a("B"));',
    'chdir-object-named-invoke-count': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} $f=chdir(...); $f->__invoke(a("A"),a("B"));',
    'chdir-stringable-unpack-positional': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(...[new O])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-selection': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } function swap(){global $f; echo 'A'; $f='ini_restore'; return ['directory'=>new O];} $f='chdir'; echo $f(...swap())?'T':'F'; echo include 'one.php'; echo '|',$f;",
    'chdir-stringable-unpack-ordinary-before-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(new O,...[])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-ordinary-after-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(...[],directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-first-class-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f(...[],...['directory'=>new O],...[])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-invoke': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f->__invoke(...['directory'=>new O])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-capture-retired': b"<?php class O {function __toString():string {global $x,$a; echo ($x==='changed' && $a===[])?'E':'N'; echo 'T'; throw new Exception('X');}} $x=new O; $a=['directory'=>&$x]; function later(){global $x,$a; echo 'A'; $x='changed'; $a=[]; return [];} $f=chdir(...); $f->__invoke(...$a,...later());",
    'chdir-stringable-unpack-mutate-cwd': b"<?php class O { function __toString():string { echo 'S'; chdir('__SUB__'); return '..'; } } echo chdir(...['directory'=>new O])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } chdir(...[new O]);',
    'chdir-stringable-unpack-invoke-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(...["directory"=>new O]);',
    'chdir-stringable-unpack-inherited-case-throw': b'<?php class P { function __ToStRiNg():string { throw new Exception("X"); } } class O extends P {} $f=chdir(...); $f->__invoke(...[],...["directory"=>new O],...[]);',
    'chdir-stringable-unpack-strict': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } chdir(...[new O]);',
    'chdir-stringable-unpack-strict-first-class': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } $f=chdir(...); $f(...["directory"=>new O]);',
    'chdir-stringable-unpack-strict-invoke': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(...["directory"=>new O]);',
    'chdir-object-unpack-unknown': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a(){echo "A"; return new O;} $f=chdir(...); $f->__invoke(...["bad"=>a()]);',
    'chdir-object-unpack-duplicate': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(...[a("A")],...["directory"=>a("B")]);',
    'chdir-object-unpack-array-order': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} function later(){echo "L"; return [];} chdir(...["directory"=>a("A"),a("B")],...later());',
    'chdir-object-unpack-pack-order': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} $f=chdir(...); $f->__invoke(...["directory"=>a("A")],...[a("B")]);',
    'chdir-object-unpack-empty-count': b'<?php $f=chdir(...); $f->__invoke(...[],...[]);',
    'chdir-object-unpack-positional-count': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(...[a("A"),a("B")]);',
    'set-unpack-retained': b"<?php echo set_include_path(...['include_path'=>'__SUB__']); echo include 'one.php';",
    'ini-set-unpack-retained': b"<?php echo ini_set(...['value'=>'__SUB__'],...['option'=>'include_path']); echo include 'one.php';",
    'ini-restore-unpack-retained': b"<?php set_include_path('__SUB__'); ini_restore(...['option'=>'include_path']); echo include 'one.php';",
    'set-stringable-direct': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo set_include_path(new O); echo include 'one.php';",
    'set-stringable-first-class': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=set_include_path(...); echo $f(new O); echo include 'one.php';",
    'set-stringable-named-invoke': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=set_include_path(...); echo $f->__invoke(include_path:new O); echo include 'one.php';",
    'set-stringable-selection': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } function swap($v){global $f; echo 'A'; $f='ini_restore'; return new O;} $f='set_include_path'; echo $f(include_path:swap($f)); echo include 'one.php'; echo '|',$f;",
    'set-stringable-mutate-ini': b"<?php class O {function __toString():string {echo set_include_path('inner'); return 'outer';}} echo set_include_path(new O); echo '|'; echo set_include_path('.:');",
    'set-stringable-empty': b"<?php class O {function __toString():string {echo set_include_path('inner'); return '';}} echo set_include_path(new O)?'T':'F'; echo set_include_path('.:');",
    'set-stringable-unpack-capture-retired': b"<?php class O {function __toString():string {global $x,$a; echo ($x==='changed' && $a===[])?'E':'N'; echo 'T'; return 'outer';}} $x=new O; $a=['include_path'=>&$x]; function later(){global $x,$a; echo 'A'; $x='changed'; $a=[]; return [];} $f=set_include_path(...); echo $f->__invoke(...$a,...later()); echo '|',set_include_path('end');",
    'set-stringable-ordinary-after-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo set_include_path(...[],include_path:new O); echo include 'one.php';",
    'set-stringable-nested-chdir': b"<?php class P {function __toString():string {echo 'P';return '__SUB__';}} class O {function __toString():string {echo chdir(new P)?'T':'F';return '.:';}} echo set_include_path(new O); echo include 'one.php';",
    'set-stringable-caught-throw': b"<?php class O {function __toString():string {set_include_path('inner');throw new Exception('X');}} try{set_include_path(new O);}catch(Exception $e){echo set_include_path('end');}",
    'set-stringable-nul': b'<?php class O {function __toString():string {echo "S";return "a\\0b";}} set_include_path(new O);',
    'set-stringable-invoke-nul': b'<?php class O {function __toString():string {echo "S";return "a\\0b";}} $f=set_include_path(...);$f->__invoke(include_path:new O);',
    'set-stringable-mutated-nul': b'<?php class O {function __toString():string {set_include_path("inner");return "a\\0b";}} try{set_include_path(new O);}catch(ValueError $e){echo set_include_path(".:");}',
    'set-stringable-inherited-case-throw': b'<?php class P {function __ToStRiNg():string {throw new Exception("X");}} class O extends P {} $f=set_include_path(...);$f->__invoke(...[],...["include_path"=>new O],...[]);',
    'set-stringable-strict': b'<?php declare(strict_types=1);class O {function __toString():string {echo "T";return "outer";}} set_include_path(include_path:new O);',
    'set-stringable-strict-first-class': b'<?php declare(strict_types=1);class O {function __toString():string {echo "T";return "outer";}} $f=set_include_path(...);$f(...[new O]);',
    'set-stringable-strict-invoke': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'outer';}} $f=set_include_path(...);echo $f->__invoke(include_path:new O);",
    'set-object-nonstringable': b'<?php class O {} set_include_path(new O);',
    'set-object-named-unknown': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} function a(){echo 'A';return new O;} $f=set_include_path(...);$f->__invoke(directory:a());",
    'set-object-unpack-duplicate': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} function a($s){echo $s;return new O;} set_include_path(...[a('A')],...['include_path'=>a('B')]);",
    'set-object-unpack-count': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} function a($s){echo $s;return new O;} $f=set_include_path(...);$f->__invoke(...[a('A'),a('B')]);",
    'ini-set-object-value': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} ini_set('include_path',new O);",
    'ini-set-object-value-strict': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'outer';}} ini_set('include_path',new O);",
    'ini-set-object-value-invoke-named': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} $f=ini_set(...);$f->__invoke(value:new O,option:'include_path');",

}


def b64(data):
    return base64.b64encode(data).decode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree


def main():
    out = Path(tempfile.mkdtemp(prefix='include-mutable-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
               ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php',
               ROOT / 'frontend/target.php', ROOT / 'frontend/SourcePrinter.php',
               ROOT / 'frontend/encoding.php', ROOT / 'frontend/wire.php',
               ROOT / 'spec/schema.json', ROOT / 'spec/php.watsup', ROOT / 'adapter/main.ml',
               ROOT / 'frontend/wire.py', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', PROFILE, Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    vendor_before = vendor_identity()
    profile = json.loads(PROFILE.read_text())
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    environment = {**os.environ, 'LC_ALL': 'C'}
    default_cwd = os.fsencode(ROOT.resolve())
    records = []
    for name, template in CASES.items():
        directory = out / name
        directory.mkdir()
        cwd = os.fsencode(directory.resolve()) if name == 'chdir-relative' else default_cwd
        sub = directory / 'sub'
        sub.mkdir()
        main_path = directory / 'main.php'
        local = directory / 'one.php'
        alternate = sub / 'one.php'
        local.write_bytes(b'<?php return 8;')
        alternate.write_bytes(b'<?php return 7;')
        sub_bytes = os.fsencode(sub.resolve())
        source = template.replace(b'__SUB__', sub_bytes)
        main_path.write_bytes(source)
        main_bytes = os.fsencode(main_path.resolve())
        mutate = directory / 'mutate.php'
        if name == 'included-function-chdir':
            mutate.write_bytes(b"<?php function f(){return chdir('__SUB__');} f();".replace(b'__SUB__', sub_bytes))
        entries = []
        for cwd_key, include_path, target in [(cwd, b'.:', local), (cwd, sub_bytes, alternate),
                                               (sub_bytes, b'.:', alternate)]:
            opened = os.fsencode(target.resolve())
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'one.php'),
                            'cwd': b64(cwd_key), 'include_path': b64(include_path),
                            'status': 'opened', 'resolved': b64(opened),
                            'opened': b64(opened), 'source': b64(target.read_bytes())})
        if name in ('chdir-stringable-mutate-cwd', 'chdir-stringable-nested-conversion', 'chdir-stringable-named-mutate-cwd', 'chdir-stringable-unpack-mutate-cwd'):
            case_cwd = os.fsencode(directory.resolve())
            opened = os.fsencode(local.resolve())
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'one.php'),
                            'cwd': b64(case_cwd), 'include_path': b64(b'.:'),
                            'status': 'opened', 'resolved': b64(opened),
                            'opened': b64(opened), 'source': b64(local.read_bytes())})
        if name == 'included-function-chdir':
            mutate_bytes = os.fsencode(mutate.resolve())
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'mutate.php'),
                            'cwd': b64(cwd), 'include_path': b64(b'.:'), 'status': 'opened',
                            'resolved': b64(mutate_bytes), 'opened': b64(mutate_bytes),
                            'source': b64(mutate.read_bytes())})
        missing_error = os.strerror(errno.ENOENT).encode()
        chdir_entries = [
            {'cwd': b64(cwd), 'requested': b64(sub_bytes), 'status': 'success',
             'next_cwd': b64(sub_bytes)},
            {'cwd': b64(cwd), 'requested': b64(b'missing'), 'status': 'failure',
             'stream_error': b64(missing_error), 'errno': errno.ENOENT},
            {'cwd': b64(cwd), 'requested': b64(b''), 'status': 'failure',
             'stream_error': b64(missing_error), 'errno': errno.ENOENT},
            {'cwd': b64(cwd), 'requested': b64(b'123'), 'status': 'failure',
             'stream_error': b64(missing_error), 'errno': errno.ENOENT},
        ]
        if name == 'chdir-relative':
            chdir_entries.append({'cwd': b64(cwd), 'requested': b64(b'sub'),
                                  'status': 'success', 'next_cwd': b64(sub_bytes)})
        if name in ('chdir-stringable-mutate-cwd', 'chdir-stringable-nested-conversion', 'chdir-stringable-named-mutate-cwd', 'chdir-stringable-unpack-mutate-cwd'):
            chdir_entries.append({'cwd': b64(sub_bytes), 'requested': b64(b'..'),
                                  'status': 'success',
                                  'next_cwd': b64(os.fsencode(directory.resolve()))})
        snapshot = {'version': 2, 'main': b64(main_bytes), 'cwd': b64(cwd),
                    'include_path': b64(b'.:'), 'entries': entries,
                    'chdir_entries': chdir_entries}
        snapshot_path = directory / 'snapshot.json'
        snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
        model_command = [str(ROOT / 'bin/php-semantics'), str(main_path),
                         '--file-snapshot', str(snapshot_path), '--steps', '100000', '--timeout', '60']
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(main_path)]
        process_cwd = directory if name == 'chdir-relative' else ROOT
        # Two directory pauses plus include replay measured 150s; each request keeps its 60s cap.
        model_producer_timeout = 180 if name == 'chdir-stringable-nested-conversion' else 90
        model = subprocess.run(model_command, cwd=process_cwd, env=environment, capture_output=True, timeout=model_producer_timeout)
        native = subprocess.run(native_command, cwd=process_cwd, env=environment, capture_output=True, timeout=30)
        for label, result in [('model', model), ('native', native)]:
            (directory / (label + '.stdout')).write_bytes(result.stdout)
            (directory / (label + '.stderr')).write_bytes(result.stderr)
        try:
            outcome = json.loads(model.stdout)
            matching = (base64.b64decode(outcome.get('stdout', '')) == native.stdout
                        and base64.b64decode(outcome.get('stderr', '')) == native.stderr
                        and outcome.get('exit_status') == native.returncode
                        and outcome.get('status') in {'normal', 'php_error', 'static_rejection'})
        except (ValueError, KeyError):
            outcome = {}
            matching = False
        records.append({'case': name, 'result': 'pass' if matching else 'fail',
                        'source_sha256': digest(main_path), 'snapshot_sha256': digest(snapshot_path),
                        'local_sha256': digest(local), 'alternate_sha256': digest(alternate),
                        'mutate_sha256': digest(mutate) if mutate.exists() else None,
                        'model_command': model_command, 'native_command': native_command,
                        'model_producer_timeout': model_producer_timeout,
                        'process_cwd': str(process_cwd.resolve()),
                        'model_process_exit': model.returncode, 'native_exit': native.returncode,
                        'model_status': outcome.get('status'),
                        'model_stdout_sha256': digest(directory / 'model.stdout'),
                        'model_stderr_sha256': digest(directory / 'model.stderr'),
                        'native_stdout_sha256': digest(directory / 'native.stdout'),
                        'native_stderr_sha256': digest(directory / 'native.stderr')})
        print(name, records[-1]['result'], outcome.get('status'), flush=True)
    after = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    vendor_after = vendor_identity()
    report = {'inputs': before, 'input_changes': [key for key in before if before[key] != after[key]],
              'vendor_tree': vendor_before,
              'chdir_fact_basis': 'Created finite subdirectory canonicalized with Path.resolve; ENOENT number and C-locale strerror from errno.ENOENT/os.strerror, checked against pinned native raw outputs',
              'profile': profile, 'environment': {'LC_ALL': 'C', 'cwd': str(ROOT.resolve())},
              'cases': records, 'passed': all(row['result'] == 'pass' for row in records)}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    assert report['passed'] and not report['input_changes'] and vendor_before == vendor_after


if __name__ == '__main__':
    main()
