#!/usr/bin/env python
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import sys
import subprocess
import logging
import multiprocessing
import os

log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

def parse_opts(argv):
    parser = argparse.ArgumentParser("Tool to let you know what packages need"
                                     "updating in a list of containers")
    parser.add_argument('-c', '--containers',
                        help="""File containing a list of containers to inspect.""",
                        default='container_list')
    parser.add_argument('-r', '--rpm-list',
                        help="""File containing a list of the latest available rpms.""",
                        default="rpm_list")
    parser.add_argument('-y', '--yum-config',
                        help="""Alternate yum configuration file.""",
                        default=False)
    parser.add_argument('-u', '--update',
                        action='store_true',
                        help="""Run yum update in any containers that need updating.""",
                        default=False)
    opts = parser.parse_args(argv[1:])

    return opts

def rm_container(name):
    log.info('Removing container: %s' % name)
    subproc = subprocess.Popen(['/usr/bin/docker', 'rm', name],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    cmd_stdout, cmd_stderr = subproc.communicate()
    if cmd_stdout:
        log.debug(cmd_stdout)
    if cmd_stderr and \
           cmd_stderr != 'Error response from daemon: ' \
           'No such container: {}\n'.format(name):
        log.debug(cmd_stderr)

def run_container_cmd(container, name, command):

    rm_container('package-check-%s' % name)

    dcmd = ['/usr/bin/docker', 'run',
            '--user', 'root',
            '--name', 'package-check-%s' % name,
            container]

    dcmd.extend(command)

    log.debug('Running docker command: %s' % ' '.join(dcmd))

    subproc = subprocess.Popen(dcmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    cmd_stdout, cmd_stderr = subproc.communicate()
    if cmd_stderr:
        log.debug(cmd_stderr)
    if subproc.returncode != 0:
        log.error('Failed running docker-puppet.py for %s' % config_volume)
    rm_container('package-check-%s' % name)

    return cmd_stdout

def get_available_rpms():
    available_rpms = {}
    available_rpms_list = [line.rstrip('\n') for line in open(opts.rpm_list)]
    for rpm in available_rpms_list:
        available_rpms[rpm] = 1

    return available_rpms

opts = parse_opts(sys.argv)

# Load up available rpms as a hash containing the latest versions of rpms.
available_rpms = get_available_rpms()

# Get a list of all the docker containers we need to inspect.
docker_containers = [line.rstrip('\n') for line in open(opts.containers)]

process_count = int(os.environ.get('PROCESS_COUNT',
                                   multiprocessing.cpu_count()))

container_rpms = {}
name = 0
for container in docker_containers:
    rpm_qa = run_container_cmd(container, str(name), ['rpm', '-qa'])
    rpms = rpm_qa.split("\n")
    container_rpms[container] = rpms
    name += 1

for container in container_rpms:
    for rpm in container_rpms[container]:
        if len(rpm) > 0 and not rpm in available_rpms:
            log.info("Should update rpm: %s container: %s\n" % (rpm, container))
#print container_rpms

