from __future__ import annotations
from typing import TYPE_CHECKING, List
from unittest import TestCase
from racketinterpreter.classes.data import (
    Boolean, ConsList, InexactNum, Integer, Procedure, RationalNum, String, Symbol
)
from racketinterpreter.util import Util

if TYPE_CHECKING:
    from racketinterpreter.classes.data import Data


def interpret_text(test_case: TestCase, text: str, expected: List[Data]):
    output, _ = Util.text_to_interpreter_result(text)

    output_len = len(output)
    expected_len = len(expected)
    test_case.assertEqual(output_len, expected_len)

    for actual_data, expected_data in zip(output, expected):
        test_case.assertEqual(type(actual_data), type(expected_data))
        if issubclass(type(expected_data), InexactNum):
            test_case.assertTrue(abs(actual_data.value - expected_data.value) < 0.01)
        elif type(expected_data) is Procedure:
            test_case.assertEqual(actual_data.value, expected_data.value)
        else:
            test_case.assertEqual(actual_data, expected_data)
