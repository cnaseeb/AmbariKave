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
from resource_management import *
from resource_management.core.system import System
import os
import kavecommon as kc

config = Script.get_config()
hostname = config["hostname"]

db_path = kc.default('configurations/mongodb/db_path', '/var/lib/mongo', kc.is_valid_directory)
logpath = kc.default('configurations/mongodb/logpath', '/var/log/mongodb/mongod.log', kc.is_valid_directory)
bind_ip = kc.default('configurations/mongodb/bind_ip', '0.0.0.0', kc.is_valid_ipv4_address)
tcp_port = kc.default('configurations/mongodb/tcp_port', '27017', kc.is_valid_port)
setname = default('configurations/mongodb/setname', 'None')

mongodb_baseurl = default('configurations/mongodb/mongodb_baseurl',
                          'http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/')


# The web status page is always accessible at a port number that is 1000 greater than the port determined by tcp_port.

mongo_hosts = default('/clusterHostInfo/mongodb_master_hosts', ['unknown'])
mongo_host = mongo_hosts[0]

mongo_arbiter_hosts = default('/clusterHostInfo/mongodb_arbiter_hosts', [])
is_arbiter = (mongo_arbiter_hosts is not None) and (hostname in mongo_arbiter_hosts)

# This is carried over from previous single mongod config, probably needs reworking
if mongo_host == "unknown":
    if bind_ip not in ['0.0.0.0', '127.0.0.1']:
        mongo_host = bind_ip
if mongo_host == hostname:
    mongo_host = 'localhost'

if setname in ["None", "False"]:
    if len(mongo_hosts) < 2:
        setname = ""

set_with_arbiters = (len(mongo_arbiter_hosts) > 0 and setname not in [None, False, "None", "False", ""])

mongodb_conf = default('configurations/mongodb/mongodb_conf', """
# mongod.conf

#where to log
logpath={{logpath}}

logappend=true

# fork and run in background
fork=true

#which port to listen for client connections?
port={{tcp_port}}
#
# The web status page is always accessible at a port number that is 1000 greater than the port determined by port.
#

#where to store the database?
dbpath={{db_path}}

# location of pidfile
pidfilepath=/var/run/mongodb/mongod.pid

# Listen to local interface only. Comment out to listen on all interfaces.
# bind_ip=127.0.0.1
bind_ip={{bind_ip}}

# Disables write-ahead journaling
# nojournal=true
{% if is_arbiter %}
nojournal=true
{% endif %}

# Enables periodic logging of CPU utilization and I/O wait
#cpu=true

# Turn on/off security.  Off is currently the default
#noauth=true
#auth=true

# Verbose logging output.
#verbose=true

# Inspect all client data for validity on receipt (useful for
# developing drivers)
#objcheck=true

# Enable db quota management
#quota=true

# Set oplogging level where n is
#   0=off (default)
#   1=W
#   2=R
#   3=both
#   7=W+some reads
#diaglog=0

# Ignore query hints
#nohints=true

# Enable the HTTP interface (Defaults to port 28017).
httpinterface=true

# Turns off server-side scripting.  This will result in greatly limited
# functionality
#noscripting=true

# Turns off table scans.  Any query that would do a table scan fails.
#notablescan=true

# Disable data file preallocation.
#noprealloc=true
{% if is_arbiter %}
noprealloc=true
{% endif %}

# Specify .ns file size for new databases.
# nssize=<size>

# Replication Options

# in replicated mongo databases, specify the replica set name here
replSet={{setname}}
# maximum size in megabytes for replication operation log
#oplogSize=1024
# path to a key file storing authentication info for connections
# between replica set members
#keyFile=/path/to/keyfile """)

replica_config_params = {"_id": setname, "members": []}
init_id = 0
for _host in mongo_hosts:
    replica_config_params["members"].append({"_id": init_id,
                                             "host": _host + ":" + str(tcp_port)})
    init_id = init_id + 1

if set_with_arbiters:
    for _host in mongo_arbiter_hosts:
        replica_config_params["members"].append({"_id": init_id,
                                                 "host": _host + ":" + str(tcp_port),
                                                 "arbiterOnly": True})
        init_id = init_id + 1

import json
replica_config_params = json.dumps(replica_config_params)
replica_config_params.replace("True", 'true')
