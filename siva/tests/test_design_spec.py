import pytest
from ..design.spec import Spec, Pass, Fail, Marginal, Max, Min, Range, Tolerance

def test_spec_result_equality():
    assert Pass() == Marginal
    assert Pass == Pass
    assert Pass != Fail

@pytest.fixture
def range_spec():
    return Range(min=98, max=102)

def test_tolerance_specs():
    test_range_spec(Tolerance(100, percent=2, units="MHz"))
    test_range_spec(Tolerance(100, range=[-2,2], units="MHz"))
    test_range_spec(Tolerance(100, range=2, units="MHz"))
    test_range_spec(Range(min=98, max=102, units="MHz"))

def test_range_spec(range_spec):
    spec = range_spec

    assert spec.range[0] == 98
    assert spec.range[1] == 102

    assert spec.min == 98
    assert spec.max == 102

    assert spec.eval(98) == Pass
    assert spec.eval(100) == Pass
    assert spec.eval(102) == Pass

    assert spec.eval(97) == Fail
    assert spec.eval(103) == Fail


def test_asymmetric_range_spec():
    spec = Range(min=98, max=115)

    assert spec.range[0] == 98
    assert spec.range[1] == 115

    assert spec.min == 98
    assert spec.max == 115

    assert spec.eval(98) == Pass
    assert spec.eval(100) == Pass
    assert spec.eval(102) == Pass

    assert spec.eval(97) == Fail
    assert spec.eval(120) == Fail


def test_min_spec():
    spec = Min(20.5, margin=0.5)

    assert spec.min == 20.5
    assert spec.eval(100) == Pass
    assert spec.eval(0) == Fail
    assert spec.eval(20.2) == Fail


def test_min_spec_with_margin():
    spec = Min(20.5, margin=0.5)

    assert spec.min == 20.5
    assert spec.eval(100) == Pass
    assert spec.eval(0) == Fail
    assert spec.eval(20.2) == Fail
    assert spec.eval(20.7) == Marginal


def test_max_spec_w_margin():
    spec = Max(20.5, margin=0.5)

    assert spec.max == 20.5
    assert spec.eval(100) == Fail
    assert spec.eval(0) == Pass
    assert spec.eval(20.2) == Marginal
    assert spec.eval(20.7) == Fail


def test_max_spec():
    spec = Max(20.5)
    assert spec.max == 20.5
    assert spec.eval(100) == Fail
    assert spec.eval(0) == Pass
    assert spec.eval(20.2) == Marginal
    assert spec.eval(20.7) == Fail

