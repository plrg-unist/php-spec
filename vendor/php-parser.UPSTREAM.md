# Vendored PHP-Parser

- Project: https://github.com/nikic/PHP-Parser
- Version: `v5.8.0`
- Commit: `044a6a392ff8ad0d61f14370a5fbbd0a0107152f`
- Annotated tag: `744279544c5df262ba19571dda3692d71c7713df`
- Tag date: `2026-07-04T14:30:59Z`
- Imported: `2026-09-08`
- Archive: https://codeload.github.com/nikic/PHP-Parser/tar.gz/044a6a392ff8ad0d61f14370a5fbbd0a0107152f
- Archive SHA-256: `1ea5871603f12e38f485dd78e84ceee16be2e02af0eab807cb4d40a6fc11730f`
- License: [BSD-3-Clause](php-parser/LICENSE)

`php-parser/` contains all 274 regular files from this upstream distribution,
with its enclosing archive directory removed. Four runtime files now carry
[documented grammar/printer corrections](../patches/README.md); all other
distribution files remain unchanged. The original archives are retained locally. The upstream archive includes the generated parsers,
library, CLI, README, license and Composer metadata; it omits development
tests, grammar sources and documentation. No nested Git repository is included.

To reproduce the import, download the exact commit archive above, verify its
SHA-256, and extract its contents into a fresh `php-parser/` directory after
removing the single enclosing directory. Reject links and escaping paths, and
compare every imported file with the corresponding archive entry. To update,
resolve the chosen upstream tag to its commit, repeat this process, and update
this record. Review the upstream changes and rerun frontend validation before
adopting a new version.

The library requires PHP >= 7.4 with tokenizer and JSON support. This project's
selected runtime is locally pinned PHP 8.5.10. Use `bin/php-syntax` for the
checked frontend, not the unmodified upstream CLI.
