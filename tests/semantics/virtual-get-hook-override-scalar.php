<?php
class VirtualOverrideParent39 {
    public int $value { get => $this->answer(); }
    private function answer() {
        echo "P:", __CLASS__, "/", static::class, "|";
        return 7;
    }
    public function parentRead() { return $this->value; }
    public function parentWrite($value) { $this->value = $value; }
}
class VirtualOverrideBridge39 extends VirtualOverrideParent39 {
    private function answer() { echo "BADBRIDGE|"; return 500; }
}
class VirtualOverrideChild39 extends VirtualOverrideBridge39 {
    public int $value { get => $this->answer(); }
    private function answer() {
        echo "C:", __CLASS__, "/", static::class, "|";
        return 13;
    }
}
class VirtualOverrideGrand39 extends VirtualOverrideChild39 {
    private function answer() { echo "BADGRAND|"; return 900; }
}
class VirtualOverrideUntypedParent39 {
    public $value { get => false; }
}
class VirtualOverrideUntypedChild39 extends VirtualOverrideUntypedParent39 {
    public $value { get => 0; }
}
function virtualOverrideRhs39() { echo "R|"; return 300; }
$parent = new VirtualOverrideParent39;
echo ((array)$parent === [] ? "PE|" : "BAD|");
$result = $parent->value;
echo "P", $result, "|";
$child = new VirtualOverrideChild39;
echo ((array)$child === [] ? "CE|" : "BAD|");
$result = $child->value;
echo "C", $result, "|";
try { $child->value = 200; }
catch (Error $error) { echo $error->getMessage(), ":", $error->getLine(), "|"; }
echo ((array)$child === [] ? "CWE|" : "BAD|");
$grand = new VirtualOverrideGrand39;
echo ((array)$grand === [] ? "GE|" : "BAD|");
$result = $grand->parentRead();
echo "T", $result, "|";
echo ((array)$grand === [] ? "RE|" : "BAD|");
try { $grand->value = virtualOverrideRhs39(); }
catch (Error $error) { echo $error->getMessage(), ":", $error->getLine(), "|"; }
echo ((array)$grand === [] ? "WE|" : "BAD|");
$result = $grand->value;
echo "W", $result, "|";
try { $grand->parentWrite(400); }
catch (Error $error) { echo $error->getMessage(), ":", $error->getLine(), "|"; }
echo ((array)$grand === [] ? "TE|" : "BAD|");
$untyped = new VirtualOverrideUntypedChild39;
echo ((array)$untyped === [] ? "UE|" : "BAD|");
$result = $untyped->value;
echo ($result === 0 ? "ZERO|" : "BAD|");
try { $untyped->value = 5; }
catch (Error $error) { echo $error->getMessage(), ":", $error->getLine(), "|"; }
echo ((array)$untyped === [] ? "UWE|" : "BAD|");
