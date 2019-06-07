# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 12:46:31 2019

Signal generator for RFI use cases for SKA.


@author: f.divruno
"""
import scipy.signal as Sig
import numpy as np
import matplotlib.pyplot as plt
import RFI_general_functions as RFI

ms = 1e-3
us = 1e-6
MHz = 1e6
km = 1e3
minute = 60
hr = 60*minute
km_h = km/hr

#%%
def Signal(Name,SamplingFreq,fcentre,Ampl_change=0, N_pulses=1, rand_phase=0, rand_displace=0):
# this function generates N periods of any signal selected, at the moment only ADS-B and DME.
    
    t_aux = []
    env_aux = []
    
    for i in range(N_pulses):
        
        if Name == 'DME':
            # signal between 1025 to 1150 MHZ
            period = 1*ms # periodicity of the signal
            offset = 12*us # separation between the pulses
            
            fc = fcentre
            Bw = 1*MHz
    
            t = np.linspace(-period/2,period/2,int(period*SamplingFreq))
    
            [k,env1] = Sig.gausspulse(t,fc,Bw/fc,retenv=1) #envolvent of the gauss pulse
    
            env2 = np.roll(env1,int(offset*SamplingFreq)) #envolvent shifted in time to generate the second pulse.
            
            t = np.linspace(0,period,int(period*SamplingFreq))
            env = env1 + env2
    
    
        if Name == 'ADS-B':
            # 
            Ton = 120*us
            fc = fcentre
            period = 1*ms # periodicity of the signal
            
            Trise = 0.1*us
            Tfall = 0.1*us
            Tpulse = 0.5*us-Trise-Tfall
            pulse_env = np.concatenate((np.linspace(0,1,int(Trise*SamplingFreq)) \
                                        ,np.ones(int(Tpulse*SamplingFreq)) \
                                        ,np.linspace(1,0,int(Tfall*SamplingFreq)) \
                                        ,np.zeros(int((1*us-Trise-Tfall-Tpulse)*SamplingFreq))))
            env = []
            for i in range(120):
                pulse_shift = (np.round(np.random.random(1))).astype(int)
                env = np.concatenate((env,np.roll(pulse_env,int(pulse_shift*0.5*us*SamplingFreq))))
            
            env = np.concatenate((env,np.zeros(int((period-Ton)*SamplingFreq))))
            t = np.linspace(0,period,int(period*SamplingFreq))
            
        try:
            t_aux = np.concatenate((t_aux,t_aux[-1]+t))
        except:
            t_aux = np.concatenate((t_aux,t))
                
        env_aux = np.concatenate((env_aux,env))


    if rand_phase:
        phase = np.random.rand(1)*2*np.pi
    else:
        phase = 0
        
    S = np.sin(2*np.pi*fc*t_aux+phase)*env_aux
    
    # displacement of the signal
    if rand_displace:
        N = int(fs/period)
        displace = int(np.random.rand(1)*N)
        S = np.roll(S,displace)
          
    if Ampl_change:
        A = np.random.rand(1)+0.1
        S = S*A
    return [t_aux,S]



def Gauss_Noise(t,fs,stdev):
    # Define a white gausian noise to add to the RFI signal.
    # noise is defined in voltage.
    # Bandwidth of the noise is -fs/2 to fs/2
    N = len(t)
    Noise = stdev*np.random.randn(N)
    return Noise

    

def multiple_emitters(Name,N_emitters,duration,fs):
    # This function generates a repetition of the basic signal N_repeat times,
    # DME:
    DME_pulse = 1*ms
    N_pulses = int(duration/DME_pulse)+1
    points = int(N_pulses*DME_pulse*fs)
    S = np.ndarray(points)
    
    for i in range(N_emitters):
        fc = 1025*MHz + np.random.rand(1)*125*MHz # randomize the center frequency.
        t1,S1 = Signal('DME',fs,fc,1,N_pulses,rand_phase=1,rand_displace=1)
        S += S1
            
    return t1[(t1<=duration)],S[(t1<=duration)]




  
    
#%% DME
#
#[t1,S1] = Signal('DME',5000*MHz,1025*MHz)
##[t1,S2 ]= Signal('DME',5000*MHz)
##[t1,S3 ]= Signal('DME',5000*MHz)
#
#plt.figure()
#plt.plot(t1*1e6,S1)
##plt.plot(t1,S2)
##plt.plot(t1,S3)
#

#%%
fs = 3000*MHz
duration= 3*ms
[t1,S_DME] = multiple_emitters('DME',20,duration,fs)
plt.figure()
plt.plot(t1,S_DME)


N = len(S_DME)
P_fft = np.abs(np.fft.fftshift(np.fft.fft(S_DME)/N))**2/50
f_fft = np.fft.fftshift(np.fft.fftfreq(N, d=1/fs))

plt.figure()
plt.plot(f_fft,10*np.log10(P_fft*1e3))
plt.title('FFT of the multiple signal DME')


#%%
#def RFI_use_case_generator(signal_type,fs,duration,precision = 'Float64'):
    

