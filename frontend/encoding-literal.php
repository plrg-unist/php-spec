<?php declare(strict_types=1);

// Zend folds only literal concatenation during AST construction (zend_ast.c:
// zend_ast_create_concat_op). This recognizes that parser action, not general
// constant evaluation. null denotes a nonliteral expression.
function encodingLiteralValue(PhpParser\Node\Expr $expression): string|int|float|null {
    $pending = [[$expression, false]];
    $values = [];
    while ($pending) {
        [$node, $joined] = array_pop($pending);
        if ($node instanceof PhpParser\Node\Scalar\String_
            || $node instanceof PhpParser\Node\Scalar\Int_
            || $node instanceof PhpParser\Node\Scalar\Float_) {
            $values[] = $node->value;
        } elseif ($node instanceof PhpParser\Node\Expr\BinaryOp\Concat) {
            if ($joined) {
                $right = array_pop($values);
                $left = array_pop($values);
                $values[] = (string)$left . (string)$right;
            } else {
                $pending[] = [$node, true];
                $pending[] = [$node->right, false];
                $pending[] = [$node->left, false];
            }
        } else {
            return null;
        }
    }
    return $values[0];
}
