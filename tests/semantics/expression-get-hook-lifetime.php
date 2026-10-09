<?php
class HookExpressionLeaf29 {
    function __destruct() { echo "D|"; }
}
function expression_leaf29(HookExpressionLeaf29 $leaf): HookExpressionLeaf29 {
    echo "G|";
    unset($GLOBALS["box"]);
    return $leaf;
}
class HookExpressionHeap29 {
    public HookExpressionLeaf29 $value {
        get => expression_leaf29($this->value);
    }
    function __construct(HookExpressionLeaf29 $leaf) { $this->value = $leaf; }
    function __destruct() { echo "B|"; }
}
$leaf = new HookExpressionLeaf29();
$weak = \WeakReference::create($leaf);
$box = new HookExpressionHeap29($leaf);
unset($leaf);
$result = $box->value;
echo $weak->get() === null ? "N|" : "L|";
unset($result);
echo $weak->get() === null ? "N|" : "L|";
