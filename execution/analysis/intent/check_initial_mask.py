from utilities.data_management import make_path, load_vector, open_w_pandas
from numpy.random import choice
from numpy import sum, where
import config

base = make_path('data/processed_data/') / config.dataset / 'analysis' / 'intent'

initial_mask = load_vector(base / 'intent_mask.csv')
contexts = open_w_pandas(base / 'contexts.csv')['contexts'].values
print('Content loaded.')

non_neutral = initial_mask != .5
non_neutral_mask = initial_mask[non_neutral].astype(bool)
non_neutral_contexts = contexts[non_neutral]

indexes = choice(sum(non_neutral), 50, replace=False).astype(int)
print('Computed sub mask')

for index in where(non_neutral_mask[indexes])[0]:
    print(index, non_neutral_mask[index], non_neutral_contexts[index])
