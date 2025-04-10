import unittest
import test_utils
import test_api
import test_analyser

if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_api))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_utils))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_analyser))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    if result.wasSuccessful():
        print("All tests passed!")
    else:
        print("Some tests failed.")