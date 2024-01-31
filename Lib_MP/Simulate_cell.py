import sys, os
sys.path.append("/home/mathias/sfit-processing-environment")
from sfit4_setup import sfit4_ctl
from read_result_sfit4 import pbp

import matplotlib.pyplot as plt

def sfit4_ctl_setup(ctlfile='sfit4.ctl', pressure=False, vmr=False, temperature=False, length=False):

    ctl = sfit4_ctl()
    ctl.read_ctl_file(ctlfile)
    
    vmr = vmr or ctl.get_value('cell.1.vmr')
    temperature = temperature or ctl.get_value('cell.1.temperature')
    pressure = pressure or ctl.get_value('cell.1.pressure')
    length = length or ctl.get_value('cell.1.length')

    ctl.replace('cell.1.vmr', vmr)
    ctl.replace('cell.1.pressure', pressure)
    ctl.replace('cell.1.temperature', temperature)
    ctl.replace('cell.1.length', len)

    ctl.write(ctlfile)

if __name__ == '__main__':
    
    ctl = sfit4_ctl()
    ctl.read_ctl_file('sfit4.ctl')
    vmr = ctl.get_value('cell.1.vmr')
    temperature = ctl.get_value('cell.1.temperature')
    length = ctl.get_value('cell.1.path')
    pressure = ctl.get_value('cell.1.pressure')
    num = 0
    print(vmr)
    while num != -1:
        print('1: VMR {}'.format(vmr))
        print('2: PRESSURE {}'.format(pressure))
        print('3: TEMPERATURE {}'.format(temperature))
        print('4: length {}\n'.format(length))
        print('Number + new value')
        new = input().split()
        try:
            num = int(new[0])
        except:
            exit()
        if num == -1:
            break
        
        match num:
            case 1:
                vmr = new[1]
            case 2:
                pressure = new[1]
            case 3:
                temperature = new[1]
            case 4:
                length = new[1]
    
        fig, ax = plt.subplots(2,4,sharex = 'col', num = 1, clear = True)
        sfit4_ctl_setup('sfit4.ctl', pressure, vmr, temperature, length)
        os.system('/home/mathias/bin/sfit4_v1.0.21')
        s = pbp('pbpfile')
        for nr in range(1,5):
            nrr = nr - 1
            ax[0,nrr].plot(s.nu[nrr], s.clc[nrr]);
            ax[0,nrr].plot(s.nu[nrr], s.obs[nrr]);
            ax[1,nrr].plot(s.nu[nrr], s.dif[nrr]);
        fig.show()
        
