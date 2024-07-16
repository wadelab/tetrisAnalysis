% Input files
brainstormdb = '/scratch/groups/Projects/P1454/brainstormdb/Tetris/data';
behaviouralData = '/groups/Projects/P1454/behavioural_data';

% get list of subjects in brainstorm database
subjectBrainstormPattern = fullfile(brainstormdb, 'R*');
subjectsBrainstormDB = dir(subjectBrainstormPattern);

% get list of subjects in project database
subjectBehaviouralDataPattern = fullfile(behaviouralData, 'R*');
subjectsBehaviouralData = dir(subjectBehaviouralDataPattern);
% FOR TESTING, DELETE LATER
subjectsBrainstormDB = subjectsBrainstormDB([1:10, 12:end]);
subjectsBehaviouralData = subjectsBehaviouralData([1:10, 12:end]);

% specify brain regions of interest
ROIs = {'Brodmann', {'V1_exvivo L', 'V1_exvivo R', 'BA4a_exvivo L', 'BA4a_exvivo R', 'BA6_exvivo L', 'BA6_exvivo R'}};


for n = 1 : length(subjectsBrainstormDB)
    % declare current subject
    subjectName = subjectsBrainstormDB(n).name;
    % declare subject's acquisition files in brainstormdb
    acqBrainstormPattern = fullfile(brainstormdb, subjectName, '*resample_band', 'data*.mat');
    acquisitions = dir(acqBrainstormPattern);
	% now loop over each acquisition
    for acq = 1: length(acquisitions)
        % identify state directories for current acquisition
        dirNamePattern = strcat('game_', num2str(acq), '*');
        statesDirPattern = fullfile(brainstormdb, subjectName, dirNamePattern);
        statesDir = dir(statesDirPattern);
		% for each acquisition, loop over each state
        for state = 1:length(statesDir)
            % declare list of files for each state for this acq.
            statesFilePattern = fullfile(statesDir(state).folder, statesDir(state).name, 'data*');
            statesFilesStruct = dir(statesFilePattern);
			% identify head model file
			headFilePattern = fullfile(statesDir(state).folder, statesDir(state).name, 'results_MN*');
			headFileStruct = dir(headFilePattern);
			% create empty container for list of file names as string
            scoutFiles = cell(1,length(statesFilesStruct));
			for scout = 1:length(scoutFiles)
				fileNameStart = fullfile(subjectName, ...
										 statesDir(state).name, ...
										 headFileStruct.name);
				fileNameEnd = fullfile(subjectName, ...
									   statesDir(state).name, ...
									   statesFilesStruct(scout).name);
				fileName = strcat('link|', ...
								  fileNameStart, ...
								  '|', ...
								  fileNameEnd);	
				scoutFiles{scout} = fileName;
			end

		% Process: Scouts time series: V1_exvivo L V1_exvivo R
 		sFiles = bst_process('CallProcess', 'process_extract_scout', scoutFiles, [], ...
			'timewindow',     [0, 1.0], ...
			'scouts',         ROIs, ...
			'scoutfunc',      1, ...  % Mean
			'isflip',         0, ...
			'isnorm',         0, ...
			'concatenate',    0, ...
			'save',           1, ...
			'addrowcomment',  1, ...
			'addfilecomment', 1);
            
            % identify generated scout files
            scoutsFilePattern = fullfile(statesDir(state).folder, ...
                                         statesDir(state).name, ...
                                         'matrix*');
            scoutsDir = dir(scoutsFilePattern);        
            % create new container for the processed scouts
            scoutFiles = cell(1,length(statesFilesStruct));
            
			for scout = 1:length(scoutFiles)
                fileName = fullfile(subjectName, ...
                                    statesDir(state).name, ...
                                    scoutsDir(scout).name);
				scoutFiles{scout} = fileName;
			end
			
            % Process: Fourier transform (FFT)
             sFiles = bst_process('CallProcess', 'process_fft', scoutFiles, [], ...
                 'avgoutput', 0);
        end
    end
end


