<?php
namespace DynamicScope27;
use AllowDynamicProperties as Dynamic;
#[Dynamic]
class Parent27 {}
class Child27 extends Parent27 {}
class Grandchild27 extends Child27 {}
$child = new Child27();
$child->extra = 7;
$grandchild = new Grandchild27();
$grandchild->extra = 9;
echo $child->extra, "|", $grandchild->extra, "|";
