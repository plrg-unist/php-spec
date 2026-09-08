<?php declare(strict_types=1);

function wireDecode($value) {
    if (!$value instanceof stdClass || ($value->wire ?? null) !== 'php-flat-1') return $value;
    if ($value->root !== 0 || count(get_object_vars($value)) !== 3) throw new RuntimeException('Invalid flat wire header');
    $rows = $value->values;
    $values = array_fill(0, count($rows), null);
    $child = static function ($ref, int $index) use (&$values): mixed {
        if (!is_int($ref) || $ref <= $index || $ref >= count($values)) throw new RuntimeException('Invalid flat reference');
        return $values[$ref];
    };
    for ($i = count($rows) - 1; $i >= 0; --$i) {
        if (count($rows[$i]) !== 2) throw new RuntimeException('Invalid flat row');
        [$kind, $payload] = $rows[$i];
        if ($kind === 0 && !is_array($payload) && !is_object($payload)) $values[$i] = $payload;
        elseif ($kind === 1) $values[$i] = array_map(fn($ref) => $child($ref, $i), $payload);
        elseif ($kind === 2) {
            $item = new stdClass();
            foreach ($payload as [$key, $ref]) {
                if (!is_string($key) || property_exists($item, $key)) throw new RuntimeException('Invalid flat object key');
                $item->{$key} = $child($ref, $i);
            }
            $values[$i] = $item;
        } else throw new RuntimeException('Invalid flat row kind');
    }
    return $values[0];
}

function wireDeep($value): bool {
    $pending = [[$value, 0]];
    while ($pending) {
        [$item, $depth] = array_pop($pending);
        if ($depth > 256) return true;
        if (is_array($item) || $item instanceof stdClass) foreach ($item as $child) $pending[] = [$child, $depth + 1];
    }
    return false;
}

function wireEncode($value) {
    if (!wireDeep($value)) return $value;
    $values = [$value];
    for ($i = 0; $i < count($values); ++$i) {
        $item = $values[$i];
        if (is_array($item) || $item instanceof stdClass) {
            $object = $item instanceof stdClass || !array_is_list($item);
            $refs = [];
            foreach ($item as $key => $child) {
                $refs[] = $object ? [$key, count($values)] : count($values);
                $values[] = $child;
            }
            $values[$i] = [$object ? 2 : 1, $refs];
        } else $values[$i] = [0, $item];
    }
    return ['wire' => 'php-flat-1', 'root' => 0, 'values' => $values];
}
