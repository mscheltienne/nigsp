#!/usr/bin/env python3
"""Tests for io."""

import sys

from os import remove
from os.path import isfile

import nibabel
import scipy
import pymatreader

from numpy import empty, asarray, genfromtxt, savetxt
from numpy.random import rand
from pytest import mark, raises

from crispyoctobroccoli import io


# ### Unit tests

def test_check_ext():
    """Text check_ext."""
    all_ext = io.EXT_1D + io.EXT_MAT + io.EXT_NIFTI
    for ext_in in all_ext:
        fname_in = f'shiny{ext_in}'

        for fname in [fname_in, fname_in.upper()]:
            has_ext, fname_out = io.check_ext(all_ext, fname)

            assert has_ext is True
            assert fname_out == fname

            has_ext, fname_out, ext_out = io.check_ext(all_ext, fname, remove=True)

            assert has_ext is True
            assert fname_out == fname[:-len(ext_in)]
            assert ext_out == ext_in

    # #!# Missing scan option

    fname_in = 'shiny.mal'
    for fname in [fname_in, fname_in.upper()]:
        has_ext, fname_out = io.check_ext('.inara', fname)

        assert has_ext is False
        assert fname_out == fname

        has_ext, fname_out, ext_out = io.check_ext('.inara', fname, remove=True)

        assert has_ext is False
        assert fname_out == fname
        assert ext_out == ''


@mark.parametrize('data', [
    (rand(3, 4)),
    (rand(3, 4, 1)),
    (rand(3, 1, 4))
])
def test_check_nifti_dim(data):
    """Test check_nifti_dim."""
    data_out = io.check_nifti_dim('kaylee', data, dim=2)

    assert all(data_out == data.squeeze())
    assert data_out.ndim == 2


@mark.parametrize('data', [
    (rand(3, 4)),
    (rand(3, 4, 1)),
    (rand(3, 1, 4))
])
def test_check_mtx_dim(data):
    """Test check_mtx_dim."""
    data_out = io.check_mtx_dim('wash', data)

    assert (data_out == data).all()
    assert data_out.ndim == 2


@mark.parametrize('data, shape', [
    (rand(3), 'rectangle'),
    (rand(3, 3), 'square')
])
def test_check_mtx_dim_cases(data, shape):
    """Test check_mtx_dim for specific shapes."""
    data_out = io.check_mtx_dim('wash', data, shape=shape)

    assert all(data_out.squeeze() == data)
    assert data_out.ndim == 2


def test_load_nifti_get_mask():
    """Test load_nifti_get_mask."""
    # #!#
    pass


def test_load_txt():
    """Test load_txt."""
    a = rand(5)
    n = 'zoe'
    savetxt(n, a)
    b = io.load_txt(n)

    assert all(a == b)

    remove(n)


def test_load_mat():
    a = rand(5)
    b = 'likealeaf'
    n = 'inthewind'

    scipy.io.savemat(n, {'data': a, 'other': b})

    c = io.load_mat(n)

    assert all(a == c)
    remove(n)


def test_export_nifti():
    # #!# NEEDS IMAGE
    # io.export_nifti(rand(3, 4, 5), img, 'book')
    # assert isfile('book.nii.gz')
    pass


@mark.parametrize('ext_in, ext_out', [
    ('.1D', '.1D'),
    ('.csv', '.csv'),
    ('.tsv', '.tsv'),
    ('', '.csv'),
    ('.mat', '.mat')
])
def test_export_mtx(ext_in, ext_out):
    """Test export_mtx."""
    data = asarray[[1, 1, 2], [3, 5, 8]]
    io.export_mtx(data, 'serenity', ext=ext_in)
    assert isfile(f'serenity{ext_out}')

    if ext_out in ['.csv', '.tsv', '.1D']:
        data_in = genfromtxt(f'serenity{ext_out}')

    if ext_out in ['.mat']:
        data_in = pymatreader.read_mat(f'serenity{ext_out}')

    assert all(data_in == data)
    # remove data
    remove(f'serenity{ext_out}')


# ### Break tests
@mark.parametrize('data', [
    (rand(3)),
    (rand(3, 4, 2))
])
def break_check_nifti_dim(data):
    """Break check_nifti_dim."""
    with raises(ValueError) as errorinfo:
        io.check_nifti_dim('jayne', data, dim=2)
    assert f'jayne is {data.ndim}D' in str(errorinfo.value)


def break_check_mtx_dim():
    with raises(ValueError) as errorinfo:
        io.check_mtx_dim('river', empty(0))
    assert 'river is empty' in str(errorinfo.value)

    with raises(NotImplementedError) as errorinfo:
        io.check_mtx_dim('river', rand(3, 4, 5))
    assert '2D matrices are' in str(errorinfo.value)

    with raises(ValueError) as errorinfo:
        io.check_mtx_dim('river', rand(3, 4), shape='square')
    assert 'river matrix has shape (3, 4)' in str(errorinfo.value)


def break_load_nifti_get_mask():
    sys.modules['nibabel'] = None
    with raises(ImportError) as errorinfo:
        io.load_nifti_get_mask('reavers')
    assert 'is required' in str(errorinfo.value)
    sys.modules['nibabel'] = nibabel


def break_load_mat():
    sys.modules['pymatreader'] = None
    with raises(ImportError) as errorinfo:
        io.load_mat('simon')
    assert 'is required' in str(errorinfo.value)
    sys.modules['pymatreader'] = pymatreader

    a = 'heart'
    n = 'ofgold'
    scipy.io.savemat(n, {'data': a})

    with raises(EOFError) as errorinfo:
        io.load_mat(n)
    assert f'{n} does not seem' in str(errorinfo.value)
    remove(n)


def break_load_xls():
    with raises(NotImplementedError) as errorinfo:
        io.load_xls('firefly')
    assert 'output is not' in str(errorinfo.value)


def break_export_nifti():
    sys.modules['nibabel'] = None
    with raises(ImportError) as errorinfo:
        io.export_nifti(rand(3), None, 'reavers')
    assert 'is required' in str(errorinfo.value)
    sys.modules['nibabel'] = nibabel


def break_export_mtx():
    with raises(NotImplementedError) as errorinfo:
        io.export_mtx(rand(3, 4), 'lostinthewoods', ext='.xls')
    assert 'output is not' in str(errorinfo.value)

    sys.modules['scipy'] = None
    with raises(ImportError) as errorinfo:
        io.load_mat('lostinthewoods')
    assert 'is required' in str(errorinfo.value)
    sys.modules['scipy'] = scipy

# ### Examples


# @fixture(scope='function')
# def loaded_lab_file(multifreq_lab_file):
#     chtrig = 1
#     header_lab, channels_lab = io.read_header_and_channels(multifreq_lab_file)

#     # just a few quick checks to make sure the data loaded correctly
#     assert len(channels_lab[0]) == 5
#     assert 'Interval=' in header_lab[0]

#     return header_lab, channels_lab, chtrig


# def test_extract_header_items_errors(loaded_lab_file):
#     header, channels, chtrig = loaded_lab_file
#     # test file without header
#     with raises(AttributeError) as errorinfo:
#         io.extract_header_items(channels, header=[])
#     assert 'without header' in str(errorinfo.value)
#     # test when header is not valid
#     with raises(AttributeError) as errorinfo:
#         io.extract_header_items(channels, header=['hello', 'bye'])
#     assert 'supported yet for txt files' in str(errorinfo.value)