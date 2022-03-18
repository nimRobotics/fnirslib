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


%% Prepare the data, and callmvgc EC function
nROIs = 3;                                         % number of regions of interests
indata = load('attack.mat');
% indata = load('normal.mat');

data = indata.pdata;        % get the data from the variable
fileSize=size(data);
disp(fileSize);

% nTrials   = indata.nTrials;                      % number of trials
nTrials = 5;
nobs = round(fileSize(1)/nTrials);          % number of observations per trial
disp(nTrials);

% Normalization and Trasform ROIs to GC-HRF
for roi = 1:nROIs
    HRF(roi,:) = (data(:,roi)-mean(data(:,roi)))/std(data(:,roi));
end

% get EC using function
[fval,pval,sig,cd] = mvgcec(HRF, nTrials, nobs, regmode, icregmode, morder, momax, tstat, alpha, mhtc, seed);

save('attack_.mat','fval','pval','sig','cd');
% save('normal_.mat','fval','pval','sig','cd');



% function to calculate Effective connectivity using MVGC toolbox
function [fval,pval,sig,cd] = mvgcec(X, ntrials, nobs, regmode, icregmode, morder, momax, tstat, alpha, mhtc, seed)
    p = 6; %  model order (number of lags)
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



