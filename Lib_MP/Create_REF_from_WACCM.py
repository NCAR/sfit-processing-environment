#!/usr/bin/python



if __name__ == '__main__':

    import sys,os
    curdir = os.path.dirname(sys.argv[0])
    sys.path.append(curdir)
    import sfit4_setup as sf4s

    if len(sys.argv) < 2:
        print 'One argument required: path to directory containg WACCM profiles'
    if len(sys.argv) < 3:
        ref_file = 'waccm.prf'
    else:
        ref_file = sys.argv[2]
        
    waccm_dir = sys.argv[1]
    sr = sf4s.reference_prf()
    sr.read_reference_prf(os.path.join(curdir,'default.ref'))
    sr.create_ref_from_WACCM(waccm_dir)
    sr.create_ref_from_WACCM(waccm_dir)
    sr.write_reference_prf(ref_file)

else:
    print 'This is a script to be run from commandline only'
