import numpy as np

def create_h(p):
    # Creates the pressure weighting function to calculate xGAS from a
    # VMR profile for GAS given the pressure levels p
    #
    # NOTE: not normalized to ground pressure !!!    #
    # Taken from Article Connor, B. J., et.al.
    # Orbiting Carbon Observatory: Inverse
    # method and prospective error analysis
    # Journal of Geophysical Research: Atmospheres, 2008, 113
    
    lh = len(p)
    h = np.zeros(lh)

    nr = 0
    h[nr] = -p[nr] + (p[nr+1] - p[nr]) / np.log(p[nr+1]/p[nr])
    nr = lh-1
    h[nr] = p[nr] - (p[nr] - p[nr-1]) / np.log(p[nr]/p[nr-1])

    for nr in np.arange(1,lh-1):
        h[nr] = (p[nr+1] - p[nr]) / np.log(p[nr+1]/p[nr]) - (p[nr] - p[nr-1]) / np.log(p[nr]/p[nr-1])
    h = np.abs(h)
        
    return(h)
    

def create_Wstar_mean(x, y_b):
    #
    # W_star = create_Wstar_mean(x, y)
    # 
    # Creates a matrix W_star such that W_star means all the points from x to
    # give an y. y is an nx2 matrix where the 1st column contains the lower
    # boundaries of the new bin and the 2nd column contains the upper
    # boundaries (excluded)

    y = np.mean(y_b,axis=1);
  
    ind = np.where(y > x[-1])[0]
    y[ind] = x[-1]
    W_star = np.zeros((y.size,x.size))
    for i in range(0,y.size):
        ind1 = np.where((x >= y_b[i,0]))[0];
        ind2 = np.where((x <= y_b[i,1]))[0];
        if ind1.size == 0:
            return(W_star)
        if ind2.size == 0:
            ind2 = ind1;
        ind1 = np.min(ind1)
        ind2 = np.max(ind2)
        if ind1 == ind2 or ind1 == ind2 + 1: 
            W_star[i,ind1] = 1;
        else:
            W_star [i, ind1:ind2+1] = 1.0 / (ind2-ind1+1);

    return(W_star)
        
def create_Wstar(x, y):
    # Construct a matrix W_star so that 
    # y = W_star*x
    # by linear interpolation
    # x and y have to monotonically increasing

    
    ind = np.where(y > x[-1])[0]
    y[ind] = x[-1];
    W_star = np.zeros((y.size,x.size));
    for i in range(0,y.size):
        ind1 = np.min(np.where((y[i] <= x))[0]);
        ind2 = np.min(np.where((y[i] >= x))[0]);
        if ind2.size == 0:
            ind2 = ind1

        if ind1 == ind2: 
            W_star[i,ind1] = 1
        else:
            W_star [i, ind1] = (x[ind2] - y[i])/(x[ind2] - x[ind1]); 
            W_star [i, ind2] = -(x[ind1] - y[i])/(x[ind2] - x[ind1]); 

    return(W_star)
