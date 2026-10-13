<?php
class ProtectedSetBackedParent60 {
    public int $value = 100 {
        get {
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
}
class ProtectedSetBackedBridge60 extends ProtectedSetBackedParent60 {}
class ProtectedSetBackedChild60 extends ProtectedSetBackedBridge60 {
    public protected(set) int $value = 200;
}
echo "BAD|";
