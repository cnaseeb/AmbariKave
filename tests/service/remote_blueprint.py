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
import base
import unittest


class TestBlueprint(base.LDTest):

    def runTest(self):
        """
        The remote_blueprint test ups a dev machine and submits a blueprint to it.
        It monitors the status of the request corresponding to the blueprint
        """
        # create remote machine
        import os
        import sys
        import json

        lD = self.pre_check()
        deploy_dir = os.path.realpath(os.path.dirname(lD.__file__) + '/../')
        af = os.path.dirname(__file__) + "/blueprints/default.aws.json"
        bp = os.path.dirname(__file__) + "/blueprints/" + self.service + ".blueprint.json"
        cf = os.path.dirname(__file__) + "/blueprints/default.cluster.json"
        if not os.path.exists(bp):
            raise ValueError("No blueprint with which to install " + self.service)
        self.verify_blueprint(af, bp, cf)
        ambari, iid = self.deploy_dev("c4.2xlarge")  # 2xlarge needed for single node hadoop!
        # clean the existing blueprint ready for re-install
        self.pull(ambari)
        self.resetambari(ambari)
        self.deploy_blueprint(ambari, bp, cf)
        return self.check(ambari)


if __name__ == "__main__":
    import sys

    verbose = False
    branch = "__local__"
    if "--verbose" in sys.argv:
        verbose = True
        sys.argv = [s for s in sys.argv if s != "--verbose"]
    if len(sys.argv) < 2:
        raise KeyError("You must specify which service to test")
    if "--branch" in sys.argv:
        branch = "__service__"
        sys.argv = [s for s in sys.argv if s != "--branch"]
    if "--this-branch" in sys.argv:
        branch = "__local__"
        sys.argv = [s for s in sys.argv if s != "--this-branch"]
    service = sys.argv[1]
    test = TestBlueprint()
    test.service = service
    test.debug = verbose
    test.branch = branch
    test.checklist = []
    if len(sys.argv) > 2:
        test.checklist = sys.argv[2:]
    suite = unittest.TestSuite()
    suite.addTest(test)
    base.run(suite)
