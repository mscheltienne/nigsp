#!/usr/bin/env python3
"""Tests for operations.surrogates."""
import numpy as np
from numpy.random import rand, seed
from pytest import raises

from nigsp.operations import surrogates, graph_fourier_transform, decomposition


# ### Unit tests
def test_random_sign():
    n_surr = 4
    random_seed = 2
    eigenvec = rand(20)

    rs = surrogates.random_sign(eigenvec, n_surr, random_seed, stack=True)

    seed(random_seed)

    rand_evec = np.empty((eigenvec.shape + (n_surr,)), dtype='float32')
    for i in range(n_surr):
        r_sign = np.random.rand(eigenvec.shape[0]).round()
        r_sign[r_sign == 0] = -1
        rand_evec[..., i] = eigenvec * r_sign
    rand_evec = np.append(rand_evec, eigenvec[..., np.newaxis], axis=-1)

    assert rs.ndim == 2
    assert rs.shape[-1] == (eigenvec.size + 1) 
    assert (rand_evec == rs).all()

    # #!# Implement stricter checks on signs
    pass 

def test_create_surr():
    eigenvec = rand(2, 2)
    timeseries = rand(2, 4)
    n_surr = 3
    seed = 2

    cs = surrogates._create_surr(timeseries, eigenvec, n_surr, seed, stack=True)

    rand_evec = surrogates.random_sign(eigenvec, n_surr, seed, stack=True)
    surr = np.empty((timeseries.shape + (n_surr+1,)), dtype='float32')
    fourier_coeff = graph_fourier_transform(timeseries, eigenvec)

    for i in range(n_surr+1):
        surr[..., i] = graph_fourier_transform(fourier_coeff, rand_evec[..., i].T)

    assert cs.ndim == 3
    assert all(cs.shape == surr.shape)
    assert (cs == surr).all()


def test_sc_informed():
    eigenvec = rand(2, 2)
    timeseries = rand(2, 4)
    n_surr = 3
    seed = 2

    surr = surrogates._create_surr(timeseries, eigenvec, n_surr, seed, stack=True)
    cs = surrogates.sc_informed(timeseries, eigenvec, n_surr, seed, stack=True)

    assert cs.ndim == 3
    assert all(cs.shape == surr.shape)
    assert (cs == surr).all()


def test_sc_uninformed():
    lapl_mtx = rand(2, 2)
    timeseries = rand(2, 4)
    n_surr = 3
    seed = 2

    symm_norm = np.eye(lapl_mtx.shape[0]) - lapl_mtx
    symm_norm_sum = symm_norm.sum(axis=-1)
    conf_model = np.outer(symm_norm_sum,
                          symm_norm_sum.T) / symm_norm.sum()
    conf_lapl = np.diag(symm_norm_sum) - conf_model
    _, surr_eigenvec = decomposition(conf_lapl)
    surr = surrogates._create_surr(timeseries, surr_eigenvec, n_surr, seed, stack=True)

    cs = surrogates.sc_informed(timeseries, lapl_mtx, n_surr, seed, stack=True)

    assert cs.ndim == 3
    assert all(cs.shape == surr.shape)
    assert (cs == surr).all()


def test_test_significance():
    pass


# ### Break tests
def test_break_random_sign():
    with raises(NotImplementedError) as errorinfo:
        surrogates.random_sign(rand(2, 3, 4, 5))
    assert 'has 4 dimensions' in str(errorinfo.value)


def test_break_create_surr():
    with raises(NotImplementedError) as errorinfo:
        surrogates._create_surr(rand(2, 3, 4, 5), rand(2, 2), 1, 2, False)
    assert 'timeseries of 4 dimensions' in str(errorinfo.value)

    with raises(NotImplementedError) as errorinfo:
        surrogates._create_surr(rand(2), rand(2, 2), 1, 2, False)
    assert ('timeseries of 1 dimensions and eigenvector matrix of 2 dimensions'
            in str(errorinfo.value))


def test_break_sc_informed():
    with raises(NotImplementedError) as errorinfo:
        surrogates.sc_informed(rand(2, 3, 4, 5), rand(2, 2))
    assert 'has 4 dimensions' in str(errorinfo.value)


def test_break_sc_uninformed():
    with raises(NotImplementedError) as errorinfo:
        surrogates.sc_uninformed(rand(2, 3, 4, 5), rand(2, 2))
    assert 'has 4 dimensions' in str(errorinfo.value)


def test_break_test_significance():
    with raises(NotImplementedError) as errorinfo:
        surrogates.test_significance(rand(2, 3, 5), method='Baobab')
    assert 'Other testing methods' in str(errorinfo.value)

    with raises(ValueError) as errorinfo:
        surrogates.test_significance(rand(2, 3, 5), rand(2, 4))
    assert 'shapes do not agree' in str(errorinfo.value)
