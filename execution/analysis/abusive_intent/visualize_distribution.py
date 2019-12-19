from utilities.data_management import read_csv, move_to_root, make_path, load_execution_params
from utilities.plotting import scatter_plot, show, hist_plot

move_to_root(4)
params = load_execution_params()

base = make_path('data/processed_data/') / params['dataset'] / 'analysis'
analysis_base = base / 'intent_abuse'

intent = read_csv(analysis_base / 'intent_predictions.csv', header=None)[0].values
abuse = read_csv(analysis_base / 'abuse_predictions.csv', header=None)[0].values
# contexts = read_csv(base / 'intent' / 'contexts.csv')['contexts'].values

abuse = abuse[:intent.shape[0]]

scatter_plot((abuse, intent), 'Intent vs abuse predictions', size=10)

ax_titles = ('Predicted abuse', 'Predicted intent')
hist_plot([abuse, intent], 'Prediction comparison histogram', ax_titles=ax_titles, c_bar_title='Document density')

hist_plot(abuse, 'Abuse histogram')
hist_plot(intent, 'Intent histogram')

show()