<?php
class HookExpressionStringValue29 {
    function __toString(): string { echo "S|"; return "19"; }
}
function expression_string29(string $backing): HookExpressionStringValue29 {
    echo "G", $backing, "|";
    return new HookExpressionStringValue29();
}
class HookExpressionString29 {
    public string $value = "7" {
        get => expression_string29($this->value);
    }
}
$box = new HookExpressionString29();
echo $box->value, "|";
