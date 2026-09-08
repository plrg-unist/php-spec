/*
   +----------------------------------------------------------------------+
   | Copyright (c) The PHP Group                                          |
   +----------------------------------------------------------------------+
   | This source file is subject to version 3.01 of the PHP license,      |
   | that is bundled with this package in the file LICENSE, and is        |
   | available through the world-wide-web at the following url:           |
   | https://www.php.net/license/3_01.txt                                 |
   | If you did not receive a copy of the PHP license and are unable to   |
   | obtain it through the world-wide-web, please send a note to          |
   | license@php.net so we can mail you a copy immediately.               |
   +----------------------------------------------------------------------+
   | Author: Andrei Zmievski <andrei@php.net>                             |
   +----------------------------------------------------------------------+
*/

/* File-mode adaptation of PHP 8.5.10 tokenizer lifecycle/lex loop.
 * Local modifications: file input, raw lexer metadata, and parse-only oracle.
 * No compilation, opcode generation, or evaluation entrypoint is called. */
#include "php.h"
#include "Zend/zend_smart_str.h"
#include "Zend/zend_exceptions.h"
#include "Zend/zend_language_scanner.h"
#include "Zend/zend_language_scanner_defs.h"
#include "Zend/zend_language_parser.h"
#include "Zend/zend_multibyte.h"

#if PHP_VERSION_ID != 80510
#error "This helper is pinned to PHP 8.5.10"
#endif

static void append_token(zval *tokens, int id, const unsigned char *text,
                         size_t length, int line, size_t pos) {
    zval item;
    array_init_size(&item, 4);
    add_next_index_long(&item, id);
    add_next_index_stringl(&item, (const char *)text, length);
    add_next_index_long(&item, line);
    add_next_index_long(&item, pos);
    add_next_index_zval(tokens, &item);
}

static void scan_file(INTERNAL_FUNCTION_PARAMETERS, bool parse) {
    zend_string *path;
    HashTable *events = NULL;
    ZEND_PARSE_PARAMETERS_START(1, parse ? 1 : 2)
        Z_PARAM_PATH_STR(path)
        Z_PARAM_OPTIONAL
        Z_PARAM_ARRAY_HT(events)
    ZEND_PARSE_PARAMETERS_END();

    if (events && zend_hash_num_elements(events) && !CG(multibyte)) {
        zend_value_error("Encoding events require zend.multibyte");
        RETURN_THROWS();
    }
    if (events) {
        if (!zend_array_is_list(events)) {
            zend_value_error("Encoding events must be a list");
            RETURN_THROWS();
        }
        zval *event;
        zend_long previous = -1;
        ZEND_HASH_FOREACH_VAL(events, event) {
            zval *token, *name;
            if (Z_TYPE_P(event) != IS_ARRAY
                || !(token = zend_hash_str_find(Z_ARRVAL_P(event), "token", sizeof("token")-1))
                || !(name = zend_hash_str_find(Z_ARRVAL_P(event), "encoding", sizeof("encoding")-1))
                || Z_TYPE_P(token) != IS_LONG || Z_LVAL_P(token) <= previous
                || Z_TYPE_P(name) != IS_STRING
                || !zend_multibyte_fetch_encoding(Z_STRVAL_P(name))) {
                zend_value_error("Encoding events require increasing token ordinals and known encodings");
                RETURN_THROWS();
            }
            previous = Z_LVAL_P(token);
        } ZEND_HASH_FOREACH_END();
    }
    zend_lex_state saved;
    zend_file_handle file;
    bool compiling = CG(in_compilation), shebang = CG(skip_shebang);
    bool encoding_declared = CG(encoding_declared);
    bool increment_lineno = CG(increment_lineno);
    zend_save_lexical_state(&saved);
    CG(skip_shebang) = 1;
    zend_stream_init_filename(&file, ZSTR_VAL(path));
    if (open_file_for_scanning(&file) == FAILURE) {
        zend_restore_lexical_state(&saved);
        CG(skip_shebang) = shebang;
        CG(increment_lineno) = increment_lineno;
        zend_destroy_file_handle(&file);
        if (!EG(exception)) zend_throw_error(NULL, "Cannot open syntax input");
        RETURN_THROWS();
    }

    if (parse) {
        CG(in_compilation) = 1;
        CG(ast) = NULL;
        CG(ast_arena) = zend_arena_create(1024 * 32);
        bool accepted = zendparse() == SUCCESS;
        zend_ast_destroy(CG(ast));
        zend_arena_destroy(CG(ast_arena));
        RETVAL_BOOL(accepted);
    } else {
        const zend_encoding *initial_encoding = CG(multibyte) ? LANG_SCNG(script_encoding) : NULL;
        zend_string *initial_source = zend_string_init((const char *)LANG_SCNG(yy_start),
            LANG_SCNG(yy_limit) - LANG_SCNG(yy_start), 0);
        zend_string *original_source = CG(multibyte)
            ? zend_string_init((const char *)LANG_SCNG(script_org), LANG_SCNG(script_org_size), 0)
            : zend_string_copy(initial_source);
        zval applied;
        array_init(&applied);
        smart_str stitched = {0};
        zend_ulong event_index = 0;
        zend_long ordinal = 0;
        size_t prefix_length = 0;
        zval tokens, token;
        array_init(&tokens);
        ZVAL_UNDEF(&token);
        int id, line = 1, remaining = -1;
        bool first = true;
        while ((id = lex_scan(&token, NULL))) {
            size_t pos = LANG_SCNG(yy_text) - LANG_SCNG(yy_start);
            if (first) {
                // File-mode scanning discards a leading shebang line.
                for (size_t i = 0; i < pos; ++i) {
                    if (LANG_SCNG(yy_start)[i] == '\n'
                        || (LANG_SCNG(yy_start)[i] == '\r'
                            && (i + 1 == pos || LANG_SCNG(yy_start)[i + 1] != '\n'))) ++line;
                }
                prefix_length = pos;
                smart_str_appendl(&stitched, (const char *)LANG_SCNG(yy_start), pos);
                first = false;
            }
            append_token(&tokens, id, LANG_SCNG(yy_text), LANG_SCNG(yy_leng), line, pos);
            smart_str_appendl(&stitched, (const char *)LANG_SCNG(yy_text), LANG_SCNG(yy_leng));
            if (Z_TYPE(token) != IS_UNDEF) {
                zval_ptr_dtor_nogc(&token);
                ZVAL_UNDEF(&token);
            }
            if (EG(exception)) break;
            zval *event = events ? zend_hash_index_find(events, event_index) : NULL;
            if (event && ordinal == Z_LVAL_P(zend_hash_str_find(Z_ARRVAL_P(event), "token", sizeof("token")-1))) {
                zval *name = zend_hash_str_find(Z_ARRVAL_P(event), "encoding", sizeof("encoding")-1);
                const zend_encoding *encoding = zend_multibyte_fetch_encoding(Z_STRVAL_P(name));
                zend_encoding_filter old_filter = LANG_SCNG(input_filter);
                const zend_encoding *old_encoding = LANG_SCNG(script_encoding);
                zval record;
                array_init(&record);
                add_assoc_long(&record, "token", ordinal);
                add_assoc_long(&record, "offset", LANG_SCNG(yy_cursor) - LANG_SCNG(yy_start));
                add_assoc_string(&record, "encoding", zend_multibyte_get_encoding_name(encoding));
                add_next_index_zval(&applied, &record);
                zend_multibyte_set_filter(encoding);
                if (old_filter != LANG_SCNG(input_filter) || (old_filter && old_encoding != encoding)) {
                    zend_multibyte_yyinput_again(old_filter, old_encoding);
                }
                ++event_index;
            }
            ++ordinal;
            if (remaining != -1) {
                if (id != T_WHITESPACE && id != T_OPEN_TAG && id != T_COMMENT
                    && id != T_DOC_COMMENT && --remaining == 0) {
                    if (LANG_SCNG(yy_cursor) < LANG_SCNG(yy_limit)) {
                        smart_str_appendl(&stitched, (const char *)LANG_SCNG(yy_cursor), LANG_SCNG(yy_limit) - LANG_SCNG(yy_cursor));
                        append_token(&tokens, T_INLINE_HTML, LANG_SCNG(yy_cursor),
                            LANG_SCNG(yy_limit) - LANG_SCNG(yy_cursor), line,
                            LANG_SCNG(yy_cursor) - LANG_SCNG(yy_start));
                    }
                    break;
                }
            } else if (id == T_HALT_COMPILER) {
                remaining = 3;
            }
            if (CG(increment_lineno)) {
                CG(zend_lineno)++;
                CG(increment_lineno) = 0;
            }
            line = CG(zend_lineno);
        }
        array_init(return_value);
        add_assoc_zval(return_value, "tokens", &tokens);
        add_assoc_str(return_value, "initial_source", initial_source);
        add_assoc_str(return_value, "original_source", original_source);
        size_t length = LANG_SCNG(yy_limit) - LANG_SCNG(yy_start);
        add_assoc_stringl(return_value, "filtered_source", (const char *)LANG_SCNG(yy_start), length);
        if (first) {
            prefix_length = length;
            smart_str_appendl(&stitched, (const char *)LANG_SCNG(yy_start), length);
        }
        smart_str_0(&stitched);
        if (stitched.s) {
            add_assoc_stringl(return_value, "preamble", ZSTR_VAL(stitched.s), prefix_length);
            add_assoc_str(return_value, "source", stitched.s);
        } else {
            add_assoc_string(return_value, "source", "");
            add_assoc_string(return_value, "preamble", "");
        }
        add_assoc_zval(return_value, "events", &applied);
        if (initial_encoding) {
            add_assoc_string(return_value, "source_encoding", zend_multibyte_get_encoding_name(initial_encoding));
        } else {
            add_assoc_null(return_value, "source_encoding");
        }
        if (CG(multibyte) && LANG_SCNG(script_encoding)) {
            add_assoc_string(return_value, "final_encoding", zend_multibyte_get_encoding_name(LANG_SCNG(script_encoding)));
        } else {
            add_assoc_null(return_value, "final_encoding");
        }
    }
    zend_restore_lexical_state(&saved);
    CG(in_compilation) = compiling;
    CG(skip_shebang) = shebang;
    CG(encoding_declared) = encoding_declared;
    CG(increment_lineno) = increment_lineno;
    zend_destroy_file_handle(&file);
    // Match token_get_all() without TOKEN_PARSE: raw lexing does not throw
    // parser exceptions. The independent parser diagnoses its token stream.
    if (!parse) zend_clear_exception();
    if (EG(exception)) RETURN_THROWS();
}

PHP_FUNCTION(php_spec_parse_file) { scan_file(INTERNAL_FUNCTION_PARAM_PASSTHRU, true); }
PHP_FUNCTION(php_spec_lex_file) { scan_file(INTERNAL_FUNCTION_PARAM_PASSTHRU, false); }

/* Use the exact pinned registry (canonical, MIME, then aliases), including
 * its C-string declaration semantics. This reads metadata, never source code. */
PHP_FUNCTION(php_spec_encoding_name) {
    zend_string *name;
    ZEND_PARSE_PARAMETERS_START(1, 1)
        Z_PARAM_STR(name)
    ZEND_PARSE_PARAMETERS_END();
    const zend_encoding *encoding = zend_multibyte_fetch_encoding(ZSTR_VAL(name));
    if (!encoding) RETURN_NULL();
    RETURN_STRING(zend_multibyte_get_encoding_name(encoding));
}

ZEND_BEGIN_ARG_WITH_RETURN_TYPE_INFO_EX(arginfo_encoding_name, 0, 1, IS_STRING, 1)
    ZEND_ARG_TYPE_INFO(0, name, IS_STRING, 0)
ZEND_END_ARG_INFO()
ZEND_BEGIN_ARG_WITH_RETURN_TYPE_INFO_EX(arginfo_parse_file, 0, 1, _IS_BOOL, 0)
    ZEND_ARG_TYPE_INFO(0, path, IS_STRING, 0)
ZEND_END_ARG_INFO()
ZEND_BEGIN_ARG_WITH_RETURN_TYPE_INFO_EX(arginfo_lex_file, 0, 1, IS_ARRAY, 0)
    ZEND_ARG_TYPE_INFO(0, path, IS_STRING, 0)
    ZEND_ARG_TYPE_INFO_WITH_DEFAULT_VALUE(0, events, IS_ARRAY, 0, "[]")
ZEND_END_ARG_INFO()
static const zend_function_entry functions[] = {
    PHP_FE(php_spec_parse_file, arginfo_parse_file)
    PHP_FE(php_spec_lex_file, arginfo_lex_file)
    PHP_FE(php_spec_encoding_name, arginfo_encoding_name)
    PHP_FE_END
};
zend_module_entry php_file_module_entry = {
    STANDARD_MODULE_HEADER, "php_spec_file", functions,
    NULL, NULL, NULL, NULL, NULL, "8.5.10-1", STANDARD_MODULE_PROPERTIES
};
ZEND_GET_MODULE(php_file)
