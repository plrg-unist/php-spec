"""Original ArrayAccess core entry and interface-contract discriminators."""


def source(name, body, *, get='return $offset;', exists='return true;',
           set='', unset='', before=''):
    return ("<?php\nerror_reporting(0);\n" + before +
            f"class {name} implements ArrayAccess {{\n" +
            " public function offsetExists(mixed $offset): bool { " + exists + " }\n" +
            " public function offsetGet(mixed $offset): mixed { " + get + " }\n" +
            " public function offsetSet(mixed $offset, mixed $value): void { " + set + " }\n" +
            " public function offsetUnset(mixed $offset): void { " + unset + " }\n" +
            "}\n" + body).encode()


CASES = [
    ('quiet-exists-does-not-test-get-null-and-empty-short-circuits',
     source('QuietModes284', """
$o284=new QuietModes284;
echo 'I:',(int)isset($o284[null]),';';
echo 'C:',$o284[null]??17,';';
echo 'E:',(int)empty($o284[true]),';';
echo 'F:',(int)empty($o284[false]),';';
""", exists="echo 'X;'; return $offset!==false;", get="echo 'G;'; return $offset;"),
     b'I:X;1;C:X;G;17;E:X;G;0;F:X;1;'),
    ('read-float-null-and-array-keys-use-raw-mixed-offsets',
     source('RawKeys284', """
$o284=new RawKeys284;
set_error_handler(function($n,$m){echo 'WRONG;';return true;},2|8192);
$a284=$o284[1.5];$b284=$o284[null];$c284=$o284[[13]];
restore_error_handler();echo 'R:',$a284,':',(int)($b284===null),':',$c284[0],';';
""", get="echo 'G;'; return $offset;"),
     b'G;G;G;R:1.5:1:13;'),
    ('direct-append-and-array-offset-set-preserve-assignment-value',
     source('DirectSets284', """
$o284=new DirectSets284;
$x284=($o284[]=13);$y284=($o284[[7]]=17);
echo 'R:',$x284,':',$y284,';';
""", set="echo 'S:',(int)($offset===null),':',$value,';';"),
     b'S:1:13;S:0:17;R:13:17;'),
    ('direct-unset-does-not-coerce-float-or-array-offsets',
     source('DirectUnsets284', """
$o284=new DirectUnsets284;
set_error_handler(function($n,$m){echo 'WRONG;';return true;},2|8192);
unset($o284[1.5],$o284[[7]],$o284[null]);
restore_error_handler();echo 'R:',(int)isset($o284),';';
""", unset="echo 'X:',(int)($offset===1.5),':',(int)($offset===null),';';"),
     b'X:1:0;X:0:0;X:0:1;R:1;'),
    ('indirect-interface-inherited-methods-use-called-child', b"""<?php
error_reporting(0);
interface IndirectAccess284 extends ArrayAccess {}
abstract class ParentAccess284 implements IndirectAccess284 {
 public function offsetExists(mixed $offset): bool { return true; }
 public function offsetGet(mixed $offset): mixed { echo 'G:',static::class,';';return $offset; }
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {}
}
class ChildAccess284 extends ParentAccess284 {}
$o284=new ChildAccess284;echo 'R:',$o284[17],':',(int)($o284 instanceof ArrayAccess),';';
""", b'R:G:ChildAccess284;17:1;'),
    ('tentative-return-notice-and-return-type-will-change', b"""<?php
error_reporting(0);
set_error_handler(function($n,$m){echo 'D:',(int)($n===8192),':',(int)($m==='Return type of NoticeAccess284::offsetExists($offset) should either be compatible with ArrayAccess::offsetExists(mixed $offset): bool, or the #[\\ReturnTypeWillChange] attribute should be used to temporarily suppress the notice'),';';return true;},8192);
if (true) { class NoticeAccess284 implements ArrayAccess {
 public function offsetExists($offset) { return true; }
 #[ReturnTypeWillChange] public function offsetGet($offset) { return 17; }
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {}
} }
restore_error_handler();$o284=new NoticeAccess284;echo 'R:',$o284[1],';';
""", b'D:1:1;R:17;'),
]

CONTRACT_CASES = [
    ('arrayaccess-static-get-is-a-core-declaration-error', b"""<?php
class StaticAccess284 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool {return true;}
 public static function offsetGet(mixed $offset): mixed {return null;}
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {}
}
""", b''),
    ('arrayaccess-narrow-offset-is-a-core-declaration-error', b"""<?php
class NarrowAccess284 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool {return true;}
 public function offsetGet(int $offset): mixed {return null;}
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {}
}
""", b''),
]
