# Python / Numpy implementation of the trend analysis presented in
# Gardiner et al., 2008 

# The following model is used to fit the annual trend (drift) +
# intra-annual variability (i.e., fourier series tuncated at n degrees): 

# Model parameters are estimated using the weighted linear least squares
# method. Bootstrap resampling can be used to evaluate the confidence
# intervals on the parameter estimates (more robust in case of
# non-normally distributed random effects in the data).


# Author: B. Bovy | GIRPAS, ULg
# downloaded from http://nbviewer.ipython.org/github/girpas-ulg/nb_tseries/blob/master/Drift_Fourier_Analysis_Bootstrap.ipynb
import pprint

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def fourier_basis(x, degree, half_period):
    """Returns a 2-d array of fourier basis."""
    A = np.ones((x.size, 2 * degree + 1))
    
    for d in range(1, degree + 1):
        A[:, 2*d-1] = np.cos(d * np.pi * x / half_period)
        A[:, 2*d] = np.sin(d * np.pi * x / half_period)
        
    return A
    

def fit_driftfourier(x, data, weights, degree, half_period=0.5):
    """
    Fit y = f(x - x.min()) to data where f is given by
    fourier series + drift.
    
    Parameters
    ----------
    x : 1-d array
        x-coordinates
    data : 1-d array
        data values
    weights : 1-d array
        weights (>=0)
    degree : int
        degree of fourier series
    half_period : float
        half period
    
    Returns
    -------
    intercept : float
        intercept at x.min()
    slope : float
        slope (drift) for the normalized data
        (x - x.min())
    pfourier : 1-d array
        Fourier series parameters for the
        normalized data
    f_drift : callable
        Can be used to calculate the drift
        given any (non-normalized) x
    f_fourier : callable
        Can be used to calculate fourier series
    f_driftfourier : callable
        Can be used to calculate drift + fourier
    residual_std : float
        estimated standard deviation of residuals
    A : 2-d array
        matrix of "coefficients"
    
    """
    xmin = x.min()
    xnorm = x - xmin
    
    # coefficient matrix
    A = np.ones((x.size, 2 * degree + 2))
    A[:, 1] = xnorm
    A[:, 2:] = fourier_basis(xnorm, degree, half_period)[:, 1:]
    
    # linear weighted least squares
    results = np.linalg.lstsq(A * weights[:, np.newaxis],
                              data * weights)

    print A.shape, results[2]
    params = results[0]
    intercept = params[0]
    slope = params[1]
    pfourier = params[2:]
    
    f_drift = lambda t: slope * (t - xmin) + intercept
    f_fourier = lambda t: np.sum(fourier_basis(t - xmin, degree,
                                               half_period)[:, 1:]
                                 * pfourier[np.newaxis, :],
                                 axis=1) + intercept
    f_driftfourier = lambda t: f_drift(t) + f_fourier(t) - intercept

    residual_std = np.sqrt(results[1][0] / (x.size - 2 * degree + 2)) 
    
    return (intercept, slope, pfourier,
            f_drift, f_fourier, f_driftfourier,
            residual_std, A)


def cf_driftfourier(x, data, weights, degree,
                    half_period=0.5, nboot=5000,
                    percentiles=(2.5, 50., 97.5)):
    """
    Calculate confidence intervals for the fitted
    parameters from fourier series + drift modelling,
    using bootstrap resampling.
    
    Parameters
    ----------
    nboot : int
        number of bootstrap replicates
    percentiles : sequence of floats
        percentiles of parameter estimate
        distributions to return 
    
    Returns
    -------
    perc : dict
        percentiles for of each parameter
        distribution
    intercept : 1-d array
        intercept estimates from bootstraped
        datasets.
    slope : 1-d array
        slope estimates
    pfourier : 2-d array
        fourier parameters estimates
    
    See Also
    --------
    :func:`fit_driftfourier`
    """
    
    # 1st fit without bootstraping
    results = fit_driftfourier(x, data, weights,
                               degree, half_period)
    f_driftfourier = results[5]
    A = results[7]
    model = f_driftfourier(x)
    residuals = data - model
    
    # generate bootstrap resamples of residuals
    # and new datasets from these resamples
    boot_dataset = np.empty((x.size, nboot))
    for i in range(nboot):
        resample_i = np.floor(np.random.rand(x.size) * x.size).astype(int)
        resample_residuals = residuals[resample_i]
        boot_dataset[:, i] = model + resample_residuals
    
    # fit all bootstrap datasets
    results_boot = np.linalg.lstsq(A * weights[:, np.newaxis],
                                   boot_dataset * weights[:, np.newaxis])
    
    params_boot = results_boot[0]
    
    # compute percentiles
    perc_boot = np.column_stack(np.percentile(params_boot,
                                              percentiles, axis=1))
    
    perc = {'intercept' : perc_boot[0],
            'slope' : perc_boot[1],
            'pfourier' : perc_boot[2:]}
    
    intercept = params_boot[0]
    slope = params_boot[1]
    pfourier = params_boot[2:]
    
    return perc, intercept, slope, pfourier
