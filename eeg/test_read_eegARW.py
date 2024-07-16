#%%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 15:37:46 2023

@author: db900, aw890
"""

import numpy as np
import matplotlib.pyplot as plt

import mne
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

legaltriggers = {
    "17": 1,
}



filename = "/raid/projects/P1507_tetris/eeg/preprocessed/SS001.set"
raw = mne.io.read_raw_eeglab(filename,preload=True)
raw.drop_channels(["HEOG", "VEOG", "M1", "M2"])
ANT_montage = mne.channels.make_standard_montage("standard_1020")
raw.set_montage(ANT_montage)

print(raw)
print(raw.info)
#%%
# pick some channels that clearly show heartbeats and blinks

raw.plot(show_scrollbars=True)
#%%
filtered = raw.copy().filter(l_freq=1.0, h_freq=40)


filtered.plot(show_scrollbars=True)
#%%

fig = filtered.plot_topomap(
    0.1,  show_names=True, colorbar=False, size=6, res=128
)
#%%


ica = mne.preprocessing.ICA(n_components=20, random_state=97, max_iter=800)
ica.fit(filtered)

#raw.load_data()
ica.plot_sources(filtered, show_scrollbars=False)


#%%
ica.plot_components()
#%%



ica.plot_properties(filtered)


ica.apply(filtered)

#%%


events, event_id = mne.events_from_annotations(filtered, event_id=legaltriggers)
print(events[:5])  # show the first 5


event_dict = {
    "aTrigger": 1,

}

      

reject_criteria = dict(
    eeg=150e-6,  # 150 µV
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
