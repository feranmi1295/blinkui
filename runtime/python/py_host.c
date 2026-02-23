#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* CPython embedding API */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "py_host.h"

/* ─────────────────────────────────────────
   Internal state
───────────────────────────────────────── */
static bool py_initialized = false;

/* ─────────────────────────────────────────
   Initialize CPython
───────────────────────────────────────── */
bool bk_py_init(void) {
    if (py_initialized) {
        fprintf(stderr, "[PyHost] Already initialized\n");
        return true;
    }

    Py_Initialize();

    if (!Py_IsInitialized()) {
        fprintf(stderr, "[PyHost] Failed to initialize CPython\n");
        return false;
    }

    py_initialized = true;
    printf("[PyHost] CPython %s initialized\n", PY_VERSION);
    return true;
}

/* ─────────────────────────────────────────
   Shutdown CPython
───────────────────────────────────────── */
void bk_py_shutdown(void) {
    if (!py_initialized) return;

    Py_Finalize();
    py_initialized = false;
    printf("[PyHost] CPython shutdown\n");
}

/* ─────────────────────────────────────────
   Check if running
───────────────────────────────────────── */
bool bk_py_is_running(void) {
    return py_initialized && Py_IsInitialized();
}

/* ─────────────────────────────────────────
   Print last Python error
───────────────────────────────────────── */
void bk_py_print_error(void) {
    if (PyErr_Occurred()) {
        PyErr_Print();
    }
}

/* ─────────────────────────────────────────
   Load a Python file
───────────────────────────────────────── */
bool bk_py_load_file(const char* filepath) {
    if (!bk_py_is_running()) {
        fprintf(stderr, "[PyHost] Python not initialized\n");
        return false;
    }

    FILE* f = fopen(filepath, "r");
    if (!f) {
        fprintf(stderr, "[PyHost] Cannot open file: %s\n", filepath);
        return false;
    }

    int result = PyRun_SimpleFile(f, filepath);
    fclose(f);

    if (result != 0) {
        fprintf(stderr, "[PyHost] Error running file: %s\n", filepath);
        bk_py_print_error();
        return false;
    }

    printf("[PyHost] Loaded: %s\n", filepath);
    return true;
}

/* ─────────────────────────────────────────
   Internal helper — get module and function
───────────────────────────────────────── */
static PyObject* bk_py_get_function(const char* module, const char* function) {
    PyObject* py_module = PyImport_ImportModule(module);
    if (!py_module) {
        fprintf(stderr, "[PyHost] Cannot import module: %s\n", module);
        bk_py_print_error();
        return NULL;
    }

    PyObject* py_func = PyObject_GetAttrString(py_module, function);
    Py_DECREF(py_module);

    if (!py_func || !PyCallable_Check(py_func)) {
        fprintf(stderr, "[PyHost] Cannot find function: %s.%s\n", module, function);
        bk_py_print_error();
        return NULL;
    }

    return py_func;
}

/* ─────────────────────────────────────────
   Call a Python function — no arguments
───────────────────────────────────────── */
bool bk_py_call(const char* module, const char* function) {
    PyObject* py_func = bk_py_get_function(module, function);
    if (!py_func) return false;

    PyObject* result = PyObject_CallNoArgs(py_func);
    Py_DECREF(py_func);

    if (!result) {
        fprintf(stderr, "[PyHost] Error calling %s.%s\n", module, function);
        bk_py_print_error();
        return false;
    }

    Py_DECREF(result);
    printf("[PyHost] Called %s.%s()\n", module, function);
    return true;
}

/* ─────────────────────────────────────────
   Call a Python function with string arg
───────────────────────────────────────── */
bool bk_py_call_with_string(
    const char* module,
    const char* function,
    const char* arg
) {
    PyObject* py_func = bk_py_get_function(module, function);
    if (!py_func) return false;

    PyObject* py_arg  = PyUnicode_FromString(arg);
    PyObject* py_args = PyTuple_Pack(1, py_arg);
    PyObject* result  = PyObject_Call(py_func, py_args, NULL);

    Py_DECREF(py_arg);
    Py_DECREF(py_args);
    Py_DECREF(py_func);

    if (!result) {
        fprintf(stderr, "[PyHost] Error calling %s.%s\n", module, function);
        bk_py_print_error();
        return false;
    }

    Py_DECREF(result);
    printf("[PyHost] Called %s.%s(\"%s\")\n", module, function, arg);
    return true;
}

/* ─────────────────────────────────────────
   Call a Python function with int arg
───────────────────────────────────────── */
bool bk_py_call_with_int(
    const char* module,
    const char* function,
    int arg
) {
    PyObject* py_func = bk_py_get_function(module, function);
    if (!py_func) return false;

    PyObject* py_arg  = PyLong_FromLong(arg);
    PyObject* py_args = PyTuple_Pack(1, py_arg);
    PyObject* result  = PyObject_Call(py_func, py_args, NULL);

    Py_DECREF(py_arg);
    Py_DECREF(py_args);
    Py_DECREF(py_func);

    if (!result) {
        fprintf(stderr, "[PyHost] Error calling %s.%s\n", module, function);
        bk_py_print_error();
        return false;
    }

    Py_DECREF(result);
    printf("[PyHost] Called %s.%s(%d)\n", module, function, arg);
    return true;
}

/* ─────────────────────────────────────────
   Call Python function and get string back
───────────────────────────────────────── */
char* bk_py_call_get_string(const char* module, const char* function) {
    PyObject* py_func = bk_py_get_function(module, function);
    if (!py_func) return NULL;

    PyObject* result = PyObject_CallNoArgs(py_func);
    Py_DECREF(py_func);

    if (!result) {
        fprintf(stderr, "[PyHost] Error calling %s.%s\n", module, function);
        bk_py_print_error();
        return NULL;
    }

    /* convert Python string to C string */
    const char* py_str = PyUnicode_AsUTF8(result);
    char* c_str = NULL;

    if (py_str) {
        c_str = strdup(py_str);
    }

    Py_DECREF(result);
    return c_str;
}