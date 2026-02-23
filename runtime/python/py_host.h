#ifndef BK_PY_HOST_H
#define BK_PY_HOST_H

#include <stdbool.h>

/* ─────────────────────────────────────────
   Python host — embeds CPython inside
   the BlinkUI C runtime
───────────────────────────────────────── */

/* Initialize CPython interpreter */
bool bk_py_init(void);

/* Shutdown CPython interpreter */
void bk_py_shutdown(void);

/* Load a Python file by path */
bool bk_py_load_file(const char* filepath);

/* Call a Python function by module and function name */
/* Returns true if call succeeded */
bool bk_py_call(const char* module, const char* function);

/* Call a Python function with a string argument */
bool bk_py_call_with_string(
    const char* module,
    const char* function,
    const char* arg
);

/* Call a Python function with an int argument */
bool bk_py_call_with_int(
    const char* module,
    const char* function,
    int arg
);

/* Get a string result from a Python function */
/* Caller must free the returned string */
char* bk_py_call_get_string(const char* module, const char* function);

/* Check if Python is initialized */
bool bk_py_is_running(void);

/* Print last Python error to stderr */
void bk_py_print_error(void);

#endif /* BK_PY_HOST_H */