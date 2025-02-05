#%%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 15:37:46 2023

@author: db900, aw890
"""
# To run this you need MNE installed in your environment (I think it is by default at YNIC) - and 
# edit the path to the 
import numpy as np
import matplotlib.pyplot as plt
import os
import mne


legaltriggers = {
    "17": 1, # This is just messing around for now. Really we want to use these triggers to indicate the start of the expt, then pull all the others from psychopyu
    "16": 2,
}


dataDir='/raid/projects/P1507_tetris/eeg/preprocessed/'
filename ="SS001.set"

fullFile=os.path.join(dataDir,filename)
print(fullFile)

raw = mne.io.read_raw_eeglab(fullFile,preload=True)
raw.drop_channels(["HEOG", "VEOG", "M1", "M2"])
ANT_montage = mne.channels.make_standard_montage("standard_1020")
raw.set_montage(ANT_montage)

print(raw)
print(raw.info)
#%%
# pick some channels that clearly show heartbeats and blinks

#%%

filtered = raw.copy().resample(200).filter(l_freq=1.0, h_freq=40)

#%%
filtered.plot()   
filtered.info['bads']=['CP1','CP4']
#%%

# Get the events from filtered so that we can crop front and back
ev=mne.events_from_annotations(filtered)

#  Find the event corresponding to 64 - note its time in samples

filtered=filtered.crop(tmin=20,tmax=3000)
ica = mne.preprocessing.ICA(n_components=20, random_state=97, max_iter=800)
ica.fit(filtered)

#raw.load_data()
ica.plot_sources(filtered, show_scrollbars=False)


#%%
ica.plot_components()
#%%



ica.plot_properties(filtered)

ica.exclude=[0,2]
ica.apply(filtered)

#%%


events, event_id = mne.events_from_annotations(filtered, event_id=legaltriggers)
print(events[:5])  # show the first 5


event_dict = {
    "aTrigger": 2,
}

      

reject_criteria = dict(
    eeg=10-6,  # 150 µV
)  # 250 µV

reject_criteria = None

epochs = mne.Epochs(
    filtered,
    events,
    event_id=event_dict,
    tmin=-0.2,
    tmax=1,
    reject=reject_criteria,
    preload=True,
)

#epochs.plot(show_scrollbars=True)
# Generate list of evoked objects from conditions names
epochs["aTrigger"].plot_image(combine="mean")
t1 = epochs.average()

t1.plot(time_unit="s")  # plot evoked response
t1.plot_topomap(times=[-0.2,.1, 0.22, 0.4], average=0.05)

# %%
