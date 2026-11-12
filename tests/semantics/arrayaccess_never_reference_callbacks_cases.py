"""Never callbacks must fail at EOF before returning a result."""

CASES = [
    {
        'id': 'all-never-callbacks-fallthrough',
        'source': '''<?php
class NeverReferenceCallbacks implements ArrayAccess {
    public function &offsetExists($offset): never { echo "E;"; }
    public function &offsetGet($offset): never { echo "G;"; }
    public function &offsetSet($offset, $value): never { echo "S;"; }
    public function &offsetUnset($offset): never { echo "U;"; }
}
$box = new NeverReferenceCallbacks();
try { isset($box[1]); } catch (TypeError $error) { echo "I;"; }
try { $box[2]; } catch (TypeError $error) { echo "R;"; }
$rhs = 17;
try { $used = $box[3] = $rhs; } catch (TypeError $error) { echo "W:", $rhs, ";"; }
try { unset($box[4]); } catch (TypeError $error) { echo "D;"; }
echo "Z;";
''',
        'expected_stdout': 'E;I;G;R;S;W:17;U;D;Z;',
    },
]
