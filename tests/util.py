from __future__ import annotations
import typing as tp
from unittest import TestCase
from racketinterpreter.classes import data as d
from racketinterpreter.util import Util

if tp.TYPE_CHECKING:
    from racketinterpreter.classes.data import Data


def interpret_text(test_case: TestCase, text: str, expected: tp.List[Data]):
    output, _ = Util.text_to_interpreter_result(text)

    output_len = len(output)
    expected_len = len(expected)
    test_case.assertEqual(output_len, expected_len)

    for actual_data, expected_data in zip(output, expected):
        test_case.assertEqual(type(actual_data), type(expected_data))
        if issubclass(type(expected_data), d.InexactNum):
            test_case.assertTrue(abs(actual_data.value - expected_data.value) < 0.01)
        elif type(expected_data) is d.Procedure:
            test_case.assertEqual(actual_data.value, expected_data.value)
        else:
            test_case.assertEqual(actual_data, expected_data)
