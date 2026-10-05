<?php
error_reporting(0);
class AccessBackingCurrent284 { public static int $value=9; }
class OwnerAccessCurrent284 implements ArrayAccess {
    private static function handle($n,$m,$f,$line) { echo 'H:',self::class,'/',get_called_class(),':',$line,';'; $GLOBALS['held284']=13; $GLOBALS['key284']=7; unset($GLOBALS['o284']); return true; }
    public static function register() { set_error_handler(self::handle(...),2); }
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { return null; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'S:',(int)($offset===null),':',$value,';'; unset($GLOBALS['rhs284'],$GLOBALS['held284']); AccessBackingCurrent284::$value=17; }
    public function offsetUnset(mixed $offset): void {}
}
class ChildAccessCurrent284 extends OwnerAccessCurrent284 { public static function handle($n,$m,$f,$line) { echo 'WRONG;'; return true; } }
$held284=&AccessBackingCurrent284::$value; $rhs284=&$held284; $o284=new ChildAccessCurrent284; ChildAccessCurrent284::register();
$r284=($o284[$key284]=$rhs284);
restore_error_handler();
echo 'R:',$r284,':',AccessBackingCurrent284::$value,':',(int)isset($o284),':',(int)isset($rhs284),';';
