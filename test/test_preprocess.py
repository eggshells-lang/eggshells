import unittest

from src.eggshells import Interpreter


class PreprocessTest(unittest.TestCase):
    def test_preprocess_simple(self):
        es = Interpreter()
        script = """(println "this is a test")"""

        result = es.preprocess_script(script)
        expected = [["(", "println", '"this is a test"', ")"]]

        self.assertEqual(result, expected)
