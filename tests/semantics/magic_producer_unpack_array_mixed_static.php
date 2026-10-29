<?php
$prefix = 7;
$alias =& $prefix;
class MagicArrayStaticBase125 {
    public static function __callStatic(string $name, array $arguments) {
        echo "B|", __CLASS__, "|", static::class, "|", $name, "|";
        foreach ($arguments as $key => $value) { echo $key, "=", $value, "|"; }
        return 23;
    }
}
class MagicArrayStaticChild125 extends MagicArrayStaticBase125 {}
$answer = MagicArrayStaticChild125::MiSs($alias, ...["arguments" => 8], ...[900 => 9]);
echo "R|", $answer, "|A|";
