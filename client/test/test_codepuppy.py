import unittest
from sys import argv

from codepuppy import CodePuppy


class TestCodePuppy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        这里是所有测试用例前的准备工作
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        这里是所有测试用例后的清理工作
        """
        pass

    def setUp(self):
        """
        这里是一个测试用例前的准备工作
        """
        print("TestCodePuppy > " + "=" * 120)

    def tearDown(self):
        """
        这里是一个测试用例后的清理工作
        """
        print("TestCodePuppy < " + "=" * 120)

    def test_no_param(self):
        CodePuppy().main()

    def test_help_param(self):
        argv.append("help")
        CodePuppy().main()


if __name__ == '__main__':
    # Test CodePuppy
    unittest.main(verbosity=2)
