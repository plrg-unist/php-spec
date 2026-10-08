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
class DynamicTypedFirstReview19 { public static int $value = 1; }
class DynamicTypedSecondReview19 { public static int $value = 9; }
class RightDynamicTypedReview19 {
    public function __toString(): string {
        global $class;
        echo "T;";
        $class = "DynamicTypedSecondReview19";
        return "2";
    }
}
$class = "DynamicAliasFirstReview19";
$replacement = "changed";
DynamicAliasFirstReview19::$value = new LeftDynamicAliasReview19();
$alias =& DynamicAliasFirstReview19::$value;
$result = ($class::$value .= "b");
echo "A:", DynamicAliasFirstReview19::$value,
     ";B:", DynamicAliasSecondReview19::$value,
     ";O:", $alias, ";C:", $class, ";X:", $result, ";";
$class = "DynamicTypedFirstReview19";
$typedAlias =& DynamicTypedFirstReview19::$value;
$typedResult = ($class::$value .= new RightDynamicTypedReview19());
echo "V:", DynamicTypedFirstReview19::$value, ";I:", DynamicTypedFirstReview19::$value === 12,
     ";A:", $typedAlias, ";J:", $typedAlias === 12,
     ";X:", $typedResult, ";K:", $typedResult === 12,
     ";B:", DynamicTypedSecondReview19::$value, ";C:", $class, ";E;";
''',
        'expected_stdout': 'L;A:changed;B:other;O:ab;C:DynamicAliasSecondReview19;X:ab;T;V:12;I:1;A:12;J:1;X:12;K:1;B:9;C:DynamicTypedSecondReview19;E;',
        'discriminator': 'Dynamic selected ENTRY retains the originally referenced cell through class-CV and property-row rebinding; final raw backing and expression result follow that captured cell. A second dynamic selection keeps a captured typed-int REF, verifies 12 and returns its integer result after the RHS changes the class CV.',
    },
    {
        'id': 'computed-property-live-rhs',
        'source': '''<?php
class ComputedStaticSlotReview19 {
    public static mixed $value;
    public static mixed $other = "other";
}
class LeftComputedStaticReview19 {
    public function __toString(): string {
        global $property, $rhs;
        echo "L;";
        $property = "other";
        $rhs = "after";
        return "a";
    }
}
$property = "value";
$rhs = "before";
ComputedStaticSlotReview19::$value = new LeftComputedStaticReview19();
$result = (ComputedStaticSlotReview19::${$property} .= $rhs);
echo "V:", ComputedStaticSlotReview19::$value,
     ";O:", ComputedStaticSlotReview19::$other,
     ";P:", $property, ";R:", $rhs, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;V:aafter;O:other;P:other;R:after;X:aafter;E;',
        'discriminator': 'A computed static property name is selected before left conversion. Changing the property CV and live RHS during conversion retains the original slot and returns the completed expression value.',
    },
    {
        'id': 'computed-property-cv-tmp-timing',
        'source': '''<?php
class ComputedTimingSlotReview19 {
    public static mixed $value;
    public static mixed $other;
}
class LeftComputedValueReview19 {
    public function __toString(): string { echo "A;"; return "a"; }
}
class LeftComputedOtherReview19 {
    public function __toString(): string { echo "B;"; return "b"; }
}
function computedTimingRhsReview19() {
    global $property;
    echo "R;";
    $property = "other";
    return "s";
}
function computedTimingNameReview19() {
    global $property;
    echo "N;";
    return $property;
}
$original = new LeftComputedValueReview19();
ComputedTimingSlotReview19::$value = $original;
ComputedTimingSlotReview19::$other = new LeftComputedOtherReview19();
$property = "value";
$result = (ComputedTimingSlotReview19::${$property} .= computedTimingRhsReview19());
echo "V:", ComputedTimingSlotReview19::$value === $original,
     ";O:", ComputedTimingSlotReview19::$other,
     ";P:", $property, ";X:", $result, ";";
$unchangedOther = new LeftComputedOtherReview19();
ComputedTimingSlotReview19::$value = new LeftComputedValueReview19();
ComputedTimingSlotReview19::$other = $unchangedOther;
$property = "value";
$result = (ComputedTimingSlotReview19::${computedTimingNameReview19()} .= computedTimingRhsReview19());
echo "V:", ComputedTimingSlotReview19::$value,
     ";O:", ComputedTimingSlotReview19::$other === $unchangedOther,
     ";P:", $property, ";X:", $result, ";E;";
''',
        'expected_stdout': 'R;B;V:1;O:bs;P:other;X:bs;N;R;A;V:as;O:1;P:other;X:as;E;',
        'discriminator': 'The direct property CV is read by the final static opcode after RHS effects, while an evaluated property-name helper returns a copied TMP before RHS evaluation. Both retain their selected slots through conversion.',
    },
    {
        'id': 'computed-property-cold-default',
        'source': '''<?php
class ColdComputedSlotReview19 {
    public const BASE = "a";
    public const OTHER = "o";
    public static string $value = self::BASE;
    public static string $other = self::OTHER;
}
class RightColdComputedReview19 {
    public function __toString(): string {
        global $property;
        echo "B;";
        $property = "other";
        return "b";
    }
    public function __destruct() { echo "D;"; }
}
$property = "value";
$result = (
    ColdComputedSlotReview19::${"value"}
    .= new RightColdComputedReview19()
);
echo "V:", ColdComputedSlotReview19::$value,
     ";O:", ColdComputedSlotReview19::$other,
     ";P:", $property, ";X:", $result, ";E;";
''',
        'expected_stdout': 'B;D;V:ab;O:o;P:other;X:ab;E;',
        'discriminator': 'Cold static defaults and a compiled constant computed name require genuine class-data preparation before capture. The evaluated RHS object survives queued work, changes an unrelated name CV during conversion, and retires after the final store. The multiline fetch tests the fetch/opcode source handoff.',
    },
    {
        'id': 'computed-property-reference-name',
        'source': '''<?php
class ComputedNameReferenceSlotReview19 {
    public static $value;
    public static $other = "other";
}
class LeftComputedNameReferenceReview19 {
    public function __toString(): string {
        global $replacement;
        echo "L;";
        ComputedNameReferenceSlotReview19::$value =& $replacement;
        return "a";
    }
}
function &computedReferenceNameReview19() {
    global $property;
    echo "N;";
    return $property;
}
function computedReferenceRhsReview19() {
    echo "R;";
    unset($GLOBALS['property']);
    $GLOBALS['property'] = "other";
    return "b";
}
$property = "value";
$oldName =& $property;
$replacement = "changed";
ComputedNameReferenceSlotReview19::$value = new LeftComputedNameReferenceReview19();
$alias =& ComputedNameReferenceSlotReview19::$value;
$result = (ComputedNameReferenceSlotReview19::${computedReferenceNameReview19()} .= computedReferenceRhsReview19());
echo "V:", ComputedNameReferenceSlotReview19::$value,
     ";A:", $alias, ";O:", ComputedNameReferenceSlotReview19::$other,
     ";N:", $oldName, ";P:", $property, ";X:", $result, ";";
class ComputedDefinedNameSlotReview19 { public static mixed $value; }
class LeftComputedDefinedNameReview19 {
    public function __toString(): string { echo "D;"; return "c"; }
}
function computedDefineNameRhsReview19() {
    global $undefinedName;
    echo "R;";
    $undefinedName = "value";
    return "d";
}
ComputedDefinedNameSlotReview19::$value = new LeftComputedDefinedNameReview19();
$result = (ComputedDefinedNameSlotReview19::${$undefinedName} .= computedDefineNameRhsReview19());
echo "V:", ComputedDefinedNameSlotReview19::$value, ";N:", $undefinedName,
     ";X:", $result, ";E;";
''',
        'expected_stdout': 'N;R;L;V:changed;A:ab;O:other;N:value;P:other;X:ab;R;D;V:cd;N:value;X:cd;E;',
        'discriminator': 'An accepted untyped by-reference name helper retains its original cell across RHS unset/rebind; the selected static alias retains its original cell across conversion rebind. An initially absent name CV becomes defined by RHS before its delayed read, so no early warning is emitted.',
    },
    {
        'id': 'computed-property-selected-roots',
        'source': '''<?php
class ComputedDynamicRootReview19 {
    public static $value = "base";
    public static $other;
}
class ComputedDynamicDecoyReview19 {
    public static $value = "decoy-value";
    public static $other = "decoy-other";
}
class LeftComputedDynamicRootReview19 {
    public function __toString(): string {
        global $class, $property, $replacement;
        echo "L;";
        $class = "ComputedDynamicDecoyReview19";
        $property = "value";
        ComputedDynamicRootReview19::$other =& $replacement;
        return "a";
    }
}
function computedDynamicRootRhsReview19() {
    global $class, $property;
    echo "R;";
    $class = "ComputedDynamicDecoyReview19";
    $property = "other";
    return "b";
}
$class = "ComputedDynamicRootReview19";
$property = "value";
$replacement = "changed";
ComputedDynamicRootReview19::$other = new LeftComputedDynamicRootReview19();
$alias =& ComputedDynamicRootReview19::$other;
$result = ($class::${$property} .= computedDynamicRootRhsReview19());
echo "B:", ComputedDynamicRootReview19::$value,
     ";O:", ComputedDynamicRootReview19::$other, ";A:", $alias,
     ";DV:", ComputedDynamicDecoyReview19::$value,
     ";DO:", ComputedDynamicDecoyReview19::$other,
     ";C:", $class, ";P:", $property, ";X:", $result, ";";
class ComputedKeywordRootReview19 {
    public static int $value = 1;
    public static int $other = 2;
    public static function append() {
        global $property;
        return (static::${$property} .= new RightComputedKeywordRootReview19());
    }
}
class ComputedKeywordChildReview19 extends ComputedKeywordRootReview19 {
    public static int $value = 7;
    public static int $other = 9;
}
class RightComputedKeywordRootReview19 {
    public function __toString(): string {
        global $property;
        echo "T;";
        $property = "other";
        return "2";
    }
}
$property = "value";
$result = ComputedKeywordChildReview19::append();
echo "PB:", ComputedKeywordRootReview19::$value,
     ";V:", ComputedKeywordChildReview19::$value,
     ";O:", ComputedKeywordChildReview19::$other,
     ";P:", $property, ";X:", $result, ";I:", ($result === 72), ";E;";
''',
        'expected_stdout': 'R;L;B:base;O:changed;A:ab;DV:decoy-value;DO:decoy-other;C:ComputedDynamicDecoyReview19;P:value;X:ab;T;PB:1;V:72;O:9;P:other;X:72;I:1;E;',
        'discriminator': 'A dynamic class is selected before RHS while the computed name CV is read afterward; its captured static alias survives conversion rebind. An ordinary static:: method selects the called child and returns the verified typed integer result despite name mutation during conversion.',
    },
    {
        'id': 'computed-property-preentry-cleanup',
        'source': '''<?php
class RightComputedPreentryReview19 {
    public function __toString(): string { echo "B;"; return "b"; }
    public function __destruct() { echo "D;"; }
}
class ComputedPreentrySlotReview19 { public static string $value; }
$property = "value";
echo "C;";
try {
    MissingComputedPreentryClassReview19::${$property}
    .= new RightComputedPreentryReview19();
} catch (Error $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
echo "N;";
$property = "absent";
try {
    ComputedPreentrySlotReview19::${$property}
    .= new RightComputedPreentryReview19();
} catch (Error $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
echo "U;";
$property = "value";
try {
    ComputedPreentrySlotReview19::${$property}
    .= new RightComputedPreentryReview19();
} catch (Error $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
class ComputedColdFailureSlotReview19 {
    public static string $value = self::MISSING;
}
echo "K;";
$property = "value";
try {
    ComputedColdFailureSlotReview19::${$property}
    .= new RightComputedPreentryReview19();
} catch (Error $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
echo "E;";
''',
        'expected_stdout': 'C;D;X:Class "MissingComputedPreentryClassReview19" not found:10;N;D;X:Access to undeclared static property ComputedPreentrySlotReview19::$absent:18;U;D;X:Typed static property ComputedPreentrySlotReview19::$value must not be accessed before initialization:26;K;D;X:Undefined constant self::MISSING:32;E;',
        'discriminator': 'Missing named class, missing computed property, and uninitialized typed property errors occur after RHS evaluation but before Stringable conversion; each evaluated temporary RHS is released during the catchable preentry failure. Fetch and RHS appear on distinct lines; Error.getLine forecasts the delayed static-fetch line, pending native observation.',
    },
]
