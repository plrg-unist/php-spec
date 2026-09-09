/* Fixture-only external clock/environment transport; does not evaluate PHP. */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>

extern char **environ;
static struct timeval request_clock;
static int request_clock_ready;
static uint64_t remaining;

static void invalid_request(void)
{
    static const char message[] = "php-spec request provider: invalid fixture transport\n";
    (void) write(STDERR_FILENO, message, sizeof(message) - 1);
    _exit(125);
}

static void read_bytes(void *buffer, size_t count)
{
    unsigned char *cursor = buffer;
    if (count > remaining)
        invalid_request();
    remaining -= count;
    while (count) {
        ssize_t got = read(198, cursor, count);
        if (got < 0 && errno == EINTR)
            continue;
        if (got <= 0)
            invalid_request();
        cursor += got;
        count -= (size_t) got;
    }
}

static uint64_t read_integer(size_t count)
{
    unsigned char bytes[8];
    uint64_t value = 0;
    read_bytes(bytes, count);
    for (size_t index = 0; index < count; index++)
        value |= (uint64_t) bytes[index] << (8 * index);
    return value;
}

__attribute__((constructor)) static void load_request(void)
{
    struct stat status;
    char magic[8];
    char **environment;
    uint64_t seconds_bits;
    int64_t seconds;
    uint32_t microseconds, count;
    if (fstat(198, &status) || !S_ISREG(status.st_mode) || status.st_size < 0)
        invalid_request();
    remaining = (uint64_t) status.st_size;
    read_bytes(magic, sizeof(magic));
    if (memcmp(magic, "PHPRQ001", sizeof(magic)))
        invalid_request();
    seconds_bits = read_integer(8);
    memcpy(&seconds, &seconds_bits, sizeof(seconds));
    microseconds = (uint32_t) read_integer(4);
    count = (uint32_t) read_integer(4);
    if (microseconds > 999999 || count > remaining / 4)
        invalid_request();
    environment = calloc((size_t) count + 1, sizeof(char *));
    if (environment == NULL)
        invalid_request();
    for (uint32_t index = 0; index < count; index++) {
        uint32_t length = (uint32_t) read_integer(4);
        if (length > remaining)
            invalid_request();
        environment[index] = malloc((size_t) length + 1);
        if (environment[index] == NULL)
            invalid_request();
        read_bytes(environment[index], length);
        if (memchr(environment[index], '\0', length) ||
            !memchr(environment[index], '=', length))
            invalid_request();
        environment[index][length] = '\0';
    }
    if (remaining || close(198))
        invalid_request();
    request_clock.tv_sec = (time_t) seconds;
    request_clock.tv_usec = (suseconds_t) microseconds;
    if ((int64_t) request_clock.tv_sec != seconds)
        invalid_request();
    environ = environment;
    request_clock_ready = 1;
}

int gettimeofday(struct timeval *restrict value, void *restrict timezone)
{
    if (!request_clock_ready || timezone != NULL)
        invalid_request();
    *value = request_clock;
    return 0;
}
