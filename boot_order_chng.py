#!/usr/bin/env python

"""

Run script cmd :-  python3.6 bootOrder.py -s 192.168.10.121 -u administrator@vsphere.local -p Root@123

"""

import atexit

from pyVim import connect
from pyVmomi import vim
from pyVim.task import WaitForTask

from tools import cli, tasks

try:
    input = raw_input
except NameError:
    pass

def get_args():
    parser = cli.build_arg_parser()
    args = parser.parse_args()

    return cli.prompt_for_password(args)

def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def new_cdrom_spec(controller_key, backing):
    connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    connectable.allowGuestControl = True
    connectable.startConnected = True
    
    cdrom = vim.vm.device.VirtualCdrom()
    cdrom.controllerKey = controller_key
    cdrom.key = -1
    cdrom.connectable = connectable
    cdrom.backing = backing
    return cdrom

def find_device(vm, device_type):
    result = []
    for dev in vm.config.hardware.device:
        if isinstance(dev, device_type):
            result.append(dev)
    return result

def set_boot(si, vm_name, boot=True):
    dc = si.content.rootFolder.childEntity[0]
    vm = si.content.searchIndex.FindChild(dc.vmFolder, vm_name)
    spec = vim.vm.device.VirtualDeviceSpec()

    vm_spec = vim.vm.ConfigSpec()

    vm_spec.bootOptions = vim.vm.BootOptions(bootOrder=[vim.vm.BootOptions.BootableCdromDevice()])
    '''
    if boot:  
        print("Setting boot from CD-ROM....")
        order = [vim.vm.BootOptions.BootableCdromDevice()]
        order.extend(list(vm.config.bootOptions.bootOrder))
        vm_spec.bootOptions = vim.vm.BootOptions(bootOrder=order)
    '''

    WaitForTask(vm.Reconfigure(vm_spec))
    print("VM will boot from cd-drive")
    #power_on(vm)

def power_on(vm):
    print("Power On VM ...")
    WaitForTask(vm.PowerOn())
    print("--------------------")

def connect_host(args):
    si = connect.SmartConnectNoSSL(host=args.host,
                                   user=args.user,
                                   pwd=args.password,
                                   port=int(args.port))
    if not si:
        print("Could not connect using specified username and password")
        return -1
    print("Connected to vCenter")
    atexit.register(connect.Disconnect, si)
    return si

def main():
    args = get_args()
    service_instance = connect_host(args) 
    content = service_instance.RetrieveContent()

    vm_name = 'testvm_rhel'
    vm = get_obj(content, [vim.VirtualMachine], vm_name)
    if not vm:
        print("VM obj not found")
    else:
        print("VM obj found")

    set_boot(service_instance, vm_name)
    '''
    vmfolder = get_obj(content, [vim.Folder], args.folder)
    resource_pool = get_obj(content, [vim.ResourcePool], args.Rpool)
    datastore = get_obj(content, [vim.Datastore], args.datastore) 

    vm_name = args.vmname + "-" + os
    vm = get_obj(content, [vim.VirtualMachine], vm_name)
    attach_iso(service_instance, datastore, args, vm_name)
    '''
if __name__ == "__main__":
    main()
