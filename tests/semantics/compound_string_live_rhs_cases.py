"""Fresh live-RHS compound originals; predictions require exact native/model checks."""


CASES = [
    {
        'id': 'compound-concat-live-rhs-cv',
        'source': '''<?php
class LeftLiveRhsReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = "after";
        return "a";
    }
}
$rhs = "before";
$target = new LeftLiveRhsReview19();
$target .= $rhs;
echo "V:", $target, ";R:", $rhs, ";E;";
''',
        'expected_stdout': 'L;V:aafter;R:after;E;',
        'discriminator': 'A defined RHS CV is read after the left conversion mutates its binding.',
    },
    {
        'id': 'compound-concat-rhs-temp-copy',
        'source': '''<?php
class LeftTempRhsReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = "after";
        return "a";
    }
}
function evaluatedRhsReview19() {
    global $rhs;
    echo "Q;";
    return $rhs;
}
$rhs = "before";
$target = new LeftTempRhsReview19();
$target .= evaluatedRhsReview19();
echo "V:", $target, ";R:", $rhs, ";E;";
''',
        'expected_stdout': 'Q;L;V:abefore;R:after;E;',
        'discriminator': 'A helper-evaluated RHS value remains a copy despite mutation of its source variable.',
    },
    {
        'id': 'compound-concat-rhs-reference-rebind',
        'source': '''<?php
class LeftRebindRhsReview19 {
    public function __toString(): string {
        echo "L;";
        unset($GLOBALS['rhs']);
        $GLOBALS['rhs'] = "after";
        return "a";
    }
}
$rhs = "before";
$alias =& $rhs;
$target = new LeftRebindRhsReview19();
$target .= $rhs;
echo "V:", $target, ";A:", $alias, ";R:", $rhs, ";E;";
''',
        'expected_stdout': 'L;V:aafter;A:before;R:after;E;',
        'discriminator': 'A borrowed CV follows its new binding after unsetting; the earlier alias retains its old cell.',
    },
    {
        'id': 'compound-concat-rhs-object-replacement',
        'source': '''<?php
class BeforeRhsReview19 {
    public function __toString(): string { echo "O;"; return "before"; }
    public function __destruct() { echo "D:before;"; }
}
class AfterRhsReview19 {
    public function __toString(): string { echo "N;"; return "after"; }
    public function __destruct() { echo "D:after;"; }
}
class LeftReplaceRhsReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = new AfterRhsReview19();
        echo "P;";
        return "a";
    }
}
$rhs = new BeforeRhsReview19();
$target = new LeftReplaceRhsReview19();
$target .= $rhs;
echo "V:", $target, ";";
unset($rhs);
echo "E;";
''',
        'expected_stdout': 'L;D:before;P;N;V:aafter;D:after;E;',
        'discriminator': 'The old RHS object has no compound-task owner; it dies inside the left callback and the replacement is converted.',
    },
    {
        'id': 'compound-concat-rhs-late-unset',
        'source': '''<?php
class LeftUnsetRhsReview19 {
    public function __toString(): string {
        echo "L;";
        unset($GLOBALS['rhs']);
        return "a";
    }
}
$rhs = "before";
$target = new LeftUnsetRhsReview19();
$target .= $rhs;
echo "V:", $target, ";E;";
''',
        'expected_stdout': 'L;V:a;E;',
        'discriminator': 'A CV that becomes undefined during conversion contributes empty bytes without a second warning.',
    },
    {
        'id': 'compound-concat-rhs-initial-undef',
        'source': '''<?php
class LeftMissingRhsReview19 {
    public function __toString(): string {
        echo "L;";
        $GLOBALS['rhs'] = "after";
        return "a";
    }
}
$target = new LeftMissingRhsReview19();
@($target .= $rhs);
echo "V:", $target, ";R:", $rhs, ";E;";
''',
        'expected_stdout': 'L;V:a;R:after;E;',
        'discriminator': 'An initially undefined RHS is latched null even when the left callback creates that variable.',
    },
    {
        'id': 'compound-concat-self-reference-control',
        'source': '''<?php
class LeftSelfRhsReview19 {
    public function __toString(): string {
        echo "L;";
        $GLOBALS['target'] = "after";
        return "a";
    }
}
$target = new LeftSelfRhsReview19();
$target .= $target;
echo "N:", $target, ";";
$target = new LeftSelfRhsReview19();
$alias =& $target;
$target .= $target;
echo "R:", $target, ";A:", $alias, ";E;";
''',
        'expected_stdout': 'L;N:aa;L;R:aafter;A:aafter;E;',
        'discriminator': 'The identical plain-CV fast path reuses left bytes, while a reference LHS and RHS have distinct pointers.',
    },
    {
        'id': 'compound-concat-rhs-object-temp-owner',
        'source': '''<?php
class BeforeTempRhsReview19 {
    public function __toString(): string { echo "O;"; return "before"; }
    public function __destruct() { echo "D:before;"; }
}
class AfterTempRhsReview19 {
    public function __toString(): string { echo "N;"; return "after"; }
    public function __destruct() { echo "D:after;"; }
}
class LeftObjectTempRhsReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = new AfterTempRhsReview19();
        echo "P;";
        return "a";
    }
    public function __destruct() { echo "D:left;"; }
}
function copiedObjectRhsReview19() {
    global $rhs;
    echo "Q;";
    return $rhs;
}
$rhs = new BeforeTempRhsReview19();
$target = new LeftObjectTempRhsReview19();
$target .= copiedObjectRhsReview19();
echo "V:", $target, ";";
unset($rhs);
echo "E;";
''',
        'expected_stdout': 'Q;L;P;O;D:left;D:before;V:abefore;D:after;E;',
        'discriminator': 'A copied object RHS stays owned through destination write and dies after the old left object.',
    },
    {
        'id': 'compound-concat-live-rhs-dimension-property',
        'source': '''<?php
class LeftPlaceRhsReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = "after";
        return "a";
    }
}
class CompoundHolderReview19 { public $slot; }
$rhs = "before";
$array = ['k' => new LeftPlaceRhsReview19()];
$array['k'] .= $rhs;
echo "D:", $array['k'], ";";
$rhs = "before";
$holder = new CompoundHolderReview19();
$holder->slot = new LeftPlaceRhsReview19();
$holder->slot .= $rhs;
echo "P:", $holder->slot, ";R:", $rhs, ";E;";
''',
        'expected_stdout': 'L;D:aafter;L;P:aafter;R:after;E;',
        'discriminator': 'Ordinary array-element and plain-property compound opcodes both read the RHS CV after left conversion.',
    },
    {
        'id': 'compound-concat-rhs-reference-return-owner',
        'source': '''<?php
class LeftReturnedRhsReview19 {
    public function __toString(): string {
        echo "L;";
        unset($GLOBALS['rhs']);
        $GLOBALS['rhs'] = "after";
        return "a";
    }
}
function &referenceRhsReview19() {
    global $rhs;
    echo "Q;";
    return $rhs;
}
$rhs = "before";
$target = new LeftReturnedRhsReview19();
$target .= referenceRhsReview19();
echo "V:", $target, ";R:", $rhs, ";E;";
''',
        'expected_stdout': 'Q;L;V:abefore;R:after;E;',
        'discriminator': 'An accepted untyped reference-return helper preserves its received RHS cell across caller CV removal and rebinding.',
    },
    {
        'id': 'compound-concat-late-left-alias',
        'source': '''<?php
class LeftLateAliasReview19 {
    public function __toString(): string {
        echo "L;";
        $GLOBALS['alias'] =& $GLOBALS['target'];
        $GLOBALS['target'] = "changed";
        return "a";
    }
}
$rhs = "b";
$target = new LeftLateAliasReview19();
$target .= $rhs;
echo "V:", $target, ";A:", $alias, ";E;";
''',
        'expected_stdout': 'L;V:ab;A:changed;E;',
        'discriminator': 'The initial unreferenced destination CV remains the final result slot after the left callback creates an alias.',
    },
]
