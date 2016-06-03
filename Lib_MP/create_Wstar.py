import numpy as np

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
