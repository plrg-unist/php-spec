<?php
class PublicUnsetParent112 {
    public int $value = 41;
    public function __unset(string $name): void {
        global $child, $error;
        echo 'U|';
        $child = null;
        throw $error;
    }
    public function __destruct() { echo 'D|'; }
}
class PublicUnsetChild112 extends PublicUnsetParent112 {}
$error = new Exception('same112');
$child = new PublicUnsetChild112();
unset($child->value);
$after = 42;
echo 'X:';
try { unset($child->value); $after = 7; echo 'A|'; }
catch (Exception $caught) { if ($caught === $error) { echo 'C|'; } echo $after, '|'; }
echo 'F|';
unset($child, $caught, $error);
echo 'E|';
