"""Fresh keyword static compound originals; native/model agreement required."""


CASES = [
    {
        'id': 'scoped-self-live-rhs',
        'source': '''<?php
class KeywordSelfSlotReview19 {
    public static mixed $value;
    public static function append() {
        global $rhs;
        return (self::$value .= $rhs);
    }
}
class LeftKeywordSelfReview19 {
    public static string $value = "decoy";
    public function __toString(): string {
        global $rhs;
        echo "L;";
        self::$value = "changed";
        $rhs = "after";
        return "a";
    }
}
$rhs = "before";
KeywordSelfSlotReview19::$value = new LeftKeywordSelfReview19();
$result = KeywordSelfSlotReview19::append();
echo "V:", KeywordSelfSlotReview19::$value, ";R:", $rhs, ";X:", $result,
     ";D:", LeftKeywordSelfReview19::$value, ";E;";
''',
        'expected_stdout': 'L;V:aafter;R:after;X:aafter;D:changed;E;',
        'discriminator': 'self retains the declaring caller class while its left conversion changes the live RHS and writes a decoy class slot.',
    },
    {
        'id': 'scoped-inherited-self-parent-static',
        'source': '''<?php
class KeywordParentSlotReview19 {
    public static mixed $value;
    public static function fromSelf() { return (self::$value .= "s"); }
}
class KeywordChildSlotReview19 extends KeywordParentSlotReview19 {
    public static mixed $value;
    public static function fromParent() { return (parent::$value .= "p"); }
    public static function fromStatic() { return (static::$value .= "t"); }
}
class KeywordGrandSlotReview19 extends KeywordChildSlotReview19 { public static mixed $value; }
class LeftKeywordParentReview19 {
    public function __toString(): string { echo "P;"; return "a"; }
}
class LeftKeywordChildReview19 {
    public function __toString(): string { echo "C;"; return "b"; }
}
class LeftKeywordGrandReview19 {
    public function __toString(): string { echo "G;"; return "c"; }
}
KeywordParentSlotReview19::$value = new LeftKeywordParentReview19();
$child = new LeftKeywordChildReview19();
$grand = new LeftKeywordGrandReview19();
KeywordChildSlotReview19::$value = $child;
KeywordGrandSlotReview19::$value = $grand;
$result = KeywordGrandSlotReview19::fromSelf();
echo "S:", KeywordParentSlotReview19::$value, ";X:", $result,
     ";C:", KeywordChildSlotReview19::$value === $child,
     ";G:", KeywordGrandSlotReview19::$value === $grand, ";";
KeywordParentSlotReview19::$value = new LeftKeywordParentReview19();
$result = KeywordGrandSlotReview19::fromParent();
echo "P:", KeywordParentSlotReview19::$value, ";X:", $result,
     ";C:", KeywordChildSlotReview19::$value === $child,
     ";G:", KeywordGrandSlotReview19::$value === $grand, ";";
$result = KeywordGrandSlotReview19::fromStatic();
echo "T:", KeywordGrandSlotReview19::$value, ";X:", $result,
     ";C:", KeywordChildSlotReview19::$value === $child, ";E;";
''',
        'expected_stdout': 'P;S:as;X:as;C:1;G:1;P;P:ap;X:ap;C:1;G:1;G;T:ct;X:ct;C:1;E;',
        'discriminator': 'Inherited self and parent select their lexical roots, while static selects the called grandchild and leaves the other slots intact.',
    },
    {
        'id': 'scoped-nested-called-scope-reentry',
        'source': '''<?php
class KeywordOuterBaseReview19 {
    public static mixed $value;
    public static function append() { return (static::$value .= "o"); }
}
class KeywordOuterChildReview19 extends KeywordOuterBaseReview19 { public static mixed $value; }
class KeywordInnerBaseReview19 {
    public static string $value = "i";
    public static function append() { return (static::$value .= new RightKeywordInnerReview19()); }
}
class KeywordInnerChildReview19 extends KeywordInnerBaseReview19 { public static string $value = "j"; }
class LeftKeywordOuterReview19 {
    public function __toString(): string {
        echo "O;";
        $inner = KeywordInnerChildReview19::append();
        echo "N:", $inner, ";";
        return "a";
    }
}
class RightKeywordInnerReview19 {
    public function __toString(): string { echo "I;"; return "b"; }
}
KeywordOuterBaseReview19::$value = "base";
KeywordOuterChildReview19::$value = new LeftKeywordOuterReview19();
$result = KeywordOuterChildReview19::append();
echo "B:", KeywordOuterBaseReview19::$value, ";C:", KeywordOuterChildReview19::$value,
     ";X:", $result, ";IP:", KeywordInnerBaseReview19::$value,
     ";IC:", KeywordInnerChildReview19::$value, ";E;";
''',
        'expected_stdout': 'O;I;N:jb;B:base;C:ao;X:ao;IP:i;IC:jb;E;',
        'discriminator': 'Two nested compounds retain distinct declaring/called-class selections through both conversion frames.',
    },
    {
        'id': 'scoped-private-self-shadow',
        'source': '''<?php
class KeywordPrivateBaseReview19 {
    private static mixed $value;
    public static function append() {
        self::$value = new LeftKeywordPrivateReview19();
        return (self::$value .= "b");
    }
    public static function read() { return self::$value; }
}
class KeywordPrivateChildReview19 extends KeywordPrivateBaseReview19 { public static mixed $value = "child"; }
class LeftKeywordPrivateReview19 {
    public function __toString(): string { echo "L;"; return "a"; }
}
$result = KeywordPrivateChildReview19::append();
echo "P:", KeywordPrivateBaseReview19::read(), ";C:", KeywordPrivateChildReview19::$value,
     ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;P:ab;C:child;X:ab;E;',
        'discriminator': 'self selects the private base declaration even when the called child publishes a same-name static property.',
    },
    {
        'id': 'scoped-static-reference-rebind',
        'source': '''<?php
class KeywordReferenceBaseReview19 {
    public static $value;
    public static function append() { return (static::$value .= "b"); }
}
class KeywordReferenceChildReview19 extends KeywordReferenceBaseReview19 {
    public static $value;
}
class LeftKeywordReferenceReview19 {
    public function __toString(): string {
        global $replacement;
        echo "L;";
        KeywordReferenceChildReview19::$value =& $replacement;
        return "a";
    }
}
KeywordReferenceBaseReview19::$value = "base";
KeywordReferenceChildReview19::$value = new LeftKeywordReferenceReview19();
$alias =& KeywordReferenceChildReview19::$value;
$replacement = "changed";
$result = KeywordReferenceChildReview19::append();
echo "B:", KeywordReferenceBaseReview19::$value,
     ";C:", KeywordReferenceChildReview19::$value,
     ";A:", $alias, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;B:base;C:changed;A:ab;X:ab;E;',
        'discriminator': 'static retains its originally referenced cell through a callback rebind, while the called-class row follows the replacement alias.',
    },
    {
        'id': 'scoped-instance-parent-forwarding',
        'source': '''<?php
class KeywordInstanceBaseReview19 {
    public static mixed $value;
    public function append() { return (static::$value .= "b"); }
}
class KeywordInstanceChildReview19 extends KeywordInstanceBaseReview19 {
    public static mixed $value;
    public function viaParent() { return parent::append(); }
}
class LeftKeywordInstanceReview19 {
    public function __toString(): string { echo "L;"; return "a"; }
}
KeywordInstanceBaseReview19::$value = "base";
$receiver = new KeywordInstanceChildReview19();
KeywordInstanceChildReview19::$value = new LeftKeywordInstanceReview19();
$result = $receiver->append();
echo "M:", KeywordInstanceChildReview19::$value, ";X:", $result,
     ";B:", KeywordInstanceBaseReview19::$value, ";";
KeywordInstanceChildReview19::$value = new LeftKeywordInstanceReview19();
$result = $receiver->viaParent();
echo "P:", KeywordInstanceChildReview19::$value, ";X:", $result,
     ";B:", KeywordInstanceBaseReview19::$value, ";E;";
''',
        'expected_stdout': 'L;M:ab;X:ab;B:base;L;P:ab;X:ab;B:base;E;',
        'discriminator': 'Instance and parent-forwarded method calls retain their called child for static selection while preserving the base slot.',
    },
]
