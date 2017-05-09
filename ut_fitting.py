#!/usr/bin/env python

import numpy as np
from scipy import optimize

class Fitter:

    def get_power_fit(x_series, y_series, guess=[1,1], return_power=True):
        # Perform a least squares linear fit in log space to get a power law 
        # relationship. Can return either a, b from y = ax^b or log_m, log_b from 
        # log(y) = log_m * log(x) + log_b, depending on "return_power".
        
        log_x = np.log10(x_series)
        log_y = np.log10(y_series)

        log_m, log_b = Fitter.get_linear_fit(log_x, log_y, guess)

        #     log_y  =      log_m * log_x  + log_b
        # 10**log(y) = 10**(log_m * log(x) + log_b)
        #         y  = 10**log_b * 10**(log(x**log_m)
        #         y  = 10**log_b * x**log_m
        #         y  =         a * x**b

        if return_power:
            # Returns the coefficient and exponent
            a = 10**log_b
            b = log_m
            return a, b
        else:
            # Returns the slope and y-intercept in log space
            return log_m, log_b

    def get_power_fit_series(axis, x_series, y_series, guess=[1,1], truncate_box=(None, None, None, None)):
        fit = Fitter.get_power_fit(x_series, y_series, guess, return_power=False)
        if VERBOSE:
            print("log_y = {:.3f} * log_x + {:.4f}".format(*fit))
            print("y = {:.10f} * x**{:.3f}".format(10**fit[1], fit[0]))

        # Get a series of points in log space and return the linear values.
        return Fitter.get_linear_series(axis, *fit, log_space=True, truncate_box=truncate_box)

    def get_linear_fit(x_series, y_series, guess=[1,1], pass_through=None):
        # Perform a least squares linear fit to the given data series constrained 
        # to passing through the given point, or unconstrained if no point is 
        # provided.
        #
        # Returns the slope and y-intercept of the best fit line.
        #
        # If you are defining a pass_through point, then guess must only have one 
        # value (for the slope).
        if pass_through:
            # Constrained to pass through a point. Find slope.
            ptx, pty = pass_through
            line_fu = lambda m, x: m * (x - ptx) + pty
            error_fu = lambda m, x, y: line_fu(m, x) - y
        else:
            # Unconstrained. Find slope and intercept
            line_fu = lambda p, x: p[0] * x + p[1]
            error_fu = lambda p, x, y: line_fu(p, x) - y

        optimal, success = optimize.leastsq(error_fu, guess, args=(x_series, y_series))

        # If the fit is constrained by a pass_through point, then 'optimal' will 
        # only contain the slope. Otherwise, the slope and intercept will be in 
        # 'optimal'
        best_m = optimal[0]
        best_b = pty - best_m * ptx if pass_through else optimal[1]

        return best_m, best_b

    def get_linear_fit_series(axis, x_series, y_series, guess, pass_through=(0,0)):
        fit = Fitter.get_linear_fit(x_series, y_series, guess, pass_through)
        if VERBOSE:
            print("y = {} * x + {}".format(*fit))
        return Fitter.get_linear_series(axis, *fit)

    def get_1_1_series(axis, pass_through=(0,0)):
        # Create a 1:1 series which fits on a plot
        pt_x, pt_y = pass_through
        return Fitter.get_linear_series(axis, slope=1, y_intercept=pt_y-pt_x)

    def get_linear_series(axis, slope=1, y_intercept=0, n=10, log_space=False, truncate_box=(None,None,None,None)):
        # Generate a series which fits into the given graph boundaries
        xmin, xmax = axis.get_xlim()
        ymin, ymax = axis.get_ylim()

        tx_min, tx_max, ty_min, ty_max = truncate_box
        xmin = tx_min if tx_min and xmin < tx_min else xmin
        xmax = tx_max if tx_max and xmax > tx_max else xmax
        ymin = ty_min if ty_min and ymin < ty_min else ymin
        ymax = ty_max if ty_max and ymax > ty_max else ymax

        if log_space:
            # Convert the boundaries to log space
            xmin, xmax, ymin, ymax = [np.log10(var) for var in (xmin, xmax, ymin, ymax)]

        y_fu = lambda x: slope * x + y_intercept
        x_fu = lambda y: (y - y_intercept) / slope

        # Get intercepts
        left_intercept = y_fu(xmin)
        right_intercept = y_fu(xmax)
        bottom_intercept = x_fu(ymin)
        top_intercept = x_fu(ymax)

        # Choose intercepts that aren't off the graph
        min_x_corr = xmin if bottom_intercept < xmin else bottom_intercept
        min_y_corr = ymin if left_intercept < ymin else left_intercept

        max_x_corr = xmax if top_intercept > xmax else top_intercept
        max_y_corr = ymax if right_intercept > ymax else right_intercept

        # Make the x and y series
        x_range = max_x_corr - min_x_corr
        x_series = np.arange(0, n+1)/n * x_range + min_x_corr

        y_range = max_y_corr - min_y_corr
        y_series = np.arange(0, n+1)/n * y_range + min_y_corr

        if log_space:
            return 10**x_series, 10**y_series
        else:
            return x_series, y_series




# For more functionality finish converting L3.py




        




















