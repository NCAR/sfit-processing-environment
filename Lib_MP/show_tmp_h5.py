import sys
from load_tmp_h5 import load_tmph5
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from Tkinter import *
from matplotlib.figure import Figure

class show_results:

    def __init__(self,h5file):

        self.h5file = h5file;
        self.h5 = load_tmph5(self.h5file)
        h5 = self.h5
        self.norm_flag = 0;
        self.auxplot = 1;
        # Find a free figure for profile
        self.winprf = plt.figure()
        # Find a free figure for microwindow
        self.winmw = plt.figure()
        # Find a free figure for AVK
        self.winavk = plt.figure()
    
        self.tkroot = Tk()
        self.tkroot.wm_title('sfit4 tmp.h5 viewer')

        self.entry = Entry(self.tkroot)

        self.spcfig = Figure(figsize=(5,3))
        self.spc_canvas = FigureCanvasTkAgg(self.spcfig, master=self.tkroot)
        self.spc_canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)
        self.update_plot('None')
        self.spc_canvas.show()

        self.auxfig = Figure(figsize=(5,3))
        self.aux_canvas = FigureCanvasTkAgg(self.auxfig, master=self.tkroot)
        self.aux_canvas.get_tk_widget().grid(row=1, column=0, columnspan=3)
        self.update_auxplot('c2y')
        self.aux_canvas.show()

        spctoolbar_frame = Frame(self.tkroot)
        spctoolbar_frame.grid(row=2,column=0, columnspan=3, sticky=W)
        spctoolbar = NavigationToolbar2TkAgg(self.spc_canvas, spctoolbar_frame)
        spctoolbar.pan()

        frame2 = Frame(self.tkroot)
        frame2.grid(row=0,column=5)


        button_norm = Button(frame2, text = 'Normalize', command = self.normalize)
        button_norm.grid(row=0, column=0,sticky=E+W)
        button_quit = Button(frame2, text = 'Quit', command = self.tkroot.quit)
        button_quit.grid(row=1, column=0,sticky=E+W)

        button_filter = Button(frame2, text = 'Filter', command = self.filter)
        button_filter.grid(row=3, column=0, sticky=E+W)

        err_value = ['None', 'SYS', 'RAN', 'TOT']
        self.err_var = StringVar(self.tkroot)
        self.err_var.set(err_value[0])
        num = 0
        m=OptionMenu(frame2, self.err_var, *err_value, 
                     command= self.update_plot)
        m.grid(row=4,column=num,stick=E+W)

        aux_value = ['c2y', 'RMS', 'AIRCOL']
        self.show_var = StringVar(self.tkroot)
        self.show_var.set(aux_value[0])
        num = 0
        m=OptionMenu(frame2, self.show_var, *aux_value, 
                     command= self.update_auxplot)
        m.grid(row=5,column=num,stick=E+W)

        filter_f = Frame(self.tkroot)
        filter_f.grid(row=1,column=5)

        self.c2y_e1 = Entry(filter_f,width=6)
        self.c2y_e1.grid(row=0, column=0)
        self.c2y_e1.delete(0, END)
        self.c2y_e1.insert(0, 0.0)
    
        c2y_l = Label(filter_f, text='< chi_y_2 >')
        c2y_l.grid(row=0, column=1)   

        self.c2y_e2 = Entry(filter_f,width=6)
        self.c2y_e2.grid(row=0, column=2, sticky=E+W)
        self.c2y_e2.delete(0, END)
        self.c2y_e2.insert(0, np.max(h5.c2y))

        self.rms_e1 = Entry(filter_f,width=6)
        self.rms_e1.grid(row=1, column=0)
        self.rms_e1.delete(0, END)
        self.rms_e1.insert(0, 0.0)
    
        rms_l = Label(filter_f, text='< RMS(%) >')
        rms_l.grid(row=1, column=1)   

        self.rms_e2 = Entry(filter_f,width=6)
        self.rms_e2.grid(row=1, column=2, sticky=E+W)
        self.rms_e2.delete(0, END)
        self.rms_e2.insert(0, 100.0/np.min(h5.snr_clc))

        


        self.tkroot.mainloop()

    def quit(self):
        self.tkroot.destroy()

    def filter(self):
        self.h5 = load_tmph5(self.h5file)
        h5 = self.h5
        f1 = self.c2y_e1.get()
        f2 = self.c2y_e2.get()
        f3 = self.rms_e1.get()
        f4 = self.rms_e2.get()
        ind = filter (lambda x: \
                      h5.c2y[x] > float(f1) \
                      and h5.c2y[x] < float(f2) \
                      and 100.0/h5.snr_clc[x] > float(f3)\
                      and 100.0/h5.snr_clc[x] < float(f4), range(0,len(h5.dnum)))
        self.h5.valid(ind)
        self.update_plot(self.err_var.get())
        self.update_auxplot(self.show_var.get())

    def normalize(self):
        if self.norm_flag == 1:
            self.norm_flag = 0
        else:
            self.norm_flag = 1

        self.update_plot(self.err_var.get())

    def update_plot(self, err):
        h5 = self.h5
        self.spc_canvas.figure.clear()
        ax = self.spc_canvas.figure.add_subplot(111)
        if self.norm_flag == 1:
            norm = h5.aircol
        else:
            norm = 1.0

        ax.plot_date(h5.dnum, h5.col_rt/norm)

        ax.set_title(h5.gasname)

        if err == 'RAN':
            ax.errorbar(h5.dnum, h5.col_rt/norm, 
                     h5.err_ran/norm, color='g', fmt=None)
        if err == 'SYS':
            ax.errorbar(h5.dnum, h5.col_rt/norm, 
                     h5.err_sys/norm, color='g', fmt=None)
        if err == 'TOT':
            ax.errorbar(h5.dnum, h5.col_rt/norm, 
                     h5.err_tot/norm, color='g', fmt=None)
        self.spc_canvas.draw()

    def update_auxplot(self, aux):
        h5 = self.h5
        self.aux_canvas.figure.clear()
        ax = self.aux_canvas.figure.add_subplot(111)
        if aux == 'c2y':
            ax.plot_date(h5.dnum, h5.c2y)
        elif aux == 'RMS':
            ax.plot_date(h5.dnum, 100.0/h5.snr_clc)
        elif aux == 'AIRCOL':
            ax.plot_date(h5.dnum, h5.aircol)
        self.aux_canvas.draw()

if __name__ == '__main__':
    if len(sys.argv)==1:
        print 'tmp.h5 file missing'
        exit()
        
    show_results(sys.argv[1])

