#!/usr/bin/env python
##############################################################################
#
# Copyright 2015 KPMG N.V. (unless otherwise stated)
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
"""
Simple python script for editing /etc/sysconfig/network and /etc.hosts
http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-hostname.html

usage: rename_me hostname [domainname]
"""
import sys
import os
import commands

newname = sys.argv[1]
domain = "localdomain"
if len(sys.argv) > 2:
    domain = sys.argv[2]

if os.path.exists("/etc/sysconfig/network"):
    # CENTOS
    f = open("/etc/sysconfig/network")
    l = f.readlines()
    f.close()
    found = False
    newlines = []
    for line in l:
        if line.startswith("#"):
            newlines.append(line.strip())
        elif "HOSTNAME=" in line:
            newlines.append("HOSTNAME=" + newname + "." + domain)
            found = True
        else:
            newlines.append(line.strip())
    if not found:
        newlines.append("HOSTNAME=" + newname + "." + domain)

    f = open("/etc/sysconfig/network", "w")
    f.write("\n".join(newlines) + "\n")
    f.close()
elif os.path.exists('/etc/hostname'):
    # UBUNTU
    os.system('echo ' + newname + ' > /etc/hostname ')

if domain == "localdomain":
    # support machine with no domain name / DNS ...
    stat, out = commands.getstatusoutput("hostname -d")
    dom = ""
    if not stat and len(out):
        dom = "." + out
        domain = out
    os.system("hostname " + newname + dom)
else:
    os.system("hostname " + newname + "." + domain)

if len(domain) and os.path.exists('/etc/hostname'):
    if os.path.exists('/etc/hosts'):
        # UBUNTU
        f = open("/etc/hosts")
        l = f.readlines()
        l = [i.rstrip() for i in l]
        f.close()
        if '127.0.0.1' in l[0]:
            l = ["127.0.0.1 " + newname + "." + domain + " localhost.localdomain localhost " + newname] + l[1:]
        f = open("/etc/hosts", 'w')
        f.write('\n'.join(l))
        f.close()

if os.path.exists("/etc/sysconfig/network"):
    # CENTOS
    os.system("/etc/init.d/network restart; service network restart;")
elif os.path.exists('/etc/hostname'):
    # UBUNTU
    os.system("service hostname restart")
