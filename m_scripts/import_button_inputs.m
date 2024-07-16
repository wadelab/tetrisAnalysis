% project directory
dataDir = '/scratch/groups/Projects/P1454/brainstormdb/Tetris/data';
% get list of subjects in brainstorm database
subjectsBrainstormPattern = fullfile(dataDir, 'R*');
subjectsBrainstormDB = dir(subjectsBrainstormPattern);
% delete later
subjectsBrainstormDB = subjectsBrainstormDB([1:10, 12:14]);


for n = 1 : length(subjectsBrainstormDB)
	% declare current subject name
    subjectName = subjectsBrainstormDB(n).name;
	
    acqBrainstormPattern = fullfile(dataDir, subjectName, '*resample_band', 'data*.mat');
    acquisitions = dir(acqBrainstormPattern);
	% set directory names to move .mat files to
	leftDirName = 'left_button_inputs'; 
	rightDirName = 'right_button_inputs';
	for acq = 1 : length(acquisitions)
		% declare acquisition to be worked on
		acqFileName = fullfile(acquisitions(acq).folder, acquisitions(acq).name);
		acqFileName = extractAfter(acqFileName, 'data');
		sFiles = {acqFileName};

		% import left button inputs
		sEventFiles = bst_process('CallProcess', 'process_import_data_event', sFiles, [], ...
			'subjectname', subjectName, ...
			'condition',   '2', ...
			'eventname',   '2', ...
			'timewindow',  [0, 1000], ...
			'epochtime',   [-0.4, 0.4], ...
			'createcond',  1, ...
			'ignoreshort', 1, ...
			'usectfcomp',  1, ...
			'usessp',      1, ...
			'freq',        [], ...
			'baseline',    []);

		% identify directory for imported left button inputs (trigger '2') 
		leftButtonPattern = fullfile(subjectsBrainstormDB(n).folder, subjectsBrainstormDB(n).name, '2');
		leftButtonDataDir = dir(fullfile(leftButtonPattern, 'data*'));
		leftButtonChannelDir = dir(fullfile(leftButtonPattern, 'channel*'));
		% now iterate over data files and move them
		leftFiles = cell(1,length(leftButtonDataDir));
		for i = 1 : length(leftButtonDataDir)
			fileName = fullfile(leftButtonDataDir(i).folder, leftButtonDataDir(i).name);
			fileName = extractAfter(fileName, 'data');
			leftFiles{i} = fileName;
		end
		% now move files to new directory
		leftFiles = bst_process('CallProcess', 'process_movefile', leftFiles, [], ...
			'subjectname', subjectName, ...
			'folder',      leftDirName);

		% now import right button inputs
		sEventFiles = bst_process('CallProcess', 'process_import_data_event', sFiles, [], ...
			'subjectname', subjectName, ...
			'condition',   '4', ...
			'eventname',   '4', ...
			'timewindow',  [0, 1000], ...
			'epochtime',   [-0.4, 0.4], ...
			'createcond',  1, ...
			'ignoreshort', 1, ...
			'usectfcomp',  1, ...
			'usessp',      1, ...
			'freq',        [], ...
			'baseline',    []);

		% identify directory for imported right button inputs (trigger '4') 
		rightButtonPattern = fullfile(subjectsBrainstormDB(n).folder, subjectsBrainstormDB(n).name, '4');
		rightButtonDataDir = dir(fullfile(rightButtonPattern, 'data*'));
		rightButtonChannelDir = dir(fullfile(rightButtonPattern, 'channel*'));
		% now iterate over data files and move them
		rightFiles = cell(1,length(rightButtonDataDir));
		for i = 1 : length(rightButtonDataDir)
			fileName = fullfile(rightButtonDataDir(i).folder, rightButtonDataDir(i).name);
			fileName = extractAfter(fileName, 'data');
			rightFiles{i} = fileName;
		end
		% now move files to new directory
		rightFiles = bst_process('CallProcess', 'process_movefile', rightFiles, [], ...
			'subjectname', subjectName, ...
			'folder',      rightDirName);
	end
	% now move over the channel file
	ChannelPath = fullfile(leftButtonChannelDir.folder, leftButtonChannelDir.name);
	leftChannelFilePath = fullfile(subjectsBrainstormDB(n).folder, subjectsBrainstormDB(n).name, leftDirName);
	copyfile(ChannelPath, leftChannelFilePath);
	% copy it to the right button inputs folder too
	rightChannelFilePath = fullfile(subjectsBrainstormDB(n).folder, subjectsBrainstormDB(n).name, rightDirName);
	copyfile(ChannelPath, rightChannelFilePath);
end

