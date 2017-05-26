#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd

import geoutilities.ut_fitting as utf
from geoutilities.ut_basic import printer

class Grapher:
    # Provide functions for conveniently graphing data

    plot_colors = list('rgbcm')
    line_styles = '-', '--', ':',
    point_markers = 'o', '^', 'D',

    def __init__(self):
        self.setup_format_lists()


    # Point and line formats
    def setup_format_lists(self):
        # Create list of format pairs for lines and points
        self.line_formats = [(l, c) for l in Grapher.line_styles for c in Grapher.plot_colors]
        self.point_formats = [(m, c) for m in Grapher.point_markers for c in Grapher.plot_colors]
        
        # Create iterators to make accessing a format set easier
        self.reset_format_iters()

    def reset_format_iters(self):
        self.reset_line_format_iter()
        self.reset_point_format_iter()

    def reset_line_format_iter(self):
        self.line_format_iter = iter(self.line_formats)
        return self.line_format_iter

    def reset_point_format_iter(self):
        self.point_format_iter = iter(self.point_formats)
        return self.point_format_iter

    def get_next_line_formats(self, n=1):
        # Get the next n line formats. Returns a generator
        iter = self.line_format_iter
        iter_reset = self.reset_line_format_iter
        return (self._get_next(iter, iter_reset) for _ in range(n))

    def get_next_point_formats(self, n=1):
        # Get the next n point formats. Returns a generator
        iter = self.point_format_iter
        iter_reset = self.reset_point_format_iter
        return (self._get_next(iter, iter_reset) for _ in range(n))

    def get_line_formats(self, n=1, return_str=True):
        list = ['{}{}'.format(c,l) for l, c in self.get_next_line_formats(n)]
        if return_str and n == 1:
            return list[0]
        else:
            return list

    def get_point_formats(self, n=1, return_str=True):
        list = ['{}{}'.format(c,m) for m, c in self.get_next_point_formats(n)]
        if return_str and n == 1:
            return list[0]
        else:
            return list

    def _get_next(self, iter, reset_fu, resetable=True):
        # Meant to be an internal function
        #
        # Get the next item in a list which circles back to the front.
        # iter is the iterator
        # reset_fu is the function which resets the iterator to the beginning
        # resetable dictates whether the iterator will reset after reaching the 
        # end.
        try:
            return next(iter)
        except StopIteration:
            # Prevents and infinite loop of errors
            if resetable:
                # Reset the iter and retry getting next
                new_iter = reset_fu()
                return self._get_next(new_iter, reset_fu, resetable=False)
            else:
                # Resetting the iter failed. Rethrow the error. 
                raise StopIteration
            
        


    # Plotting functions
    # Future: Make generic plotting function which takes a specific plotting 
    # function as an argument? Generic does the plotting and specific does all 
    # the formatting. Basically one specific function for each problem?
    def show_plots(self):
        plt.show()

    def plot_fit(self, x_series, y_series, axis=None, log=False, lineformat=None, markerformat=None):
        fit_fu = utf.Fitter.get_power_fit_series if log else utf.Fitter.get_linear_fit_series
        fit_series = fit_fu(axis, x_series, y_series)

        if axis is None:
            axis = plt.gca()

        if lineformat is None and markerformat is None:
            linefomat = self.get_line_formats()
            markerformat  = self.get_point_formats()
        elif lineformat is None:
            lineformat = '  '
        elif markerformat is None:
            markerformat = '  '

        lc = lineformat[0] 
        ls = lineformat[1:]
        mc = markerformat[0]
        ms = markerformat[1:]
        # mc will be ignored for now... assumed to be same as lc

        #xticks = axis.get_xticks()
        #yticks = axis.get_yticks()
        plot_fu = axis.loglog if log else axis.plot
        plot_fu(*fit_series, linestyle=ls, marker=ms, color=lc)
        #axis.set_xticks(xticks)
        #axis.set_yticks(yticks)

    def pd_plot_cumsum(self, pd_data, title='', axis=None, logx=True, xticks=None, extras=False, show=False):
        # Assumes cumsum is in the columns (col -> y values), row indices 
        # (first column) are the x values
        #
        # Meant for cumsum grain size distribution plotting

        if not axis:
            extras = True
            self.reset_line_format_iter()

            fig = plt.figure()
            axis = plt.gca()

        # Generate a list of style strings
        n_cols = pd_data.columns.size
        styles = self.get_line_formats(n_cols)

        # plot the pd dataframe
        pd_data.plot(ax=axis, logx=logx, style=styles, legend=True)

        if xticks is not None:
            axis.set_xticks(xticks)
            p = lambda x: 2 if x < 1 else 1 if x < 10 else 0
            xtick_labels = [
                    "{:.{precision}f}".format(value, precision=p(value))
                    for value in xticks.values]
            #xtick_labels = [("{:.2f}" if value < 5 else "{:.1f}").format(value) for value in xticks.values]
            axis.set_xticklabels(xtick_labels)
            axis.set_xlabel("Geometric Mean of grain size classes ($mm$)")

            xmin = min(pd_data.index.min(), xticks.iloc[0])
            xmax = max(pd_data.index.max(), xticks.iloc[-1])
            axis.set_xlim((xmin, xmax))

        if extras:
            # Plot will be a standalone graph.
            # Draw extra things to make it look nice
            axis.set_ylim((0,1))
            axis.set_ylabel(r"$\%$ finer")
            axis.set_title(title)

            # Draw D50 and D84 lines
            axis.axhline(0.5, color='b', linestyle=':')
            axis.annotate(r"$D_{50}$", xycoords='axes fraction', xy=(0.05, 0.5), xytext=(0.05, 0.51))
            axis.axhline(0.84, color='b', linestyle=':')
            axis.annotate(r"$D_{84}$", xycoords='axes fraction', xy=(0.05, 0.84), xytext=(0.05, 0.85))

        if show:
            plt.show()

    def pd_plot_hydraulic_geometry(self, pd_data, name, axes=None, extras=False, show=False, show_legend=False):
        # Assumes columns are Discharge (Q) in first column and one or more of 
        # Velocity (V), Depth (D), or Width (W) in remaining columns
        #
        # Axes are a list of axes to plot each column. None will create a new 
        # axis for each column
        #
        # Rows are data points

        printer(n=2)
        printer("Plotting {}".format(name))

        if axes is None:
            # Making a new plot
            print("Making new axes")
            extras = True
            show = True
            self.reset_point_format_iter()
            fig, axes = plt.subplots(pd_data.columns.size, 1)

        variables = pd_data.columns
        discharge = pd_data.index.values
        for axis, key in zip(axes, variables):
            printer(" Plotting {} geometry".format(key))
            line_style = self.get_line_formats()
            point_style = self.get_point_formats()

            series = pd_data[key]

            #Grapher.set_log_boundaries(axis, discharge, series.values)
                
            # Plot best fit power law
            # comes before series plot function if xlim and ylim set externally
            self.plot_fit(discharge, series.values, axis, True, line_style)

            # Plot series
            series.plot(ax=axis, style=point_style, loglog=True, legend=show_legend)

        if extras:
            # Plot will be a standalone graph.
            # Draw extra things to make it look nice
            axes[0].set_title("{}".format(name))

        if show:
            plt.show()

    def pd_plot(self, pd_data, title='', axis=None, logx=False, show=False):
        # Assumes columns are y values, row indices (first column) are the x 
        # values
        #
        # Generic plotting of a pd dataframe (such as a multiple time series) 
        # using my custom formatting

        fig = None
        if not axis:
            self.reset_line_format_iter()

            fig = plt.figure()
            axis = plt.gca()

        # Generate a list of style strings
        n_cols = pd_data.columns.size
        styles = self.get_line_formats(n_cols)

        # plot the pd dataframe
        pd_data.plot(ax=axis, logx=logx, style=styles, legend=True)

        if show:
            plt.show()

        if fig is not None:
            return fig, axis


    # Helper class functions
    def calc_log_boundaries(value, lower=True):
        decade = 10**np.floor(np.log10(value))
        truncate = np.floor if lower else np.ceil

        multiplier = truncate(value / decade)
        boundary = multiplier * decade
        #print(value, decade, value/decade, truncate, multiplier, boundary)

        return boundary

    def set_log_boundaries(axis, x_series, y_series):
        # Hard to do the y values with a shared y boundary.
        # More recent plots with smaller range overwrite older plots.
        # Will ignore the y for now
        xmin = np.min(x_series)
        xmax = np.max(x_series)
        ymin = np.min(y_series)
        ymax = np.max(y_series)

        #print("init xlim", xmin, xmax)
        #print("init ylim", ymin, ymax)
            
        new_xmin = Grapher.calc_log_boundaries(xmin, lower=True)
        new_xmax = Grapher.calc_log_boundaries(xmax, lower=False)
        new_ymin = Grapher.calc_log_boundaries(ymin, lower=True)
        new_ymax = Grapher.calc_log_boundaries(ymax, lower=False)

        #print(new_xmin, new_xmax, new_ymin, new_ymax)

        axis.set_xlim(new_xmin, new_xmax)
        axis.set_ylim(new_ymin, new_ymax)

        #print("new xlim", axis.get_xlim())
        #print("new ylim", axis.get_ylim())


