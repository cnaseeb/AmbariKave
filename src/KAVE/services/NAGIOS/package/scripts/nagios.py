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
import os
import subprocess
from resource_management import *
from kavecommon import ApacheScript


class Nagios(ApacheScript):
    nagios_conf_file = "/etc/httpd/conf.d/nagios.conf"
    nagios_contacts_file = "/etc/nagios/objects/contacts.cfg"

    def install(self, env):
        import params
        super(Nagios, self).install(env)
        env.set_params(params)
        self.install_packages(env)
        Execute('yum -y install epel-release')
        Execute('yum clean all')
        Execute('yum -y install nagios')
        Execute('yum -y install nagios-plugins')
        self.configure(env)

    def configure(self, env):
        import params
        env.set_params(params)
        File(self.nagios_conf_file,
             content=InlineTemplate(params.nagios_conf_file),
             mode=0755
             )
        File(self.nagios_contacts_file,
             content=InlineTemplate(params.nagios_contacts_file),
             mode=0755
             )

        # SET NAGIOS ADMINPASSWORD
        Execute('mkdir -p ' + os.path.dirname(params.nagios_passwd_file))
        p = subprocess.Popen(['htpasswd','-i', params.nagios_passwd_file, 'nagiosadmin'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        stdout, stderr = p.communicate(str(params.nagios_admin_password))
        if p.returncode:
            raise Exception('Unable to create nagios admin password, did you enter wrong password second time?'
                            + str(stdout) + str(stderr))
        Execute('chown apache:apache ' + params.nagios_passwd_file)
        Execute('chmod 700 ' + params.nagios_passwd_file)
        super(Nagios, self).configure(env)

    def start(self, env):
        import params
        env.set_params(params)
        super(Nagios, self).start(env)
        Execute('service nagios start')

    def stop(self, env):
        Execute("service nagios stop")
        super(Nagios, self).stop(env)

    def status(self, env):
        Execute("service nagios status")
        super(Nagios, self).status(env)

if __name__ == "__main__":
    Nagios().execute()
