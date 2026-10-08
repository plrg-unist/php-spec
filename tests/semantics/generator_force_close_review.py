#!/usr/bin/env python3
"""Ordinary last-owner Generator force-close source counterexamples."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
from generator_review import run

ROOT = Path(__file__).resolve().parents[2]
REQUEST_CASES = set()
NATIVE_ERROR_PREFIXES = {}

# Existing FD198 transport: primitive request inputs, no PHP evaluation.
REQUEST_EXEC = '''import os,sys
fd=os.open(sys.argv[-1],os.O_RDONLY)
os.dup2(fd,198,inheritable=True)
if fd!=198: os.close(fd)
os.chdir(sys.argv[-3])
env=dict(os.environ,LD_PRELOAD=sys.argv[-2])
os.execve(sys.argv[1],sys.argv[1:-3],env)
'''
CASES = {'graph-temporary-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function outer(){try{yield from inner();}finally{echo'
                           b' "O";}}$g=outer();echo $g->current();unset($g);echo "Z";\n',
                           b'1IOZ',
                           0),
 'inherited-private-forced-finally': (b'<?php\nclass Owner {private $v=7;private function mark(){echo "M",$this->v;}public function seq(){try{yield 1;}finally{$this->mark();echo self::class,":",static::class;}}}class Child extends Owner {}$c=new Child;$g=$c->seq();unset($c);echo $g->current();unset($g);echo "Z";\n',
                                      b'1M7Owner:ChildZ',
                                      0),
 'foreach-iterator-force-close': (b'<?php\nclass It implements Iterator {private $i=0;function rewind():void{echo "R";$this->i=0;}function valid():bool{return $this->i<1;}function current():mixed{echo "C";return 7;}function key():mixed{return 0;}function next():void{echo "N";$this->i++;}}function seq(){try{foreach(new It as $v){yield $v;echo "X";}}finally{echo "F";}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                                  b'RC7FZ',
                                  0),
 'foreach-generator-force-close': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function seq(){try{foreach(inner() as $v){yield $v;echo "X";}}finally{echo "O";}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                                   b'1IOZ',
                                   0),
 'graph-child-parameter': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function outer($i){try{yield from $i;}finally{echo "O'
                           b'";}}$i=inner();$g=outer($i);echo $g->current();unset($i);unset($g);echo "Z";\n',
                           b'1OIZ',
                           0),
 'graph-child-external': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function outer($i){try{yield from $i;}finally{echo "O'
                          b'";}}$i=inner();$g=outer($i);echo $g->current();unset($g);echo $i->valid()?"T":"F";echo $i->current();unset($'
                          b'i);echo "Z";\n',
                          b'1OT1IZ',
                          0),
 'graph-shared-siblings': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function outer($i,$label){try{yield from $i;}finally{'
                           b'echo $label;}}$i=inner();$a=outer($i,"A");$b=outer($i,"B");echo $a->current(),":",$b->current();unset($i);un'
                           b'set($a);echo "X";echo $b->current();unset($b);echo "Z";\n',
                           b'1:1AX1BIZ',
                           0),
 'array-reference-cache-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function payload(){$v=inner();$v->current();r'
                                 b'eturn [&$v];}function seq(){try{yield from payload();}finally{echo "O";}}$g=seq();$g->current();unset($g'
                                 b');echo "Z";\n',
                                 b'OIZ',
                                 0),
 'array-reference-cache-cell': (b'<?php\nfunction payload(){$v=new stdClass;return [&$v];}function seq(){try{yield from payload();}finally{'
                                b'echo "F";}}$g=seq();$g->current();unset($g);echo "Z";\n',
                                b'FZ',
                                0),
 'array-no-finally-cached-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function seq(){yield from [inner()];}$g=seq()'
                                   b';$g->current()->current();unset($g);echo "Z";\n',
                                   b'IZ',
                                   0),
 'unstarted-body-silent': (b'<?php\nfunction seq(){try{echo "B";yield 1;}finally{echo "F";}}$g=seq();echo "C";unset($g);echo "Z";\n',
                           b'CZ',
                           0),
 'catch-bypassed-nested-finally': (b'<?php\nfunction seq(){try{try{yield 1;echo "X";}catch(Throwable $e){echo "C";}finally{echo "A";}}fina'
                                   b'lly{echo "B";}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                                   b'1ABZ',
                                   0),
 'paused-finally-return': (b'<?php\nfunction seq(){try{try{return 7;yield 0;}finally{echo "A";yield 1;echo "X";}}finally{echo "O";}}$g=seq'
                           b'();echo $g->current();unset($g);echo "Z";\n',
                           b'A1OZ',
                           0),
 'paused-finally-return-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function payload(){$i=inner();$i->current();return $i;}function seq(){try{try{return payload();yield 0;}finally{echo "A";yield 1;echo "X";}}finally{echo "O";}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                                 b'A1IOZ',
                                 0),
 'paused-finally-throw': (b'<?php\nfunction seq(){try{try{throw new Exception("old");yield 0;}finally{echo "A";yield 1;echo "X";}}finally'
                          b'{echo "O";}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                          b'A1OZ',
                          0),
 'paused-finally-break': (b'<?php\nfunction seq(){try{while(true){try{break;}finally{echo "A";yield 1;echo "X";}}echo "Y";}finally{echo "'
                          b'O";}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                          b'A1OZ',
                          0),
 'paused-finally-goto': (b'<?php\nfunction seq(){try{try{goto done;}finally{echo "A";yield 1;echo "X";}done:echo "Y";}finally{echo "O";}'
                         b'}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                         b'A1OZ',
                         0),
 'finally-explicit-return': (b'<?php\nfunction seq(){try{try{yield 1;}finally{echo "F";return 7;}}finally{echo "O";}}$g=seq();echo $g->c'
                             b'urrent();unset($g);echo "Z";\n',
                             b'1FOZ',
                             0),
 'finally-throw-caller-catch': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";throw new Exception("E");}}$g=seq();echo $g->current('
                                b');try{unset($g);}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()===null?"N":"X";}echo "Z'
                                b'";\n',
                                b'1FE:NZ',
                                0),
 'graph-finalizer-exception-chain': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";throw new Exception("inner");}}function out'
                                     b'er(){try{yield from inner();}finally{echo "O";throw new Exception("outer");}}$g=outer();echo $g->cur'
                                     b'rent();try{unset($g);}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()->getMessage();'
                                     b'}echo "Z";\n',
                                     b'1IOouter:innerZ',
                                     0),
 'caller-unwind-pending-exception': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";throw new Exception("new");}}function go(){$g'
                                     b'=seq();echo $g->current();throw new Exception("old");}try{go();}catch(Exception $e){echo $e->getMess'
                                     b'age(),":",$e->getPrevious()->getMessage();}echo "Z";\n',
                                     b'1Fnew:oldZ',
                                     0),
 'forbidden-yield-expression-effects': (b'<?php\nfunction mark($v){echo $v;return $v;}function seq(){try{yield 1;}finally{try{yield mark("K'
                                        b'")=>mark("V");}catch(Error $e){echo $e->getMessage();}}}$g=seq();echo $g->current();unset($g);ec'
                                        b'ho "Z";\n',
                                        b'1KVCannot yield from finally in a force-closed generatorZ',
                                        0),
 'forbidden-yield-from-expression-effects': (b'<?php\nfunction operand(){echo "A";return [];}function seq(){try{yield 1;}finally{try{yie'
                                             b'ld from operand();}catch(Error $e){echo $e->getMessage();}}}$g=seq();echo $g->current();unse'
                                             b't($g);echo "Z";\n',
                                             b'1ACannot use "yield from" in a force-closed generatorZ',
                                             0),
 'forbidden-yield-delayed-cv': (b'<?php\nfunction warn($l,$m){echo "W";return true;}set_error_handler("warn");function seq(){try{yield 1;}f'
                                b'inally{try{yield $missing;}catch(Error $e){echo "E";}}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                                b'1EZ',
                                0),
 'forbidden-yield-from-delayed-cv': (b'<?php\nfunction warn($l,$m){echo "W";return true;}set_error_handler("warn");function seq(){try{yi'
                                     b'eld 1;}finally{try{yield from $missing;}catch(Error $e){echo "E";}}}$g=seq();echo $g->current();unse'
                                     b't($g);echo "Z";\n',
                                     b'1WEZ',
                                     0),
 'forbidden-yield-from-invalid-type': (b'<?php\nfunction seq(){try{yield 1;}finally{try{yield from 7;}catch(Error $e){echo $e->getMessage('
                                       b');}}}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                                       b'1Cannot use "yield from" in a force-closed generatorZ',
                                       0),
 'operand-throw-before-forbidden-yield': (b'<?php\nfunction operand(){echo "A";throw new Exception("operand");}function seq(){try{yield 1'
                                          b';}finally{yield operand();}}$g=seq();echo $g->current();try{unset($g);}catch(Exception $e){e'
                                          b'cho $e->getMessage();}echo "Z";\n',
                                          b'1AoperandZ',
                                          0),
 'forced-from-cv-handler-throw': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W";throw new Exception("handler");}function seq(){try{yield 1'
                                  b';}finally{yield from $missing;}}set_error_handler("warn");$g=seq();echo $g->current();try{unset($g);'
                                  b'}catch(Throwable $e){echo get_class($e),":",$e->getMessage(),":",$e->getPrevious()?$e->getPrevious()'
                                  b'->getMessage():"N";}echo "Z";',
                                  b'1WError:Cannot use "yield from" in a force-closed generator:handlerZ',
                                  0),
 'forced-finalizer-starts-other-generator': (b'<?php\nfunction child(){try{yield 2;}finally{echo "I";}}function seq(){try{yield 1;}final'
                                             b'ly{echo "O";$h=child();echo $h->current();$GLOBALS["h"]=$h;}}$g=seq();echo $g->current();uns'
                                             b'et($g);echo "X",$h->valid()?"T":"F";unset($h);echo "Z";',
                                             b'1O2XTIZ',
                                             0),
 'pending-caller-exception-finalizer-catches-new': (b'<?php\nfunction seq(){try{try{yield 1;}finally{echo "F";throw new Exception("new");}}'
                                                    b'catch(Exception $e){echo "C",$e->getMessage(),":",$e->getPrevious()?"P":"N";}finally'
                                                    b'{echo "O";}}function go(){$g=seq();echo $g->current();throw new Exception("old");}tr'
                                                    b'y{go();}catch(Exception $e){echo "E",$e->getMessage(),":",$e->getPrevious()?"P":"N";'
                                                    b'}echo "Z";',
                                                    b'1FCnew:NOEold:NZ',
                                                    0),
 'normal-finally-suffix': (b'<?php\nfunction seq(){try{yield 1;echo "X";}finally{echo "F";}echo "S";}$g=seq();echo $g->current();unset($g)'
                           b';echo "Z";\n',
                           b'1FZ',
                           0),
 'finally-throw-outer-catch': (b'<?php\nfunction seq(){try{try{yield 1;}finally{echo "F";throw new Exception("E");}}catch(Exception $e){ec'
                               b'ho "C";}finally{echo "O";}echo "S";}$g=seq();echo $g->current();unset($g);echo "Z";\n',
                               b'1FCOSZ',
                               0),
 'no-finally-compiled-local-order': (b'<?php\nfunction child($n){try{yield 1;}finally{echo $n;}}function seq(){$a=child("A");$a->current'
                                     b'();$b=child("B");$b->current();yield 0;}$g=seq();echo $g->current();unset($g);echo "Z";',
                                     b'0ABZ',
                                     0),
 'unstarted-compiled-parameter-order': (b'<?php\nfunction child($n){try{yield 1;}finally{echo $n;}}function seq($a,$b){try{echo "X";yield 0'
                                        b';}finally{echo "F";}}$a=child("A");$b=child("B");$a->current();$b->current();$g=seq($a,$b);unset'
                                        b'($a,$b);echo "C";unset($g);echo "Z";',
                                        b'CABZ',
                                        0),
 'goto-within-forced-finally': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "A";goto inside;echo "X";inside:echo "B";}}$g=seq();echo '
                                b'$g->current();unset($g);echo "Z";',
                                b'1ABZ',
                                0),
 'forced-yield-key-value-release-order': (b'<?php\nfunction child($n){try{yield 0;}finally{echo $n;}}function keyval(){$g=$GLOBALS["k"];u'
                                          b'nset($GLOBALS["k"]);return $g;}function value(){$g=$GLOBALS["v"];unset($GLOBALS["v"]);return'
                                          b' $g;}function seq(){try{yield 1;}finally{yield keyval()=>value();}}$v=child("V");$v->current'
                                          b'();$k=child("K");$k->current();$g=seq();echo $g->current();try{unset($g);}catch(Error $e){ec'
                                          b'ho "E";}echo "Z";',
                                          b'1KVEZ',
                                          0),
 'forced-from-temp-release': (b'<?php\nfunction child(){try{yield 0;}finally{echo "I";}}function value(){$g=child();$g->current();return '
                              b'$g;}function seq(){try{yield 1;}finally{yield from value();}}$g=seq();echo $g->current();try{unset($g);}'
                              b'catch(Error $e){echo "E";}echo "Z";',
                              b'1IEZ',
                              0),
 'forced-from-multiline-cv': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l;return true;}\nfunction seq(){try{yield 1;}finally{\nyield fr'
                              b'om\n$missing;\n}}\nset_error_handler("warn");$g=seq();echo $g->current();try{unset($g);}catch(Error $e){ech'
                              b'o "E",$e->getLine();}echo "Z";',
                              b'1W5E5Z',
                              0),
 'iterator-raw-cache-child-order': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}class It implements Iterator{public $v;functi'
                                    b'on __construct(){$this->v=inner();$this->v->current();}function rewind():void{echo "R";}function val'
                                    b'id():bool{echo "V";return true;}function &current():mixed{echo "C";return $this->v;}function key():m'
                                    b'ixed{echo "K";return 0;}function next():void{echo "N";}}function seq(){try{yield from new It;}finall'
                                    b'y{echo "O";}}$g=seq();$g->current();unset($g);echo "Z";',
                                    b'RVCKOIZ',
                                    0),
 'forced-body-real-trace': (b'<?php\nfunction seq(){try{yield 1;}finally{try{throw new Exception("E");}catch(Exception $e){foreach($e->getT'
                            b'race() as $r){echo $r["function"],";";}}}}function go(){$g=seq();echo $g->current();unset($g);echo "Z";}go()'
                            b';',
                            b'1seq;go;Z',
                            0)}
DECLARATIONS = {'finally-break-live-loop': (b'<?php\nfunction seq(){while(true){try{yield 1;echo "X";}finally{echo "F";break;}}echo "S";}$g=seq();echo '
                             b'$g->current();unset($g);echo "Z";\n',
                             b'jump out of a finally block is disallowed',
                             2),
 'finally-goto-live-label': (b'<?php\nfunction seq(){try{yield 1;echo "X";}finally{echo "F";goto done;}echo "X";done:echo "S";}$g=seq();'
                             b'echo $g->current();unset($g);echo "Z";\n',
                             b'jump out of a finally block is disallowed',
                             2)}
UNSUPPORTED = {'request-end-required': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";}}$g=seq();echo $g->current();echo "Z";\n',
                          b'1ZF',
                          'Generator force-close at request end',
                          0),
 'self-cache-cycle-required': (b'<?php\nfunction seq(){try{$self=yield 1;yield 2;}finally{echo "F";}}$g=seq();echo $g->current(),$g->send('
                               b'$g);unset($g);echo "Z";',
                               b'12ZF',
                               'Generator force-close at request end',
                               0),
 'finalizer-exit-required': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";exit(7);}}$g=seq();echo $g->current();unset($g);echo '
                             b'"Z";\n',
                             b'1F',
                             'Generator force-close terminal cleanup',
                             7),
 'finalizer-exit-started-local-required': (b'<?php\nfunction child(){try{yield 2;}finally{echo "I";}}function seq(){try{yield 1;}finally{$'
                                           b'h=child();$h->current();echo "F";exit(7);}}$g=seq();echo $g->current();unset($g);echo "Z";',
                                           b'1FI',
                                           'Generator force-close terminal cleanup',
                                           7),
 'forced-from-cv-handler-exit-required': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W";exit(6);}function seq(){try{yield 1;}finally{yield'
                                          b' from $missing;}}set_error_handler("warn");$g=seq();echo $g->current();unset($g);echo "Z";',
                                          b'1W',
                                          'Generator force-close terminal cleanup',
                                          6)}

WATCHED = [
    "spec/semantics/30-storage.watsup",
    "spec/semantics/39-ownership.watsup", "spec/semantics/40-control.watsup",
    "spec/semantics/80-call-control.watsup",
    "spec/semantics/148-core-intrinsics.watsup", "spec/semantics/257-request-destructors.watsup",
    "spec/semantics/280-generators.watsup", "spec/semantics/289-generator-delegation.watsup",
    "spec/semantics/301-cycle-collection.watsup",
    "spec/semantics/303-generator-force-close.watsup", "spec/semantics/modules.json",
    "tests/semantics/profile.json", "bin/php-semantics", "_build/default/adapter/main.exe",
    "tests/semantics/generator_force_close_review.py", "tests/semantics/generator_review.py",
]


def fingerprints():
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in WATCHED}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["native", "full"], default="full")
    parser.add_argument("--select", help="Comma-separated exact case IDs")
    args = parser.parse_args()
    names = args.select.split(",") if args.select else list(CASES) + list(DECLARATIONS) + list(UNSUPPORTED)
    assert names and len(names) == len(set(names)) and all(n in CASES or n in DECLARATIONS or n in UNSUPPORTED for n in names)
    if set(names) & REQUEST_CASES:
        WATCHED.extend(["native/request_clock.c", "scripts/build-request-provider.sh", ".tools/request-clock.so"])
    profile = json.loads((ROOT / "tests/semantics/profile.json").read_text())
    php = ROOT / ".tools/php/bin/php"
    flags = [v for key, value in profile.items() for v in ["-d", f"{key}={value}"]]
    directory = Path(tempfile.mkdtemp(prefix="generator-force-close-review-", dir=ROOT / ".tools"))
    report = {"result": "fail", "mode": args.mode, "records": [], "agreements": 0,
              "unsupported": 0, "root": str(ROOT), "selection": names, "before": fingerprints(),
              "base": json.loads((ROOT / ".tools/base.json").read_text()) if (ROOT / ".tools/base.json").is_file() else None,
              "profile": profile,
              "environment": {"LC_ALL": "C", "TZ": "UTC"},
              "php_sha256": hashlib.sha256(php.read_bytes()).hexdigest()}
    print(directory, flush=True)
    try:
        (directory / "case-fixture.py").write_bytes(Path(__file__).read_bytes())
        for item in ["base.json", "parent-composition.json", "parent-union.diff"]:
            provenance = ROOT / ".tools" / item
            if provenance.is_file():
                (directory / item).write_bytes(provenance.read_bytes())
        identity = run([str(php), "-n", *flags, "-r", "echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);"], directory / "runtime", 10)
        assert identity.returncode == 0 and not identity.stderr
        report["runtime"] = json.loads(identity.stdout)
        assert report["runtime"][:4] == ["8.5.10", "cli", 8, False]
        assert all(report["runtime"][5][key] == value for key, value in profile.items())
        for name in names:
            case = directory / name
            case.mkdir()
            source = CASES[name][0] if name in CASES else DECLARATIONS[name][0] if name in DECLARATIONS else UNSUPPORTED[name][0]
            path = case / "source.php"
            path.write_bytes(source)
            row = {"id": name, "source_sha256": hashlib.sha256(source).hexdigest(), "model_status": "UNRUN"}
            report["records"].append(row)
            native_command = [str(php), "-n", *flags, str(path)]
            model_command = [str(ROOT / "bin/php-semantics"), str(path), "--steps", "100000", "--timeout", "60"]
            if name in REQUEST_CASES:
                b64 = lambda value: base64.b64encode(value).decode()
                request = {"env": [[b64(b"LC_ALL"), b64(b"C")], [b64(b"TZ"), b64(b"UTC")]],
                           "argv": [b64(os.fsencode(path))], "file": b64(os.fsencode(path)),
                           "seconds": "1700000000", "microseconds": 125000,
                           "variables": b64(b"EGPCS"), "jit": True, "cwd": b64(os.fsencode(ROOT))}
                context, payload = case / "request.json", case / "request-input.bin"
                context.write_text(json.dumps(request) + "\n")
                entries = [base64.b64decode(k) + b"=" + base64.b64decode(v) for k, v in request["env"]]
                payload.write_bytes(b"PHPRQ001" + struct.pack("<qII", int(request["seconds"]), request["microseconds"], len(entries))
                                    + b"".join(struct.pack("<I", len(e)) + e for e in entries))
                native_command[-1:-1] = ["-d", "variables_order=EGPCS", "-d", "auto_globals_jit=1"]
                native_command = [sys.executable, "-c", REQUEST_EXEC, *native_command,
                                  str(ROOT), str(ROOT / ".tools/request-clock.so"), str(payload)]
                model_command += ["--request-context", str(context)]
                row.update(request=request, request_profile={**profile, "variables_order": "EGPCS", "auto_globals_jit": "1"})
            native = run(native_command, case / "native", 10)
            row.update(native_exit=native.returncode, native_stdout=base64.b64encode(native.stdout).decode(), native_stderr=base64.b64encode(native.stderr).decode())
            if name in DECLARATIONS:
                message, line = DECLARATIONS[name][1:]
                expected_error = b"Fatal error: " + message + b" in " + os.fsencode(path) + f" on line {line}\nStack trace:\n#0 {{main}}\n".encode()
                assert native.returncode == 255 and not native.stdout and native.stderr == expected_error, (name, native.stderr)
            else:
                expected = CASES[name][1] if name in CASES else UNSUPPORTED[name][1]
                expected_exit = CASES[name][2] if name in CASES else UNSUPPORTED[name][3]
                prefix = NATIVE_ERROR_PREFIXES.get(name)
                error_matches = native.stderr.lstrip(b"\r\n").startswith(prefix.replace(b"{file}", os.fsencode(path))) if prefix else not native.stderr
                assert native.returncode == expected_exit and error_matches and native.stdout == expected, (name, native)
            if args.mode == "full":
                model = run(model_command, case / "model", 90)
                row["model_exit"] = model.returncode
                assert not model.stderr, (name, model.stderr)
                observation = json.loads(model.stdout)
                row["model_status"] = observation["status"]
                if name in UNSUPPORTED:
                    assert model.returncode == 1 and observation["status"] == "unsupported" and observation["reason"] == UNSUPPORTED[name][2], (name, observation)
                    report["unsupported"] += 1
                else:
                    expected_status = "static_rejection" if name in DECLARATIONS else "explicit_exit" if CASES[name][2] else "normal"
                    assert model.returncode == 0 and observation["status"] == expected_status, (name, observation)
                    assert observation["reason"] is None
                    assert observation["exit_status"] == native.returncode
                    assert base64.b64decode(observation["stdout"], validate=True) == native.stdout
                    assert base64.b64decode(observation["stderr"], validate=True) == native.stderr
                    report["agreements"] += 1
                assert observation["frontend"] == "accepted" and observation["checked"] == "program"
            row["passed"] = True
            print(name, repr(native.stdout), "pass", flush=True)
        report["result"] = "pass"
    except BaseException as error:
        report["failure"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        report["after"] = fingerprints()
        if report["after"] != report["before"]:
            report["result"] = "fail"
            report["failure"] = {"type": "InputChanged", "message": "source/semantic inputs changed during campaign"}
        (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("generator-force-close:", report["result"], report["agreements"], "agreements", report["unsupported"], "controls")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
