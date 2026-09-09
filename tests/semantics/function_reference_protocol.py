from pathlib import Path
import function_call_protocol
ROOT = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    raise SystemExit(0 if function_call_protocol.main(ROOT / 'tests/semantics/function_reference_protocol_cases.json', 'function-reference-protocol') else 1)
