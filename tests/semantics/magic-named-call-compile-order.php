<?php
class MagicNamedCompile114 {
    public function __call(string $name, array $arguments) { echo 'C|'; return 0; }
}
function effect114() { echo 'Q|'; return 7; }
echo 'NEVER|';
$child = new MagicNamedCompile114();
$child->missing(name: effect114(), effect114());
