import read_from_file as rn
import pdb
class stv:
    def __init__(self, filename):

        stvf = rn.read_from_file(filename)
        
        stvf.skipline()
        self.nr_layer = stvf.next(1).pop(0)
        stvf.skip_reminder_of_line()
        stvf.skipline()
        self.Z = stvf.next(self.nr_layer)
        stvf.skipline()
        self.P = stvf.next(self.nr_layer)
        stvf.skipline()
        self.T = stvf.next(self.nr_layer)
        
        nr_gas = stvf.next(1).pop(0)
        self.ap_col = []
        self.ap_vmr = []
        self.rt_col = []
        self.rt_vmr = []
        self.gas = []
        for gas in range(0,nr_gas):
            stvf.skipline()
            self.gas.append(stvf.next(1).pop(0))
            self.ap_col.extend(stvf.next(1))
            self.ap_vmr.append(stvf.next(self.nr_layer))
            stvf.skipline()
            stvf.skipline()
            self.rt_col.extend(stvf.next(1))
            self.rt_vmr.append(stvf.next(self.nr_layer))

        nr_aux = stvf.next(1).pop(0)
        self.aux = []
        self.ap_aux = []
        self.rt_aux = []
        for aux in range(0,nr_aux):
            self.aux.append(stvf.next(1).pop(0))
        for aux in range(0,nr_aux):
            self.ap_aux.append(stvf.next(1).pop(0))
        for aux in range(0,nr_aux):
            self.rt_aux.append(stvf.next(1).pop(0))
        del stvf

