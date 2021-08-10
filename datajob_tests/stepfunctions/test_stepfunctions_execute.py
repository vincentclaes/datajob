import unittest
from datetime import datetime

from datajob.stepfunctions import stepfunctions_execute


class TestStepfunctionsExecute(unittest.TestCase):
    def test_generate_unique_name_successfully(self):
        # freeze time
        current_date = datetime(2021, 1, 1, 12, 0, 1)
        # test with a long string and check that the result will be max allowed characters
        unique_name = stepfunctions_execute._generate_unique_name(
            name="a" * stepfunctions_execute.MAX_CHARS, unique_identifier=current_date
        )
        self.assertEqual(len(unique_name), stepfunctions_execute.MAX_CHARS)

        # test with a short string and check that the datetime will be appended
        unique_name = stepfunctions_execute._generate_unique_name(
            name="a" * 1, unique_identifier=current_date
        )
        self.assertEqual(unique_name, "a-20210101T120001")
