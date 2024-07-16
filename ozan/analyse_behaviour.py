#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from modules import *
from statistics import *
from features import *

import pingouin as pg
import json

with open('params.json') as file:
    params = json.load(file)

# output directories
HMM_DIR = params['hmm_dir']
FIG_DIR = params['fig_dir']
BEHAVIOUR_DIR = params['behaviour_dir']

# preprocessing params
PARTICIPANTS = params['participants']
IGNORE_PARTICIPANTS = params['participants_to_ignore']
IGNORE_FEATURES = summary_features + game_state_features
DF_FILE_NAME = params['preprocessed_dataframe_output_name']

# analysis config
N_STATES = params['n_states']
N_MODEL_FITS = params['n_model_fits']
SECONDS_PER_EPOCH = params['seconds_per_epoch']
PCA_LABELS = params['pca_component_labels']
COMPONENTS = params['components']
Z_COMPONENTS = params['z_components']

# initialise selected visualisation parameters
sns_styleset()
np.set_printoptions(suppress=True)

# run pca on lindstedt data for feature engineering if not already done
if not os.path.isfile(os.path.join(BEHAVIOUR_DIR, 'pca.pkl')):
    loadings, pca = princomp(file_name='lindstedt_archival_episodes.tsv', 
                             features_to_drop=IGNORE_FEATURES,
                             input_path=BEHAVIOUR_DIR,
                             n_components=4, 
                             cutoff=0.2,
                             display_loadings=True)


# if behavioural data has been preprocessed, read the dataframe
df_path = os.path.join(BEHAVIOUR_DIR, DF_FILE_NAME)
if os.path.isfile(df_path):
    df = pd.read_csv(df_path)
# otherwise preprocess it
else:
    df = preprocess_all_episodes_files(features_to_drop=IGNORE_FEATURES, 
                                       components=COMPONENTS,
                                       component_labels=PCA_LABELS,
                                       participants_to_ignore=IGNORE_PARTICIPANT,
                                       input_path=BEHAVIOUR_DIR)
# plot distributions of our observations 
print('histograms of component scores across all states and episodes')
freq_distributions_global_component_scores(
        df=df,
        components=COMPONENTS,
        standardised=False,
        fig_dir=FIG_DIR)

freq_distributions_global_component_scores(
        df=df,
        components=COMPONENTS,
        standardised=True,
        fig_dir=FIG_DIR)

print('histograms of component scores across all states and episodes - this time a multiplot')
multiplot_freq_distributions_global_component_scores(
        df=df,
        components=COMPONENTS,
        standardised=False,
        fig_dir=FIG_DIR)

multiplot_freq_distributions_global_component_scores(
        df=df,
        components=COMPONENTS,
        standardised=True,
        fig_dir=FIG_DIR)


model_dir = os.path.join(HMM_DIR, f'{N_STATES}_state_{len(COMPONENTS)}_component_HMM')
if os.path.isdir(model_dir):
    MODEL, POST_PROB, X, LL = load_pickled_HMM(
            HMM_dir=HMM_DIR,
            model_dir=model_dir,
            group_model=True,
            n_states=N_STATES,
            components=COMPONENTS,
            nth_fit=1,
            null_model=False
            )



# otherwise generate them
else:
    models, post_probs, Xs, LLs, start_probs = [], [], [], [], []
    for i in range(1, N_MODEL_FITS+1):
        MODEL, POST_PROB, X, LL, START_PROB =  fit_group_HMM(
                                                    df=df,
                                                    n_states=N_STATES,
                                                    components=list(Z_COMPONENTS.keys()),
                                                    component_labels=Z_COMPONENTS,
                                                    n_iter=200,
                                                    verbose=True,
                                                    covar_type='diag',
                                                    null_model=False,
                                                    nth_fit=i,
                                                    model_dir=HMM_DIR)
        models += [MODEL]
        post_probs += [POST_PROB]
        Xs += [X]
        LLs += [LL]
        start_probs += [START_PROB]


# now fit the chance model
NULL_MODEL, NULL_POST_PROB, NULL_X, NULL_LL, NULL_START_PROB = fit_group_HMM(df, 
                                        n_states=N_STATES, 
                                        components=list(Z_COMPONENTS.keys()), 
                                        component_labels=Z_COMPONENTS, 
                                        n_iter=200, 
                                        verbose=True, 
                                        covar_type='diag', 
                                        null_model=True,
                                        nth_fit=1,
                                        model_dir=HMM_DIR)


# load the model with the best fit


# get list of most likely states using viterbi algorithm
HMM_states_list = MODEL.decode(X)[1].tolist()
null_HMM_states_list = NULL_MODEL.decode(X)[1].tolist()
# append to dataframe
df['HMM_state'] = np.array(HMM_states_list)+1
df['null_HMM_state'] = np.array(null_HMM_states_list)+1

# produce descriptive plots of each behavioural state
boxplot_state_component_scores(
                df=df,
                components=Z_COMPONENTS,
                n_states=N_STATES,
                violin=False,
                fig_dir=FIG_DIR)

boxplot_state_component_scores(
                df=df,
                components=Z_COMPONENTS,
                n_states=N_STATES,
                violin=True,
                fig_dir=FIG_DIR)

# same for null model
boxplot_state_component_scores(
                df=df,
                components=COMPONENTS,
                n_states=N_STATES,
                null_model=True,
                violin=False,
                fig_dir=FIG_DIR)

boxplot_state_component_scores(
                df=df,
                components=COMPONENTS,
                n_states=N_STATES,
                null_model=True,
                violin=True,
                fig_dir=FIG_DIR)

# visualise histograms of scores for each component across each state
freq_distributions_component_scores_across_states(
        df=df,
        components=Z_COMPONENTS,
        n_states=N_STATES,
        fig_dir=FIG_DIR)
    
# same for null model
freq_distributions_component_scores_across_states(
        df=df,
        components=COMPONENTS,
        n_states=N_STATES,
        null_model=True,
        fig_dir=FIG_DIR)

# plot transition matrix of the model
plot_transition_matrix(
        model=MODEL,
        components=COMPONENTS,
        n_states=N_STATES,
        null_model=False,
        fig_dir=FIG_DIR)

# same for null model 
plot_transition_matrix(
        model=NULL_MODEL,
        components=COMPONENTS,
        n_states=N_STATES,
        null_model=True,
        fig_dir=FIG_DIR)

# plot histogram of maximum fractional occupancies
histogram_max_frac_occ(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        fig_dir=FIG_DIR)

# plot bar chart of state fractional occupancies
bar_chart_of_fractional_occupancies(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=False,
        cmap='tab10',
        fig_dir=FIG_DIR)

# same for null model 
bar_chart_of_fractional_occupancies(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=True,
        cmap='tab10',
        fig_dir=FIG_DIR)

# plot bar chart of sum total line clears across states
bar_chart_of_lines_cleared_across_states(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=False,
        cmap='tab10',
        fig_dir=FIG_DIR)

# same for null model
bar_chart_of_lines_cleared_across_states(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=True,
        cmap='tab10',
        fig_dir=FIG_DIR)

# produce visualisation of state sequence and observations for each game
for participant in PARTICIPANTS:
    n_games = df[df['SID'] == participant]['game_number'].nunique()
    for game_number in range(1, n_games+1):
        print(f'plotting state sequence and observations for participant {participant} game {game_number}')
        viz_states(df, 
                   n_states=N_STATES,
                   post_prob=POST_PROB,
                   components=list(Z_COMPONENTS.keys()), 
                   component_labels=Z_COMPONENTS, 
                   player_id=participant,
                   nth_game=game_number,
                   show_plot=False,
                   null_model=False,
                   cmap='tab10', 
                   fig_dir=FIG_DIR)


# generate .csv files containing state epochs and timestamps to import to brainstorm
generate_all_state_timestamps(
        preprocessed_eps=df,
        participants_to_ignore=IGNORE_PARTICIPANTS,
        slice_length=SECONDS_PER_EPOCH,
        null_model=False,
        input_path=BEHAVIOUR_DIR)

# same for null model
generate_all_state_timestamps(
        preprocessed_eps=df,
        participants_to_ignore=IGNORE_PARTICIPANTS,
        slice_length=SECONDS_PER_EPOCH,
        null_model=True,
        input_path=BEHAVIOUR_DIR)


# test difference in line clears between states
lines_df = df.groupby(['SID', 'HMM_state'])['cleared'].sum().reset_index()

lines_aov = pg.rm_anova(
        data=lines_df,
        dv='cleared',
        within='HMM_state',
        subject='SID',
        detailed=True)

print('---\n RM-ANOVA lines cleared between states\n---')
print(lines_aov)

# run pairwise tests lines cleared between states
lines_posthoc = pg.pairwise_tests(
        data=lines_df,
        dv='cleared',
        within='HMM_state',
        subject='SID',
        alpha=0.05,
        padjust='holm',
        effsize='cohen')

print('---\nposthoc tests for lines cleared between states\n---')
print(lines_posthoc)
        
# compute percentage of drops in State 2 that result in line clears
state_2 = df[df['HMM_state'] == 2]
state_2_clears = state_2[state_2['cleared'] > 0]
state_2_no_clears = state_2[state_2['cleared'] == 0]
perc_state_2_clears = np.round(len(state_2_clears) / len(state_2) * 100)
print(f"{perc_state_2_clears}% of drops in State 2 resulted in at least 1 line clear")



frac_occ = fractional_occupancy_at_each_game(df=df, n_states=N_STATES, state=3)
