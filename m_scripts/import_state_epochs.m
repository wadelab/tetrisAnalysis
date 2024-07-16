 brainstormdb = '/scratch/groups/Projects/P1454/brainstormdb/Tetris/data';
behaviouralData = '/groups/Projects/P1454/behavioural_data';
state_names = 'state 1, state 2, state 3';

% get list of subjects in brainstorm database
subjectBrainstormPattern = fullfile(brainstormdb, 'R*');
subjectsBrainstormDB = dir(subjectBrainstormPattern);

% get list of subjects in project database
subjectBehaviouralDataPattern = fullfile(behaviouralData, 'R*');
subjectsBehaviouralData = dir(subjectBehaviouralDataPattern);
% FOR TESTING, DELETE LATER
subjectsBrainstormDB = subjectsBrainstormDB([1:10, 12:end]);
subjectsBehaviouralData = subjectsBehaviouralData([1:10, 12:end]);


for n = 1 : length(subjectsBrainstormDB)
    
    % declare current subject
    subjectName = subjectsBrainstormDB(n).name;
    % declare subject's acquisition files in brainstormdb
    acqBrainstormPattern = fullfile(brainstormdb, subjectName, '*resample_band', 'data*.mat');
    acquisitions = dir(acqBrainstormPattern);
    % declare subject's behavioural data directory
    acqBehaviouralPattern = fullfile(subjectsBehaviouralData(n).folder, subjectsBehaviouralData(n).name, 'state_timestamps*.csv');
    acqBehaviouralData = dir(acqBehaviouralPattern);
    
    % populate container with acquisition file names
    for acq = 1 : length(acqBehaviouralData)
        % declare acquisition to be worked on
        acqFileName = fullfile(acquisitions(acq).folder, acquisitions(acq).name);
        acqFileName = extractAfter(acqFileName, 'data');
        sFiles = {acqFileName};
        % declare events file to import
        eventsFileName = fullfile(acqBehaviouralData(acq).folder, acqBehaviouralData(acq).name);
        rawFiles = eventsFileName;
        
        % import HMM state epochs from file
        sFiles = bst_process('CallProcess', 'process_evt_import', sFiles, [], ...
            'evtfile', {rawFiles, 'CSV-TIME'}, ...
            'evtname', state_names);
        
        % import state epochs into database
        sFiles = bst_process('CallProcess', 'process_import_data_event', sFiles, [], ...
            'subjectname', subjectName, ...
            'condition',   '', ...
            'eventname',   state_names, ...
            'timewindow',  [], ...
            'epochtime',   [0, 1.0], ...
            'createcond',  1, ...
            'ignoreshort', 1, ...
            'usectfcomp',  1, ...
            'usessp',      1, ...
            'freq',        [], ...
            'baseline',    []);

        % now prepend the game number to each folder of state epochs
        statesPattern = fullfile(subjectsBrainstormDB(n).folder, subjectsBrainstormDB(n).name, 'state*');
        statesDir = dir(statesPattern);
        for state = 1 : length(statesDir) 
            % define old and new labels
            stateDirName = fullfile(statesDir(state).folder, statesDir(state).name);
            prefix = strcat('game_', num2str(acq), '_');
            newStateDirName = strcat(prefix, statesDir(state).name);
            % identify files to be moved
            if exist(stateDirName, 'dir')
                statesFilePattern = fullfile(statesDir(state).folder, statesDir(state).name, 'data*');
                filesStruct = dir(statesFilePattern);
                sFiles = cell(1,length(filesStruct));
                for i = 1 : length(filesStruct)
                    fileName = fullfile(filesStruct(i).folder, filesStruct(i).name);
                    fileName = extractAfter(fileName, 'data');
                    sFiles{i} = fileName;
                end
                % move over the channel file
                channelFilePath = fullfile(statesDir(state).folder, statesDir(state).name, 'channel*');
                newChannelFilePath = fullfile(statesDir(state).folder, newStateDirName);
                movefile(channelFilePath, newChannelFilePath);
                % now move files to new directory
                sFiles = bst_process('CallProcess', 'process_movefile', sFiles, [], ...
                    'subjectname', subjectName, ...
                    'folder',      newStateDirName);

            end
        end
    end
end

