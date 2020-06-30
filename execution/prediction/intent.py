from model.networks import generate_intent_network
from utilities.data_management import make_path, check_existence, get_embedding_path, get_model_path, open_w_pandas, \
    make_dir, vector_to_file, get_prediction_path
from utilities.data_management.model_management import load_model_weights
from utilities.pre_processing import runtime_clean
from fasttext import load_model
from model.layers.realtime_embedding import RealtimeEmbedding
from config import dataset, max_tokens, embedding_dimension, execute_verbosity

prediction_path = get_prediction_path('intent')
contexts_path = make_path('data/processed_data') / dataset / 'analysis' / 'intent' / 'contexts.csv'
weights_path = get_model_path('intent')
embeddings_path = get_embedding_path()

# Ensure paths are correct
check_existence([weights_path, contexts_path, embeddings_path])
make_dir(prediction_path)
print('Config complete.')

# Generate model and load weights
model = generate_intent_network(max_tokens, embedding_dimension=embedding_dimension)
load_model_weights(model, weights_path)
print('Model loaded.')

# Load data and embedding model
data_source = runtime_clean(open_w_pandas(contexts_path)['contexts'].values)
embeddings = load_model(str(embeddings_path))
embedded_data = RealtimeEmbedding(embeddings, data_source, uniform_weights=True)
print('Data loaded.')

predictions = model.predict_generator(embedded_data, verbose=execute_verbosity)
vector_to_file(predictions, prediction_path)
print('Predictions saved.')
