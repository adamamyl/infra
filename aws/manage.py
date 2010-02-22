#!/usr/bin/env python
'''Automate standard tasks with AWS (EC2) using boto.

You should specify credentials (access key, secret key) either via ~/.boto or
via environment variables. See http://code.google.com/p/boto/wiki/BotoConfig.

Research
========

Doing stuff with EBS
  * http://www.elastician.com/2009/12/creating-ebs-backed-ami-from-s3-backed.html
  * http://aws-musings.com/how-to-expand-your-ebs-volume/

Post install scripts
  * http://alestic.com/2009/08/runurl
  * http://alestic.com/2009/06/ec2-user-data-scripts

May be useful
  * http://www.elastician.com/2009/12/creating-ebs-backed-ami-from-s3-backed.html

Questions:
=========

1. Why use EBS now EC2 instances can be permanent and size limitations are
much removed (now 160GB on instance)?
  * EBS I/O performance is problematic
    (http://victortrac.com/EC2_Ephemeral_Disks_vs_EBS_Volumes)
  * EBS is additional expense
  * EBS does have nicer snapshotting than instance but is possible
'''
import os
import uuid
import time

import boto
import boto.ec2


def get_regions():
    regions = dict([ (x.name,x) for x in
        boto.ec2.regions() ])
    return regions

class Manager(object):
    # Alestic Debian Lenny images (see http://alestic.com/)
    # unfortunately images have different names on different instances ..
    amis = {
        'eu-west-1':  {
            'debian-lenny': 'ami-b8446fcc',
            'debian-squeeze': 'ami-8c446ff8',
            },
        'us-east-1':  {
            'debian-lenny': 'ami-dcf615b5',
            'debian-squeeze': 'ami-dcf615b5',
            },
        'us-west-1': {
            'debian-lenny': 'ami-b33a6bf6'
            }
        }
    # yes, i know they are inconsistent!
    key_pairs = {
        'eu-west-1': 'okfn-eu1-kp',
        'us-east-1': 'okfn-kp',
        'us-west-1': 'okfn-kp-us-west-1'
        }
    default_ami_type = 'debian-lenny'
    region_names = [ 'us-east-1', 'us-west-1', 'eu-west-1' ]

    def __init__(self, region=None):
        '''
        @param region: AWS region identifier (us-east-1, us-west-1, eu-west-1)
        '''
        # simple default self.connection
        # self.conn = boto.self.connect_ec2(AKEY, SKEY)
        self.conn = None
        self.regions = get_regions()
        self.region = region

    def _connect(self):
        region = self.regions[self._region]
        self.conn = region.connect()

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value
        if self._region is not None:
            self._connect()
    
    def placement(self):
        '''The placement of an existing instance in this region (or None if no
        instance).
        '''
        reservation = self.conn.get_all_instances()
        existing = reservation[0].instances[0] if reservation else None
        placement = getattr(existing, 'placement', None)
        return placement

    def create_instance(self, ami=None, **kwargs):
        '''Create a standard EC2 instance using our default security groups.

        @return: boto instance object representing created instance.
        '''
        # create a dedicated secgroup for this machine
        secname = 'instance-%s' % uuid.uuid4()
        oursecgroup = self.conn.create_security_group(secname, secname)
        secgroups = [ 'default', 'www-only', 'ssh-only', secname ]

        ourami = ami if ami else self.amis[self.region][self.default_ami_type]
        ourkwargs = {
            'placement': self.placement(),
            'instance_type': 'm1.small',
            'key_name': self.key_pairs[self.region],
            'security_groups': secgroups
        }
        ourkwargs.update(kwargs)

        reservation = self.conn.run_instances(ourami, **ourkwargs)
        instance = reservation.instances[0]
        while instance.state == 'pending':
            time.sleep(10)
            print('Waiting for instance to go active')
            instance.update()
        # TODO: now do post-boot stuff
        # 1. attach ip
        ipaddr = self.conn.allocate_address()
        self.conn.associate_address(instance.id, ipaddr.public_ip)
        # 2. Set up storage, either of:
        #   a) attach EBS instances
        #   b) relocate var on /mnt (which is the large volume) (see
        #   aws_fabfile.py)
        # 3. install standard software
        return instance
    
    def associate_address(self, instance_id, ipaddr):
        '''Associate address.'''
        self.conn.associate_address(instance_id, ipaddr)

    def create_security_groups(self):
        '''Create standard security groups (web, ssh).
        '''
        web = self.conn.create_security_group('www-only', 'www-only')
        web.authorize('tcp', 80, 80, '0.0.0.0/0')
        web.authorize('tcp', 443, 443, '0.0.0.0/0')
        ssh = self.conn.create_security_group('ssh-only', 'ssh-only')
        ssh.authorize('tcp', 22, 22, '0.0.0.0/0')

    def instance_security_groups(self):
        '''Get security groups to apply to a given instance'''
        existing = self.conn.get_all_security_groups()
        # if not 'SecurityGroup:www-only' not in existing:
            # self.create_security_groups()
        # assume we apply all groups
        # since sec groups cannot be changed once instance created may be worth
        # creating a dedicated group just for this instance
        return existing

    # see here for details on attaching and checking volume is available
    # http://groups.google.com/group/boto-users/browse_thread/thread/c4051181a1b8904d
    def create_ebs(self, instance):
        '''Create a 60GB EBS and attach to instance at /dev/sdh
        '''
        v = self.conn.create_volume(60, instance.placement)
        v.attach(instance.id, '/dev/sdh')

    def info(self):
        '''Get dictionary of info about this region's instances, security
        groups etc.
        '''
        res = {
            'region': self.conn.region,
            'security-groups': self.conn.get_all_security_groups(),
            'addresses': self.conn.get_all_addresses(),
            }
        res['instances'] = self.conn.get_all_instances()
        return res

    def print_info(self):
        '''Print results of info() to stdout'''
        print('Available Regions', get_regions())
        res = self.info()
        print('Current Region', res['region'])
        print('Addresses', res['addresses'])
        for instset in res['instances']:
            for inst in instset.instances:
                # TODO: describe an instance better
                print inst, inst.state, inst.dns_name, inst.placement
        return ''

    def image_info(self, image_id):
        '''Print information about image specified by image_id'''
        m = Manager()
        image = m.conn.get_image(image_id)
        print image


import os
import sys
import optparse
import inspect
def _object_methods(obj):
    methods = inspect.getmembers(obj, inspect.ismethod)
    methods = filter(lambda (name,y): not name.startswith('_'), methods)
    methods = dict(methods)
    return methods

if __name__ == '__main__':
    # image_info(Manager.ami_debian_euwest)
    _methods = _object_methods(Manager)
    usage = '''%prog {action} [args]

    '''
    usage += '\n    '.join(
        [ '%s: %s' % (name, m.__doc__.split('\n')[0] if m.__doc__ else '') for (name,m)
        in _methods.items() ])
    parser = optparse.OptionParser(usage)
    parser.add_option('-r', '--region', dest='region',
            help='Region to connect to (default: %s)' % ','.join(Manager.region_names),
            default=Manager.region_names[0])
    options, args = parser.parse_args()

    if not args or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)
    manager = Manager(options.region)
    method = args[0]
    out = getattr(manager, method)(*args[1:])
    print out
