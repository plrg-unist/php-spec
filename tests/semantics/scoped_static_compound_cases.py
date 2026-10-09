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
    {
        'id': 'stringable-property-name-temp',
        'source': '''<?php
class StringableNameSlotReview19 {
    public static mixed $value = "a";
    public static mixed $other = "other";
}
class StringableComputedNameReview19 {
    public function __toString(): string {
        global $property, $rhs;
        echo "N;";
        $property = "other";
        $rhs = "after";
        return "value";
    }
    public function __destruct() { echo "D;"; }
}
function stringableComputedNameReview19() {
    echo "H;";
    return new StringableComputedNameReview19();
}
$property = "value";
$rhs = "before";
$result = (StringableNameSlotReview19::${stringableComputedNameReview19()} .= $rhs);
echo "V:", StringableNameSlotReview19::$value,
     ";O:", StringableNameSlotReview19::$other,
     ";P:", $property, ";R:", $rhs, ";X:", $result, ";E;";
''',
        'expected_stdout': 'H;N;D;V:aafter;O:other;P:other;R:after;X:aafter;E;',
        'discriminator': 'A helper-returned NAME temporary casts once, changes the live RHS/name CV, then retires before the primitive static compound read and copied expression result.',
    },
    {
        'id': 'stringable-property-name-borrowed-cv',
        'source': '''<?php
class BorrowedNameSlotReview19 {
    public static mixed $value = "a";
    public static mixed $other = "o";
}
class BorrowedNameReview19 {
    public function __toString(): string {
        global $property, $rhs;
        echo "N;";
        $property = "other";
        $rhs = "after";
        echo "B;";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        $rhs = "retired";
    }
}
$property = new BorrowedNameReview19();
$rhs = "before";
$result = (BorrowedNameSlotReview19::${$property} .= $rhs);
echo "V:", BorrowedNameSlotReview19::$value,
     ";O:", BorrowedNameSlotReview19::$other,
     ";P:", $property, ";R:", $rhs, ";X:", $result, ";E;";
''',
        'expected_stdout': 'N;B;D;V:aretired;O:o;P:other;R:retired;X:aretired;E;',
        'discriminator': 'The cast receiver survives replacement of its borrowed NAME CV through the rest of the method; its final destructor changes the RHS before the selected property is read.',
    },
    {
        'id': 'stringable-property-name-slot-rebind',
        'source': '''<?php
class NameRebindSlotReview19 {
    public static mixed $value = "a";
}
class NameTypedRebindSlotReview19 {
    public static int $value = 1;
}
class NameRebindReview19 {
    public function __toString(): string {
        global $mode, $class;
        echo "N;";
        if ($mode === 1) { $class = "NameTypedRebindSlotReview19"; }
        return "value";
    }
    public function __destruct() {
        global $mode, $alias, $replacement, $rhs;
        echo "D;";
        if ($mode === 1) {
            NameRebindSlotReview19::$value =& $alias;
            $rhs = "b";
        } else {
            NameTypedRebindSlotReview19::$value =& $replacement;
            $rhs = "2";
        }
    }
}
function nameRebindReview19() { return new NameRebindReview19(); }
$mode = 1;
$class = "NameRebindSlotReview19";
$alias = "old";
$replacement = 7;
$rhs = "before";
echo "1;";
$first = ($class::${nameRebindReview19()} .= $rhs);
echo "V:", NameRebindSlotReview19::$value, ";A:", $alias,
     ";C:", $class, ";X:", $first, ";";
$mode = 2;
$original = 1;
NameTypedRebindSlotReview19::$value =& $original;
$rhs = "before";
echo "2;";
$second = (NameTypedRebindSlotReview19::${nameRebindReview19()} .= $rhs);
echo "V:", NameTypedRebindSlotReview19::$value, ";A:", $original,
     ";B:", $replacement, ";X:", $second, ";I:", ($second === 72), ";E;";
''',
        'expected_stdout': '1;N;D;V:oldb;A:oldb;C:NameTypedRebindSlotReview19;X:oldb;2;N;D;V:72;A:1;B:72;X:72;I:1;E;',
        'discriminator': 'A NAME temporary destructor changes the selected row alias before compound capture, with dynamic class mutation preserving the original root. A typed reference rebind updates the new cell and returns integer72 while the old cell stays1.',
    },
    {
        'id': 'stringable-property-name-errors-cleanup',
        'source': '''<?php
class NameErrorSlotReview19 {
    public static int $value;
}
class NameErrorReview19 {
    public function __toString(): string {
        global $chosen, $nameException;
        echo "N;";
        if ($chosen === "throw") { throw $nameException; }
        return $chosen;
    }
    public function __destruct() { echo "D;"; }
}
class NameErrorRightReview19 {
    public function __toString(): string { echo "B;"; return "b"; }
    public function __destruct() { echo "R;"; }
}
function nameErrorReview19() { echo "H;"; return new NameErrorReview19(); }
function nameErrorRightReview19() { echo "Q;"; return new NameErrorRightReview19(); }
$nameException = new Exception("name");
$chosen = "value";
echo "C;";
try {
    MissingNameErrorClassReview19::${nameErrorReview19()}
        .= nameErrorRightReview19();
} catch (Throwable $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
$chosen = "absent";
echo "P;";
try {
    NameErrorSlotReview19::${nameErrorReview19()}
        .= nameErrorRightReview19();
} catch (Throwable $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
$chosen = "value";
echo "U;";
try {
    NameErrorSlotReview19::${nameErrorReview19()}
        .= nameErrorRightReview19();
} catch (Throwable $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
$chosen = "throw";
echo "T;";
try {
    NameErrorSlotReview19::${nameErrorReview19()}
        .= nameErrorRightReview19();
} catch (Throwable $error) {
    echo "X:", $error->getMessage(), ":", $error->getLine(), ";";
}
class NamePendingSlotReview19 {
    public static mixed $value = "a";
}
class NamePendingReview19 {
    public function __toString(): string { echo "N;"; return "value"; }
    public function __destruct() {
        global $pendingNameException, $rhs;
        echo "D;";
        $rhs = "after";
        throw $pendingNameException;
    }
}
function namePendingReview19() { echo "H;"; return new NamePendingReview19(); }
$pendingNameException = new Exception("free");
$rhs = "before";
$pendingResult = "sentinel";
echo "F;";
try {
    $pendingResult = (NamePendingSlotReview19::${namePendingReview19()} .= $rhs);
} catch (Throwable $error) {
    echo "X:", $error->getMessage(), ";";
}
echo "V:", NamePendingSlotReview19::$value,
     ";R:", $rhs, ";Z:", $pendingResult, ";E;";
''',
        'expected_stdout': 'C;H;Q;D;R;X:Class "MissingNameErrorClassReview19" not found:24;P;H;Q;N;D;R;X:Access to undeclared static property NameErrorSlotReview19::$absent:32;U;H;Q;N;D;R;X:Typed static property NameErrorSlotReview19::$value must not be accessed before initialization:40;T;H;Q;N;D;R;X:Access to undeclared static property NameErrorSlotReview19::$:48;F;H;N;D;X:free;V:aafter;R:after;Z:sentinel;E;',
        'discriminator': 'Class/read-access/uninitialized failures release evaluated NAME then RHS. Throwing NAME conversion is replaced by empty-property lookup Error. A pending NAME destructor exception still permits scalar compound store before catch, but aborts the outer result assignment.',
    },
    {
        'id': 'stringable-property-name-cold-owners',
        'source': '''<?php
class ColdStringableNameSlotReview19 {
    public const BASE = "a";
    public const OTHER = "o";
    public static string $value = self::BASE;
    public static string $other = self::OTHER;
    public static function run() {
        global $property;
        $result = (static::${coldStringableNameReview19()} .= coldStringableNameRightReview19());
        echo "V:", static::$value, ";A:", self::$value,
             ";O:", static::$other, ";P:", $property, ";X:", $result, ";E;";
    }
}
class ColdStringableNameChildReview19 extends ColdStringableNameSlotReview19 {
    public const BASE = "c";
    public static string $value = self::BASE;
}
class ColdStringableNameReview19 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        echo "D:", ColdStringableNameChildReview19::$value, ";";
        ColdStringableNameChildReview19::$value = "d";
    }
}
class ColdStringableNameRightReview19 {
    public function __toString(): string {
        echo "B:", ColdStringableNameChildReview19::$value, ";";
        return "b";
    }
    public function __destruct() {
        echo "R:", ColdStringableNameChildReview19::$value, ";";
    }
}
function coldStringableNameReview19() { echo "H;"; return new ColdStringableNameReview19(); }
function coldStringableNameRightReview19() { echo "Q;"; return new ColdStringableNameRightReview19(); }
$property = "value";
ColdStringableNameChildReview19::run();
''',
        'expected_stdout': 'H;Q;N;D:c;B:d;R:db;V:db;A:a;O:o;P:other;X:db;E;',
        'discriminator': 'An inherited static:: method selects the called child through NAME conversion and deferred defaults; NAME retirement changes its current value before RHS conversion, while the owned RHS temporary survives through final store.',
    },
    {
        'id': 'stringable-property-name-pending-paths',
        'source': r'''<?php
class NamePendingTypedSlotReview19 { public static int $value = 7; }
class NamePendingMixedSlotReview19 { public static mixed $value = "a"; }
class NamePendingReview19 {
    public function __toString(): string { echo "N;"; return "value"; }
    public function __destruct() {
        global $mode, $rhs, $pending;
        echo "D;";
        if ($mode === 1) { $rhs = "2"; }
        if ($mode === 2) { $rhs = "x"; }
        if ($mode === 4) { $rhs = ["x"]; }
        throw $pending;
    }
}
class NamePendingRightReview19 {
    public function __toString(): string { echo "B;"; return "b"; }
    public function __destruct() { echo "R;"; }
}
function pendingNameReview19() { echo "H;"; return new NamePendingReview19(); }
function pendingRightReview19() { echo "Q;"; return new NamePendingRightReview19(); }
$mode = 1;
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "S;";
try { $result = (NamePendingTypedSlotReview19::${pendingNameReview19()} .= $rhs); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingTypedSlotReview19::$value, ";I:", (NamePendingTypedSlotReview19::$value === 72), ";Z:", $result, ";";
$mode = 2;
NamePendingTypedSlotReview19::$value = 7;
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "T;";
try { $result = (NamePendingTypedSlotReview19::${pendingNameReview19()} .= $rhs); }
catch (Throwable $e) {
    echo "X:", ($e instanceof TypeError), ":";
    $previous = $e->getPrevious();
    if ($previous === null) { echo "none"; } else { echo $previous->getMessage(); }
    echo ";";
}
echo "V:", NamePendingTypedSlotReview19::$value, ";Z:", $result, ";";
$mode = 3;
$pending = new Exception("free");
$result = "sentinel";
echo "O;";
try { $result = (NamePendingMixedSlotReview19::${pendingNameReview19()} .= pendingRightReview19()); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingMixedSlotReview19::$value, ";Z:", $result, ";";
$mode = 4;
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "A;";
try { $result = @(NamePendingMixedSlotReview19::${pendingNameReview19()} .= $rhs); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingMixedSlotReview19::$value, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'S;H;N;D;X:free;V:7;I:;Z:sentinel;T;H;N;D;X::none;V:7;Z:sentinel;O;H;Q;N;D;R;X:free;V:a;Z:sentinel;A;H;N;D;X:free;V:a;Z:sentinel;E;',
        'discriminator': 'A pending NAME-destructor exception prevents weak integer verification and leaves its original exception unchanged; it also suppresses RHS Stringable entry while releasing the owned temporary, and aborts suppressed array conversion before store.',
    },

    {
        'id': 'stringable-property-name-pending-masks',
        'source': r'''<?php
class NamePendingMasksSlotReview19 {
    public static int|float $number = 7;
    public static bool $boolean = false;
    public static float|bool $floatbool = false;
    public static int|bool $intbool = false;
    public static int $reference = 7;
    public static string $text = "a";
}
class NamePendingMasksReview19 {
    public function __toString(): string { global $chosen; echo "N;"; return $chosen; }
    public function __destruct() { global $rhs, $pending; echo "D;"; $rhs = "2"; throw $pending; }
}
function pendingMasksNameReview19() { echo "H;"; return new NamePendingMasksReview19(); }
$chosen = "number";
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "U;";
try { $result = (NamePendingMasksSlotReview19::${pendingMasksNameReview19()} .= $rhs); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingMasksSlotReview19::$number, ";I:", (NamePendingMasksSlotReview19::$number === 72), ";Z:", $result, ";";
$chosen = "boolean";
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "B;";
try { $result = (NamePendingMasksSlotReview19::${pendingMasksNameReview19()} .= $rhs); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingMasksSlotReview19::$boolean, ";I:", (NamePendingMasksSlotReview19::$boolean === false), ";Z:", $result, ";";
$chosen = "floatbool";
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "F;";
try { $result = (NamePendingMasksSlotReview19::${pendingMasksNameReview19()} .= $rhs); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingMasksSlotReview19::$floatbool, ";I:", (NamePendingMasksSlotReview19::$floatbool === false), ";Z:", $result, ";";
$chosen = "intbool";
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "I;";
try { $result = (NamePendingMasksSlotReview19::${pendingMasksNameReview19()} .= $rhs); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingMasksSlotReview19::$intbool, ";I:", (NamePendingMasksSlotReview19::$intbool === false), ";Z:", $result, ";";
$chosen = "reference";
$alias = 7;
NamePendingMasksSlotReview19::$reference =& $alias;
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "R;";
try { $result = (NamePendingMasksSlotReview19::${pendingMasksNameReview19()} .= $rhs); }
catch (Throwable $e) {
    echo "X:", ($e instanceof TypeError), ":";
    $previous = $e->getPrevious();
    if ($previous === null) { echo "none"; } else { echo $previous->getMessage(); }
    echo ";";
}
echo "V:", NamePendingMasksSlotReview19::$reference, ";A:", $alias, ";Z:", $result, ";";
$chosen = "text";
$textAlias = "a";
NamePendingMasksSlotReview19::$text =& $textAlias;
$rhs = "before";
$pending = new Exception("free");
$result = "sentinel";
echo "S;";
try { $result = (NamePendingMasksSlotReview19::${pendingMasksNameReview19()} .= $rhs); }
catch (Throwable $e) { echo "X:", $e->getMessage(), ";"; }
echo "V:", NamePendingMasksSlotReview19::$text, ";A:", $textAlias, ";Z:", $result, ";";
class BorrowedDoubleThrowNameReview19 {
    public function __toString(): string {
        global $borrowedProperty, $castPending;
        echo "N;";
        $borrowedProperty = "unused";
        throw $castPending;
    }
    public function __destruct() { global $dtorPending; echo "D;"; throw $dtorPending; }
}
$castPending = new Exception("cast");
$dtorPending = new Exception("drop");
$borrowedProperty = new BorrowedDoubleThrowNameReview19();
$result = "sentinel";
echo "C;";
try { $result = (NamePendingMasksSlotReview19::${$borrowedProperty} .= "b"); }
catch (Throwable $e) {
    echo "X:", $e->getMessage(), ";Q:";
    $previous = $e->getPrevious();
    if ($previous === null) { echo "none"; } else { echo $previous->getMessage(); }
    echo ";";
}
echo "P:", $borrowedProperty, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'U;H;N;D;X:free;V:72;I:1;Z:sentinel;B;H;N;D;X:free;V:;I:1;Z:sentinel;F;H;N;D;X:free;V:;I:1;Z:sentinel;I;H;N;D;X:free;V:;I:1;Z:sentinel;R;H;N;D;X:1:free;V:7;A:7;Z:sentinel;S;H;N;D;X:free;V:a2;A:a2;Z:sentinel;C;N;D;X:Access to undeclared static property NamePendingMasksSlotReview19::$;Q:drop;P:unused;Z:sentinel;E;',
        'discriminator': 'Pending numeric int|float conversion succeeds, weak bool masks abort, typed-int REF rejection chains a new TypeError, an initially string typed REF performs the fast compound store, and borrowed cast/destructor double-throw still performs the empty-name address lookup.',
    },

    {
        'id': 'stringable-property-name-owned-reference',
        'source': r'''<?php
class OwnedReferenceNameSlotReview19 { public static mixed $value = "a"; }
class OwnedReferenceNameReview19 {
    public function __toString(): string {
        global $name, $rhs;
        echo "N;";
        unset($GLOBALS["name"]);
        $GLOBALS["name"] = "other";
        $rhs = "after";
        return "value";
    }
    public function __destruct() {
        global $alias, $rhs;
        echo "D;";
        OwnedReferenceNameSlotReview19::$value =& $alias;
        $rhs = "retired";
    }
}
function &ownedReferenceNameReview19() { global $name; echo "H;"; return $name; }
$name = new OwnedReferenceNameReview19();
$alias = "old";
$rhs = "before";
$result = (OwnedReferenceNameSlotReview19::${ownedReferenceNameReview19()} .= $rhs);
echo "V:", OwnedReferenceNameSlotReview19::$value, ";A:", $alias,
     ";P:", $name, ";R:", $rhs, ";X:", $result, ";E;";
''',
        'expected_stdout': 'H;N;D;V:oldretired;A:oldretired;P:other;R:retired;X:oldretired;E;',
        'discriminator': 'An accepted99 untyped returned REF retains the old name cell across actual global unset/rebind; its final release changes the selected alias and live RHS before capture.',
    },
    {
        'id': 'stringable-property-name-pending-cold-failure',
        'source': r'''<?php
class PendingColdNameSlotReview19 { public static string $value = self::MISSING; }
class PendingColdNameReview19 {
    public function __toString(): string { global $name; echo "N;"; $name = "other"; return "value"; }
    public function __destruct() { global $drop; echo "D;"; throw $drop; }
}
class PendingColdNameRightReview19 {
    public function __toString(): string { echo "B;"; return "b"; }
    public function __destruct() { echo "R;"; }
}
function pendingColdNameRightReview19() { echo "Q;"; return new PendingColdNameRightReview19(); }
$name = new PendingColdNameReview19();
$drop = new Exception("drop");
$result = "sentinel";
try { $result = (PendingColdNameSlotReview19::${$name} .= pendingColdNameRightReview19()); }
catch (Throwable $e) {
    echo "X:", $e->getMessage(), ";Q:";
    $previous = $e->getPrevious();
    if ($previous === null) { echo "none"; } else { echo $previous->getMessage(); }
    echo ";L:", $e->getLine(), ";";
}
echo "P:", $name, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'Q;N;D;R;X:Undefined constant self::MISSING;Q:drop;L:2;P:other;Z:sentinel;E;',
        'discriminator': 'A borrowed selected receiver destructor leaves a pending exception before genuine cold static initialization; initializer failure replaces it while the evaluated RHS temporary retires.',
    },
    {
        'id': 'stringable-property-name-cold-double-throw',
        'source': r'''<?php
class ColdDoubleNameSlotReview20 { public static string $value = self::MISSING; }
class ColdDoubleNameReview20 {
    public function __toString(): string {
        global $name, $cast;
        echo "N;";
        $name = "other";
        throw $cast;
    }
    public function __destruct() { global $drop; echo "D;"; throw $drop; }
}
class ColdDoubleNameRightReview20 {
    public function __toString(): string { echo "B;"; return "b"; }
    public function __destruct() { echo "R;"; }
}
function coldDoubleNameRightReview20() { echo "Q;"; return new ColdDoubleNameRightReview20(); }
$name = new ColdDoubleNameReview20();
$cast = new Exception("cast");
$drop = new Exception("drop");
$result = "sentinel";
try { $result = (ColdDoubleNameSlotReview20::${$name} .= coldDoubleNameRightReview20()); }
catch (Throwable $e) {
    echo "X:", $e->getMessage(), ";Q:";
    $previous = $e->getPrevious();
    if ($previous === null) { echo "none;C:none"; }
    else {
        echo $previous->getMessage(), ";C:";
        $before = $previous->getPrevious();
        if ($before === null) { echo "none"; } else { echo $before->getMessage(); }
    }
    echo ";";
}
echo "P:", $name, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'Q;N;D;R;X:Access to undeclared static property ColdDoubleNameSlotReview20::$;Q:drop;C:cast;P:other;Z:sentinel;E;',
        'discriminator': 'Failed NAME conversion and throwing receiver cleanup preserve empty-name lookup before cold defaults, chain Error to drop to cast, and retire the owned RHS without stringifying it.',
    },
]


CASES += [
    {
        'id': 'stringable-name-ordinary-live-byref',
        'source': r'''<?php
class FromStaticNameBaseReview20 {
    public static string $value = "a";
    public static function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
}
class FromStaticNameChildReview20 extends FromStaticNameBaseReview20 {
    public static string $value = "c";
}
class FromStaticNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        FromStaticNameChildReview20::$value = "d";
        $rhs = new FromStaticRightReview20();
    }
}
class FromStaticRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
$property = new FromStaticNameReview20();
$rhs = "before";
$result = FromStaticNameChildReview20::append($property, $rhs);
$rhs = "done";
echo "V:", FromStaticNameChildReview20::$value,
     ";B:", FromStaticNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'H;N;D;B;R;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'An inherited ordinary static call keeps lexical Base/called Child while borrowed by-ref NAME retirement changes the live Stringable RHS; carrier bytes and fresh request-string storage preserve the caller cells.',
    },
    {
        'id': 'stringable-name-from-callable-live-byref',
        'source': r'''<?php
class FromStaticNameBaseReview20 {
    public static string $value = "a";
    public static function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
}
class FromStaticNameChildReview20 extends FromStaticNameBaseReview20 {
    public static string $value = "c";
}
class FromStaticNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        FromStaticNameChildReview20::$value = "d";
        $rhs = new FromStaticRightReview20();
    }
}
class FromStaticRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
$property = new FromStaticNameReview20();
$rhs = "before";
$closure = Closure::fromCallable([FromStaticNameChildReview20::class, "append"]);
$result = $closure($property, $rhs);
$rhs = "done";
echo "V:", FromStaticNameChildReview20::$value,
     ";B:", FromStaticNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'H;N;D;B;R;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'A retained static Closure::fromCallable wrapper freezes lexical Base/called Child and exact saved CLOSURE_SCOPE through borrowed by-ref NAME retirement, RHS conversion and the final property write without another closure owner.',
    },
]


CASES += [
    {
        'id': 'stringable-name-ordinary-instance-byref',
        'source': r'''<?php
class FromInstanceNameBaseReview20 {
    public static string $value = "a";
    public function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
    public function __destruct() {
        echo "W;";
    }
}
class FromInstanceNameChildReview20 extends FromInstanceNameBaseReview20 {
    public static string $value = "c";
}
class FromInstanceNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        FromInstanceNameChildReview20::$value = "d";
        $rhs = new FromInstanceRightReview20();
    }
}
class FromInstanceRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
$property = new FromInstanceNameReview20();
$rhs = "before";
$receiver = new FromInstanceNameChildReview20();
$result = $receiver->append($property, $rhs);
$rhs = "done";
$receiver = null;
echo "V:", FromInstanceNameChildReview20::$value,
     ";B:", FromInstanceNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'H;N;D;B;R;W;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'An inherited instance call preserves lexical Base/called Child while borrowed by-ref NAME retirement installs a live Stringable RHS; explicit receiver release occurs before observing caller cells and the stored result.',
    },
    {
        'id': 'stringable-name-from-callable-instance-byref',
        'source': r'''<?php
class FromInstanceNameBaseReview20 {
    public static string $value = "a";
    public function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
    public function __destruct() {
        echo "W;";
    }
}
class FromInstanceNameChildReview20 extends FromInstanceNameBaseReview20 {
    public static string $value = "c";
}
class FromInstanceNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        FromInstanceNameChildReview20::$value = "d";
        $rhs = new FromInstanceRightReview20();
    }
}
class FromInstanceRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
$property = new FromInstanceNameReview20();
$rhs = "before";
$closure = Closure::fromCallable([new FromInstanceNameChildReview20(), "append"]);
$result = $closure($property, $rhs);
$rhs = "done";
$closure = null;
echo "V:", FromInstanceNameChildReview20::$value,
     ";B:", FromInstanceNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'H;N;D;B;R;W;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'A nonstatic Closure::fromCallable preserves the exact receiver-bearing scope through computed NAME retirement and the distinct RHS callback; explicit Closure release retires its sole receiver without invalidating saved selection evidence.',
    },
]


CASES += [
    {
        'id': 'stringable-name-direct-factory-instance-byref',
        'source': '''<?php
class FromFactoryNameBaseReview20 {
    public static string $value = "a";
    public function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
    public function __destruct() {
        echo "W;";
    }
}
class FromFactoryNameChildReview20 extends FromFactoryNameBaseReview20 {
    public static string $value = "c";
}
class FromFactoryNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        FromFactoryNameChildReview20::$value = "d";
        $rhs = new FromFactoryRightReview20();
    }
}
class FromFactoryRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
$property = new FromFactoryNameReview20();
$rhs = "before";
echo "Q;";
$callback = [new FromFactoryNameChildReview20(), "append"];
$closure = Closure::fromCallable(callback: $callback);
$callback = null;
echo "F;";
$result = $closure($property, $rhs);
$rhs = "done";
$closure = null;
echo "V:", FromFactoryNameChildReview20::$value,
     ";B:", FromFactoryNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'Q;F;H;N;D;B;R;W;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'Direct fromCallable control retains the inherited by-ref Stringable NAME/RHS body and retires the receiver after callback-array release.',
    },
    {
        'id': 'stringable-name-captured-factory-instance-byref',
        'source': '''<?php
class FromFactoryNameBaseReview20 {
    public static string $value = "a";
    public function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
    public function __destruct() {
        echo "W;";
    }
}
class FromFactoryNameChildReview20 extends FromFactoryNameBaseReview20 {
    public static string $value = "c";
}
class FromFactoryNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        FromFactoryNameChildReview20::$value = "d";
        $rhs = new FromFactoryRightReview20();
    }
}
class FromFactoryRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
$property = new FromFactoryNameReview20();
$rhs = "before";
echo "Q;";
$callback = [new FromFactoryNameChildReview20(), "append"];
$factory = Closure::fromCallable(...);
$closure = $factory(callback: $callback);
$callback = null;
$factory = null;
echo "F;";
$result = $closure($property, $rhs);
$rhs = "done";
$closure = null;
echo "V:", FromFactoryNameChildReview20::$value,
     ";B:", FromFactoryNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'Q;F;H;N;D;B;R;W;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'A first-class captured fromCallable factory receives a named callback, retires before the returned method Closure runs, and preserves by-ref Stringable NAME/RHS effects and explicit receiver retirement.',
    },
    {
        'id': 'stringable-name-variable-factory-argument-retirement',
        'source': '''<?php
class InvokeFactoryNameBaseReview20 {
    public static string $value = "a";
    public function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
    public function __destruct() {
        echo "W;";
    }
}
class InvokeFactoryNameChildReview20 extends InvokeFactoryNameBaseReview20 {
    public static string $value = "c";
}
class InvokeFactoryNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        InvokeFactoryNameChildReview20::$value = "d";
        $rhs = new InvokeFactoryRightReview20();
    }
}
class InvokeFactoryRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
function clearFactoryInvokeArgumentReview20() {
    global $factory;
    $factory = null;
    echo "A;";
    return [new InvokeFactoryNameChildReview20(), "append"];
}
$property = new InvokeFactoryNameReview20();
$rhs = "before";
echo "Q;";
$factory = Closure::fromCallable(...);
$closure = $factory(callback: clearFactoryInvokeArgumentReview20());
echo "F;";
$result = $closure($property, $rhs);
$rhs = "done";
$closure = null;
echo "V:", InvokeFactoryNameChildReview20::$value,
     ";B:", InvokeFactoryNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'Q;A;F;H;N;D;B;R;W;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'Variable factory control keeps its selected owner through caller-cell clearing before the returned inherited by-reference NAME/RHS method runs.',
    },
    {
        'id': 'stringable-name-explicit-factory-invoke-byref',
        'source': '''<?php
class InvokeFactoryNameBaseReview20 {
    public static string $value = "a";
    public function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
    public function __destruct() {
        echo "W;";
    }
}
class InvokeFactoryNameChildReview20 extends InvokeFactoryNameBaseReview20 {
    public static string $value = "c";
}
class InvokeFactoryNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        InvokeFactoryNameChildReview20::$value = "d";
        $rhs = new InvokeFactoryRightReview20();
    }
}
class InvokeFactoryRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
function clearFactoryInvokeArgumentReview20() {
    global $factory;
    $factory = null;
    echo "A;";
    return [new InvokeFactoryNameChildReview20(), "append"];
}
$property = new InvokeFactoryNameReview20();
$rhs = "before";
echo "Q;";
$factory = Closure::fromCallable(...);
$closure = $factory->__invoke(callback: clearFactoryInvokeArgumentReview20());
echo "F;";
$result = $closure($property, $rhs);
$rhs = "done";
$closure = null;
echo "V:", InvokeFactoryNameChildReview20::$value,
     ";B:", InvokeFactoryNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'Q;A;F;H;N;D;B;R;W;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'Literal explicit __invoke preserves the selected factory through argument-cell clearing, then independently owns the inherited receiver through NAME/RHS callbacks and explicit retirement.',
    },
    {
        'id': 'stringable-name-factory-invoke-alias-byref',
        'source': '''<?php
class AliasFactoryNameBaseReview20 {
    public static string $value = "a";
    public function append(&$property, &$rhs) {
        echo "H;";
        return (static::${$property} .= $rhs);
    }
    public function __destruct() {
        echo "W;";
    }
}
class AliasFactoryNameChildReview20 extends AliasFactoryNameBaseReview20 {
    public static string $value = "c";
}
class AliasFactoryNameReview20 {
    public function __toString(): string {
        global $property;
        echo "N;";
        $property = "other";
        return "value";
    }
    public function __destruct() {
        global $rhs;
        echo "D;";
        AliasFactoryNameChildReview20::$value = "d";
        $rhs = new AliasFactoryRightReview20();
    }
}
class AliasFactoryRightReview20 {
    public function __toString(): string {
        echo "B;";
        return "retired";
    }
    public function __destruct() {
        echo "R;";
    }
}
function clearAliasFactoryArgumentReview20() {
    global $alias;
    $alias = null;
    echo "A;";
    return [new AliasFactoryNameChildReview20(), "append"];
}
$property = new AliasFactoryNameReview20();
$rhs = "before";
echo "Q;";
$factory = Closure::fromCallable(...);
$alias = $factory->__invoke(...);
echo "S:", $alias === $factory ? "same" : "different", ";";
$factory = null;
echo "I;";
$closure = $alias(callback: clearAliasFactoryArgumentReview20());
echo "F;";
$result = $closure($property, $rhs);
$rhs = "done";
$closure = null;
echo "V:", AliasFactoryNameChildReview20::$value,
     ";B:", AliasFactoryNameBaseReview20::$value,
     ";P:", $property, ";R:", $rhs, ";Z:", $result, ";E;";
''',
        'expected_stdout': 'Q;S:same;I;A;F;H;N;D;B;R;W;V:dretired;B:a;P:other;R:done;Z:dretired;E;',
        'discriminator': 'Literal first-class __invoke preserves factory identity and its creation authority; selected CONFIG retains it as both caller cells are cleared, and the returned receiver retires independently after by-reference NAME/RHS effects.',
    },
    {
        'id': 'from-callable-direct-getter-live',
        'source': '''<?php
class FactoryGetterExceptionReview20 extends Exception {
    public function replace($message) {
        $this->message = $message;
        echo "M;";
    }
    public function __destruct() { echo "D;"; }
}
function discardFactoryGetterArgumentReview20() {
    global $factory, $callback;
    $factory = null;
    echo "A;";
    return $callback;
}
echo "Q;";
$receiver = new FactoryGetterExceptionReview20("before");
$callback = [$receiver, "getMessage"];
$factory = null;
$closure = Closure::fromCallable(callback: discardFactoryGetterArgumentReview20());
$callback = null;
echo "F;";
$receiver->replace("after");
$receiver = null;
echo "H;";
$result = $closure();
$closure = null;
echo "V:", $result, ";E;";
''',
        'expected_stdout': 'Q;A;F;M;H;D;V:after;E;',
        'discriminator': 'Direct factory control reads the live Throwable message and owns its receiver until explicit returned-Closure release.',
    },
    {
        'id': 'from-callable-factory-getter-live',
        'source': '''<?php
class FactoryGetterExceptionReview20 extends Exception {
    public function replace($message) {
        $this->message = $message;
        echo "M;";
    }
    public function __destruct() { echo "D;"; }
}
function discardFactoryGetterArgumentReview20() {
    global $factory, $callback;
    $factory = null;
    echo "A;";
    return $callback;
}
echo "Q;";
$receiver = new FactoryGetterExceptionReview20("before");
$callback = [$receiver, "getMessage"];
$factory = Closure::fromCallable(...);
$closure = $factory(callback: discardFactoryGetterArgumentReview20());
$callback = null;
echo "F;";
$receiver->replace("after");
$receiver = null;
echo "H;";
$result = $closure();
$closure = null;
echo "V:", $result, ";E;";
''',
        'expected_stdout': 'Q;A;F;M;H;D;V:after;E;',
        'discriminator': 'Selected captured factory survives argument-cell clearing; the returned getter retains only its receiver, reads the changed message after factory retirement and retires that receiver at explicit release.',
    },
    {
        'id': 'from-callable-factory-getter-copy',
        'source': '''<?php
class FactoryGetterCopyExceptionReview20 extends Exception {
    public function replace($message) { $this->message = $message; echo "M;"; }
    public function __destruct() { echo "D;"; }
}
echo "Q;";
$receiver = new FactoryGetterCopyExceptionReview20("before");
$factory = Closure::fromCallable(...);
$direct = Closure::fromCallable([$receiver, "getMessage"]);
$captured = $factory(callback: [$receiver, "getMessage"]);
$copy = clone $captured;
echo "S:", $direct == $captured ? "same" : "different", ";";
echo "I:", $direct === $captured ? "same" : "different", ";";
echo "C:", $copy == $captured ? "same" : "different", ";";
echo "J:", $copy === $captured ? "same" : "different", ";";
$factory = null;
$direct = null;
$captured = null;
$receiver->replace("after");
$receiver = null;
echo "F;";
$result = $copy();
$copy = null;
echo "V:", $result, ";E;";
''',
        'expected_stdout': 'Q;S:same;I:different;C:same;J:different;M;F;D;V:after;E;',
        'discriminator': 'Direct and factory captures compare equal without identical objects; cloning preserves method, receiver and nonowning source certificate after the other captures and factory retire.',
    },

]
