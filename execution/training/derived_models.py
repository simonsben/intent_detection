from utilities.data_management import open_w_pandas, make_path, check_existence, check_writable, save_prepared, \
    move_to_root
from model.extraction import n_gram_matrix, othering_matrix
from model.training import train_xg_boost
from numpy import save, array

move_to_root()

# Define source files
data_base = make_path('data/prepared_data/')
pre_filename = data_base / '24k-abusive-tweets.csv'
partial_filename = data_base / '24k-abusive-tweets_partial.csv'
lexicon_path = make_path('data/prepared_lexicon/nrc_emotion_lexicon.csv')
dataset_name = pre_filename.stem
processed_base = make_path('data/processed_data/') / dataset_name / 'derived'
model_dir = make_path('data/models/' + dataset_name + '/derived/')

# Check files
check_existence(pre_filename)
check_existence(partial_filename)
check_existence(lexicon_path)
check_writable(processed_base)
check_writable(model_dir)

# Load dataset
pre_dataset = open_w_pandas(pre_filename)
partial_dataset = open_w_pandas(partial_filename)
print('Data loaded.')

sub_layers = [
    {
        'model_name': 'othering',
        'executor': othering_matrix,
        'dataset': partial_dataset
    },
    {
        'model_name': 'word_n_grams',
        'executor': n_gram_matrix,
        'dataset': pre_dataset
    },
    {
        'model_name': 'char_n_grams',
        'executor': lambda doc: n_gram_matrix(doc, 5000, False),
        'dataset': pre_dataset
    }
]

for layer in sub_layers:
    model_filename = model_dir / (layer['model_name'] + '.bin')
    if model_filename.exists():
        print('Skipping', layer['model_name'])
        continue

    model_name = layer['model_name']
    print('Starting', model_name)

    # Train model
    document_matrix = layer['executor'](layer['dataset'])
    model, (train, test) \
        = train_xg_boost(document_matrix, layer['dataset']['is_abusive'], return_data=True)

    # Save model
    model.save_model(str(model_filename))
    save_prepared(processed_base, model_name, train[0], test[0])
    save(processed_base / (model_name + '_terms.npy'), array(document_matrix.columns))
    print(layer['model_name'], 'completed.')