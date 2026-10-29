<?php
class MagicPositionalPayload126 {
    public function __destruct() { echo 'D|positional|'; }
}
class MagicNamedPayload126 {
    public function __destruct() { echo 'D|named|'; }
}
class MagicInvalidPayload126 {
    public function __destruct() { echo 'D|invalid|'; }
}
class MagicTarget126 {
    public function __call(string $name, array $arguments) {
        echo 'H|', $name, '|';
        return 38;
    }
    public function __destruct() { echo 'D|target|'; }
}
function magicGenerator126(): Generator {
    try {
        echo 'Y0|'; yield 0 => new MagicPositionalPayload126();
        echo 'Y1|'; yield 'named' => new MagicNamedPayload126();
        echo 'Y2|'; yield false => new MagicInvalidPayload126();
    } finally { echo 'F|'; }
}
class MagicAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $target;
        echo 'G|';
        $target = null;
        return magicGenerator126();
    }
    public function __destruct() { echo 'D|aggregate|'; }
}
$target = new MagicTarget126();
try {
    $answer = $target->missing(...new MagicAggregate126());
    echo 'BAD|', $answer, '|';
} catch (Error $error) {
    echo 'E|', $error->getMessage(), '|';
}
echo 'Z|';
