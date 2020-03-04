from utilities.data_management import move_to_root, make_path, open_w_pandas, check_existence

move_to_root()

base = make_path('data/prepared_data/')
original_path = base / 'wikipedia_corpus.csv'
reduced_path = base / 'wikipedia_corpus_reduced.csv'

num_documents = 100000
modifiers = ['', '_partial']

check_existence(original_path)
print('Config complete.')

for modifier in modifiers:
    data = open_w_pandas(base / ('wikipedia_corpus' + modifier + '.csv'))
    print('Loaded ' + modifier + ' data.')

    data = data.sample(num_documents).reset_index(drop=True)
    print('Sampled data.')

    data.to_csv(base / ('wikipedia_corpus_reduced' + modifier + '.csv'))
    print('Saved data.')