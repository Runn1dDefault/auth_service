import unittest

from tests import test_dao
from tests import test_api


if __name__ == '__main__':
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(test_dao)
    suite.addTests(loader.loadTestsFromModule(test_api))

    runner = unittest.TextTestRunner()
    runner.run(suite)
