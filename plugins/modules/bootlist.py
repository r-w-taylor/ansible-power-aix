#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020- IBM, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
author:
- AIX Development Team (@pbfinley1911)
module: bootlist
short_description: Alters the list of boot devices available to the system
description:
- Alters the list of possible boot devices from which the system may be booted.
  When the system is booted, it will scan the devices in the list and attempt to
  boot from the first device it finds containing a boot image.
version_added: '2.9'
requirements:
- AIX >= 7.1 TL3
- Python >= 2.7
options:
  force:
    description:
    - Indicates that the boot list must be modified even if the
      validation of the I(speed) and I(duplex) attributes, if specified,
      is not possible.
    type: bool
    default: no
  normal:
    description:
    - Normal boot list. The normal list designates possible boot devices
      for when the system is booted in normal mode.
    - Mutually exclusive with I(both).
    type: list
    elements: dict
    suboptions: &attrs
      device:
        description:
        - Specifies the name of the specific or generic device to include
          in the boot list.
        - "The following generic device keywords are supported:"
        - C(fd) specifies any standard I/O-attached diskette drive.
        - C(scdisk) specifies any SCSI-attached disk.
        - C(badisk) specifes any direct bus-attached disk.
        - C(cd) specifies any SCSI-attached CD-ROM.
        - C(rmt) specifies any SCSI-attached tape device.
        - C(ent) specifies any Ethernet adapter.
        - C(tok) specifies any Token-Ring adapter.
        - C(fddi) specifies any Fiber Distributed Data Interface adapter.
        type: str
        required: yes
      blv:
        description:
        - Specifies the boot logical volume on the target disk that is
          to be included in the boot list.
        type: str
      pathid:
        description:
        - Specifies the path ID of the target disk.
        - You can specify one or more path IDs by entering a comma-separated
          list of the required paths to be added to the boot list.
        type: str
      bserver:
        description:
        - Specifies the IP address of the BOOTP server.
        type: str
      gateway:
        description:
        - Specifies the IP address of the gateway.
        type: str
      client:
        description:
        - Specifies the IP address of the client.
        type: str
      speed:
        description:
        - Specifies the network adapter speed.
        type: str
      duplex:
        description:
        - Specifies the mode of the network adapter.
        type: str
      vlan_tag:
        description:
        - Specifies the virtual local area network (VLAN) identification value.
        type: int
      vlan_pri:
        description:
        - Specifies the VLAN priority value.
        type: int
      filename:
        description:
        - Specifies the name of the file that is loaded by Trivial File Transfer
          Protocol (TFTP) from the BOOTP server.
        type: str
  service:
    description:
    - Service boot list. The service list designates possible boot
      devices for when the system is booted in service mode.
    - Mutually exclusive with I(both).
    type: list
    elements: dict
    suboptions: *attrs
  both:
    description:
    - Both the normal boot list and the service boot list will be set to the
      same list of devices.
    - Mutually exclusive with I(normal) and I(service).
    type: list
    elements: dict
    suboptions: *attrs
'''

EXAMPLES = r'''
- name: Set normal and service boot lists
  bootlist:
    normal:
      - device: hdisk0
        blv: hd5
      - device: hdisk1
        blv: hd5
        pathid: "1"
      - device: ent0
        client: 129.35.9.23
        gateway: 129.35.21.1
        bserver: 129.12.2.10
    service:
      - device: cd0

- name: Set both normal and service boot lists to the same device
  bootlist:
    both:
      - device: hdisk0
'''

RETURN = r'''
msg:
    description: The execution message.
    returned: always
    type: str
stdout:
    description: The standard output
    returned: always
    type: str
stderr:
    description: The standard error
    returned: always
    type: str
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    # Attributes common to normal, service and both
    attrs = dict(
        device=dict(type='str', required=True),
        blv=dict(type='str'),
        pathid=dict(type='str'),
        bserver=dict(type='str'),
        gateway=dict(type='str'),
        client=dict(type='str'),
        speed=dict(type='str'),
        duplex=dict(type='str'),
        vlan_tag=dict(type='int'),
        vlan_pri=dict(type='int'),
        filename=dict(type='str')
    )
    module = AnsibleModule(
        argument_spec=dict(
            normal=dict(type='list', elements='dict', options=attrs),
            service=dict(type='list', elements='dict', options=attrs),
            both=dict(type='list', elements='dict', options=attrs),
            force=dict(type='bool', default=False)
        ),
        mutually_exclusive=[
            ['normal', 'both'],
            ['service', 'both']
        ]
    )

    results = dict(
        changed=False,
        msg='',
        stdout='',
        stderr='',
    )

    bootlist_path = module.get_bin_path('bootlist', required=True)

    # Set bootlists
    for mode in ['normal', 'service', 'both']:
        if mode not in module.params:
            continue
        if not module.params[mode]:
            continue
        cmd = [bootlist_path, '-m', mode]
        if module.params['force']:
            cmd += ['-F']
        for entry in module.params[mode]:
            cmd += [entry['device']]
            for attr, val in entry.items():
                if attr == 'device' or not val:
                    continue
                cmd += [attr + '=' + str(val)]

        module.run_command(cmd, check_rc=True)
        results['changed'] = True

    module.exit_json(**results)


if __name__ == '__main__':
    main()
