<?php
class HookExpressionUntyped29 {
    public $value = 7 {
        get => $this->value + 1;
    }
}
$box = new HookExpressionUntyped29();
echo $box->value, "|";
$box->value = 17;
echo $box->value, "|";
