<?php
class CovParent40 {
    public int|string $value {
        get { echo "P:", __CLASS__, "/", static::class, "|"; return "root"; }
    }
    public function parentRead() { return $this->value; }
}
class CovBridge40 extends CovParent40 {}
class CovChild40 extends CovBridge40 {
    public int $value {
        get { echo "C:", __CLASS__, "/", static::class, "|"; return $this->answer(); }
    }
    private function answer() { return 13; }
}
class CovGrand40 extends CovChild40 {
    private function answer() { return 900; }
}
function covRhs40() { echo "R|"; return 300; }
$parent = new CovParent40;
echo ((array) $parent === []) ? "PE|" : "BAD|";
echo $parent->value, "|";
$child = new CovChild40;
echo ((array) $child === []) ? "CE|" : "BAD|";
echo $child->value, "|";
$grand = new CovGrand40;
echo ((array) $grand === []) ? "GE|" : "BAD|";
echo $grand->parentRead(), "|";
try { $grand->value = covRhs40(); }
catch (Error $error) { echo $error->getMessage(), ":", $error->getLine(), "|"; }
echo ((array) $grand === []) ? "WE|" : "BAD|";
echo $grand->value, "|";
