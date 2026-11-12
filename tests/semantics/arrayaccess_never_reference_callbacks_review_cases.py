"""Never callbacks may leave through ordinary Error without an EOF TypeError."""

CASES = [{
    'id': 'ordinary-abrupt-error-never-callbacks',
    'source': '''<?php
class AbruptNeverReferenceReview implements ArrayAccess {
 public function &offsetExists($offset): never { echo 'E;'; throw new Error('abrupt'); }
 public function &offsetGet($offset): never { echo 'G;'; throw new Error('abrupt'); }
 public function &offsetSet($offset, $value): never { echo 'S;'; throw new Error('abrupt'); }
 public function &offsetUnset($offset): never { echo 'U;'; throw new Error('abrupt'); }
}
$box = new AbruptNeverReferenceReview;
try { isset($box[1]); } catch (TypeError $e) { echo 'BAD;'; } catch (Error $e) { echo 'I;'; }
try { $read = $box[2]; } catch (TypeError $e) { echo 'BAD;'; } catch (Error $e) { echo 'R;'; }
$rhs = 17;
try { $out = ($box[3] = $rhs); } catch (TypeError $e) { echo 'BAD;'; } catch (Error $e) { echo 'W:', $rhs, ';'; }
try { unset($box[4]); } catch (TypeError $e) { echo 'BAD;'; } catch (Error $e) { echo 'D;'; }
echo 'Z;';
''',
    'expected_stdout': 'E;I;G;R;S;W:17;U;D;Z;',
}]
