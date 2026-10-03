# Warning reads and borrowed references

Module208 extends PHP 8.5.10 strict identity reads. When the left CV initially
refers to a reference cell and the right CV is missing, `===` and `!==` retain
the old cell's borrowed payload location across the warning callback. Rebinding
the left name selects another cell; an in-place write updates the retained cell.
The comparison reads that old payload against the missing read's original null.

The source-derived certificate records both names/lines, operator and cell. A
separate pointer moves into the genuine saved caller and authenticates the resumed
task after rebinding. It adds no reference-cell owner. Nested callbacks keep
distinct pointers; throw cleanup retires only the interrupted scope. Expired
borrowed lifetime is Unsupported. Native tests keep the cell alive; owner-removal
negatives are constructed helper controls only.

Defined ordinary `$GLOBALS[key]` uses the real global table independently of
request mode. Callback locals remain separate. Missing-global warnings, whole
table snapshots and request auto-globals retain their separate bounds. Plain CVs
that become reference wrappers during the callback, arithmetic left pointers,
truth/cast/copy/SEND and other producers remain open. Paused return validation
is not part of this slice.

Primary timing comes from `IS_IDENTICAL`/`IS_NOT_IDENTICAL`, undefined-CV helpers,
direct `FETCH_GLOBAL` compilation and singleton-reference `ARRAY_UNPACK` in the
pinned Zend sources. Bounded author and independent gates are accepted:

| Tested source | Source observations | Reached checks |
| --- | --- | --- |
| Private f15d1f056 | Six normal tuples plus one Unsupported control0agreement; independent three models reuse native originals | Author3/162; independent2/130 |
| Getter/setter composition f9592b6ca | Fresh static-setter source1 and independent nested null-getter/array-setter source1 | Author1/74; independent1/111 |
| Method-string composition c67e3511f | Fresh selected inherited static caller/handler source1 | One77 |

The independent getter gate uses finite-file facts with include_path=.:; the
other gates use ordinary13. Their exact revisions, raw commands, streams, exits
and separate peer reviews are in the [ledger](../../coverage/semantics/warning-reads-review.json).
Canonical publication is source-equivalent and adds no fresh runtime credit.

The maintained compiler is the regular `.tools/spectec/bin/p4spectec` executable
provisioned by `scripts/build-deps.sh`. In a built project root, prepare then run
only the selected current interaction:

```sh
python3 -B tests/semantics/warning_read_string_protocol.py prepare
python3 -B tests/semantics/warning_read_string_protocol.py run .tools/warning-reads/PREPARED/report.json
```

Use the actual preparation directory. The fixed runner records full streams,
exits and owned cleanup, with native45s/model90s/finite300s limits and150s/330s
phases. The prior static-setter interaction has its own fixed protocol helper;
the historical seven-source family retains its zero-agreement control. Reused
local tools establish no fresh offline rebuild or complete-core coverage.
