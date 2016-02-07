#define NPY_NO_DEPRECATED_API NPY_1_10_API_VERSION
#include "Python.h"
#include "numpy/arrayobject.h"
#include "trueskill.h"
#include <sstream>
#include <vector>

template<typename T>
static bool validate_stride(PyArrayObject *x, const char *argname)
{
	int ndims = PyArray_NDIM(x);
	int stride = PyArray_STRIDE(x,ndims-1);

	if (stride != sizeof(T))
	{
		std::ostringstream s;
		s << "Expected PyArray '" << argname << "' with stride " << sizeof(T) << ", encountered stride " << stride;
		PyErr_SetString(PyExc_ValueError, s.str().c_str());
		Py_INCREF(PyExc_ValueError);
	}
	return stride == sizeof(T);
}

static PyObject* quality_1vs1(PyObject *self, PyObject *args)
{
	PyArrayObject *env_obj, *r1_obj, *r2_obj;
	if (!PyArg_ParseTuple(args, "OOO", &env_obj, &r1_obj, &r2_obj))
		return NULL;

	if (!validate_stride<double>(env_obj,"env") || !validate_stride<double>(r1_obj,"r1") || !validate_stride<double>(r2_obj,"r2"))
		return NULL;

	npy_intp *env_dims = PyArray_DIMS(env_obj);
	npy_intp *r1_dims = PyArray_DIMS(r1_obj);
	npy_intp *r2_dims = PyArray_DIMS(r2_obj);
	PyArrayObject *q = (PyArrayObject*)PyArray_ZEROS(1, r1_dims, NPY_DOUBLE, 0);

	for (int n=0; n<r1_dims[0]; ++n)
	{
		*(npy_double*)PyArray_GETPTR1(q,n) = trueskill::quality_1vs1(
			(npy_double*)PyArray_GETPTR1(env_obj,0),
			(npy_double*)PyArray_GETPTR1(r1_obj,n),
			(npy_double*)PyArray_GETPTR1(r2_obj,n)
			);
	}

	return Py_BuildValue("N",q);
}

static PyObject* likelihood_outcome_1vs1(PyObject *self, PyObject *args)
{
	PyArrayObject *env_obj, *score12_obj, *r1_obj, *r2_obj;
	if (!PyArg_ParseTuple(args, "OOOO", &env_obj, &score12_obj, &r1_obj, &r2_obj))
		return NULL;

	if (!validate_stride<double>(env_obj,"env") || !validate_stride<double>(r1_obj,"r1") || !validate_stride<double>(r2_obj,"r2"))
		return NULL;

	npy_intp *n_dims = PyArray_DIMS(score12_obj);
	PyArrayObject *L = (PyArrayObject*)PyArray_ZEROS(1, n_dims, NPY_DOUBLE, 0);

	for (int n=0; n<n_dims[0]; ++n)
	{
		*(npy_double*)PyArray_GETPTR1(L,n) = trueskill::likelihood_outcome_1vs1(
			(npy_double*)PyArray_GETPTR1(env_obj,0), 
			*(npy_int*)PyArray_GETPTR1(score12_obj,n),
			(npy_double*)PyArray_GETPTR1(r1_obj,n),
			(npy_double*)PyArray_GETPTR1(r2_obj,n)
			);
	}

	return Py_BuildValue("N",L);
}


static PyObject* rate_1vs1(PyObject *self, PyObject *args)
{
	PyArrayObject *env_obj, *pid1_obj, *pid2_obj, *score12_obj, *ratings_by_pid_obj;
	if (!PyArg_ParseTuple(args, "OOOOO", &env_obj, &pid1_obj, &pid2_obj, &score12_obj, &ratings_by_pid_obj))
		return NULL;

	if (!validate_stride<double>(env_obj,"env") || !validate_stride<double>(ratings_by_pid_obj,"ratings_by_pid"))
		return NULL;

	npy_intp *n_dims = PyArray_DIMS(pid1_obj);
	npy_intp nx2_dims[] = { n_dims[0], 2 };
	PyArrayObject *r1 = (PyArrayObject*)PyArray_ZEROS(2, nx2_dims, NPY_DOUBLE, 0);
	PyArrayObject *r2 = (PyArrayObject*)PyArray_ZEROS(2, nx2_dims, NPY_DOUBLE, 0);
	PyArrayObject *L = (PyArrayObject*)PyArray_ZEROS(1, n_dims, NPY_DOUBLE, 0);
	PyArrayObject *nGames1 = (PyArrayObject*)PyArray_ZEROS(1, n_dims, NPY_INT, 0);
	PyArrayObject *nGames2 = (PyArrayObject*)PyArray_ZEROS(1, n_dims, NPY_INT, 0);

	std::vector<int> gameCount(n_dims[0],0);
	for (int n=0; n<n_dims[0]; ++n)
	{
		int pid1 = *(npy_int*)PyArray_GETPTR1(pid1_obj,n);
		int pid2 = *(npy_int*)PyArray_GETPTR1(pid2_obj,n);
		int score12 = *(npy_int*)PyArray_GETPTR1(score12_obj,n);

		// record prior rating
		*(npy_double*)PyArray_GETPTR2(r1,n,trueskill::MU) = *(npy_double*)PyArray_GETPTR2(ratings_by_pid_obj,pid1,trueskill::MU);
		*(npy_double*)PyArray_GETPTR2(r1,n,trueskill::SIGMA) = *(npy_double*)PyArray_GETPTR2(ratings_by_pid_obj,pid1,trueskill::SIGMA);
		*(npy_double*)PyArray_GETPTR2(r2,n,trueskill::MU) = *(npy_double*)PyArray_GETPTR2(ratings_by_pid_obj,pid2,trueskill::MU);
		*(npy_double*)PyArray_GETPTR2(r2,n,trueskill::SIGMA) = *(npy_double*)PyArray_GETPTR2(ratings_by_pid_obj,pid2,trueskill::SIGMA);

		// update and record player game count
		*(npy_int*)PyArray_GETPTR1(nGames1,n) = gameCount[pid1]++;
		*(npy_int*)PyArray_GETPTR1(nGames2,n) = gameCount[pid2]++;

		// record likelihood of outcome based on prior rating
		*(npy_double*)PyArray_GETPTR1(L,n) = trueskill::likelihood_outcome_1vs1(
			(npy_double*)PyArray_GETPTR1(env_obj,0),
			score12,
			(npy_double*)PyArray_GETPTR1(ratings_by_pid_obj, pid1), 
			(npy_double*)PyArray_GETPTR1(ratings_by_pid_obj, pid2)
			);

		// update rating
		trueskill::rate_1vs1(
			(npy_double*)PyArray_GETPTR1(env_obj,0), 
			score12, 
			(npy_double*)PyArray_GETPTR1(ratings_by_pid_obj, pid1), 
			(npy_double*)PyArray_GETPTR1(ratings_by_pid_obj, pid2)
			);
	}

	return Py_BuildValue("NNNNN",r1,r2,nGames1,nGames2,L);
}

static PyMethodDef PyTrueSkillMethods[] = {
    {"quality_1vs1",  quality_1vs1, METH_VARARGS, "Calculate match quality for 1vs1 matches"},
    {"likelihood_outcome_1vs1",  likelihood_outcome_1vs1, METH_VARARGS, "Calculate likelihood of outcomes for 1vs1 matches"},
	{"rate_1vs1",  rate_1vs1, METH_VARARGS, "Updating ratings for a series of matches"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpytrueskill(void)
{
    (void) Py_InitModule("pytrueskill", PyTrueSkillMethods);
	import_array();
}
