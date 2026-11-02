"""Native-first mixed declared-layout clone with reinserted dynamic keys."""

CASES = {
    'mixed-reinsert-view-cow': b"<?php\n#[AllowDynamicProperties] class Packet162 { public int $fixed = 7; }\n$left = new Packet162;\n$left->live = 1; unset($left->live); $left->live = 2;\nforeach ($left as $ignored) {}\n$view = (array)$left;\necho 'B|', $left->live, ':', $view['live'], ':', $view['fixed'], '|';\n$copy = clone $left;\necho 'C|', $left->live, ':', $copy->live, ':', $copy->fixed, '|';\n$copy->live = 3;\necho 'W|', $left->live, ':', $copy->live, ':', $view['live'], '|';\n",
    'mixed-reinsert-order-cow': b"<?php\n#[AllowDynamicProperties] class M { public int $fixed = 7; }\n$a = new M;\n$a->live = 1; $a->tail = 9; unset($a->live); $a->live = 2;\nforeach ($a as $key => $value) {} $view = (array)$a;\n$b = clone $a;\nforeach ($a as $key => $value) echo 'S', $key, ':', $value, '|';\nforeach ($b as $key => $value) echo 'C', $key, ':', $value, '|';\nunset($b->live); $b->live = 4; $b->tail = 10;\nforeach ($a as $key => $value) echo 'A', $key, ':', $value, '|';\nforeach ($b as $key => $value) echo 'B', $key, ':', $value, '|';\nforeach ($view as $key => $value) echo 'V', $key, ':', $value, '|';\n",
    'mixed-reinsert-callback-order': b"<?php\n#[AllowDynamicProperties] class M { public int $fixed = 7; function __clone(): void { echo 'K', $this->live, '|'; unset($this->live); $this->live = 8; } }\n$a = new M;\n$a->live = 1; $a->tail = 9; unset($a->live); $a->live = 2;\nforeach ($a as $key => $value) {} $view = (array)$a;\n$b = clone $a;\nforeach ($a as $key => $value) echo 'S', $key, ':', $value, '|';\nforeach ($b as $key => $value) echo 'C', $key, ':', $value, '|';\nforeach ($view as $key => $value) echo 'V', $key, ':', $value, '|';\n",
    'mixed-repeat-tombstones': b"<?php\n#[AllowDynamicProperties] class M { public int $fixed = 7; }\n$a = new M;\n$a->x = 1; unset($a->x); $a->x = 2; unset($a->x); $a->y = 9; $a->x = 3;\nforeach ($a as $key => $value) {} $b = clone $a;\nforeach ($b as $key => $value) echo $key, ':', $value, '|';\nunset($a->x); $a->x = 5;\nforeach ($a as $key => $value) echo 'A', $key, ':', $value, '|';\nforeach ($b as $key => $value) echo 'B', $key, ':', $value, '|';\n",
}

EXPECTED = {
    'mixed-reinsert-view-cow': b'B|2:2:7|C|2:2:7|W|2:3:2|',
    'mixed-reinsert-order-cow': b'Sfixed:7|Stail:9|Slive:2|Cfixed:7|Ctail:9|Clive:2|Afixed:7|Atail:9|Alive:2|Bfixed:7|Btail:10|Blive:4|Vfixed:7|Vtail:9|Vlive:2|',
    'mixed-reinsert-callback-order': b'K2|Sfixed:7|Stail:9|Slive:2|Cfixed:7|Ctail:9|Clive:8|Vfixed:7|Vtail:9|Vlive:2|',
    'mixed-repeat-tombstones': b'fixed:7|y:9|x:3|Afixed:7|Ay:9|Ax:5|Bfixed:7|By:9|Bx:3|',
}
