clear
close all;
[ret, name] = system('hostname')

disp(name)
if strfind(name,'d2')
    eeglabdir = '/raid/toolbox/eeglab2024.0/';
    rawdatadir = '/raid/projects/P1507_tetris/eeg/raw';
    eeglabdata = '/raid/projects/P1507_tetris/eeg/preprocessed';
    procpath = '/raid/projects/P1507_tetris/eeg/output';
else
    % We are on YNiC probably
    eeglabdir = '/groups/labs/wadelab/toolbox/eeglab_2024/';
    rawdatadir = '/scratch/groups/Projects/P1507/eeg/raw';
    eeglabdata = '/scratch/groups/Projects/P1507/eeg/preprocessed';
    procpath = '/scratch/groups/Projects/P1507/eeg/output';

end

% if ~exist(dbpath,'dir')
%     mkdir(dbpath);
% end
% if ~exist(procpath,'dir')
%     mkdir(procpath);
% end

addpath(eeglabdir);
[ALLEEG EEG CURRENTSET ALLCOM] = eeglab('nogui');
% plugin_askinstall('ANTeepimport');
dlist = dir(strcat(rawdatadir,'/S*'))

for sno = 1:length(dlist)
    s = dlist(sno).name;
    if ~exist(strcat(eeglabdata,'/',num2str(s),'.set'),'file')
        tic
        EEGpath = strcat(rawdatadir,'/',num2str(s));
        d = dir(strcat(EEGpath,'/*.cnt'))       % index the directory containing the EEG files
        counter = length(d);
        c = 1;
        fname = d(c).name;
        EEG = pop_loadeep_v4(strcat(EEGpath,'/',fname));    % load the EEG data
        if counter>1
            for c = 2:counter                       % loop through all cnt files
                fname = d(c).name;
                EEG2 = pop_loadeep_v4(strcat(EEGpath,'/',fname));    % load the EEG data
                EEG = pop_mergeset(EEG, EEG2);
            end
        end
        EEG = eeg_checkset( EEG );
        EEG=pop_chanedit(EEG, 'lookup',strcat(eeglabdir,'/plugins/dipfit/standard_BEM/elec/standard_1005.elc'));
        EEG = pop_saveset( EEG, 'filename',strcat('S',num2str(s),'.set'),'filepath',eeglabdata);
        toc
    end
end
rmpath(eeglabdir);