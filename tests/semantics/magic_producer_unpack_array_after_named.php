<?php
class MagicArrayOrder125 {
    public static function __callStatic(string $name, array $arguments) { echo "BAD|body|"; }
}
$pack = ["arguments" => 7, 900 => 8];
$answer = 42;
try { $answer = MagicArrayOrder125::MiSs(...$pack); }
catch (Throwable $error) { echo "E|", $error->getMessage(), "|", $answer, "|"; }
echo "A|";
