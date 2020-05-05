from numpy import all, sum, where, argmax, percentile, abs, min, max, ndarray
from keras.models import Model
from model.layers.realtime_embedding import RealtimeEmbedding
from config import training_verbosity, batch_size


def rescale(values):
    tmp = values + min(values)
    return tmp / max(tmp)


def print_bits(values):
    print(
        percentile(values, 98),
        percentile(values, 97),
        percentile(values, 95),
        percentile(values, 90),
        percentile(values, 80),
        percentile(values, 70)
    )


def train_deep_learner(model, current_labels, data_source, rounds=2, training_documents=250000, min_confidence=.985,
                       label_modifier=.4):
    """
    Performs X rounds of training on deep network to learn from then update the current labels
    :param Model model: Keras model to be trained
    :param ndarray current_labels: Current set of document labels
    :param RealtimeEmbedding data_source: Array of documents with each token enumerated corresponding to word embeddings
    :param int rounds: Number of reinforcement-training rounds [default 3]
    :param int training_documents: Number of epochs in each reinforcement-training round [default 3]
    :param float min_confidence: Min predicted value for document to *contain intent* [default .985]
    :param float label_modifier: Modifier applied to current labels [default .4]
    :return model, current labels, new_predictions
    """
    positive_threshold = min_confidence
    negative_threshold = (1 - min_confidence)

    current_labels = current_labels.copy()
    predictions = None

    for round_number in range(rounds):
        data_source.update_labels(current_labels)

        # Get subset of non uncertain data to use for training
        training_mask = current_labels != .5    # Only use labels that are not *uncertain*
        data_source.set_mask(training_mask)

        # Compute constants for the round
        steps_per = int(training_documents / batch_size)

        # Train model
        data_source.set_usage_mode(True)
        model.fit_generator(data_source, verbose=training_verbosity, steps_per_epoch=steps_per, shuffle=True)

        # Make predictions for all documents
        data_source.set_usage_mode(False)
        predictions = model.predict_generator(data_source, verbose=training_verbosity)\
            .reshape(-1)

        # Limit prediction values to [0, 1]
        bounded_predictions = predictions.copy()
        bounded_predictions[bounded_predictions < 0] = 0
        bounded_predictions[bounded_predictions > 1] = 1
        print_bits(bounded_predictions)

        # Compute mask of documents with positive and negative intent
        new_positives = bounded_predictions > positive_threshold
        new_negatives = bounded_predictions < negative_threshold

        # Apply confidence modifications to new labels
        current_labels[new_positives] += label_modifier
        current_labels[new_negatives] -= label_modifier

        # Restrict label value range to [0, 1]
        current_labels[current_labels < 0] = 0
        current_labels[current_labels > 1] = 1

        print(sum(new_positives) + sum(new_negatives), 'classified in deep training round', round_number + 1)

    return model, current_labels, predictions