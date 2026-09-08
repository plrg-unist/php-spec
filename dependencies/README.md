# Pinned build and corpus inputs

Run `scripts/build-deps.sh` from any directory. It builds PHP, the local OCaml
switch, and SpecTec using local inputs; ordinary builds do not fetch packages.
`JOBS=8` is the default. `scripts/opam-exec.sh COMMAND ...` selects that switch
and the local SpecTec libraries. Generated tools and logs live under `.tools/`. PHP configures a disposable
`.tools/php-src` copy because its configure script edits a source header template.
Run `scripts/verify-inputs.py` to check imported bytes, executable modes and links.

System prerequisites (tested Ubuntu 24.04, x86_64): Bash, Python 3.12, GCC 13.3,
make 4.3, pkg-config 1.8, autoconf 2.71, Bison 3.8, re2c 3.1, xz-utils, patch,
unzip, opam 2.5.2 and GMP development headers (`libgmp-dev`). The local switch
builds OCaml 5.1.0 itself. On Debian/Ubuntu install `build-essential python3
pkg-config autoconf bison re2c xz-utils patch unzip libgmp-dev opam`.

| Input | Pin and provenance |
|---|---|
| `vendor/php-src` | Complete PHP 8.5.10 release, including PHPT fixtures and `run-tests.php`; tag commit `34308a6666b2d489c509541ea9befea9e2b42348`. [Official announcement](https://www.php.net/releases/8_5_10.php), [release metadata](https://www.php.net/releases/index.php?json&version=8.5.10). The retained `.tar.xz` SHA256 is `6a8bebaa4d5a979a38db29a9373e9851f60c6b11f72172c585947e78f3081957`, matching `php-release.json`. PHP/Zend and bundled component notices remain in the source tree. |
| `vendor/p4-spectec` | Unchanged Git tree `da36ac3c434cd291940293a63da64544307730a3`, imported from the existing workspace checkout. [Upstream](https://github.com/kaist-plrg/p4-spectec/tree/da36ac3c434cd291940293a63da64544307730a3); Apache-2.0, `LICENSE`. P4 compiler submodule content is unnecessary and not imported. |
| `vendor/opam-repository`, `vendor/opam-cache` | The exact 97 package recipes in `opam-packages.txt`, imported from the study's compatible switch/repository and its content-addressed archive cache. Recipes retain origins, checksums and individual license fields; archives include upstream licenses. This includes all non-system compiler/library/PPX inputs, not only the top-level packages. |
| `vendor/php-parser-source` | PHP-Parser v5.8.0, commit `044a6a392ff8ad0d61f14370a5fbbd0a0107152f`; BSD-3-Clause. Distribution plus unchanged upstream `grammar/` and `test/` obtained from a detached checkout because the distribution excludes them. The complete checkout archive is retained separately under `vendor/archives`. This is evidence; execution uses `vendor/php-parser`. |
| `corpora/bolaray` | All 25 application snapshots copied byte-for-byte from the supplied [BolaRay artifact](https://zenodo.org/records/13744942) benchmark directory. `bolaray-snapshots.json` records per-application tree hashes, file counts and license notices. Components keep their licenses; an absent application license is recorded without inventing one. The published image archive hash is informational; the supplied unpacked source was pinned directly. |

`files.jsonl` is the complete per-file SHA256/mode manifest for these imports;
it also records internal SpecTec symlinks. No nested repositories are imported.
Upstream source paths and URLs above are provenance, never runtime dependencies.
The original PHP-Parser distribution provenance remains in
`vendor/php-parser.UPSTREAM.md`.

The PHP build is CLI, NTS, 64-bit on this host, with tokenizer, JSON and mbstring.
Bundled libmbfl supports source-encoding profiles; mbregex is disabled to avoid
an unnecessary external regex dependency. Normal calls use `-n` plus explicit
syntax-relevant INI settings. This is a syntax oracle, not an application runtime.

For the complete Linux isolation audit, run `scripts/portable-check.sh`. It needs
`sudo`, mount and network namespaces. It copies source inputs without Git or build
products to a fresh `/var/tmp` path, hides `/home` and `/tmp`, disables networking,
and runs dependency builds plus the documented build/test/validation/inventory
checks. The printed audit directory retains the results for inspection.
