

clc; clear all; close all;

% mvgc params
regmode   = 'OLS';                   % VAR model estimation regression mode ('OLS', 'LWR' or empty for default)
icregmode = 'LWR';                   % information criteria regression mode ('OLS', 'LWR' or empty for default)
morder    = 'BIC';                   % model order to use ('actual', 'AIC', 'BIC' or supplied numerical value)
momax     = 20;                      % maximum model order for model order estimation
tstat     = 'F';                     % statistical test for MVGC:  'chi2' for Geweke's chi2 test (default) or'F' for Granger's F-test
alpha     = 0.05;                    % significance level for significance test
mhtc      = 'Bonferroni';            % multiple hypothesis test correction (see routine 'significance')
seed      = 0;                       % random seed (0 for unseeded)

% other params
phase = "normal";                                   % normal trials, phase = 2 attack trials
nROIs = 11;                                         % number of regions of interests
myFiles = dir(char('procData/'+phase+'/*mat'));     % read .mat files from dir
nFiles = size(myFiles,2);                           % total number of subjects/files
outpath = 'ecoutput/';                              % dir path for storing the output files
fval_all = zeros(nROIs, nROIs, nFiles);             % placeholder to store fvals
pval_all = zeros(nROIs, nROIs, nFiles);             % placeholder to store pvals
sig_all = zeros(nROIs, nROIs, nFiles);              % placeholder to store sig
cd_all = zeros(nFiles);                             % placeholder to store causal density

%% Prepare the data, and callmvgc EC function
for i = 1:length(myFiles)
    indata = load(string(myFiles(i).folder)+'/'+string(myFiles(i).name));
    data = indata.pdata;        % get the data from the variable
    fileSize=size(data);
    disp('Processing file: '+phase+'/'+string(myFiles(i).name));
    disp(fileSize);
    
    nTrials   = indata.nTrials;                      % number of trials
    nobs      = round(fileSize(1)/nTrials);          % number of observations per trial
    disp(nTrials);
    
    % Normalization and Trasform ROIs to GC-HRF
    for roi = 1:nROIs
        HRF(roi,:) = (data(:,roi)-mean(data(:,roi)))/std(data(:,roi));
    end
    
    % get EC using function
    [fval,pval,sig,cd] = mvgcec(HRF, nTrials, nobs, regmode, icregmode, morder, momax, tstat, alpha, mhtc, seed);
    fval_all(:,:,i) = fval;
    pval_all(:,:,i) = pval;
    sig_all(:,:,i) = sig;
    cd_all(i) = cd;
    
    clear HRF
end

save(phase+'.mat','fval_all','pval_all','sig_all','cd_all');


% function to calculate Effective connectivity using MVGC toolbox
function [fval,pval,sig,cd] = mvgcec(X, ntrials, nobs, regmode, icregmode, morder, momax, tstat, alpha, mhtc, seed)
    p = 6;
    [AT] = tsdata_to_var(X,p,regmode);
    nvars = size(AT,1); % number of variables
   
    % Calculate information criteria up to max model order
    ptic('\n*** tsdata_to_infocrit\n');
    [AIC,BIC] = tsdata_to_infocrit(X,momax,icregmode);
    ptoc('*** tsdata_to_infocrit took ');
    [~,bmo_AIC] = min(AIC);
    [~,bmo_BIC] = min(BIC);

    amo = size(AT,3); % actual model order

    % Select model order
    if     strcmpi(morder,'actual')
        morder = amo;
    elseif strcmpi(morder,'AIC')
        morder = bmo_AIC;
    elseif strcmpi(morder,'BIC')
        morder = bmo_BIC;
    else
    end

    % Granger causality estimation
    % Calculate time-domain pairwise-conditional causalities. Return VAR parameters so we can check VAR.
    ptic('\n*** GCCA_tsdata_to_pwcgc... ');
    [F,A,SIG] = GCCA_tsdata_to_pwcgc(X,morder,regmode); % use same model order for reduced as for full regressions
    ptoc;
    % Check for failed (full) regression
    assert(~isbad(A),'VAR estimation failed');
    % Check for failed GC calculation
    assert(~isbad(F,false),'GC calculation failed');
    % Check VAR parameters (but don't bail out on error - GCCA mode is quite forgiving!)
    rho = var_specrad(A);
    fprintf('\nspectral radius = %f\n',rho);
    if rho >= 1,       fprintf(2,'WARNING: unstable VAR (unit root)\n'); end
    if ~isposdef(SIG), fprintf(2,'WARNING: residuals covariance matrix not positive-definite\n'); end

    % Significance test using theoretical null distribution, adjusting for multiple hypotheses.
    pval = mvgc_pval(F,morder,nobs,ntrials,1,1,nvars-2,tstat);  % calculate p-value
    sig  = significance(pval,alpha,mhtc);     % calculate significance 0 or 1, significance(pval,alpha,correction)
    fval = F;        

    % Causal Density
    cd = mean(F(~isnan(F)));
end



