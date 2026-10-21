# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit #turns out i am allowed scipy
from scipy import fft #fourier 1D
#from scipy.signal import find_peaks #added as chisquared big! #good try but no
#main()
import os
import sys


def data_table(filename):
    """Extract collumn data from .dat file (everything after &END)
    Parameter:
        filename: str
            string/path of file to be called, 'assessment_data_kswk7629.dat'
            
    Returns: 
        pandas.DataFrame or None:
            DataFrame containing the data from the file with column names as defined
            in the header. Returns None if file cannot be read
    """
    try:
        with open(filename, 'r') as file: #opens file linked to 'filename' variable in read mode
            lines = file.readlines() #lines = ["First line\n", "Second line\n", "Third line\n", ...ect]
        
            if not filename.endswith(".dat"):
                raise ValueError(f"expected .dat when {filename}")
                

        table_start = None 
        for i, line in enumerate(lines): #assign multiple values from a tuple to variables in a single statement
            # Use strip() to remove whitespace and find &END
            if line.strip().startswith('&END'): #needed due to space :( essentially does a line contain &END
                table_start = i + 1
                print(f"Found &END at line {i}: {repr(line.strip())}")
                break
        
        if table_start is None: 
            # aka if line.strip().startswith('&END'): not triggered
            raise ValueError("No &END marker found in file")
    
        #(first non-empty line after &END)
        header_line = None
        header_index = None   

     
        for i in range(table_start,len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('&'): 
                header_line = line
                header_index = i
                # print(f"Found header at line {i}: {header_line}") #should be &END marker+1
                break
    
        if header_line is None:
            raise ValueError("No data header found after &END") #figure out another selection method
    
        #Read table using pandas as pd, starting from header
        data = pd.read_csv(filename,  #i checked _csv can be used for .dat so thats neat
                           sep='\t',  # seperates stuff into tabs (tabular data)
                           skiprows=header_index,
                           engine='python') #pandas as pd uses C engine (e.g:c++) by default
        
        print(f"data with shape: {data.shape}")
        return data

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found, check 'filename ='")
        return None
    except ValueError:
        print(f"file {filename} is empty")
    except Exception as e:
        print(f"Error parsing metadata: {e}")
        return {}

        
        
def channel_seperator(data):
    """seperates the data into CH1 (channel 1) & CH2 (channel 2)
    for both energy level collumns based on table data values 1 or 2
    
    Parameter(s):
        data: tabular data
            The original data table with Time and Channel columns formatted
            by def data_table(filename):
            
    Returns:
        dictionary:
            dict with seperated data for ch1 and ch2 for all energies
    """
    if data is None or data.empty: # another value error type from == instead of is
        print("data doesn't have a value") #maybe do indexing of lines or line selection if bugs found
        return None
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"Expected pandas.pd DataFrame, got {type(data)}")
        return None
    energy_list = []
    for col in data.columns:
        if 'Time (us) @ ' in col:
            energy = col.replace('Time (us) @ ', '')
            energy_list.append(energy)

    if not energy_list:
        print("No energy columns found")
        return None

    seperated_data = {}
    for energy in energy_list: #in hindsight should have returned energy_list but oh well
        seperated_data[energy] = {'CH1': None, 'CH2': None}
        time_collumn = f'Time (us) @ {energy}'
        channel_collumn = f'Channel @ {energy}' #attempt at new collumn for later
        
        if time_collumn not in data.columns or channel_collumn not in data.columns:
            print(f"Note: collumns for {energy} not present in data")
            continue
        
        time_data = data[time_collumn]
        channel_values = data[channel_collumn]
        #seperate by channel (data is 1 or 2, not both)
        
        ch1_mask = channel_values == 1
        seperated_data[energy]['CH1'] = {
            'times': time_data[ch1_mask].values,
            'channels': channel_values[ch1_mask].values
        }
        ch2_mask = channel_values == 2
        seperated_data[energy]['CH2'] = {
            'times': time_data[ch2_mask].values,
            'channels': channel_values[ch2_mask].values
        }
    
    return seperated_data
    
# def histogram(seperated_data, energy='5keV', bins = 200): #default is 200
#     """Creates a histogram using tabular data based on time
    
#     Parameters:
#         data: tabular data
#             The original data table with Time and Channel columns formatted
#             by def data_table(filename):
            
#         seperated_data:
#             Dictionary with a seperated listings of CH1 and CH2
#         bins: int
#             Number of histograms across time
#         energy: str
#             Energy level to be plotted such as energy='5keV'
#     Returns:
#         Histogram:
#             Compiles CH1 time data and CH2 time data into histograms over a time period
    
    
#     """

#     if seperated_data is None:
#         raise ValueError("separated_data is None")
#         return None, None
#     if energy not in seperated_data:
#         print("error of not found in data has been sprung")
#         return None, None
#     if not isinstance(seperated_data, dict):
#         raise TypeError(f"Expected dict, got {type(seperated_data)}")
#         return None, None
#     if not isinstance(bins, int) or bins <= 0:
#         raise ValueError(f"bins must be positive int, got {bins}")
#     # if seperated_data[energy]['CH1'] is None:
#     #     print(f"Warning: No CH1 data for {energy}")
#     #     return None, None
    
    
#     ch1_times = seperated_data[energy]['CH1']['times'] #need to add ch2 version
#     ch2_times = seperated_data[energy]['CH2']['times']
    
#     all_times= np.concatenate([ch1_times, ch2_times])#Join a sequence of arrays along an existing axis.
#     #creating histogram
#     #all_times = ch1_times #experimentation
#     counts, bin_edges = (np.histogram(all_times, bins = bins, range = None))
#     bin_centering = 0.5*(bin_edges[:-1] + bin_edges[1:])
#     bin_width = bin_edges[1]-bin_edges[0]
    
#     error = np.sqrt(counts) # standard error (see lab book as sample)
#     fig, ax = plt.subplots(figsize=(12,8))
#     counts_unittime = counts / bin_width
#     error_unittime = error / bin_width
    
#     ax.errorbar(bin_centering, counts_unittime, yerr=error_unittime, fmt='o', markersize=3,
#                     capsize=2, color ='red', label=f'{energy} data')
    
#     ax.set_xlabel('Time (', fontsize = 10)
#     ax.set_ylabel('Counts', fontsize = 10)
#     ax.set_title(f'Histogram of time data for {energy}', fontsize = 10)
#     ax.legend(fontsize = 8)
#     ax.grid(True, alpha=0.2)
    
#     # total_counts = np.sum(counts)
#     # mean_time = np.mean(all_times) #if i want it later
    
#     return fig, ax



def histogram_ch1(seperated_data, energy='5keV', bins = 200): #default is 200
    """Creates/Plots a histogram using tabular data (pd.dataframe) based on time
    
    Parameters:
        data: tabular data
            The original data table with Time and Channel columns formatted
            by def data_table(filename):
            
        seperated_data:
            Dictionary with a seperated listings of CH1 and CH2
        bins: int
            Number of histograms across time
        energy: str
            Energy level to be plotted such as energy='5keV'
    Returns:
        Histogram:
            Compiles CH1 time data into histograms over a time period
    
    
    """

    if seperated_data is None:
        raise ValueError("separated_data is None")
        return None, None
    if energy not in seperated_data:
        print("error of not found in data has been sprung")
        return None, None
    if not isinstance(seperated_data, dict):
        raise TypeError(f"Expected dict, got {type(seperated_data)}")
        return None, None
    if not isinstance(bins, int) or bins <= 0:
        raise ValueError(f"bins must be positive int, got {bins}")
    # if seperated_data[energy]['CH1'] is None:
    #     print(f"Warning: No CH1 data for {energy}")
    #     return None, None
    
    
    ch1_times = seperated_data[energy]['CH1']['times'] #need to add ch2 version
    #power of ctrl c + v for ch2 plot
    counts, bin_edges = (np.histogram(ch1_times, bins = bins, range = None))
    bin_centering = 0.5*(bin_edges[:-1] + bin_edges[1:])
    bin_width = bin_edges[1]-bin_edges[0]
    
    #error = np.sqrt(counts) # standard error (see lab book as sample)
    fig, ax = plt.subplots(figsize=(12,8))
    counts_unittime = counts / bin_width
    #error_unittime = error / bin_width
    
    #counts_unittime y axis again
    ax.hist(bin_centering, bins = bin_edges, weights=counts_unittime, #bin_centering placeholder
            label=f'{energy} data')
            #for outline 'step'
            
            
    ax.set_xlabel('Time (μs)', fontsize = 10)
    ax.set_ylabel('Counts', fontsize = 10)
    ax.set_title(f'Histogram of ch1 time data for {energy}', fontsize = 10)
    ax.legend(fontsize = 8)
    ax.grid(True, alpha=0.2)
    
    # total_counts = np.sum(counts)
    # mean_time = np.mean(all_times) #if i want it later
    
    return fig, ax

def histogram_ch2(seperated_data, energy='5keV', bins = 200): #default is 200
    """Creates/Plots a histogram using tabular data (pd.dataframe) based on time
    
    Parameters:
        data: tabular data
            The original data table with Time and Channel columns formatted
            by def data_table(filename):
            
        seperated_data:
            Dictionary with a seperated listings of CH1 and CH2
        bins: int
            Number of histograms across time
        energy: str
            Energy level to be plotted such as energy='5keV'
    Returns:
        Histogram:
            Compiles CH2 time data into histograms over a time period
    
    
    """

    if seperated_data is None:
        raise ValueError("separated_data is None")
        return None, None
    if energy not in seperated_data:
        print("error of not found in data has been sprung")
        return None, None
    if not isinstance(seperated_data, dict):
        raise TypeError(f"Expected dict, got {type(seperated_data)}")
        return None, None
    if not isinstance(bins, int) or bins <= 0:
        raise ValueError(f"bins must be positive int, got {bins}")
    # if seperated_data[energy]['CH1'] is None:
    #     print(f"Warning: No CH1 data for {energy}")
    #     return None, None
    
    
    ch2_times = seperated_data[energy]['CH2']['times'] #need to add ch2 version

    counts, bin_edges = (np.histogram(ch2_times, bins = bins, range = None))
    bin_centering = 0.5*(bin_edges[:-1] + bin_edges[1:])
    bin_width = bin_edges[1]-bin_edges[0]
    
    #error = np.sqrt(counts) # standard error (see lab book as sample)
    fig, ax = plt.subplots(figsize=(12,8))
    counts_unittime = counts / bin_width
    #error_unittime = error / bin_width
    
    #counts_unittime y axis again #yes weights = is needed
    ax.hist(bin_centering, bins = bin_edges, weights=counts_unittime, #bin_centering placeholder
            label=f'{energy} data')#histtype = 'step', color = 'red', label=f'{energy} data')
            #for outline 'step'
            
    
    ax.set_xlabel('Time (μs)', fontsize = 10)
    ax.set_ylabel('Counts', fontsize = 10)
    ax.set_title(f'Histogram ch2 of time data for {energy}', fontsize = 10)
    ax.legend(fontsize = 8)
    ax.grid(True, alpha=0.2)
    
    # total_counts = np.sum(counts)
    # mean_time = np.mean(all_times) #if i want it later
    
    return fig, ax

#use scipy for curve fitting, also have difference from that curve be used for a new sin wave
#so maybe 1 def with plot then another or 2 defs for comparisson to each thing


def channel_retriever(filename = None):
    """Function to retreive data
    Parameter:
        filename:
            filename string 'assessment_data_kswk7629.dat'
    Returns:
        sin looking wave, combined with exp decay
    """
    if filename is None:
        filename = 'assessment_data_kswk7629.dat'
    data = data_table(filename)
    
    if data is None:
        raise FileNotFoundError("Data not found, file may be missing")
        return
    if data is not None:
        print("Data loaded successfully... probably")
        #print(data.head()) #prints first few lines of data
        
        channels = channel_seperator(data)
        if channels is None:
            print("error in channel seperation")
            return
        #not robust
        energy_list = list(channels.keys())
    #     for energy in energy_list: #probably a mistake to not call on energy but oh well
    #         if energy not in channels:
    #             print("where energy")
    #             return
            
    #         if channels[energy]['CH1'] is not None:
                
    #             ch1_times = channels[energy]['CH1']['times']
    #             if len(ch1_times) > 0:
    #                 print(ch1_times[:5])
    #                 print(f"total ch1 times: {len(ch1_times)}")
    #             else:
    #                 print("ch1 data not found")
    #         else:
    #             print("ch1 unavalible")
                    
    #         if channels[energy]['CH2'] is not None:
                        
    #             ch2_times = channels[energy]['CH2']['times']
    #             if len(ch2_times) > 0:
    #                 print(ch2_times[:5])
    #                 print(f"total ch2 times: {len(ch2_times)}") #defo seems to work
    #             else:
    #                 print("ch2 data not found")
    #         else:
    #             print("ch2 unavalible")

    # else:
    #     print("where data")
        
    for energy in energy_list:
        if energy not in channels:
            print(f"{energy} not found in channels")
            continue
        if channels[energy]['CH1'] is not None:
            ch1_times = channels[energy]['CH1']['times']
            if len(ch1_times) > 0:
                # print(f"{energy} CH1 first 5 times: {ch1_times[:5]}")
                # print(f"total ch1 times: {len(ch1_times)}")
                continue
            else:
                print(f"{energy} ch1 data empty")
        else:
            print(f"{energy} ch1 unavailable")
            
            # Check CH2 data
        if channels[energy]['CH2'] is not None:
            ch2_times = channels[energy]['CH2']['times']
            if len(ch2_times) > 0:
                # print(f"total ch2 times: {len(ch2_times)}")
                continue
            else:
                print(f"{energy} ch2 data empty")
        else:
            print(f"{energy} ch2 unavailable")
        #fig, ax = histogram_ch1(seperated_data = channel_seperator(data), energy=energy, bins = 100)
        fig, ax = histogram_ch1(seperated_data = channel_seperator(data), energy=energy, bins = 200)
        fig, ax = histogram_ch2(seperated_data = channel_seperator(data), energy=energy, bins = 200)
        #might explode if given 1 channel
        
        if fig is not None and ax is not None: #for curve of best fit
            # print(f'Histogram created for {energy}') #1st try lets go
            continue
        else:
            print(f"Failed to create histogram for {energy}")




def asymmetry_model(t, B, beta, tau_damp=None):
    """Asymmetry model from equation
    
    Parameters:
        t: array
            time array (μs)
        B: array
            magnetic field (T)
        beta: flt
            detector angle (rad)
        tau_damp: flt
            damping time (μs), if None use undamped version
        
    Returns:
        A(t) = (1/3) * (sin(beta)/beta) * cos(γBt) * exp(-t/tau_damp) [if damped]
    """
    gamma = 851.616  # Mrad·s⁻¹·T⁻¹
    gamma_rad_per_us = gamma  # Already in rad/μs since 1 Mrad/s = 1 rad/μs
    
    prefactor = (1/3) * (np.sin(beta) / beta)
    
    omega = gamma_rad_per_us * B  # rad/μs
    oscillation = np.cos(omega * t)
    
    if tau_damp is not None and tau_damp > 0: #followed video advice on define then try 
        damping = np.exp(-t / tau_damp) #make something after to fit
        #maybe use a tau error?
    else: 
        damping = 1.0
    
    return prefactor * oscillation * damping


def fit_damped_sinusoidal(times, diff, errors=None, include_harmonic=False):
    #~57° roughly difference from phase in sin, aim for something similar for cos
    """Fit damped 'oscillation' model with frequency estimation from FFT and Front Weighting.
    Probably should have been abstracted (more).
    Parameters:
        times: numpy array
            time array (μs)
        diff: numpy array
            difference
        errors: numpy array
            errors for the diff data, used for weighted fitting
        include_harmonic: bool
            not in use, 4 harmonic detection, example of scope creep
    Returns:
        best_parameters, best_covariance, standard_errors, best_fit, guess_times, best_chi: tuple
            best_parameters : list of 3 floats
                B(T), beta(rad), tau_damp(rad)
            best_covariance : numpy array (3x3)
            standard_errors : numpy array
            best_fit : numpy array
            guess_times : numpy array
            best_chi : float
    Notes:
        Fitting Strategy:
            1st. Primary fit: Full damped model
            2nd. First fallback: Fixed τ_damp at initial guess
            3rd. Second fallback: Undamped model
    """
    #can't be bothered renaming, code partly relic from trying to not use scipy to sin curvefit
    # Gets rid of NaN and infinite
    mask = np.isfinite(times) & np.isfinite(diff)
    if errors is not None:
        mask &= np.isfinite(errors)
    
    if np.std(diff) < 1e-10:
        print("Warning: Data appears constant")
    
    guess_times = times[mask]
    guess_diff = diff[mask]
    guess_errors = errors[mask] if errors is not None else None
    
    if len(guess_times) < 10:
        print("Warning: Too few valid data points for fitting")
        return None, None, None, None, None
    
    # FFT to get initial frequency
    try:
        dt = guess_times[1] - guess_times[0]
        n = len(guess_diff)
        from scipy import signal
        diff_detrended = signal.detrend(guess_diff - np.mean(guess_diff))
        window = signal.windows.hann(n)
        diff_windowed = diff_detrended * window
        fft_vals = np.abs(fft.rfft(diff_windowed))
        fft_freq = fft.rfftfreq(n, dt)
        
        #Plots FFT for debugging
        # plt.figure(figsize=(10,4))
        # plt.plot(fft_freq, fft_vals, 'b-')
        # plt.xlabel('Frequency (1/μs)')
        # plt.ylabel('FFT Amplitude')
        # plt.title('FFT of Difference Data')
        # plt.grid(True, alpha=0.3)
        # plt.show()
        
        # #Find main peak 
        # min_period = 0.5
        # max_period = 5.0
        # min_freq = 1.0/max_period
        # max_freq = 1.0/min_period
        # freq_mask = (fft_freq >= min_freq) & (fft_freq <= max_freq)
        min_freq = 0.1
        max_freq = 4.0
        freq_mask = (fft_freq >= min_freq) & (fft_freq <= max_freq)

        if np.any(freq_mask):
            main_peak_idx = np.argmax(fft_vals[freq_mask])
            main_peak_freq = fft_freq[freq_mask][main_peak_idx]
            omega_guess = 2 * np.pi * main_peak_freq
            print(f"FFT main peak: {main_peak_freq:.3f} 1/μs")
        else:
            # Default guess if FFT fails (failsafes!)
            time_range = guess_times[-1] - guess_times[0]
            omega_guess = 2 * np.pi * 2 / time_range
            print("default freq")
        # if np.any(freq_mask):
        #     fft_in_range = fft_vals[freq_mask]
        #     freqencies_in_range = fft_freq[freq_mask]
        #     # for peaks with min prominence
        #     peaks, properties = find_peaks(fft_in_range, prominence=0.1 * np.max(fft_in_range))
        #     if len(peaks) > 0:
        #         prominences = properties['peak_heights'] - properties['left_bases']
        #         best_peak = peaks[np.argmax(prominences)]
        #         main_peak_freq = freqencies_in_range[best_peak] #this didn't work
        #         omega_guess = 2 * np.pi * main_peak_freq #worth a try to decrease chi squared
        #         print(f" FFT: {main_peak_freq:.3f} 1/μs")
            
        #     else:
        #         main_peak = np.argmax(fft_in_range)
        #         main_peak_freq = freqencies_in_range[main_peak]
        #         omega_guess = 2 * np.pi * main_peak_freq
        #         print(f" FFT: {main_peak_freq:.3f} 1/μs")
        
        
        
    except Exception as e:
        print(f"FFT failed: {e}")
        time_range = guess_times[-1] - guess_times[0]
        omega_guess = 2 * np.pi * 2 / time_range
        
    
    #omega to B field guess
    gamma = 851.616  # Mrad·s⁻¹·T⁻¹
    B_guess = omega_guess / gamma  # B in Tesla
    
    beta_guess = 1.0  # rad (~57 degrees, maybe i should try pi/2 given phase of B graph 1)
    tau_damp_guess = 5.0  # μs (middle of 2-10 μs range guven by tasksheet)
    
    initial_guess = [B_guess, beta_guess, tau_damp_guess]

    

    
    best_parameters = None
    best_covariance = None #brought me lots of problems
    best_fit = None
    best_chi = np.inf
    
    
    
    def create_front_weights(n, decay_rate=2.0):
        """Creates weights that are higher for early times (front (left) of data), 
        adapted from medium weights function (see old .py files)
        
        Parameters:
            n: int 
                number of points
            decay_rate: flt
                (higher = faster decay)
        
        Returns:
            weights: array 
            array of weights normalized to mean=1
        """
        weights = np.linspace(decay_rate, 1.0, n)
        weights = weights / np.mean(weights)
        return weights

    n = len(guess_times)
    #middle_weights = create_middle_linear_weights(n, peak_weight=1.8, end_weight=0.5)
    lower_bounds = [0, 0, 0]    # B min (T), beta min (rad), tau_damp min (μs) #tau not fit?
    upper_bounds = [0.03, np.pi/2, np.inf] # B max (T), beta max (rad), tau_damp max (μs)
    front_weights = create_front_weights(n = len(guess_times), decay_rate=3.0)

    try:
        if guess_errors is not None:
            scaled_errors = guess_errors / front_weights
            print(f"Attempt main fit with tau_damp_guess = {tau_damp_guess}")
            optimal_paramters, covariance = curve_fit(
                    asymmetry_model, guess_times, guess_diff,
                    p0=initial_guess, sigma=scaled_errors,
                    absolute_sigma=True, maxfev=20000, #note absolute_sigma=True since these are still errors
                    bounds=(lower_bounds, upper_bounds) 
                    )
            #print(f"YES tau_damp fitted = {optimal_paramters[2]:.3f}")
            #does in fact trigger, why tau no fit :(
            
        else:
            sigma = 1.0 / front_weights
            optimal_paramters, covariance = curve_fit(
                asymmetry_model, guess_times, guess_diff,
                p0=initial_guess, sigma=sigma, 
                absolute_sigma=False, #custom weights as guess_errors is None
                maxfev=5000,
                bounds=(lower_bounds, upper_bounds)
        )
            print("guess_errors is None")
        
        fit_curve = asymmetry_model(guess_times, *optimal_paramters)
        residuals = guess_diff - fit_curve
        chi2 = np.sum((residuals/guess_errors)**2) if guess_errors is not None else np.sum(residuals**2)
        redchi = chi2 / (len(guess_times) - len(optimal_paramters))
        print(f"Damped free fit reduced χ² = {redchi:.2f}, amplitude = {optimal_paramters[0]:.2f}, τ = {optimal_paramters[1]:.3f}")
        

    
        best_parameters, best_covariance, best_fit = optimal_paramters, covariance, fit_curve
        best_chi = redchi
    except Exception as e:
        #redundant model
        print(f"Damped free fit failed: {e}")
        def model_fixed_freq(t, B, beta):
            """following convention outlined in scipy vid, redundant function,
            This model is used as a fallback when the full damped fit fails thus,
            τ is fixed at tau_damp_guess (5.0 μs)
            Parameters:
                t : np.array() or float
                    Time values in microseconds (μs). assume np.array().
                B : float
                    Magnetic field strength in Tesla (T). Parameter to be optimized.
                beta : float
                    Detector angle in radians (rad). Parameter to be optimized, but doesn't.
                Returns:
                    Asymmetry A(t): np.array
                        A(t) = (1/3) * (sin(β)/β) * cos(γ·B·t) * exp(-t / τ_constant)
                        
                """
            return asymmetry_model(t, B, beta, tau_damp_guess)
        
        # lower_fixed = [20000, 1e-6, -np.pi, -np.inf]
        # upper_fixed = [np.inf, np.inf, np.pi, np.inf]
        #initial_guess = [B_guess, beta_guess, tau_damp_guess]
        initial_guess = [B_guess, beta_guess] #guess it's fixed tau
        
        lower_bounds = [0, 0.0]      # FFallback
        upper_bounds = [0.03, 1.5]
        try:
            if guess_errors is not None:
                optimal_paramters_fixed, covariance_fixed = curve_fit(model_fixed_freq, guess_times, guess_diff,
                                                   p0=initial_guess, sigma=guess_errors,
                                                   absolute_sigma=True, maxfev=5000,
                                                   bounds=(lower_bounds, upper_bounds))

            else:
                optimal_paramters_fixed, covariance_fixed = curve_fit(model_fixed_freq, guess_times, guess_diff,
                                                   p0=initial_guess, maxfev=5000,
                                                   bounds=(lower_bounds, upper_bounds))
            best_parameters = [optimal_paramters_fixed[0], optimal_paramters_fixed[1], tau_damp_guess]
            best_covariance = np.zeros((3,3))
            best_covariance[:2,:2] = covariance_fixed
            best_fit = asymmetry_model(guess_times, *best_parameters)
            
            if guess_errors is not None:
                residuals = guess_diff - best_fit
                chi2 = np.sum((residuals / guess_errors)**2)
                best_chi = chi2 / (len(guess_times) - 2)
                print(f"Fixed-tau fit: B={best_parameters[0]*1000:.2f} mT, β={best_parameters[1]:.2f} rad, χ²={best_chi:.2f}")

    
        

        except Exception as e:
            print(f"Fixed-frequency damped fit failed: {e}")
            import traceback
            traceback.print_exc()
            try:
                #redundant backup model
                def model_undamped(t, B, beta):
                    """following convention outlined in scipy vid, redundant function
                    Parameters:
                        t : np.array() or float
                            Time values in microseconds (μs). assume np.array().
                        B : float
                            Magnetic field strength in Tesla (T). Parameter to be optimized.
                        beta : float
                            Detector angle in radians (rad). Parameter to be optimized, but doesn't.
                        Returns:
                            Asymmetry A(t): np.array
                                A(t) = (1/3) * (sin(β)/β) * cos(γ·B·t) * exp(-t / τ_constant)
                        """
                    return asymmetry_model(t, B, beta, None)
    
                initial_guess_undamped = [B_guess, beta_guess]
                lower_bounds_undamped = [0, 0.5]
                upper_bounds_undamped = [0.03, 1.5] #backup plan, do something similar again
     
                if guess_errors is not None: 
                    opt_undamped, cov_undamped = curve_fit(
                        model_undamped, guess_times, guess_diff,
                        p0=initial_guess_undamped, sigma=guess_errors,
                        absolute_sigma=True, maxfev=5000,
                        bounds=(lower_bounds_undamped, upper_bounds_undamped)
                            )
                else:
                    opt_undamped, cov_undamped = curve_fit(
                        model_undamped, guess_times, guess_diff,
                        p0=initial_guess_undamped, maxfev=5000,
                        bounds=(lower_bounds_undamped, upper_bounds_undamped)
                            )
                    
                best_parameters = [opt_undamped[0], opt_undamped[1], None]
                best_covariance = np.zeros((3,3))
                best_covariance[:2,:2] = cov_undamped
                best_fit = asymmetry_model(guess_times, *best_parameters)
    
                if guess_errors is not None:
                    residuals = guess_diff - best_fit
                    chi2 = np.sum((residuals / guess_errors)**2)
                    best_chi = chi2 / (len(guess_times) - 2)
                    print(f"Undamped fit: B={best_parameters[0]*1000:.2f} mT, β={best_parameters[1]:.2f} rad, χ²={best_chi:.2f}")
        
            except Exception as e2:
                print(f"Undamped fit failed: {e2}")
                import traceback #yes it is standard library
                traceback.print_exc()
    

            
    if best_parameters is None:
        print("All fitting attempts failed.")
        
        return None, None, None, None, None
    if (abs(best_parameters[0] - B_guess) < 1e-3 and 
        abs(best_parameters[1] - beta_guess) < 1e-3 and
        abs(best_parameters[2] - tau_damp_guess) < 1e-3): #debugging assistant
        print("Note: Beta and tau_damp close to initial guesses - data may not constrain these parameters well")
    #tau_damp relic from sin symmetry plot, i just kept it
    # Calculate standard errors
    try:
        standard_errors = np.sqrt(np.diag(best_covariance))
    except:
        standard_errors = np.zeros_like(best_parameters)
    
    return best_parameters, best_covariance, standard_errors, best_fit, guess_times, best_chi

def sin_caller(filename = None): #ver 2
    """Improved 'oscillatory' fit with harmonic detection
    This function processes all energy levels in the data, creates histograms,
    calculates asymmetry and fits damped oscillatory models.
    Parameters:
        filename: str
            filename string (optional)
    Returns:
        (all_fit_results, fitted_asymmetry, B_fields): tuple
            all_fit_results : dict
                Dictionary containing fit results for each energy. Keys are energy strings
            fitted_asymmetry : dict
                Placeholder for asymmetry fit data
            B_fields: dict
                Dictionary mapping energy strings (e.g. '10keV') to T
    Notes:
        Should have abstracted more
    """
    if filename is None:
        filename = 'assessment_data_kswk7629.dat'
    data = data_table(filename)
    if data is None:
        print("Failed to load data")
        return
    
    channels = channel_seperator(data)
    if channels is None:
        print("Failed to separate channels")
        return
    
    all_fit_results = {}
    fitted_asymmetry = {}
    energy_list = list(channels.keys())
    
    #gamma_muon = 851.616  # Mrad·s⁻¹·T⁻¹  
    #gamma_muon_rad = gamma_muon * 1e6 
    B_fields = {}
    
    
    for energy in energy_list:
        if energy not in channels:
            print(f"Energy {energy} not found in channels")
            continue
            
        ch1_times = channels[energy]['CH1']['times']
        ch2_times = channels[energy]['CH2']['times']
        
        if len(ch1_times) == 0 or len(ch2_times) == 0:
            print(f"Insufficient data for {energy}")
            continue
        
        # Creates histogram for differences
        bins = 200
        all_times = np.concatenate([ch1_times, ch2_times])
        bin_edges = np.histogram_bin_edges(all_times, bins=bins)
        
        counts1, _ = np.histogram(ch1_times, bins=bin_edges)
        counts2, _ = np.histogram(ch2_times, bins=bin_edges)
        
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        # bin_width = bin_edges[1] - bin_edges[0]
        
        # Converts to rates
        # rate1 = counts1 / bin_width
        # rate2 = counts2 / bin_width
        # error1 = np.sqrt(counts1) / bin_width
        # error2 = np.sqrt(counts2) / bin_width
        
        # diff = rate1 - rate2 #shorthand differential #if karma is real this is how
        # diff_error = np.sqrt(error1**2 + error2**2)
        
        
        total_counts = counts1 + counts2
        mask = total_counts > 0
        asymmetry = np.zeros_like(counts1, dtype=float)
        asymmetry_error = np.zeros_like(counts1, dtype=float)
        
        if np.any(mask):
            asymmetry[mask] = (counts1[mask] - counts2[mask]) / total_counts[mask]
            delta_Counts_1 = np.sqrt(counts1[mask])
            delta_Counts_2 = np.sqrt(counts2[mask])
            numerator = (counts1[mask]**2 * delta_Counts_2**2 + counts2[mask]**2 * delta_Counts_1**2)
            denominator = total_counts[mask]**4
            asymmetry_error[mask] = 2 * np.sqrt(numerator / denominator)
        

        mask_fit = np.isfinite(bin_centers) & np.isfinite(asymmetry) & np.isfinite(asymmetry_error)
        bin_centers_fit = bin_centers[mask_fit]
        asymmetry_fit = asymmetry[mask_fit]
        asymmetry_error_fit = asymmetry_error[mask_fit]
        

        half_index = len(bin_centers_fit) // 2
        bin_centers_fit = bin_centers_fit[:half_index] #fit asymmetry, not diff
        asymmetry_fit = asymmetry_fit[:half_index]
        asymmetry_error_fit = asymmetry_error_fit[:half_index]
        
        print(f"Fitting asymmetry for {energy} with {len(bin_centers_fit)} points")
        
        mask_plot = np.isfinite(bin_centers) & np.isfinite(asymmetry) & np.isfinite(asymmetry_error)
        bin_centers_plot = bin_centers[mask_plot]
        asymmetry_plot = asymmetry[mask_plot]
        asymmetry_error_plot = asymmetry_error[mask_plot]
        
        
        
        
        result = fit_damped_sinusoidal(   #important
            bin_centers_fit, asymmetry_fit, asymmetry_error_fit,  #lol
            include_harmonic=True)
        
        
        
        
        
        if result[0] is not None:
            optimal_parameters, covariance, standard_errors, fit_curve, guess_times, best_chi = result
            if len(optimal_parameters) == 3:
                B_value, beta_value, tau_value = optimal_parameters
                
                #omega from B for plotting
                gamma = 851.616
                omega_value = gamma * B_value
                #5-parameter for asymmetry plotting
                A = 1.0  #amplitude will be normalized in plot
                tau = tau_value# if tau_value is not None else 3.0 #backup plan
                omega = omega_value
                phi = 0.0
                c = 0.0
                
                B_error = standard_errors[0] if standard_errors is not None else 0 #units?
                beta_error = standard_errors[1] if standard_errors is not None and len(standard_errors) > 1 else 0
                tau_error = standard_errors[2] if standard_errors is not None else 0

                B_fields[energy] = B_value
                if energy == '15keV' and B_value < B_fields['10keV']:
                    print("Warning: B field decreased from 10keV to 15keV - possible fit issue")
                    #i find it odd 25kev flatlines B but oh well.
                    #maybe decay rate less? but just... doesn't
                #print(f"  B field: {B_value*1000:.2f} mT")  #Debugger assistant
                if beta_value < 0.3 or beta_value > 1.8:
                    print(f"\nWarning: beta={beta_value:.2f} rad seems a bit weird")

                plot_parameters = [A, tau, omega, phi, c]
                
                print(f"\n{energy} Fit Results:")
                print(f"  B field: {B_value*1000:.2f} mT")
                print(f"  Beta: {beta_value:.2f} rad")
                if tau_value is not None:
                    print(f"  Tau_damp: {tau_value:.2f} μs")
                else:
                    print("Tau_damp: undamped")
                print(f"  Reduced χ² = {best_chi:.2f}")
                
                all_fit_results[energy] = {
                    'B': B_value,
                    'B_error': B_error,
                    'beta': beta_value,
                    'beta_error': beta_error,
                    'tau_damp': tau_value,
                    'tau_damp_error': tau_error,
                    'chi2': best_chi
                        }
                
                
            elif len(optimal_parameters) >= 5:
                #[A, tau, omega, phi, c] format
                A, tau, omega, phi, c = optimal_parameters[:5]
                
                #B field from omega
                gamma = 851.616
                B_value = omega / gamma
                B_fields[energy] = B_value
                
                plot_parameters = [A, tau, omega, phi, c]
                
                print(f"\n{energy} Fit Results:")
                print(f"  Amplitude: {A:.2f}") #for reference
                print(f"  Frequency: {omega:.3f} rad/μs → Period: {2*np.pi/omega:.3f} μs")
                print(f"  Phase: {phi:.3f} rad")
                print(f"  Offset: {c:.2f}")
                print(f"  B field: {B_fields[energy]*1000:.2f} mT")
                print(f"  Reduced χ² = {best_chi:.2f}")
                
                # Stores fit results
                all_fit_results[energy] = {
                    'B': B_value,
                    'omega': omega,
                    'tau': tau,
                    'chi2': best_chi
                }
            else:
                print(f"Unexpected parameter format for {energy}: {optimal_parameters}")
                continue
            
            if len(optimal_parameters) == 3:
                B_value, beta_value, tau_value = optimal_parameters
                gamma = 851.616
                prefactor = (1/3) * (np.sin(beta_value) / beta_value)
                omega_value = gamma * B_value
    
                if tau_value is not None and tau_value > 0:
                    fit_curve_asymmetry = prefactor * np.cos(omega_value * bin_centers_plot) * np.exp(-bin_centers_plot / tau_value)
                else:
                    fit_curve_asymmetry = prefactor * np.cos(omega_value * bin_centers_plot)
                    #remaking asymmetry
                plot_parameters = [prefactor, tau_value, omega_value, 0.0, 0.0]
            else:
                fit_curve_asymmetry = fit_curve
                
            #re-eval of errors
            # residuals = asymmetry_plot - fit_curve_asymmetry
            # residuals_std = np.std(residuals)
    
            # signal_amplitude = np.mean(np.abs(asymmetry_plot))
            # if signal_amplitude > 0:
            #     fractional_error = residuals_std / signal_amplitude
            #     B_error = fractional_error * B_value  # in Tesla #modify B_error
            #     all_fit_results[energy]['B_error'] = B_error
                
            #     #print(f"  B error (from residuals): ±{B_error*1000:.2f} mT")
            # else:
            #     B_error = B_value * 0.1  # fallback 10%
                
            # fractional_error = np.std(residuals) / np.mean(np.abs(asymmetry_plot))

            # #how much does β affect the fit?
            # beta_perturb = 0.05
            # prefactor_orig = (1/3) * (np.sin(beta_value) / beta_value)
            # prefactor_pert = (1/3) * (np.sin(beta_value + beta_perturb) / (beta_value + beta_perturb))
            # relative_change = abs((prefactor_pert - prefactor_orig) / prefactor_orig)

            # if relative_change > 0:
            #     #beta uncertainty
            #     beta_error_estimate = fractional_error / (relative_change / beta_perturb)
            #     all_fit_results[energy]['beta_error'] = beta_error_estimate
                
                
                
            # fractional_error = np.std(residuals) / np.mean(np.abs(asymmetry_plot))

            # # Tau error - fractional error also as i am lazy
            # if tau_value is not None and tau_value > 0:
            #     tau_error = fractional_error * tau_value
            # else:
            #     tau_error = 1.0  # fallback

            # print(f"  τ error: ±{tau_error:.2f} μs")
            # all_fit_results[energy]['tau_damp_error'] = tau_error
            
            if best_chi > 60 and tau_error > 3.0: #silly plan #but it worked good
                try:
                    #now a redundant model
                    def model_undamped(t, B, beta): #now redundant
                        """following convention outlined in scipy vid, redundant funct
                        Parameters:
                            t : np.array() or float
                                Time values in microseconds (μs). assume np.array().
                            B : float
                                Magnetic field strength in Tesla (T). Parameter to be optimized.
                            beta : float
                                Detector angle in radians (rad). Parameter to be optimized, but doesn't.
                            Returns:
                                Asymmetry A(t): np.array
                                    A(t) = (1/3) * (sin(β)/β) * cos(γ·B·t) * exp(-t / τ_constant)
                            """
                        return asymmetry_model(t, B, beta, None)
                    opt_undamped, cov_undamped = curve_fit(
                        model_undamped, bin_centers_fit, asymmetry_fit,
                        p0=[B_value, beta_value],  # Use current B and beta as starting point
                        sigma=asymmetry_error_fit,
                        absolute_sigma=True,
                        maxfev=5000,
                        bounds=([0, 0.0], [0.03, 1.5]))
                    
                    fit_curve_asymmetry_undamped = prefactor * np.cos(omega * bin_centers_plot)
                    
                    residuals_undamped = asymmetry_plot - fit_curve_asymmetry_undamped
                    chi2_undamped = np.sum((residuals_undamped / asymmetry_error_plot)**2) if np.any(asymmetry_error_plot > 0) else np.sum(residuals_undamped**2)
                    redchi_undamped = chi2_undamped / (len(asymmetry_plot) - 2)
    
                    if redchi_undamped < best_chi:
                        print(f"Undamped fit is better! (χ²={redchi_undamped:.2f} vs {best_chi:.2f})")
                        B_value = opt_undamped[0]
                        beta_value = opt_undamped[1]
                        tau_value = None
                        best_chi = redchi_undamped
        
                        # Updates the fit curve and plot parameters
                        fit_curve_asymmetry = fit_curve_asymmetry_undamped
                        plot_parameters = [prefactor, None, omega, 0.0, 0.0]
        
                        # Updates the dictionary
                        all_fit_results[energy]['B'] = B_value
                        all_fit_results[energy]['beta'] = beta_value
                        all_fit_results[energy]['tau_damp'] = None
                        all_fit_results[energy]['chi2'] = redchi_undamped
        
                        # Recalc errors #probably don't need to but eh
                        residuals = asymmetry_plot - fit_curve_asymmetry
                        fractional_error = np.std(residuals) / np.mean(np.abs(asymmetry_plot))
                        B_error = fractional_error * B_value
                        all_fit_results[energy]['B_error'] = B_error
        
                        # Beta error for undamped
                        beta_perturb = 0.05
                        prefactor_orig = (1/3) * (np.sin(beta_value) / beta_value)
                        prefactor_pert = (1/3) * (np.sin(beta_value + beta_perturb) / (beta_value + beta_perturb))
                        relative_change = abs((prefactor_pert - prefactor_orig) / prefactor_orig)
                        if relative_change > 0:
                            beta_error_estimate = fractional_error / (relative_change / beta_perturb)
                            all_fit_results[energy]['beta_error'] = beta_error_estimate
        
                        print(f"Updated B field: {B_value*1000:.2f} mT, β: {beta_value:.2f} rad, χ²={redchi_undamped:.2f}")
                    else:
                        print(f"Undamped fit not better (χ²={redchi_undamped:.2f})")
        
                except Exception as e:
                    print(f"Undamped fit failed: {e}")

    
            plot_asymmetry_separate(energy, bin_centers_plot, asymmetry_plot, 
                                asymmetry_error_plot, fit_curve_asymmetry, 
                                plot_parameters, best_chi)

            if standard_errors is not None and len(standard_errors) >= 3:
                if len(standard_errors) >= 5:
                    print(f" τ error: ±{standard_errors[1]:.3f}")
                    print(f" ω error: ±{standard_errors[2]:.3f}")
                else:
                    print(f" B error: ±{all_fit_results[energy]['B_error']*1000:.2f} mT")
                    print(f" β error: ±{standard_errors[1]:.3f} rad")
                    print(f" τ error: ±{tau_error:.3f} μs")
        else:
            print(f"Fit failed for {energy}")
    
    if B_fields:
        print("="*35) #style
        print("B Field Results for All Energies:")
        print("="*35)
        for energy, B in B_fields.items():
            print(f"{energy}: {B*1000:.2f} mT")

        # plot_B_vs_energy(B_fields)
        #commented out for memory efficiency
        # fit_quadratic_to_B(B_fields)
    else:
        print("No B fields found - cannot create B vs Energy plot")
    
    return all_fit_results, fitted_asymmetry, B_fields

def fit_quadratic_to_B(B_fields, return_coefficient=False):
    """This function takes a dict of magnetic field values at different implantation
    energies, performs a quadratic fit, and plots the results for: B(E) = a·E² + b·E + c
    
    Parameters:
        B_fields : dict
            Dictionary mapping energy strings (e.g.'10keV') to magnetic field
            values in T
    return_coefficient : bool, default=False
        If True, returns the fitted coefficients and their uncertainties. 
        elif False, only displays the plot and prints results without returning values.
    
    Returns:
        tuple or None
    """
    energies = list(B_fields.keys())
    B_values = list(B_fields.values())

    # Convert energy strings to numbers
    energies = [(e.replace('keV', '')) for e in energies]
    energies = np.array(energies).astype(float)
    B_values = np.array(B_values)
    
    if len(energies) < 3:
        print("Need at least 3 energies for quadratic fit")
        return
    
    def quadratic(E, a, b, c):
        """following convention outlined in scipy vid
        Parameters:
            E : np.array()
                Implantation energy in keV. Can be a single value or array of values.
            a : float
                Quadratic coefficient (units: T/keV²). Determines curvature of the parabola.
            b : float
                Linear coefficient (units: T/keV). Determines the slope at zero energy.
            c : float
                Constant offset (units: T). Magnetic field at zero energy.
        Returns:
            np.array():
                Magnetic field B in T, calculated as a·E² + b·E + c.
            
        """
                
        return a * E**2 + b * E + c #e exponent
    
    try:
        popt, pcov = curve_fit(quadratic, energies, B_values) #popt is shorthand for optimal_parameters
        perr = np.sqrt(np.diag(pcov)) #pcov shorthand optimal_covariance
        
        # Create plot with fit
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Data points #why is it flatlined>? #future josh here, defined as int not float
        ax.plot(energies, B_values*1000, 'bo', markersize=8, label='Data')
        
        E_fit = np.linspace(min(energies), max(energies), 100)
        B_fit = quadratic(E_fit, *popt)
        ax.plot(E_fit, B_fit*1000, 'r-', linewidth=2, 
                label=f'Fit: B = {popt[0]:.2e}E² + {popt[1]:.3f}E + {popt[2]:.2f}')
        
        ax.set_xlabel('Implantation Energy (keV)', fontsize=12)
        ax.set_ylabel('Magnetic Field B = uH*1000 (mT)', fontsize=12) #change
        ax.set_title('Magnetic Field vs Energy with Quadratic Fit', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        #parameter box
        text = (f'a = {popt[0]:.3e} ± {perr[0]:.3e}T/keV²\n'
                f'b = {popt[1]:.4f} ± {perr[1]:.6f}T/keV\n' #units provided
                f'c = {popt[2]:.5f} ± {perr[2]:.5f}T') 
        ax.text(0.02, 0.98, text, transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.show()
        
        print("\nQuadratic Fit Results:")
        print(f" a = {popt[0]:.3e} ± {perr[0]:.3e} T/keV²")
        print(f" b = {popt[1]:.4f} ± {perr[1]:.6f} T/keV")
        print(f" c = {popt[2]:.5f} ± {perr[2]:.5f} T") #tweaked to see data
        
        if return_coefficient:
            return (float(popt[0]), float(popt[1]), float(popt[2])), \
                (float(perr[0]), float(perr[1]), float(perr[2]))
        else:
            return None
    except Exception as e:
        print(f"Quadratic fit failed: {e}")


def plot_asymmetry_separate(energy, times, data, errors, fit_curve, params, chi2):
    """separate plot of asymmetry function
    Parameters:
        energy : str
            Implantation energy (e.g.'10keV') used for title.
        times : np.array
            Time bin centers in μs where asymmetry is calculated.
        data : np.array
            Calculated asymmetry values data.
        errors : np.array
            Using equation from guidance
        fit_curve : np.array
            Best-fit asymmetry values from the asymmetry_model using optimized parameters
            (B, beta, tau_damp).
        params : list/dict of flt
            List of 5 parameters: [A, tau, omega, phi, c]
        chi2 : flt
            Reduced chi-squared value from the fit, for accuracy of fit.
    Returns:
        fig, ax
        
    """
    
    A, tau, omega, phi, c = params[:5]
    # #not going to lie this function feels handwavy at best
    # # Normalize cause example looks like it as x < 1
    # norm_data = (data - c) / (A*3) #brute forced the 1/3 amplitude
    # norm_fit = (fit_curve - c) / (A*3) #relic of sinfit attempt (actually looked good)
    # norm_errors = errors / (A*3) #keeping for case of need brute forcing
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.errorbar(times, data, yerr=errors, 
                fmt='o', markersize=4, capsize=2, alpha=0.7,   #changed so more visible
                color='blue', ecolor='gray', label='Data') #colour 
    
    ax.plot(times, fit_curve, 'r-', linewidth=2, label='Fit')
    
    if tau is not None and tau > 0 and not np.isinf(tau):
    #use prefactor from the model
        prefactor = (1/3)  # Approximate envelope without beta dependence
        envelope = prefactor * np.exp(-times / tau)
        ax.plot(times, envelope, 'k--', alpha=0.5, label='Envelope')
        ax.plot(times, -envelope, 'k--', alpha=0.5)
        
    # ax.plot(times, np.exp(-times/tau)/3, 'k--', alpha=0.5, label='Envelope')
    # ax.plot(times, -np.exp(-times/tau)/3, 'k--', alpha=0.5)
    # ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5) #old asymmetry funct remains
    # ax.axhline(y=1/3, color='gray', linestyle=':', alpha=0.3)
    # ax.axhline(y=-1/3, color='gray', linestyle=':', alpha=0.3) #set to max 1/3
    #basically copied from previous one, see assymetry function 4 for step by step
    ax.set_xlabel('Time (μs)', fontsize=12)
    ax.set_ylabel('Normalized Asymmetry Ratio', fontsize=12) #reanemed cause sample report
    ax.set_title(f'{energy} - Asymmetry Function', fontsize=14)
    ax.set_ylim(-0.5, 0.5)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Parameter box
    if tau is not None: #fixing
        text = (f'τ = {tau:.3f} μs\n'
            f'f = {omega/(2*np.pi):.3f} 1/μs\n'
            f'χ² = {chi2:.2f}\n')
            # f'B'
            # )
    else:
        text = (f'τ = undamped\n'
                f'f = {omega/(2*np.pi):.3f} 1/μs\n'
                f'χ² = {chi2:.2f}')  
        
    ax.text(0.02, 0.98, text, transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', alpha=0.5))
    
    plt.tight_layout()
    plt.show()
    return fig, ax


# def magnetic_field_muon(omega): #basically useless as i just find it easier to calc in function
#     """Calculates B for inputted omega
#     Parameters:
#         omega: flt 
#             Angular frequency from fit in (rad/μs) #larmor
#     Returns:
#         B: flt
#             Magnetic field strength in Tesla
#     """
#     gamma_muon = 851.616e6 #assume it is just in mega 10**6
#     omega_rad_per_s = omega * 1e6
    
#     # B = ω / γ for reference ωt = γBt
#     B = omega_rad_per_s / gamma_muon
    
#     return B

#make plot_B_vs_energy(B_fields) funct

# def plot_B_vs_energy(B_fields): #think about retreiving stuff L ater
#     """Plots B field against energies
#     Parameters:
#         B_fields : dict
#             Dictionary mapping energy strings (e.g.'10keV') to magnetic field
#     Returns:
#         fig, ax (plotting)
#     """
#     energies = list(B_fields.keys()) #returns energies in kev, probs need more format to axis
#     B_values = list(B_fields.values()) #format 'should' be ok cause flt val, not str

#     fig, ax = plt.subplots(figsize=(10,6)) #right now value error
    
#     #    for energy in energy_list: #remember
#     #energies = energies.astype(float) #looking at .astype(int) from guidance vid
#     energies = [(e.replace('keV', '')) for e in energies]
#     energies = np.array(energies).astype(int) #remember it's array, not standalone variable
#     ax.plot(energies, B_values, 'o-', markersize=8, linewidth=2)
#     ax.set_xlabel('Energy (keV)')
#     ax.set_ylabel('Magnetic Field B (T)')
#     ax.set_title('Magnetic Field vs Energy')
#     ax.grid(True, alpha=0.3)
    
#     plt.show()
    
#     return fig, ax



# def main():
#     """main, call and compile the things in my code
#     Returns:
#         channel_retriever(): function
#             calls with file to retreive the data
#         ProcessData(): function
#             what's wanted to pass
#     """
#     try:
#         channel_retriever('assessment_data_kswk7629.dat')
#     except Exception as e:
#         print(f"something went wrong in channel_retriever: {e}") #final debugger
#     try:
#         ProcessData('assessment_data_kswk7629.dat')
#     except Exception as e:
#         print(f"something went wrong in sin_caller: {e}") #robustness
        

def get_empty_results_dict():
    """Properties/parameters of 10keV plot as a dictionary.
    Returns:
        results: dict
            "10keV_B" : float 
                magnetic field at 10keV in T
            "10keV_B_error" : float
                uncertainty in B
            "beta" : float
                detector angle in rad
            "beta_error" : float
                uncertainty in beta (radians)
            "10keV_tau_damp_error" : float
                uncertainty in tau_damp (seconds)
            "B(Energy)_coeffs" : tuple of 3 floats
                quadratic coefficients (a, b, c)
            "B(Energy)_coeffs_errors" : tuple of 3 floats
                uncertainties
    """
    return {
        "10keV_B": None,
        "10keV_B_error": None,
        "beta": None,
        "beta_error": None,
        "10keV_tau_damp": None,
        "10keV_tau_damp_error": None,
        "B(Energy)_coeffs": (None, None, None), #did it want coeffs? ffs
        "B(Energy)_coeffs_errors": (None, None, None)
    }


def ProcessData(filename):
    """Processes the muon spectroscopy data and return fit results for assessment.
    
    This function shows the full data analysis function structure
    Parameters:
        filename: str
            'assessment_data_kswk7629.dat'
    Returns:
        results: dict
            "10keV_B" : float 
                magnetic field at 10keV in T
            "10keV_B_error" : float
                uncertainty in B
            "beta" : float
                detector angle in rad
            "beta_error" : float
                uncertainty in beta (radians)
            "10keV_tau_damp_error" : float
                uncertainty in tau_damp (seconds)
            "B(Energy)_coeffs" : tuple of 3 floats
                quadratic coefficients (a, b, c)
            "B(Energy)_coeffs_errors" : tuple of 3 floats
                uncertainties
    Notes:
        B fields are converted from mT to Tesla (divided by 1000)
        Tau_damp is converted from μs to seconds (multipled by 1e-6)
        Requires at least 3 energies for quadratic fit
    """
    data = data_table(filename)
    if data is None:
        return get_empty_results_dict()
    
    channels = channel_seperator(data)
    if channels is None:
        return get_empty_results_dict()
    try:
        channel_retriever('assessment_data_kswk7629.dat')
    except Exception as e:
        print(f"something went wrong in channel_retriever: {e}") #final debugger

    all_fit_results, _, B_fields = sin_caller(filename)  # sin_caller now has auto filename for robustness

    results = get_empty_results_dict()

    if '10keV' in B_fields:
        results["10keV_B"] = B_fields['10keV'] / 1000 #mili Tesla???
        if '10keV' in all_fit_results:
            results["10keV_B_error"] = all_fit_results['10keV'].get('B_error', 0) /1000
            results["beta"] = all_fit_results['10keV'].get('beta', None) 
            results["beta_error"] = all_fit_results['10keV'].get('beta_error', 0)
            results["10keV_tau_damp"] = all_fit_results['10keV'].get('tau_damp', None)
            
            tau_damp_value = all_fit_results['10keV'].get('tau_damp', None)
            #results["10keV_tau_damp_error"] = all_fit_results['10keV'].get('tau_damp_error', 0)
            if tau_damp_value is not None:
                results["10keV_tau_damp"] = tau_damp_value * 1e-6
                results["10keV_tau_damp_error"] = all_fit_results['10keV'].get('tau_damp_error', 0) 
            else:
                results["10keV_tau_damp"] = None
                results["10keV_tau_damp_error"] = 0
        
        else:
            print("something went wrong")
    # Fits the quadratic to B v Energy
    if len(B_fields) >= 3:
        coefficient, coefficient_errors = fit_quadratic_to_B(B_fields, return_coefficient=True)
        if coefficient is not None and coefficient[0] is not None:
            results["B(Energy)_coeffs"] = coefficient
            results["B(Energy)_coeffs_errors"] = coefficient_errors #coeffs
    
    return results
    
    # results={"10keV_B":None, #this would be the magnetic field for 10keV data (T)
    #          "10keV_B_error":None, # the error in the magnetic field (T)
    #          "beta": None, #Detector angle in radians
    #          "beta_error": None, #uncertainity in detector angle (rad)
    #          "10keV_tau_damp": None, #Damping time for 10keV (s)
    #          "10keV_tau_damp_error": None, #and error (s)
    #          "B(Energy)_coeffs":(None,None,None), #tuple of a,b,c for quadratic,linear and constant terms
    #                                               #for fitting B dependence on energy
    #                                               #(T/keV^2,T/keV,T)
    #          "B(Energy)_coeffs_errors":(None,None,None), # Errors in above in same order.
    #          }

if __name__=="__main__":
    # Put your test code in side this if statement to stop it being run when you import your code
    #Please avoid using raw_input as the testing is going to be done by a computer programme, so
    #can't input things from a keyboard....
    filename='assessment_data_kswk7629.dat'
    if not os.path.exists(filename):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_directory, filename)
        if os.path.exists(alt_path):
            filename = alt_path
            print(f"Using file from script directory: {filename}")
        else:
            print(f"Error: File '{filename}' not found in current or script directory.")
            print(f"Current directory: {os.getcwd()}")
            sys.exit(1)

    try:
        test_results = ProcessData(filename)
        print(test_results)
    except Exception as e:
        print(f"Error processing file '{filename}': {e}")
        sys.exit(1)