#!/usr/bin/env python

import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd

#import .ut_fitter as utf
#import .ut_grapher as utg
import geoutilities.ut_basic as utb

# This file is intended to deal with distribution processing. But it is kinda 
# messy right now... Lots of half baked code because of project deadlines.  
# Could use an overhaul. Perhaps a Distribution class and a Math class that 
# operates on the distributions? That is kinda how the code is turning out as 
# is.

class PDDistributions:

    gravity = 9.81 # m/s^2
    density_water = 1000 # kg/m^3
    density_sediment = 2650 # kg/m^3
    slope = 0.02

    # Methods
    # Perform calculations on internal distribution dataframe
    def __init__(self, pd_data, max_size, auto=True, cumsummed=False):
        # Assumes pd_data is formatted with grain size classes for rows and 
        # different distributions for columns. Smallest grain size class first
        #
        # Cumsummed indicates whether the provided data is a cumsum 
        # distribution or a regular distribution.
        #
        # Will ignore non-numeric indices
        # 
        # Example:
        # Grain  Set1   Set2 ...
        #  Size
        #  ...
        #  0.3   0.18   0.46
        #  0.5   0.37   0.85
        #  0.7   0.52   1.09
        #  1     0.78   1.38
        #  1.4   1.17   1.63
        #  2     1.46   1.65
        #  2.8   1.62   1.61
        #  4     2.18   1.64
        #  5.6   3.11   2.11
        #  ...

        # Remove non-numeric indices
        indices = pd_data.index.values
        numeric = [obj for obj in indices if utb.isnumeric(obj)]
        self.data = pd_data.loc[pd.Index(numeric)]
        self.max_size = max_size

        # Set the maximum value by hand
        if cumsummed:
            # Don't know if the cumsum is normalized or not
            previous = self.data.iloc[-1].max()
            self.data.loc[max_size] =  previous if previous > 1 else 1
        else:
            # Not a cumsum distribution
            self.data.loc[max_size] =  0

        if auto:
            if cumsummed:
                self.cumsum = self.data / self.data.max()
            else:
                self.calc_normalized_cumsum()
            self.calc_class_geometric_means()

            self.calc_line_functions()


    def get_size_classes(self):
        return self.data.index.values

    def calc_normalized_cumsum(self, data=None):
        if data is None:
            self.data_cumsum =  self.data.cumsum() / self.data.sum()
        else:
            return data.cumsum() / data.sum()

    def calc_class_geometric_means(self):

        classes = self.data.index.get_values()
        #n_classes = classes.size
        #offset = (np.arange(n_classes)+1)%n_classes

        Db = classes[:-1] # class min size
        Db1 = classes[1:] # class max size
        #Db = classes.get_values() # class min size
        #Db1 = Db[offset].copy() #D_b,i+1; class max size
        #Db1[-1] = self.max_size # must manually set largest value

        Di = (Db * Db1)**(1/2) # geometric mean

        self.class_geometric_means =  pd.Series(Di, index=classes[:-1])

    def calc_distribution_geometric_means(self):
        # Calculate the geometric mean of each size class assuming the grain 
        # size classes provided represent the minimum size in that class 
        # (passing size)
        #
        # max_size represents the maximum size of the largest grain size class
        #
        # Requires the output of calc_normalized_cumsum()
        #
        # D_g = 2**av(psi)
        # av(psi) = sum[i=1->n](psi_i * f_i)
        # psi_i = (psi_b,i + psi_b,i+1)/2
        # psi_b,i = log2(D_i) = log(D_i)/log(2)
        # D_i == grain size for class i
        # f_i = f_f,i+1 - f_f,i == fraction of grains in this range

        # number of columns
        distributions = cumsum_data.columns
        n_distributions = distributions.size

        # number of rows
        size_classes = cumsum_data.index
        n_size_classes = size_classes.size

        # offest will be used for advanced indexing to identify class upper 
        # values of each size class
        offset = (np.arange(n_size_classes)+1)%n_size_classes
        
        # get the geometric means
        psi_i = np.log2(class_geometric_means)

        # Fraction of next bigger size class
        cs = cumsum_data.values # Get numpy array of data
        cs1 = cs[offset,:] # cs_i+1. Last row is garbage; will be max_size
        cs1[-1,:] = np.ones(n_distributions) # manually set the last row to 100%

        # Need to subtract rows as is (ignore the index labels)
        f_i = pd.DataFrame(cs1 - cs, columns=distributions, index=size_classes)

        psi = f_i.multiply(psi_i, axis=0)
        av_psi = psi.sum(axis=0)

        Dg = 2**av_psi
        self.geometric_mean = Dg

    def calc_shear_stress(self, depth, slope):
        # shear = density gravity depth slope
        rho = DistributionMather.density_water
        g = DistributionMather.gravity

        self.shear_stresses = rho * g * depth * slope

    def calc_fractional_transport():
        # frac trans rate = q_b p_i / f_i
        qb_key = condition_keys['qb']
        qb = flow_conditions.loc[qb_key]

        fi = surface_data
        
        # For some reason, the trasport data has an extra size class (0.10mm).
        # Combine 0.10mm with 0.21mm and delete 0.10mm
        pi = transport_data.drop(0.10)
        pi.loc[0.21] = transport_data.loc[0.10] + transport_data.loc[0.21]

        fractional_rates = qb * (pi / fi)

        return fractional_rates

    def calc_overall_sampler(self):
        # Calculate the overall distribution from the selected columns
        # 
        # Sum the values in each grain size class then calc new cumsum 
        # distributions
        #
        # Raw values are summed b/c normalized distributions would need 
        # weights, which are based on the raw values anyway.
        
        sizes = self.data.index
        times = self.data_cumsum.columns.levels[0]
        self.time_sums = pd.DataFrame(index=sizes, columns=times).fillna(0)

        # Sum the masses from different samplers at each timestep
        # Gets rid of the MultiIndex too.
        for time in self.data_cumsum.columns.levels[0]:
            # Pick the data subset
            slicer_key = (slice(None)),(time, slice(1,5))
            data = self.data.loc[slicer_key]
            
            # sum up the masses in each size class
            self.time_sums[time] = data.sum(axis=1)

        # calculate the new normalized cumsum
        self.time_cumsums = self.calc_normalized_cumsum(data=self.time_sums)

    def calc_line_functions(self):
        # Generate a dataframe of line functions by linear interpolating 
        # between cumsum rows. df[row,col] is the line from df[row,col] to 
        # df[row+1,col]
        #
        # f_i(x) = m_i * x + y_i - m_i * x_i
        #
        # Recommended to change df such that anything outside of the defined 
        # distribution is a flat line. (add padding lines before/after df)
        
        df = self.cumsum
        length = df.index.size
        index = df.index.values.reshape(length,1)
        columns = df.columns
        n = index.size

        y = df.values # Get the numpy array out of df
        y0 = y[:n-1,:]
        y1 = y[1:, :]

        x0 = index[:n-1]
        x1 = index[1:]

        m = (y1-y0) / (x1 - x0)
        b = y0 - m * x0
        
        #print(m, b)

        self.line_matrix = pd.Panel([m,b], items=['m','b'],
                major_axis=index[:-1,:].ravel(), minor_axis=columns.ravel())
        #self.line_matrix = np.array([m,b])
        #self.line_slope = pd.DataFrame(m, index=index[:-1,:].ravel(), columns=columns.ravel())
        #self.line_intercept = pd.DataFrame(b, index=index[:-1,:].ravel(), columns=columns.ravel())
        
    def calc_percentile_size(self, percent):
        # Calculate the Di grain size where i is the percent less than, such as 
        # D50 or D84
        
        print("Calculating D{}...".format(percent))
        fraction = percent / 100

        cumsum = self.cumsum
        np_cumsum = cumsum.values
        lines = self.line_matrix
        #line_slope = self.line_slope
        #line_intercept = self.line_intercept

        smaller = np_cumsum <= fraction
        larger = np_cumsum > fraction
        #print(cumsum)
        #print(smaller)
        #print(larger)

        sizes, runs = np.where(np.logical_and(smaller[:-1,:], larger[1:,:]))

        #print(line_slope)
        #print(line_intercept)
        #print(sizes, runs)
        #print(lines)
        #print()
        #m = lines['m']
        #print(m)
        #coefficients = np.extract(indices, lines)
        coefficients = lines.values[:,sizes,runs]
        #print(coefficients)

        m = coefficients[0,:]
        b = coefficients[1,:]
        values = (fraction - b) / m

        return values
        #print(cumsum.index.values[indices[0]])


    # Class methods
    # Perform calculations (usually binary operations) on external distribution 
    # dataframes.
    def compare_distributions(pd_distributions_A, pd_distributions_B, min_size=None, max_size=None):
        # Compare the distributions in A to Distributions in B. If 
        # distributions do not have matching grain sizes classes, they will be 
        # linearly interpolated
        #
        # Distributions should be the measured mass values, NOT cumsum or 
        # otherwise normalized data. Grain size should be the index and 
        # runs/times/etc should be the columns
        #
        # Output will have indices (size classes) from A and columns from A

        A_raw = pd_distributions_A
        B_raw = pd_distributions_B

        index_out = A_raw.index
        columns_out = A_raw.columns

        # Fix raw_distributions classes
        # Make function for converting from A to B size classes

        # Pad the B distribution so that line segments on the ends will have 
        # zero slope
        B_index = B_raw.index.values
        if max_size is not None and max_size not in B_index:
            B_index = np.append(B_index, max_size)
        if min_size is not None and min_size not in B_index:
            B_index = np.insert(B_index, 0, min_size)
        B_raw = B_raw.reindex(B_index, fill_value=0)

        # Calculate non-normalized cumsum of A and B
        rA_cumsum = A_raw.cumsum()
        rB_cumsum = B_raw.cumsum()
        #max_rB = rB_cumsum.

        # Generate functions for line segments of B
        rB_lines = DistributionMather.generate_line_functions(rB_cumsum)

        # Convert B to match A size classes
        A_index = A_raw.index.values
        rB_a = DistributionMather.convert(A_index, rB_lines)

        #fig = plt.figure()
        #axis = plt.gca()
        #B_cumsum.plot(ax=axis)
        #B_a.plot(ax=axis)
        #plt.show()
        
        # normalize the distributions
        #A_cumsum = rA_cumsum / rA_cumsum.max(axis=0)
        #Ba_cumsum = rB_a / rB_cumsum.max(axis=0)

        # Compare input distributions to self distributions.
        #  Use Kolmogorov-Smirnov test
        distribution_fit = DistributionMather.ks_test(rA_cumsum, rB_a)

        return distribution_fit
        
    
    def generate_line_functions(df):
        # Generate a dataframe of line functions by linear interpolating 
        # between dataframe rows. df[row,col] is the line from df[row,col] to 
        # df[row+1,col]
        #
        # f_i(x) = m_i * x + y_i - m_i * x_i
        #
        # Recommended to change df such that anything outside of the defined 
        # distribution is a flat line. (add padding lines before/after df)
        
        index = df.index.values.reshape(15,1)
        columns = df.columns
        n = index.size

        y = df.values # Get the numpy array out of df
        y0 = y[:n-1,:]
        y1 = y[1:, :]

        x0 = index[:n-1]
        x1 = index[1:]

        m = (y1-y0) / (x1 - x0)
        b = y0 - m * x0

        # Generate an array of line functions
        line = lambda m_i, b_i: (lambda x: m_i * x + b_i) # define the line function
        vfunc = np.vectorize(lambda fline, m_i, b_i: fline(m_i, b_i)) # vectorizing the line function
        funcs = vfunc(line, m, b) # Creating the array of line functions

        # Make dataframe of line functions
        df_f = pd.DataFrame(funcs, index=index[:14].reshape(14,), columns=columns, dtype='object')

        return df_f
        

    def convert(A_index, Bf):
        # Convert distributions for B so that the indices match those in A
        # A is a cumsum dataframe
        # Bf is a dataframe of functions (because A and B likely won't have the 
        # same size classes). The functions could potentially be anything, but 
        # linear interpolation functions are assumed.
        #
        # A and Bf must have grain sizes as index.
        #
        # Output is a dataframe representing the converted B distribution
        Bf_indices = Bf.index.values
        Bf_times = Bf.columns.values

        # Find the index of each size class of B relative to A
        # This dictates which B function to use
        # The -1 is because searchsorted is for inserting, whereas I want to 
        # call the line function on the element to the left
        arg_index = np.searchsorted(Bf_indices, A_index, side='left') - 1

        # This is the size class for the above argument indices
        arg_class = Bf_indices[arg_index]

        # Could not figure out a better way of doing this....
        out = pd.DataFrame(index=A_index, columns=Bf_times)
        for time in Bf_times:
            Bf_time = Bf[time]
            funcs_df = Bf_time.loc[arg_class]

            funcs = funcs_df.values
            input = A_index

            for f, gs in zip(funcs, input):
                out.loc[gs, time] = f(gs)

        return out

    def ks_test(A_df, B_df):
        # A_df is the non-normalized cumsum dataframe
        # B_df is the non-normalized B cumsum data converted to use A index 
        # (grain size)
        #
        # A_df and B_df must have grain sizes as index.
        #
        # Output would ideally be a 3D array or dataframe: size x time x HS fit
        #
        #XXXXXXXXX K_s test is the sum of the distribution differences squared
        # K_s is more complicated than I can figure out at the moment. It is 
        # based on the largest difference value between the distributions. I 
        # will return that?
        
        A = A_df.values
        B = B_df.values
        index = A_df.index.values
        times = A_df.columns.values
        hs_times_str = B_df.columns.values

        # normalize distributions
        An = A / np.amax(A, axis=0)
        Bn = B / np.amax(B, axis=0)

        # Distance (absolute value) between distributions
        dist = np.absolute(An[:,:,np.newaxis] - Bn[:,np.newaxis,:])

        # Methods for 
        #sup = np.amax(dist, axis=0)
        sqrt_sum = np.sum(dist, axis=0)**.5

        # Pick a method to actually return
        method_data = sqrt_sum
        out_df = pd.DataFrame(data=method_data,
                index=times, columns=hs_times_str)

        return out_df


