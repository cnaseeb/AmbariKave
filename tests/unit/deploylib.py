##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################
import unittest
import base


class TestDeployLib(unittest.TestCase):

    def runTest(self):
        """
        Tests which cehck the function of the deployment library,
        but do not need any environment parameters or access to aws
        """
        import kavedeploy as lD

        lD.testproxy()
        self.assertIsNot(lD.which("ls"), None)
        self.assertRaises(RuntimeError, lD.run_quiet, ("thisisnotacommand"))
        stdout = lD.run_quiet(['which', 'ls'], shell=False)
        self.assertTrue('/bin/ls' in stdout)
        self.assertIsNot(lD.which("pdsh"), None,
                         "pdsh is not installed, please install it in order to test the multiremotes functionality, "
                         "sudo yum -y install pdsh")
        lD.run_quiet("touch /tmp/fake_test_ssh_key.pem")
        lD.run_quiet("chmod 400 /tmp/fake_test_ssh_key.pem")
        test = lD.remoteHost("root", "test", '/tmp/fake_test_ssh_key.pem')
        test = lD.multiremotes([test.host], access_key='/tmp/fake_test_ssh_key.pem')


class TestJSON(unittest.TestCase):

    def runTest(self):
        """
        Checks that every json file under the deployment or tests dir is correct json!
        """
        import kavedeploy as lD
        import os

        deploydir = os.path.dirname(lD.__file__)
        testdir = os.path.dirname(__file__)
        import glob
        import json

        jsons = glob.glob(deploydir + "/*/*.json") + glob.glob(testdir + "/../*/*.json") + glob.glob(
            testdir + "/../*/*/*.json")
        for jsonfile in jsons:
            # print jsonfile
            f = open(jsonfile)
            l = f.read()
            f.close()
            self.assertTrue(len(l) > 1, "json file " + jsonfile + " is a fragment or corrupted")
            try:
                interp = json.loads(l)
            except:
                self.assertTrue(False, "json file " + jsonfile + " is not complete or not readable")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDeployLib())
    suite.addTest(TestJSON())
    return suite


if __name__ == "__main__":
    base.run(suite())
