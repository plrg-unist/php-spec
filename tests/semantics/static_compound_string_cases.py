"""Fresh static Stringable compound originals; expectations need native/model agreement."""


CASES = [
    {
        'id': 'static-compound-live-rhs-and-result',
        'source': '''<?php
class StaticLiveSlotReview19 { public static mixed $value; }
class LeftStaticLiveReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = "after";
        return "a";
    }
}
$rhs = "before";
StaticLiveSlotReview19::$value = new LeftStaticLiveReview19();
$result = (StaticLiveSlotReview19::$value .= $rhs);
echo "V:", StaticLiveSlotReview19::$value, ";R:", $rhs, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;V:aafter;R:after;X:aafter;E;',
        'discriminator': 'The captured static destination receives the late RHS CV value and the full used expression result.',
    },
    {
        'id': 'static-compound-late-alias',
        'source': '''<?php
class StaticLateAliasSlotReview19 { public static $value; }
class LeftStaticLateAliasReview19 {
    public function __toString(): string {
        echo "L;";
        $GLOBALS['alias'] =& StaticLateAliasSlotReview19::$value;
        StaticLateAliasSlotReview19::$value = "changed";
        return "a";
    }
}
StaticLateAliasSlotReview19::$value = new LeftStaticLateAliasReview19();
$result = (StaticLateAliasSlotReview19::$value .= "b");
echo "V:", StaticLateAliasSlotReview19::$value, ";A:", $alias, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;V:ab;A:changed;X:ab;E;',
        'discriminator': 'An initially plain static slot detaches an alias created during left conversion.',
    },
    {
        'id': 'static-compound-initial-reference-rebind',
        'source': '''<?php
class StaticRefSlotReview19 { public static $value; }
class LeftStaticRefReview19 {
    public function __toString(): string {
        global $replacement;
        echo "L;";
        StaticRefSlotReview19::$value =& $replacement;
        return "a";
    }
}
StaticRefSlotReview19::$value = new LeftStaticRefReview19();
$alias =& StaticRefSlotReview19::$value;
$replacement = "changed";
$result = (StaticRefSlotReview19::$value .= "b");
echo "V:", StaticRefSlotReview19::$value, ";A:", $alias, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;V:changed;A:ab;X:ab;E;',
        'discriminator': 'An initially referenced destination writes the original cell after the static property is rebound.',
    },
    {
        'id': 'static-compound-typed-right-late-alias',
        'source': '''<?php
class StaticTypedSlotReview19 { public static string $value = "a"; }
class RightStaticTypedReview19 {
    public function __toString(): string {
        echo "R;";
        $GLOBALS['alias'] =& StaticTypedSlotReview19::$value;
        StaticTypedSlotReview19::$value = "changed";
        return "b";
    }
}
$rhs = new RightStaticTypedReview19();
$result = (StaticTypedSlotReview19::$value .= $rhs);
echo "V:", StaticTypedSlotReview19::$value, ";A:", $alias, ";X:", $result, ";E;";
''',
        'expected_stdout': 'R;V:ab;A:changed;X:ab;E;',
        'discriminator': 'A typed string destination retains its initial direct slot through a right conversion that creates an alias.',
    },
    {
        'id': 'static-compound-inherited-destination',
        'source': '''<?php
class StaticParentSlotReview19 { public static mixed $value; }
class StaticChildSlotReview19 extends StaticParentSlotReview19 {}
class LeftStaticInheritedReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = "after";
        return "a";
    }
}
StaticParentSlotReview19::$value = new LeftStaticInheritedReview19();
$rhs = "before";
$result = (StaticChildSlotReview19::$value .= $rhs);
echo "P:", StaticParentSlotReview19::$value, ";C:", StaticChildSlotReview19::$value, ";X:", $result, ";E;";
''',
        'expected_stdout': 'L;P:aafter;C:aafter;X:aafter;E;',
        'discriminator': 'A child request selects the shared parent property declaration before callbacks.',
    },
    {
        'id': 'static-compound-typed-integer-result',
        'source': '''<?php
class StaticIntSlotReview19 { public static int $value = 1; }
class RightStaticIntReview19 {
    public function __toString(): string { echo "R;"; return "2"; }
}
$rhs = new RightStaticIntReview19();
$result = (StaticIntSlotReview19::$value .= $rhs);
echo "V:", StaticIntSlotReview19::$value, ";I:", StaticIntSlotReview19::$value === 12,
     ";X:", $result, ";J:", $result === 12, ";E;";
''',
        'expected_stdout': 'R;V:12;I:1;X:12;J:1;E;',
        'discriminator': 'Weak typed static verification changes both the stored value and used expression result to integer.',
    },
    {
        'id': 'static-compound-typed-reference-new-source',
        'source': '''<?php
class StaticRefSourceReview19 { public static int|string $value = "1"; }
class OtherRefSourceReview19 { public static int $value = 0; }
class RightNewSourceReview19 {
    public function __toString(): string {
        echo "R;";
        StaticRefSourceReview19::$value = 1;
        OtherRefSourceReview19::$value =& StaticRefSourceReview19::$value;
        echo "B:", StaticRefSourceReview19::$value === 1, ";";
        return "2";
    }
}
$alias =& StaticRefSourceReview19::$value;
$result = (StaticRefSourceReview19::$value .= new RightNewSourceReview19());
echo "V:", StaticRefSourceReview19::$value, ";I:", StaticRefSourceReview19::$value === 12,
     ";S:", StaticRefSourceReview19::$value === "12", ";T:", OtherRefSourceReview19::$value,
     ";TS:", OtherRefSourceReview19::$value === "12", ";X:", $result, ";E;";
''',
        'expected_stdout': 'R;B:1;V:12;I:;S:1;T:12;TS:1;X:12;E;',
        'discriminator': 'An initially string typed reference uses the unchecked concat path after its callback installs an additional int source.',
    },
    {
        'id': 'static-compound-typed-late-alias-source-history',
        'source': '''<?php
class StaticTypedHistoryReview19 { public static string $value = "a"; }
class RightStaticHistoryReview19 {
    public function __toString(): string {
        echo "R;";
        $GLOBALS['alias'] =& StaticTypedHistoryReview19::$value;
        StaticTypedHistoryReview19::$value = "changed";
        return "b";
    }
}
$result = (StaticTypedHistoryReview19::$value .= new RightStaticHistoryReview19());
echo "V:", StaticTypedHistoryReview19::$value, ";A:", $alias, ";X:", $result, ";";
$alias = 2;
echo "N:", $alias, ";I:", $alias === 2, ";S:", $alias === "2", ";E;";
''',
        'expected_stdout': 'R;V:ab;A:changed;X:ab;N:2;I:;S:1;E;',
        'discriminator': 'The detached alias retains its original static string source, which still coerces a later integer write.',
    },
    {
        'id': 'static-compound-rhs-temporary-owner',
        'source': '''<?php
class StaticTmpSlotReview19 { public static $value; }
class BeforeStaticTmpReview19 {
    public function __toString(): string { echo "O;"; return "before"; }
    public function __destruct() { echo "D:before;"; }
}
class AfterStaticTmpReview19 {
    public function __toString(): string { echo "N;"; return "after"; }
    public function __destruct() { echo "D:after;"; }
}
class LeftStaticTmpReview19 {
    public function __toString(): string {
        global $rhs;
        echo "L;";
        $rhs = new AfterStaticTmpReview19();
        echo "P;";
        return "a";
    }
    public function __destruct() { echo "D:left;"; }
}
function evaluatedStaticTmpReview19() { global $rhs; echo "Q;"; return $rhs; }
$rhs = new BeforeStaticTmpReview19();
StaticTmpSlotReview19::$value = new LeftStaticTmpReview19();
$result = (StaticTmpSlotReview19::$value .= evaluatedStaticTmpReview19());
echo "V:", StaticTmpSlotReview19::$value, ";X:", $result, ";";
unset($rhs);
echo "E;";
''',
        'expected_stdout': 'Q;L;P;O;D:left;D:before;V:abefore;X:abefore;D:after;E;',
        'discriminator': 'The evaluated RHS object survives replacement through static final store; old left destruction precedes FREE_OP_DATA destruction.',
    },
    {
        'id': 'static-compound-preentry-error-priority',
        'source': '''<?php
class StaticUninitPriorityReview19 { public private(set) static string $value; }
class StaticSetPriorityReview19 { public private(set) static string $value = "a"; }
class StaticReadPriorityReview19 { private static string $value = "a"; }
class RightStaticPriorityReview19 {
    public function __toString(): string { echo "wrong;"; return "b"; }
    public function __destruct() { echo "D;"; }
}
function evaluatedStaticPriorityReview19() { echo "Q;"; return new RightStaticPriorityReview19(); }
try { StaticUninitPriorityReview19::$value .= evaluatedStaticPriorityReview19(); }
catch (Error $error) { echo "U:", $error->getMessage(), ";"; }
unset($error);
try { StaticSetPriorityReview19::$value .= evaluatedStaticPriorityReview19(); }
catch (Error $error) { echo "S:", $error->getMessage(), ";"; }
unset($error);
try { StaticReadPriorityReview19::$value .= evaluatedStaticPriorityReview19(); }
catch (Error $error) { echo "R:", $error->getMessage(), ";"; }
unset($error);
echo "E;";
''',
        'expected_stdout': 'Q;D;U:Typed static property StaticUninitPriorityReview19::$value must not be accessed before initialization;Q;D;S:Cannot indirectly modify private(set) property StaticSetPriorityReview19::$value from global scope;Q;D;R:Cannot access private property StaticReadPriorityReview19::$value;E;',
        'discriminator': 'RHS evaluation precedes address checks, while read/uninitialized/set errors stop conversion and free its temporary before the catch.',
    },
    {
        'id': 'static-compound-history-reentry-and-spare',
        'source': '''<?php
$spare = "12";
$spareAlias =& $spare;
class StaticRepeatSlotReview19 { public static string $value = "a"; }
class RightStaticRepeatReview19 {
    public function __toString(): string {
        global $alias, $phase;
        echo "R", $phase, ";";
        if ($phase === 1) { $GLOBALS['alias'] =& StaticRepeatSlotReview19::$value; }
        else { StaticRepeatSlotReview19::$value =& $alias; }
        StaticRepeatSlotReview19::$value = "changed" . $phase;
        return "b";
    }
}
function repeatStaticCompoundReview19() {
    global $rhs;
    return (StaticRepeatSlotReview19::$value .= $rhs);
}
$rhs = new RightStaticRepeatReview19();
$phase = 1;
$result = repeatStaticCompoundReview19();
echo "X:", $result, ";";
$phase = 2;
$result = repeatStaticCompoundReview19();
echo "X:", $result, ";";
$alias = 2;
echo "A:", $alias, ";I:", $alias === 2, ";S:", $alias === "2", ";";
$other = "other";
StaticRepeatSlotReview19::$value =& $alias;
StaticRepeatSlotReview19::$value =& $other;
$alias = 3;
echo "B:", $alias, ";I:", $alias === 3, ";S:", $alias === "3", ";";
class StaticRepeatRawReview19 { public static int|string $value = "1"; }
class OtherRepeatRawReview19 { public static int $value = 0; }
class RightStaticRepeatRawReview19 {
    public function __toString(): string {
        echo "R3;";
        StaticRepeatRawReview19::$value = 1;
        OtherRepeatRawReview19::$value =& StaticRepeatRawReview19::$value;
        echo "B3:", StaticRepeatRawReview19::$value === 1, ";";
        return "2";
    }
}
$rawAlias =& StaticRepeatRawReview19::$value;
$result = (StaticRepeatRawReview19::$value .= new RightStaticRepeatRawReview19());
echo "V:", StaticRepeatRawReview19::$value, ";S:", StaticRepeatRawReview19::$value === "12",
     ";T:", OtherRepeatRawReview19::$value, ";TS:", OtherRepeatRawReview19::$value === "12",
     ";X:", $result, ";E;";
''',
        'expected_stdout': 'R1;X:ab;R2;X:abb;A:2;I:;S:1;B:3;I:;S:1;R3;B3:1;V:12;S:1;T:12;TS:1;X:12;E;',
        'discriminator': 'Repeated same-site retirement preserves distinct type-source history and removal identity; a real spare reference also separates raw-write cell evidence from task metadata.',
    },
    {
        'id': 'static-compound-typed-reference-verification-and-rejection',
        'source': '''<?php
class StaticVerifyRefReview19 { public static int $value = 1; }
class RightVerifyRefReview19 {
    public function __toString(): string { echo "R;"; return "2"; }
    public function __destruct() { echo "D;"; }
}
class RightRejectRefReview19 {
    public function __toString(): string { echo "X;"; return "x"; }
    public function __destruct() { echo "DX;"; }
}
$alias =& StaticVerifyRefReview19::$value;
$result = (StaticVerifyRefReview19::$value .= new RightVerifyRefReview19());
echo "V:", StaticVerifyRefReview19::$value, ";I:", StaticVerifyRefReview19::$value === 12,
     ";A:", $alias, ";J:", $alias === 12, ";X:", $result, ";K:", $result === 12, ";";
try { $failed = (StaticVerifyRefReview19::$value .= new RightRejectRefReview19()); }
catch (TypeError $error) { echo "T;"; }
unset($error);
echo "V:", StaticVerifyRefReview19::$value, ";I:", StaticVerifyRefReview19::$value === 12,
     ";A:", $alias, ";F:", isset($failed), ";E;";
''',
        'expected_stdout': 'R;D;V:12;I:1;A:12;J:1;X:12;K:1;X;DX;T;V:12;I:1;A:12;F:;E;',
        'discriminator': 'A captured typed nonstring reference verifies the final concat, converts the used result, and retains its value while releasing the RHS when verification rejects.',
    },
]
