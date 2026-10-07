#!/usr/bin/env python3
"""Independent ordinary-source Generator creation/resumption counterexamples."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'eager-default': (b'<?php\nclass Box {function __construct(){echo "D";}} function seq($p=new Box){echo "B";yield 7;echo "A";} $g=seq();echo "C";echo $g->valid()?"T":"F";echo $g->current();$g->next();echo $g->valid()?"T":"F";echo $g->current()===null?"N":"X";', b'DCBT7AFN'),
    'eager-type': (b'<?php\nfunction seq(int $v){echo "B";yield $v;} echo "A";try{$g=seq([]);echo "X";}catch(TypeError $e){echo "T";} echo "Z";', b'ATZ'),
    'first-current-rewind': (b'<?php\nfunction seq(){echo "A";yield 1;echo "B";yield 2;echo "C";} $g=seq();echo "D";echo $g->current();echo $g->valid()?"T":"F";$g->rewind();echo $g->key();$g->next();echo $g->current();try{$g->rewind();echo "X";}catch(Exception $e){echo "R";}$g->next();echo $g->valid()?"T":"F";echo $g->current()===null?"N":"X";', b'DA1T0B2RCFN'),
    'fresh-next': (b'<?php\nfunction seq(){echo "A";yield 1;echo "B";yield 2;echo "C";} $g=seq();echo "D";$g->next();echo $g->current();echo $g->key();$g->next();echo $g->valid()?"T":"F";', b'DAB21CF'),
    'arbitrary-key-history': (b'<?php\nfunction seq($obj){yield -4=>10;yield 11;yield "9"=>12;yield 13;yield 5=>14;yield 15;yield [1]=>16;yield $obj=>17;yield 18;} $o=new stdClass;$g=seq($o);foreach($g as $k=>$v){if($v===16){echo $k===[1]?"A":"X";}elseif($v===17){echo $k===$o?"O":"X";}else{echo $k,":",$v,";";}}', b'-4:10;0:11;9:12;1:13;5:14;6:15;AO7:18;'),
    'delayed-key-cv': (b'<?php\nfunction keyval(){echo "K";return "held";} function value(){echo "V";return 3;}function seq(){yield keyval()=>value();$k="old";yield $k=>($k="new");}foreach(seq() as $k=>$v){echo "[",$k,":",$v,"]";}', b'KV[held:3][new:new]'),
    'arg-value-reference': (b'<?php\nfunction seq($v,&$r){echo "B";yield $v;yield $r;$r=8;} $x=1;$r=2;$g=seq($x,$r);$x=3;$r=4;echo "C";foreach($g as $v){echo $v;}echo ":",$x,":",$r;', b'CB14:3:8'),
    'empty-initialization': (b'<?php\nfunction seq(){if(false)yield 1;echo "E";}$g=seq();echo "C";echo $g->valid()?"T":"F";echo $g->current()===null?"N":"X";echo $g->key()===null?"N":"X";$g->rewind();echo "R";try{foreach($g as $v){echo "X";}}catch(Exception $e){echo "Q";}', b'CEFNNRQ'),
    'closure-reference': (b'<?php\n$x=2;$f=function()use(&$x){echo "B";yield $x;$x++;yield $x;};$g=$f();unset($f);$x=4;echo "C";echo $g->current();$g->next();echo $g->current(),":",$x;$g->next();', b'CB45:5'),
    'resume-trace': (b'<?php\nfunction seq(){throw new Exception("x");yield 1;}function resume($g){$g->current();}$g=seq();echo "C";try{resume($g);}catch(Exception $e){foreach($e->getTrace() as $row){echo $row["function"],";";}}', b'Cseq;current;resume;'),
    'bare-return-compatible': (b'<?php\nfunction seq():Generator {return;yield 1;}$g=seq();echo "C";echo $g->valid()?"T":"F";$g->rewind();echo "R";', b'CFR'),
    'compatible-types': (b'<?php\nfunction a():Generator {yield 1;} function b():Iterator {yield 2;}function c():Traversable {yield 3;}function d():object {yield 4;}function e():mixed {yield 5;}function f():Generator|array {yield 6;}foreach(a() as $v){echo $v;}foreach(b() as $v){echo $v;}foreach(c() as $v){echo $v;}foreach(d() as $v){echo $v;}foreach(e() as $v){echo $v;}foreach(f() as $v){echo $v;}', b'123456'),
    'nested-yield-isolation': (b'<?php\nfunction plain(){function child(){yield 1;} $f=function(){yield 2;};echo "O";return 3;}echo plain();', b'O3'),
    'foreach-resume-trace': (b'<?php\nfunction seq(){throw new Exception("x");yield 1;}function resume($g){foreach($g as $v){echo "X";}}$g=seq();echo "C";try{resume($g);}catch(Exception $e){foreach($e->getTrace() as $row){echo $row["function"],";";}}', b'Cseq;resume;'),
    'nullary-yield': (b'<?php\nfunction seq(){yield;yield 8;}$g=seq();echo $g->current()===null?"N":"X";echo $g->key();$g->next();echo $g->current(),":",$g->key();', b'N08:1'),
    'yielded-array-alias-copy': (b'<?php\nfunction seq(&$r){$a=[&$r];yield $a;$a[0]=9;yield $a;}$r=1;$g=seq($r);$v=$g->current();$v[1]=2;$r=3;echo $g->current()[0],":",isset($g->current()[1])?"X":"N";$g->next();echo ":",$v[0],":",$g->current()[0],":",isset($g->current()[1])?"X":"N";$g->next();echo ":",$r;', b'3:N:9:9:N:9'),
    'generator-retval-skips-stringable-return': (b'<?php\nclass Str {function __toString():string {echo "X";return "str";}}function seq():Generator|string {if(false)yield 1;return new Str;}$g=seq();echo "C";echo $g->valid()?"T":"F";unset($g);echo "Z";', b'CFZ'),
    'running-cached-getters': (b'<?php\nfunction seq(){yield 1;echo $GLOBALS["g"]->current(),":",$GLOBALS["g"]->key(),":";echo $GLOBALS["g"]->valid()?"T":"F";yield 2;}$g=seq();$g->current();$g->next();echo $g->current();', b'1:0:T2'),
    'implicit-key-signed64-wrap': (b'<?php\nfunction seq(){yield PHP_INT_MAX=>1;yield 2;yield 3;}foreach(seq() as $k=>$v){echo $k,":",$v,";";}', b'9223372036854775807:1;-9223372036854775808:2;-9223372036854775807:3;'),
    'early-getreturn-initializes': (b'<?php\nfunction seq():Generator {echo "A";yield 1;echo "B";return 9;}$g=seq();echo "C";try{$g->getReturn();echo "X";}catch(Exception $e){echo "R";}echo $g->current();$g->rewind();$g->next();echo $g->getReturn();', b'CAR1B9'),
    'empty-getreturn-completes': (b'<?php\nfunction seq(){if(false)yield 1;echo "B";return 6;}$g=seq();echo "C";echo $g->getReturn();echo $g->valid()?"T":"F";echo $g->current()===null?"N":"X";$g->rewind();echo "R";', b'CB6FNR'),
    'getreturn-array-copy': (b'<?php\nfunction seq(){yield 1;return [2,3];}$g=seq();$g->next();$r=$g->getReturn();$r[0]=9;echo $g->getReturn()[0],":",$r[0],":",$g->getReturn()[1];', b'2:9:3'),
    'inherited-method-scope': (b'<?php\nclass A {private $x=4;const C="A";function seq(){yield $this->x;yield self::C;yield static::class;}}class B extends A {}$b=new B;$g=$b->seq();unset($b);echo "C";foreach($g as $v){echo $v,";";}', b'C4;A;B;'),
    'over-arity-trace-before-initialize': (b'<?php\nfunction seq(){echo "B";yield 1;}function value(){echo "A";return 3;}$g=seq();try{$g->current(value());}catch(ArgumentCountError $e){$t=$e->getTrace();echo $t[0]["function"],":",$t[0]["args"][0],":";}echo $g->current();', b'Acurrent:3:B1'),
    'intersection-native-acceptance': (b'<?php\nfunction seq():Iterator&Countable {yield 1;}$g=seq();echo $g instanceof Generator?"G":"X";echo $g instanceof Countable?"C":"N";foreach($g as $v){echo $v;}', b'GN1'),
    'private-creation-live-resumer': (b'<?php\nclass A {private $x=4;private function seq(){yield $this->x;}public function make(){return $this->seq();}}$a=new A;$g=$a->make();unset($a);echo "C";echo $g->current();', b'C4'),
    'same-function-nested-resume-trace': (b'<?php\nfunction seq($n){if($n){foreach(seq($n-1) as $v){yield $v;}}else{throw new Exception("x");yield 1;}}function go($g){$g->current();}$g=seq(2);try{go($g);}catch(Exception $e){foreach($e->getTrace() as $r){echo $r["function"],":";if($r["function"]==="seq"){echo $r["args"][0];}echo ";";}}', b'seq:0;seq:1;seq:2;current:;go:;'),
    'parent-constant-default': (b'<?php\nclass Box{public $n;function __construct($n){echo "D";$this->n=$n;}}const C=new Box(4);function seq($x=C){echo "B";yield $x;return $x;}$g=seq();echo "C";$c=C;$c->n=9;unset($c);echo $g->current()===C?"I":"X";echo $g->current()->n;$g->next();echo $g->getReturn()===C?"R":"X";echo $g->getReturn()->n;unset($g);echo C->n,"Z";', b'DCBI9R99Z'),
    'parent-deferred-autoload': (b'<?php\nfunction loader($name){echo "L";if($name==="Later"){class Later{public $x=8;}}}function seq(){echo "B";$x=new Later;yield $x->x;}$load=function($name){loader($name);};spl_autoload_register($load);$g=seq();echo "C";unset($load);echo $g->current();echo "D";', b'CBL8D'),
    'parent-fold-precision-warning': (b'<?php\nfunction notice($l,$m,$f,$n){echo "H|";ini_set("precision","5");}function seq($v){yield "L" . 1.234567;$a=false;$a[(string)$v]=7;yield $a;}set_error_handler("notice");$g=seq(1.234567);ini_set("precision","3");echo $g->current(),"|";$g->next();foreach($g->current() as $k=>$v){echo $k,":",$v,"|";}$g->next();echo "D";', b'L1.234567|H|1.23:7|D'),
}
CASES['started-finally-force-close'] = (b'<?php\nfunction seq(){try{echo "A";yield 1;echo "B";yield 2;}finally{echo "F";}}$g=seq();foreach($g as $v){echo $v;break;}echo "C";foreach($g as $v){echo $v;break;}echo "D";$g->next();echo $g->current();unset($g);echo "Z";', b'A1C1DB2FZ')

DECLARATIONS = {
    'invalid-scalar-supertype': (b'<?php\nfunction seq():int {yield 1;}\necho "X";', b'Generator return type must be a supertype of Generator, int given', 2),
    'invalid-class-supertype': (b'<?php\nfunction seq():Countable {yield 1;}\necho "X";', b'Generator return type must be a supertype of Generator, Countable given', 2),
    'invalid-dnf-supertype': (b'<?php\nfunction seq():(Iterator&Countable)|false {yield 1;}\necho "X";', b'Generator return type must be a supertype of Generator, (Iterator&Countable)|false given', 2),
}
UNSUPPORTED = {
    'unstarted-release': (b'<?php\nclass Box {function __destruct(){echo "D";}}function seq($b){try{echo "B";yield 1;}finally{echo "F";}}$g=seq(new Box);echo "C";unset($g);echo "Z";', b'CDZ'),
    'yielded-object-retirement': (b'<?php\nclass Box {function __destruct(){echo "D";}}function seq($o){yield $o;unset($o);yield 0;}$o=new Box;$g=seq($o);unset($o);echo "C";$v=$g->current();$g->next();echo "N";unset($v);echo "V";unset($g);echo "Z";', b'CNDVZ'),
    'previous-yield-retirement-before-cv': (b'<?php\n$v=1;class Box {function __destruct(){$GLOBALS["v"]=9;echo "D";}}function seq(){global $v;yield new Box;yield $v=>$v;}$g=seq();$g->current();echo "C";$g->next();echo $g->key(),":",$g->current();', b'CD9:9'),
    'closed-last-yield-owner': (b'<?php\nclass Box {function __destruct(){echo "D";}}function seq(){yield new Box;}$g=seq();$g->current();echo "A";$g->next();echo "B";echo $g->current()===null?"N":"X";unset($g);echo "C";', b'ABNDC'),
    'request-finally-force-close': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";}}$g=seq();echo $g->current();echo "Z";', b'1ZF'),
}
UNSUPPORTED_REASONS = {
    'unstarted-release': "ordinary destructor release before request stage",
    'yielded-object-retirement': "ordinary destructor release before request stage",
    'previous-yield-retirement-before-cv': "ordinary destructor release before request stage",
    'closed-last-yield-owner': "ordinary destructor release before request stage",
    'request-finally-force-close': "Generator force-close at request end",
}


def run(command, stem, timeout):
    result = subprocess.run(command, cwd=stem.parent, capture_output=True,
                            timeout=timeout, env=dict(os.environ, LC_ALL="C", TZ="UTC"))
    stem.with_suffix(".stdout").write_bytes(result.stdout)
    stem.with_suffix(".stderr").write_bytes(result.stderr)
    stem.with_suffix(".command.json").write_text(json.dumps(command) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["native", "full"], default="full")
    parser.add_argument("--select", help="Comma-separated exact case IDs")
    args = parser.parse_args()
    names = args.select.split(",") if args.select else list(CASES) + list(DECLARATIONS) + list(UNSUPPORTED)
    assert names and len(set(names)) == len(names) and all(n in CASES or n in DECLARATIONS or n in UNSUPPORTED for n in names)
    profile = json.loads((ROOT / "tests/semantics/profile.json").read_text())
    php = ROOT / ".tools/php/bin/php"
    flags = [arg for key, value in profile.items() for arg in ["-d", f"{key}={value}"]]
    directory = Path(tempfile.mkdtemp(prefix="generator-independent-", dir=ROOT / ".tools"))
    report = {"result": "fail", "mode": args.mode, "selected": names, "profile": profile,
              "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "environment": {"LC_ALL": "C", "TZ": "UTC"}, "agreements": 0, "unsupported": 0,
              "records": [], "tools": {"php_sha256": hashlib.sha256(php.read_bytes()).hexdigest()}}
    print(directory, flush=True)
    try:
        (directory / "candidate.diff").write_bytes(subprocess.check_output(["git", "diff", "HEAD"], cwd=ROOT))
        candidate = ROOT / 'spec/semantics/280-generators.watsup'
        if candidate.exists():
            (directory / 'candidate-generator.watsup').write_bytes(candidate.read_bytes())
        report["tools"]["test_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if args.mode == "full":
            report["tools"]["adapter_sha256"] = hashlib.sha256((ROOT / "_build/default/adapter/main.exe").read_bytes()).hexdigest()
        identity = run([str(php), "-n", *flags, "-r",
                        "echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);"],
                       directory / "runtime", 10)
        assert identity.returncode == 0 and not identity.stderr
        report["runtime"] = json.loads(identity.stdout)
        assert report["runtime"][:4] == ["8.5.10", "cli", 8, False]
        assert all(report["runtime"][5][key] == value for key, value in profile.items())
        for name in names:
            case = directory / name
            case.mkdir()
            if name in DECLARATIONS:
                source, message, line = DECLARATIONS[name]
                expected = b''
            else:
                source, expected = (CASES | UNSUPPORTED)[name]
            path = case / "source.php"
            path.write_bytes(source)
            row = {"id": name, "source_sha256": hashlib.sha256(source).hexdigest()}
            report["records"].append(row)
            native = run([str(php), "-n", *flags, str(path)], case / "native", 10)
            row["native_exit"] = native.returncode
            if name in DECLARATIONS:
                expected_error = b'Fatal error: ' + message + b' in ' + os.fsencode(path) + b' on line ' + str(line).encode() + b'\nStack trace:\n#0 {main}\n'
                assert native.returncode == 255 and not native.stdout and native.stderr == expected_error, (name, native)
            else:
                assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native)
            if args.mode == "full":
                model = run([str(ROOT / "bin/php-semantics"), str(path), "--steps", "100000", "--timeout", "60"], case / "model", 90)
                row["model_exit"] = model.returncode
                assert not model.stderr, (name, model.stderr)
                observation = json.loads(model.stdout)
                row["model_status"] = observation["status"]
                assert observation["frontend"] == "accepted" and observation["checked"] == "program"
                if name in UNSUPPORTED:
                    assert model.returncode == 1 and observation["status"] == "unsupported", (name, observation)
                    assert observation["reason"] == UNSUPPORTED_REASONS[name], (name, observation)
                    report["unsupported"] += 1
                else:
                    assert model.returncode == 0 and observation["status"] == ("static_rejection" if name in DECLARATIONS else "normal"), (name, observation)
                    assert observation["reason"] is None
                    if name in DECLARATIONS:
                        assert observation["diagnostic"]["class"] == "CompileError" and observation["diagnostic"]["line"] == line
                        assert base64.b64decode(observation["diagnostic"]["message"], validate=True) == message
                    else:
                        assert observation["diagnostic"] is None
                    assert observation["exit_status"] == native.returncode
                    assert base64.b64decode(observation["stdout"], validate=True) == native.stdout, (name, observation)
                    assert base64.b64decode(observation["stderr"], validate=True) == native.stderr, (name, observation)
                    report["agreements"] += 1
            row["passed"] = True
            print(name, "pass", flush=True)
        report["result"] = "pass"
    except BaseException as error:
        report["failure"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(directory / "report.json", report["result"], flush=True)


if __name__ == "__main__":
    main()
