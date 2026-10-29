"""Reached-cycle originals retained as refusal controls, not agreements."""
from throwable_previous_graph_cases import CASES as PREVIOUS_CASES

CASES = {
    'visited-cell-cycle-control': PREVIOUS_CASES['cell-cycle-control'],
    'active-cycle-before-count-control': b"<?php\nfunction activeChild147($x): TypeError { return new TypeError('inner', 7); }\n$left = new stdClass; $right = new stdClass; $other = new stdClass; $left->next = $left; $right->next = $other; $other->next = 0; $other->extra = 0;\n$p = activeChild147($left); $q = activeChild147($right);\n$a = new RuntimeException('root', 7, $p); $b = new RuntimeException('root', 7, $q);\necho 'B|'; try { echo $a <=> $b, '|'; } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\n",
}
