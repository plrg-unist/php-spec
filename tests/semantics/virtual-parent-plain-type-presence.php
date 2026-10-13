<?php
class PresencePlain61Parent {
    public $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return "13"; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class PresencePlain61Bridge extends PresencePlain61Parent {}
class PresencePlain61Child extends PresencePlain61Bridge {
    public $value = 200;
    private function answer() { return 500; }
}
class PresencePlain61Grand extends PresencePlain61Child {
    private function answer() { return 900; }
}
$parent = new PresencePlain61Parent;
$child = new PresencePlain61Child;
$grand = new PresencePlain61Grand;
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
