/* Optional Bison reduction coverage; never used by the ordinary oracle. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

__attribute__((constructor)) static void enable_parser_trace(void) {
    int *debug = dlsym(RTLD_DEFAULT, "zenddebug");
    if (!debug) {
        fputs("coverage build lacks exported zenddebug\n", stderr);
        abort();
    }
    *debug = 1;
}
