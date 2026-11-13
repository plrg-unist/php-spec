"""Late marked current keys retain real base-cell providers after owner loss."""
from string_offset_request_callback_raw_key_cell_owner_cases import CASES as OWNERS

CASES = [dict(OWNERS[0],
    id='request-callback-marked-raw-key-current-base-owner',
    source=OWNERS[0]['source'].replace('requestRawCellOwner', 'requestRawMarkedOwner').replace(
        '    $GLOBALS[$name] = $message;',
        '    $replacementKey = $message;\n    $GLOBALS[$name] =& $replacementKey;'),
    read_line=21),
    dict(OWNERS[1],
    id='request-callback-marked-raw-key-distinct-base-owner',
    source=OWNERS[1]['source'].replace('requestRawCellOwner', 'requestRawMarkedOwner').replace(
        '    $name = "key";',
        '    $GLOBALS["alias"] =& $GLOBALS["key"];\n    $name = "key";').replace(
        '";P:", $keeper, ";Z;"', '";P:", $keeper, ";A:", $alias, ";Z;"'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;P:abc;A:String offset cast occurred;Z;',
    read_line=25)]
