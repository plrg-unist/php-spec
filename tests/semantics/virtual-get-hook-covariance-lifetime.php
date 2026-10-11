<?php
class Animal40 {
    public function tag() { return "ANIMAL|"; }
}
class Dog40 extends Animal40 {
    public function tag() { return "DOG|"; }
    public function __destruct() { echo "DD|"; }
}
function freshDog40() {
    global $weak_leaf;
    echo "H|";
    $leaf = new Dog40;
    $weak_leaf = WeakReference::create($leaf);
    return $leaf;
}
class CovLifeParent40 {
    public Animal40 $value { get => new Animal40; }
    public function parentRead() { return $this->value; }
    public function __destruct() { echo ((array) $this === []) ? "BEMPTY|" : "BAD|"; }
}
class CovLifeBridge40 extends CovLifeParent40 {}
class CovLifeChild40 extends CovLifeBridge40 {
    public Dog40 $value { get => freshDog40(); }
}
class CovLifeGrand40 extends CovLifeChild40 {}
$box = new CovLifeGrand40;
$weak_box = WeakReference::create($box);
$kept = $box->parentRead();
echo $kept->tag();
echo ((array) $box === []) ? "EMPTY|" : "BAD|";
echo ($weak_leaf->get() !== null) ? "LIVE|" : "BAD|";
unset($box);
echo ($weak_box->get() === null) ? "BN|" : "BAD|";
echo ($weak_leaf->get() !== null) ? "LIVE|" : "BAD|";
unset($kept);
echo ($weak_leaf->get() === null) ? "N|" : "BAD|";
