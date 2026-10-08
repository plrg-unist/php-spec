"""Fresh static-selector compound originals; native/model agreement required."""


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
    {
        'id': 'dynamic-class-live-rhs',
        'source': '''<?php
class DynamicStaticFirstReview19 { public static mixed $value; }
class DynamicStaticSecondReview19 { public static mixed $value = "other"; }
class LeftDynamicStaticReview19 {
    public function __toString(): string {
        global $class, $rhs;
        echo "L;";
        $class = "DynamicStaticSecondReview19";
        $rhs = "after";
        return "a";
    }
}
$class = "DynamicStaticFirstReview19";
$rhs = "before";
DynamicStaticFirstReview19::$value = new LeftDynamicStaticReview19();
$result = ($class::$value .= $rhs);
echo "A:", DynamicStaticFirstReview19::$value,
     ";B:", DynamicStaticSecondReview19::$value,
     ";C:", $class, ";R:", $rhs, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;A:aafter;B:other;C:DynamicStaticSecondReview19;R:after;X:aafter;E;',
        'discriminator': 'The class CV changes during left conversion, while final store and expression result retain the class selected for the original property fetch; the RHS CV stays live.',
    },
    {
        'id': 'dynamic-rhs-rebind-before-capture',
        'source': '''<?php
class DynamicRhsFirstReview19 { public static mixed $value; }
class DynamicRhsSecondReview19 { public static mixed $value = "other"; }
class LeftDynamicRhsReview19 {
    public function __toString(): string { echo "L;"; return "a"; }
}
function dynamicRhsRebindReview19() {
    global $class;
    echo "R;";
    $class = "DynamicRhsSecondReview19";
    return "b";
}
$class = "DynamicRhsFirstReview19";
DynamicRhsFirstReview19::$value = new LeftDynamicRhsReview19();
$result = ($class::$value .= dynamicRhsRebindReview19());
echo "A:", DynamicRhsFirstReview19::$value,
     ";B:", DynamicRhsSecondReview19::$value,
     ";C:", $class, ";X:", $result, ";E;";
''',
        'expected_stdout': 'R;L;A:ab;B:other;C:DynamicRhsSecondReview19;X:ab;E;',
        'discriminator': 'The class CV changes during RHS evaluation, before compound capture, while the final destination remains the class selected by FETCH_CLASS.',
    },
    {
        'id': 'dynamic-helper-string-once',
        'source': '''<?php
class DynamicHelperFirstReview19 { public static mixed $value; }
class DynamicHelperSecondReview19 { public static mixed $value = "other"; }
class LeftDynamicHelperReview19 {
    public function __toString(): string {
        global $class, $rhs;
        echo "L;";
        $class = "DynamicHelperSecondReview19";
        $rhs = "after";
        return "a";
    }
}
function dynamicStringSelectorReview19() {
    global $class, $calls;
    echo "C;";
    $calls++;
    return $class;
}
$class = "DynamicHelperFirstReview19";
$calls = 0;
$rhs = "before";
DynamicHelperFirstReview19::$value = new LeftDynamicHelperReview19();
$result = (dynamicStringSelectorReview19()::$value .= $rhs);
echo "A:", DynamicHelperFirstReview19::$value,
     ";B:", DynamicHelperSecondReview19::$value,
     ";C:", $class, ";R:", $rhs, ";N:", $calls, ";X:", $result, ";";
$class = "DynamicHelperFirstReview19";
DynamicHelperFirstReview19::$value = "x";
$scalar = ($class::$value .= "y");
DynamicHelperFirstReview19::$value = "overwritten";
echo "S:", $scalar, ";F:", DynamicHelperFirstReview19::$value,
     ";B:", DynamicHelperSecondReview19::$value, ";E;";
''',
        'expected_stdout': 'C;L;A:aafter;B:other;C:DynamicHelperSecondReview19;R:after;N:1;X:aafter;S:xy;F:overwritten;B:other;E;',
        'discriminator': 'An untyped helper supplies the class string once; callback changes cannot re-evaluate that helper or redirect the retained destination. A scalar-only dynamic CONCAT then returns copied xy, survives destination overwrite, and must bypass selected Stringable ENTRY creation.',
    },
    {
        'id': 'dynamic-tmp-object-selector-release',
        'source': '''<?php
class DynamicObjectFirstReview19 {
    public static mixed $value;
    public function __destruct() { echo "Q;"; }
}
class DynamicObjectSecondReview19 { public static mixed $value = "other"; }
class LeftDynamicObjectReview19 {
    public function __toString(): string { echo "L;"; return "a"; }
}
function dynamicObjectSelectorReview19() {
    echo "C;";
    return new DynamicObjectFirstReview19();
}
function dynamicObjectRhsReview19() { echo "R;"; return "b"; }
DynamicObjectFirstReview19::$value = new LeftDynamicObjectReview19();
$result = (dynamicObjectSelectorReview19()::$value .= dynamicObjectRhsReview19());
echo "A:", DynamicObjectFirstReview19::$value,
     ";B:", DynamicObjectSecondReview19::$value, ";X:", $result, ";E;";
''',
        'expected_stdout': 'C;Q;R;L;A:ab;B:other;X:ab;E;',
        'discriminator': 'FETCH_CLASS consumes and releases its temporary object selector before RHS evaluation, while nonowning class metadata survives through Stringable conversion.',
    },
    {
        'id': 'dynamic-captured-reference-rebind',
        'source': '''<?php
class DynamicAliasFirstReview19 { public static $value; }
class DynamicAliasSecondReview19 { public static $value = "other"; }
class LeftDynamicAliasReview19 {
    public function __toString(): string {
        global $class, $replacement;
        echo "L;";
        DynamicAliasFirstReview19::$value =& $replacement;
        $class = "DynamicAliasSecondReview19";
        return "a";
    }
}
$class = "DynamicAliasFirstReview19";
$replacement = "changed";
DynamicAliasFirstReview19::$value = new LeftDynamicAliasReview19();
$alias =& DynamicAliasFirstReview19::$value;
$result = ($class::$value .= "b");
echo "A:", DynamicAliasFirstReview19::$value,
     ";B:", DynamicAliasSecondReview19::$value,
     ";O:", $alias, ";C:", $class, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;A:changed;B:other;O:ab;C:DynamicAliasSecondReview19;X:ab;E;',
        'discriminator': 'Dynamic selected ENTRY retains the originally referenced cell through class-CV and property-row rebinding; final raw backing and expression result follow that captured cell.',
    },
]
