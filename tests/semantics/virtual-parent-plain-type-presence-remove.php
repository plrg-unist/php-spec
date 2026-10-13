<?php
class PresencePlainRemove61Parent {
    public int $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return "13"; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class PresencePlainRemove61Bridge extends PresencePlainRemove61Parent {}
class PresencePlainRemove61Child extends PresencePlainRemove61Bridge {
    public $value = 200;
    private function answer() { return 500; }
}
class PresencePlainRemove61Grand extends PresencePlainRemove61Child {
    private function answer() { return 900; }
}
$parent = new PresencePlainRemove61Parent;
$child = new PresencePlainRemove61Child;
$grand = new PresencePlainRemove61Grand;
$raw = (array) $parent;
echo $raw === [] ? "EMPTY|" : ($raw === ["value" => null] ? "NULL|" : "BAD|");
$raw = (array) $child;
echo $raw === ["value" => 200] ? "C200|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
$result = $child->value;
echo $result === "13" ? "CS|" : "BAD|";
echo $grand->parentRead(), "|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
$result = $grand->value;
echo $result === "13" ? "GS|" : "BAD|";
