<?php
class MagicEmptyProducer125 {
    public function __call(string $name, array $arguments) {
        echo "B|", $name, "|", func_num_args(), "|", (int)($arguments === []), "|"; return 23;
    }
}
function magicEmptyGenerator125() {
    try { echo "G|"; if (false) { yield 0 => 7; } echo "Z|"; }
    finally { echo "F|"; }
}
$receiver = new MagicEmptyProducer125();
$pack = [];
$answer = $receiver->MiSs(...$pack, ...magicEmptyGenerator125());
echo "R|", $answer, "|A|";
