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
    'unstarted-release': (b'<?php\nclass Box {function __destruct(){echo "D";}}function seq($b){try{echo "B";yield 1;}finally{echo "F";}}$g=seq(new Box);echo "C";unset($g);echo "Z";', b'CDZ'),
    'foreach-resume-trace': (b'<?php\nfunction seq(){throw new Exception("x");yield 1;}function resume($g){foreach($g as $v){echo "X";}}$g=seq();echo "C";try{resume($g);}catch(Exception $e){foreach($e->getTrace() as $row){echo $row["function"],";";}}', b'Cseq;resume;'),
    'nullary-yield': (b'<?php\nfunction seq(){yield;yield 8;}$g=seq();echo $g->current()===null?"N":"X";echo $g->key();$g->next();echo $g->current(),":",$g->key();', b'N08:1'),
    'yielded-array-alias-copy': (b'<?php\nfunction seq(&$r){$a=[&$r];yield $a;$a[0]=9;yield $a;}$r=1;$g=seq($r);$v=$g->current();$v[1]=2;$r=3;echo $g->current()[0],":",isset($g->current()[1])?"X":"N";$g->next();echo ":",$v[0],":",$g->current()[0],":",isset($g->current()[1])?"X":"N";$g->next();echo ":",$r;', b'3:N:9:9:N:9'),
    'yielded-object-retirement': (b'<?php\nclass Box {function __destruct(){echo "D";}}function seq($o){yield $o;unset($o);yield 0;}$o=new Box;$g=seq($o);unset($o);echo "C";$v=$g->current();$g->next();echo "N";unset($v);echo "V";unset($g);echo "Z";', b'CNDVZ'),
    'previous-yield-retirement-before-cv': (b'<?php\n$v=1;class Box {function __destruct(){$GLOBALS["v"]=9;echo "D";}}function seq(){global $v;yield new Box;yield $v=>$v;}$g=seq();$g->current();echo "C";$g->next();echo $g->key(),":",$g->current();', b'CD9:9'),
}
UNSUPPORTED = {
    "started-finally-force-close": (b'<?php\nfunction seq(){try{echo "A";yield 1;echo "B";yield 2;}finally{echo "F";}}$g=seq();foreach($g as $v){echo $v;break;}echo "C";foreach($g as $v){echo $v;break;}echo "D";$g->next();echo $g->current();unset($g);echo "Z";', b'A1C1DB2FZ'),
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
    names = args.select.split(",") if args.select else list(CASES) + list(UNSUPPORTED)
    assert names and len(set(names)) == len(names) and all(n in CASES or n in UNSUPPORTED for n in names)
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
            source, expected = (CASES | UNSUPPORTED)[name]
            path = case / "source.php"
            path.write_bytes(source)
            row = {"id": name, "source_sha256": hashlib.sha256(source).hexdigest()}
            report["records"].append(row)
            native = run([str(php), "-n", *flags, str(path)], case / "native", 10)
            row["native_exit"] = native.returncode
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
                    report["unsupported"] += 1
                else:
                    assert model.returncode == 0 and observation["status"] == "normal", (name, observation)
                    assert observation["reason"] is None and observation["diagnostic"] is None
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
