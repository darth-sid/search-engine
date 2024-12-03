#include <Python.h>

static PyObject* hamming_distance(PyObject *self, PyObject *args) {
    int hash_1, hash_2;

    if (!PyArg_ParseTuple(args, "ii", &hash_1, &hash_2)) {
        return NULL;
    }

    int dist = 0;
    int x = hash_1 ^ hash_2;
    for(; x > 0; x = (x >> 1)){
        dist += x % 2;
    }

    return PyLong_FromLong(dist);
}

static PyMethodDef simhash_methods[] {
    {"hamming_distance", hamming_distance, METH_VARARGS, ""}
}

static struct PyModuleDef simhashC = {
    PyModuleDef_HEAD_INIT,
    "simhashC",
    "A simhashing module written in C",
    -1,
    simhash_methods
};

PyMODINIT_FUNC PyInit_simhashC(void) {
    return PyModule_Create(&simhashC);
}
