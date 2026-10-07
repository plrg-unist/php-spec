#!/usr/bin/env python3
"""Backed asymmetric instance setters and compound string source controls."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'setter-simple-rhs-type-priority': b"<?php\nclass Denied { public private(set) int $x = 1; }\nfunction rhs() { echo 'R|'; return 'bad'; }\n$o = new Denied();\ntry { $o->x = rhs(); } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\necho $o->x;\n",
    'setter-protected-family': b"<?php\nclass Owner { public protected(set) int $x = 1; public function put($o, $v) { $o->x = $v; } }\nclass Child extends Owner { public function putChild($v) { $this->x = $v; } }\nclass Stranger { public function put($o) { $o->x = 9; } }\n$o = new Child(); $o->putChild(2); echo $o->x, '|';\n(new Owner())->put($o, 3); echo $o->x, '|';\ntry { (new Stranger())->put($o); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $o->x;\n",
    'setter-private-called-scope': b"<?php\nclass Owner { public private(set) int $x = 1; public function put($v) { $this->x = $v; echo get_called_class(), '|'; } }\nclass Child extends Owner { public function denied() { $this->x = 9; } }\n$o = new Child(); $o->put(2); echo $o->x, '|';\ntry { $o->denied(); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $o->x;\n",
    'setter-prototype-ancestor': b"<?php\nclass Root { public protected(set) int $x = 1; public function put($o) { $o->x = 3; } }\nclass Leaf extends Root { public protected(set) int $x = 2; }\n$o = new Leaf(); (new Root())->put($o); echo $o->x, '|';\ntry { $o->x = 4; } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $o->x;\n",
    'setter-dimension-effect-order': b"<?php\nclass Denied { public private(set) array $a = [1]; }\nfunction key_value() { echo 'K|'; return 0; }\nfunction rhs() { echo 'R|'; return 7; }\n$o = new Denied();\ntry { $o->a[key_value()] = rhs(); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $o->a[0];\n",
    'setter-object-interior-raw-versus-alias': b"<?php\nclass Box { public int $n = 1; }\nclass Holder {\n    public private(set) Box $box;\n    public function __construct() { $this->box = new Box(); }\n    public function bind(&$v) { $this->box =& $v; }\n}\n$o = new Holder(); $o->box->n = 2; echo $o->box->n, '|';\n$external = new Box(); $o->bind($external);\ntry { $o->box->n = 3; } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $external->n, '/', $o->box->n;\n",
    'setter-reference-acquisition': b"<?php\nclass Denied { public private(set) int $x = 1; public private(set) array $a = [2]; }\nfunction bump(&$v) { echo 'B|'; $v = 8; }\n$o = new Denied();\ntry { $r =& $o->x; } catch (Error $e) { echo $e->getMessage(), '|'; }\ntry { bump($o->x); } catch (Error $e) { echo $e->getMessage(), '|'; }\ntry { foreach ($o->a as &$v) { echo 'F|'; $v = 9; } } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $o->x, '/', $o->a[0];\n",
    'setter-escaped-typed-alias': b"<?php\nclass Owner {\n    public private(set) int $x = 1;\n    public function escape() { $GLOBALS['escaped'] =& $this->x; }\n}\n$o = new Owner(); $o->escape(); $escaped = '7'; echo $o->x, '|';\ntry { $escaped = []; } catch (TypeError $e) { echo 'T|'; }\ntry { $o->x = 8; } catch (Error $e) { echo 'E|'; }\necho $escaped, '/', $o->x;\n",
    'setter-compound-and-uninitialized': b"<?php\nclass Denied { public private(set) int $x = 1; public private(set) int $u; }\nfunction rhs() { echo 'R|'; return 2; }\n$o = new Denied();\ntry { $o->x += rhs(); } catch (Error $e) { echo $e->getMessage(), '|'; }\ntry { $o->x++; } catch (Error $e) { echo $e->getMessage(), '|'; }\ntry { $o->u++; } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $o->x, '/', isset($o->u) ? 'yes' : 'no';\n",
    'setter-unset-and-owner-reinitialize': b"<?php\nclass Owner {\n    public protected(set) int $x = 1; public protected(set) int $u;\n    public function clear() { unset($this->x, $this->u); }\n    public function put() { $this->x = 4; $this->u = 5; }\n}\n$o = new Owner();\ntry { unset($o->x); } catch (Error $e) { echo $e->getMessage(), '|'; }\ntry { unset($o->u); } catch (Error $e) { echo $e->getMessage(), '|'; }\n$o->clear(); echo isset($o->x) ? 'yes|' : 'no|'; $o->put(); echo $o->x, '/', $o->u;\n",
    'setter-quiet-and-coalesce': b"<?php\nclass Denied { public private(set) int $x = 1; public private(set) ?int $u; }\nfunction rhs() { echo 'R|'; return 7; }\n$o = new Denied();\necho isset($o->x) ? 'yes|' : 'no|', empty($o->x) ? 'empty|' : 'value|';\n$o->x ??= rhs(); echo $o->x, '|';\ntry { $o->u ??= rhs(); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho isset($o->u) ? 'yes' : 'no';\n",
    'setter-strict-type-versus-access': b"<?php\ndeclare(strict_types=1);\nclass Owner { public private(set) int $x = 1; public function put($v) { $this->x = $v; } }\n$o = new Owner();\ntry { $o->put('7'); } catch (TypeError $e) { echo 'T|'; }\ntry { $o->x = '7'; } catch (Error $e) { echo get_class($e), '|'; }\necho $o->x;\n",
    'setter-rebound-closure-lexical-authority': b"<?php\nclass Owner {\n    public private(set) int $x = 1;\n    public function make() { $target = $this; return function () use ($target) { $target->x = 9; echo self::class, '/', get_called_class(), '|'; }; }\n}\nclass Unrelated {}\n$o = new Owner(); $maker = $o->make(); $bound = $maker->bindTo(new Unrelated(), Owner::class);\nunset($maker); $bound(); echo $o->x;\n",
    'setter-clone-copy-and-denial': b"<?php\nclass Owner { public protected(set) int $x = 1; public function put($v) { $this->x = $v; } }\n$original = new Owner(); $copy = clone $original; $copy->put(3);\ntry { $copy->x = 8; } catch (Error $e) { echo 'E|'; }\necho $original->x, '/', $copy->x;\n",
    'setter-computed-temporary-retirement': b"<?php\nclass Denied { public private(set) int $x = 1; }\nfunction object_value() { echo 'O|'; return $GLOBALS['o']; }\nfunction property_name() { echo 'N|'; return 'x'; }\nfunction rhs() { echo 'R|'; unset($GLOBALS['o']); return 7; }\n$o = new Denied();\ntry { object_value()->{property_name()} = rhs(); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho isset($o) ? 'bound' : 'gone';\n",
    'setter-whole-reference-binding': b"<?php\nclass Denied { public private(set) int $x = 1; }\n$o = new Denied(); $source = 'bad';\ntry { $o->x =& $source; } catch (Error $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\necho $o->x, '/', $source;\n",
    'setter-delayed-cv-receiver': b"<?php\nclass Denied { public private(set) int $x = 1; }\nclass Allowed { public int $x = 2; }\nfunction replace_receiver() { global $o; echo 'R|'; $o = new Allowed(); return 7; }\n$o = new Denied(); $old = $o; $o->x = replace_receiver();\necho get_class($o), '/', $o->x, '/', $old->x;\n",
    'setter-temporary-receiver-stays-selected': b"<?php\nclass Denied { public private(set) int $x = 1; }\nclass Allowed { public int $x = 2; }\nfunction object_value() { echo 'O|'; return $GLOBALS['o']; }\nfunction replace_receiver() { global $o; echo 'R|'; $o = new Allowed(); return 7; }\n$o = new Denied(); $old = $o;\ntry { object_value()->x = replace_receiver(); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho get_class($o), '/', $o->x, '/', $old->x;\n",
    'setter-whole-object-operations': b"<?php\nclass Box { public function __toString(): string { echo 'T|'; return 'box'; } }\nclass Holder { public private(set) Box $box; public function __construct() { $this->box = new Box(); } }\n$o = new Holder();\ntry { $o->box += 1; } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\ntry { $o->box++; } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\ntry { $o->box .= 'x'; } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\necho get_class($o->box);\n",
    'setter-whole-aliased-object-operations': b"<?php\nclass Box { public function __toString(): string { echo 'T|'; return 'box'; } }\nclass Holder { public private(set) Box $box; public function bind(&$v) { $this->box =& $v; } }\n$external = new Box(); $o = new Holder(); $o->bind($external);\ntry { $o->box += 1; } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\ntry { $o->box++; } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\ntry { $o->box .= 'x'; } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\necho get_class($o->box), '/', get_class($external);\n",
    'setter-object-conversion-throw-priority': b"<?php\nclass Box { public function __toString(): string { echo 'T|'; throw new Exception('stop'); } }\nclass Holder { public private(set) Box $box; public function __construct() { $this->box = new Box(); } }\n$o = new Holder();\ntry { $o->box .= 'x'; } catch (Throwable $e) { echo get_class($e), '|', $e->getMessage(), '|'; }\necho get_class($o->box);\n",
    'setter-nested-unset-uninitialized': b"<?php\nclass Holder { public private(set) ?array $u; public private(set) array $a = [7]; }\n$o = new Holder(); unset($o->u['missing']); echo 'U|';\ntry { unset($o->a[0]); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho isset($o->u) ? 'yes/' : 'no/', $o->a[0];\n",
    'setter-object-foreach-reference': b"<?php\nclass Holder { public private(set) int $x = 1; public int $y = 2; }\n$o = new Holder();\ntry { foreach ($o as &$v) { echo 'F|'; $v = 9; } } catch (Error $e) { echo $e->getMessage(), '|'; }\necho $o->x, '/', $o->y;\n",
    'setter-array-coalesce-two-walks': b"<?php\nclass Holder { public private(set) array $a = [1]; }\nfunction rhs() { echo 'R|'; return 7; }\n$o = new Holder(); $o->a[0] ??= rhs(); echo $o->a[0], '|';\ntry { $o->a[1] ??= rhs(); } catch (Error $e) { echo $e->getMessage(), '|'; }\necho isset($o->a[1]) ? 'yes' : 'no';\n",
    'setter-autoarray-versus-setter': b"<?php\nclass Holder { public private(set) ?int $u = null; }\nfunction rhs() { echo 'R|'; return 7; }\n$o = new Holder();\ntry { $o->u[0] = rhs(); } catch (Throwable $e) {\n    echo get_class($e), '|', $e->getMessage(), '|';\n    $previous = $e->getPrevious(); echo $previous === null ? 'none' : get_class($previous);\n}\n",
    'setter-object-increment-previous': b"<?php\nclass Box {}\nclass Holder { public private(set) Box $box; public function __construct() { $this->box = new Box(); } }\n$o = new Holder();\ntry { $o->box++; } catch (Throwable $e) {\n    echo get_class($e), '|', $e->getMessage(), '|';\n    $previous = $e->getPrevious();\n    echo $previous === null ? 'none' : get_class($previous), '|';\n    if ($previous !== null) { echo $previous->getMessage(); }\n}\n",
    'setter-authorized-concat-restored-scope': b"<?php\nclass Box { public function __toString(): string { echo 'T|'; return 'box'; } }\nclass Owner {\n    public private(set) Box|string $value;\n    public function __construct() { $this->value = new Box(); }\n    public function append() { $this->value .= 'x'; }\n}\n$o = new Owner(); $o->append(); echo $o->value;\n",
    'setter-authorized-concat-typed-alias': b"<?php\nclass Box { public function __toString(): string { echo 'T|'; return 'box'; } }\nclass Owner {\n    public private(set) Box|string $value;\n    public function bind(&$external) { $this->value =& $external; }\n    public function append() { $this->value .= 'x'; }\n}\n$external = new Box(); $o = new Owner(); $o->bind($external); $o->append();\necho $o->value, '/', $external;\n",
    'setter-concat-global-destination-unset': b"<?php\nclass Box {\n    public function __toString(): string {\n        echo 'T|'; unset($GLOBALS['value']); return 'box';\n    }\n}\n$value = new Box(); $result = ($value .= 'x');\necho $result, '/', isset($value) ? 'bound' : 'gone';\n",
    'setter-concat-right-restored-destination': b"<?php\nclass RightValue {\n    public function __toString(): string {\n        echo 'T|'; $GLOBALS['owner']->replace(); unset($GLOBALS['owner']); return 'right';\n    }\n}\nclass Owner {\n    public private(set) string $value = 'left';\n    public function replace() { $this->value = 'changed'; }\n    public function append() {\n        $result = ($this->value .= new RightValue());\n        echo $result, '/', $this->value, '/', isset($GLOBALS['owner']) ? 'bound' : 'gone';\n    }\n}\n$owner = new Owner(); $owner->append();\n",
    'setter-concat-alias-destination-core': b"<?php\nclass Box {\n    public function __toString(): string {\n        echo 'T|'; unset($GLOBALS['value']); return 'box';\n    }\n}\nclass Owner {\n    public private(set) Box|string $value;\n    public function bind(&$external) { $this->value =& $external; }\n}\n$value = new Box(); $owner = new Owner(); $owner->bind($value);\n$result = ($value .= 'x');\necho $result, '/', ($owner->value === 'boxx' ? 'string' : 'wrong'), '/', isset($value) ? 'bound' : 'gone';\n",
    'setter-concat-private-reader-scope': b"<?php\nclass Box { public function __toString(): string { echo 'T|'; return 'box'; } }\nclass Owner {\n    private Box|string $value;\n    public function __construct() { $this->value = new Box(); }\n    public function append() { $this->value .= 'x'; echo $this->value; }\n}\n$owner = new Owner(); $owner->append();\n",
    'setter-concat-recursive-same-consumer': b"<?php\nclass Box {\n    public function __toString(): string {\n        echo 'T|';\n        if ($GLOBALS['reenter']) {\n            $GLOBALS['reenter'] = false; $GLOBALS['owner']->append(); echo 'N|';\n        }\n        return 'box';\n    }\n}\nclass Owner {\n    private Box|string $value;\n    public function __construct() { $this->value = new Box(); }\n    public function append() { $this->value .= 'x'; }\n    public function show() { echo $this->value; }\n}\n$reenter = true; $owner = new Owner(); $owner->append(); $owner->show();\n",
    'setter-array-nested-property-receiver': b"<?php\nclass Item { public int $x = 1; }\nclass Owner {\n    public private(set) array $items;\n    public function __construct() { $this->items = [new Item()]; }\n    public function put() { $this->items[0]->x = rhs(); }\n}\nfunction rhs() { echo 'R|'; return 7; }\n$owner = new Owner(); $owner->put(); echo $owner->items[0]->x, '|';\ntry { $owner->items[0]->x = rhs(); }\ncatch (Throwable $e) { echo $e->getMessage(), '|'; }\necho $owner->items[0]->x;\n",
    'setter-concat-fiber-retained-destination': b"<?php\nclass Box {\n    public function __toString(): string {\n        echo 'T|'; unset($GLOBALS['target']);\n        Fiber::suspend('pause'); return 'right';\n    }\n}\nclass Owner {\n    public private(set) string $value = 'left';\n    public static function writer() {\n        return static function () { return ($GLOBALS['target']->value .= new Box()); };\n    }\n}\n$target = new Owner(); $keep = $target; $fiber = new Fiber(Owner::writer());\necho $fiber->start(), '|', isset($target) ? 'bound' : 'gone', '|';\n$fiber->resume(); echo $fiber->getReturn();\n",
    'setter-untyped-rejection': b'<?php\nclass A { public private(set) $x; }\n',
    'setter-equal-private-untyped-rejection': b'<?php\nclass A { private private(set) $x; }\n',
    'setter-weaker-set-rejection': b'<?php\nclass A { protected public(set) int $x = 1; }\n',
    'setter-implicit-final-rejection': b'<?php\nclass A { public private(set) int $x = 1; }\nclass B extends A { public int $x = 2; }\n',
    'setter-inherited-narrower-rejection': b'<?php\nclass A { public protected(set) int $x = 1; }\nclass B extends A { public private(set) int $x = 2; }\n',
    'setter-inherited-added-restriction-rejection': b"<?php\nclass A { public int $x = 1; }\nclass B extends A { public protected(set) string $x = 'x'; }\n",
    'setter-inherited-type-invariance-rejection': b"<?php\nclass A { public protected(set) int $x = 1; }\nclass B extends A { public public(set) string $x = 'x'; }\n",
    'setter-final-private-priority-rejection': b'<?php\nclass A { final private private(set) $x; }\n',
}
EXPECTED = {
    'setter-simple-rhs-type-priority': b'R|Error|Cannot modify private(set) property Denied::$x from global scope|1',
    'setter-protected-family': b'2|3|Cannot modify protected(set) property Owner::$x from scope Stranger|3',
    'setter-private-called-scope': b'Child|2|Cannot modify private(set) property Owner::$x from scope Child|2',
    'setter-prototype-ancestor': b'3|Cannot modify protected(set) property Leaf::$x from global scope|3',
    'setter-dimension-effect-order': b'K|R|Cannot indirectly modify private(set) property Denied::$a from global scope|1',
    'setter-object-interior-raw-versus-alias': b'2|Cannot indirectly modify private(set) property Holder::$box from global scope|1/1',
    'setter-reference-acquisition': b'Cannot indirectly modify private(set) property Denied::$x from global scope|Cannot indirectly modify private(set) property Denied::$x from global scope|Cannot indirectly modify private(set) property Denied::$a from global scope|1/2',
    'setter-escaped-typed-alias': b'7|T|E|7/7',
    'setter-compound-and-uninitialized': b'R|Cannot modify private(set) property Denied::$x from global scope|Cannot modify private(set) property Denied::$x from global scope|Typed property Denied::$u must not be accessed before initialization|1/no',
    'setter-unset-and-owner-reinitialize': b'Cannot unset protected(set) property Owner::$x from global scope|Cannot unset protected(set) property Owner::$u from global scope|no|4/5',
    'setter-quiet-and-coalesce': b'yes|value|1|R|Cannot modify private(set) property Denied::$u from global scope|no',
    'setter-strict-type-versus-access': b'T|Error|1',
    'setter-rebound-closure-lexical-authority': b'Owner/Unrelated|9',
    'setter-clone-copy-and-denial': b'E|1/3',
    'setter-computed-temporary-retirement': b'O|N|R|Cannot modify private(set) property Denied::$x from global scope|gone',
    'setter-whole-reference-binding': b'Error|Cannot indirectly modify private(set) property Denied::$x from global scope|1/bad',
    'setter-delayed-cv-receiver': b'R|Allowed/7/1',
    'setter-temporary-receiver-stays-selected': b'O|R|Cannot modify private(set) property Denied::$x from global scope|Allowed/2/1',
    'setter-whole-object-operations': b'TypeError|Unsupported operand types: Box + int|Error|Cannot modify private(set) property Holder::$box from global scope|T|Error|Cannot modify private(set) property Holder::$box from global scope|Box',
    'setter-whole-aliased-object-operations': b'TypeError|Unsupported operand types: Box + int|Error|Cannot modify private(set) property Holder::$box from global scope|T|Error|Cannot modify private(set) property Holder::$box from global scope|Box/Box',
    'setter-object-conversion-throw-priority': b'T|Exception|stop|Box',
    'setter-nested-unset-uninitialized': b'U|Cannot indirectly modify private(set) property Holder::$a from global scope|no/7',
    'setter-object-foreach-reference': b'F|F|9/9',
    'setter-array-coalesce-two-walks': b'1|R|Cannot indirectly modify private(set) property Holder::$a from global scope|no',
    'setter-autoarray-versus-setter': b'R|Error|Cannot indirectly modify private(set) property Holder::$u from global scope|none',
    'setter-object-increment-previous': b'Error|Cannot modify private(set) property Holder::$box from global scope|TypeError|Cannot increment Box',
    'setter-authorized-concat-restored-scope': b'T|boxx',
    'setter-authorized-concat-typed-alias': b'T|boxx/boxx',
    'setter-concat-global-destination-unset': b'T|boxx/bound',
    'setter-concat-right-restored-destination': b'T|leftright/leftright/gone',
    'setter-concat-alias-destination-core': b'T|boxx/string/gone',
    'setter-concat-private-reader-scope': b'T|boxx',
    'setter-concat-recursive-same-consumer': b'T|T|N|boxx',
    'setter-array-nested-property-receiver': b'R|7|R|Cannot indirectly modify private(set) property Owner::$items from global scope|7',
    'setter-concat-fiber-retained-destination': b'T|pause|gone|leftright',
}
COMPILED = {
    'setter-untyped-rejection': (b'Property with asymmetric visibility A::$x must have type', 2),
    'setter-equal-private-untyped-rejection': (b'Property with asymmetric visibility A::$x must have type', 2),
    'setter-weaker-set-rejection': (b'Visibility of property A::$x must not be weaker than set visibility', 2),
    'setter-implicit-final-rejection': (b'Cannot override final property A::$x', 3),
    'setter-inherited-narrower-rejection': (b'Set access level of B::$x must be protected(set) (as in class A) or weaker', 3),
    'setter-inherited-added-restriction-rejection': (b'Set access level of B::$x must be omitted (as in class A)', 3),
    'setter-inherited-type-invariance-rejection': (b'Type of B::$x must be int (as in class A)', 3),
    'setter-final-private-priority-rejection': (b'Property cannot be both final and private', 2),
}

def compile_source(info, directory, path):
    message, line = info
    observed = cross.invoke.process([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
        str(path)], directory / 'native', 30, directory)
    assert observed.returncode == 255 and observed.stdout == b''
    assert observed.stderr == b'Fatal error: ' + message + b' in ' + os.fsencode(path) + b' on line ' + str(line).encode() + b'\nStack trace:\n#0 {main}\n'
    facts = {'version': 2, 'main': cross.invoke.b64(os.fsencode(path)),
             'cwd': cross.invoke.b64(os.fsencode(directory)), 'include_path': cross.invoke.b64(b'.:'),
             'entries': [], 'chdir_entries': []}
    facts_path = directory / 'snapshot.json'
    facts_path.write_text(json.dumps(facts, sort_keys=True) + '\n')
    result = cross.invoke.process([str(ROOT / 'bin/php-semantics'), str(path), '--file-snapshot',
        str(facts_path), '--steps', '100000', '--timeout', '60'], directory / 'model', 90, directory)
    assert result.returncode == 0 and not result.stderr
    outcome = json.loads(result.stdout)
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == 'static_rejection' and outcome['exit_status'] == 255
    assert outcome['reason'] is None
    assert outcome['diagnostic']['class'] == 'CompileError' and outcome['diagnostic']['line'] == line
    assert base64.b64decode(outcome['diagnostic']['message'], validate=True) == message
    assert base64.b64decode(outcome['stdout'], validate=True) == observed.stdout
    assert base64.b64decode(outcome['stderr'], validate=True) == observed.stderr
    return {'status': 'static_rejection', 'exit_status': 255}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='instance-set-access-sources-', dir=ROOT / '.tools'))
    report = {'passed': False, 'completed': False, 'before': before,
              'profile': cross.invoke.types.PROFILE, 'selected': selected, 'records': []}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source = directory / 'source.php'; source.write_bytes(CASES[name])
            row = {'case': name, 'source_sha256': cross.invoke.sha(source), 'completed': False}
            report['records'].append(row)
            row['outcome'] = compile_source(COMPILED[name], directory, source) if name in COMPILED else cross.source(
                {'abrupt': False, 'expected_exit_status': 0, 'expected_stdout': EXPECTED[name].decode()}, directory, source)
            assert cross.snapshot(args.freeze) == before
            row['completed'] = True
            print(name, row['outcome']['status'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
