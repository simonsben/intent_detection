from numpy import argsort, all, logical_not, zeros_like, sum, zeros, ndarray, flip, abs, asarray
from scipy.sparse import csc_matrix

midpoint = 0.5


def get_max_moves(current_labels):
    """
    Compute the maximum movement based on the current labels. Allow half the percentage that is already certain

    :param ndarray current_labels: Array of current labels
    :return tuple[int,int]: Max moves for positive and negative labels
    """
    num_positive = sum(current_labels == 1)
    num_negative = sum(current_labels == 0)

    return num_positive, num_negative


def deep_rate_limit(predictions, current_labels, threshold):
    """
    Computes the contexts that should be incremented while only making a finite number of changes

    :param ndarray predictions: Array of predictions from the deep learner
    :param ndarray current_labels: Array containing the current labels being used in training
    :param float threshold: Threshold value that predictions must pass to have their label changed
    """
    certain_positives = current_labels == 1
    max_positive, max_negative = get_max_moves(current_labels)

    neg_threshold = (1 - threshold) * 2

    new_positives = all([predictions > threshold, logical_not(certain_positives)], axis=0)

    if sum(new_positives) > max_positive:
        sorted_indexes = flip(argsort(predictions))
        new_positives = zeros_like(new_positives, dtype=bool)

        new_positives[sorted_indexes[:max_positive]] = True

    certain_negatives = current_labels == 0
    new_negatives = all([predictions < neg_threshold, logical_not(certain_negatives)], axis=0)

    if sum(new_negatives) > max_negative:
        sorted_indexes = argsort(predictions)
        new_negatives = zeros_like(new_negatives, dtype=bool)

        new_negatives[sorted_indexes[:max_negative]] = True

    return new_positives, new_negatives


def term_rate_limit(positive_matrix, negative_matrix, current_labels):
    """
    Compute the contexts that should be incremented positively and negatively within a fixed number of changes

    :param csc_matrix positive_matrix: A CSC matrix with the potential positive sequences
    :param csc_matrix negative_matrix: A CSC matrix with the potential negative sequences
    :param ndarray current_labels: Array of current labels
    :return tuple[ndarray, ndarray, int, int]
    """
    max_positive, max_negative = get_max_moves(current_labels)

    new_positive, positive_index = compute_context_sums(positive_matrix, max_positive)
    new_negative, negative_index = compute_context_sums(negative_matrix, max_negative)

    return new_positive, new_negative, positive_index, negative_index


def compute_context_sums(matrix, max_moves):
    """
    Determines the contexts that will be incremented this training round

    :param csc_matrix matrix: Sparse sequence context column matrix
    :param int max_moves: Maximum number of contexts that can be *changed* in the round
    """
    if not isinstance(matrix, csc_matrix):
        raise TypeError('Passed matrix must be a CSC matrix')

    contains_sequence = asarray(matrix.sum(axis=1)).reshape(-1) > 0
    if sum(contains_sequence) <= max_moves:
        return contains_sequence > 0, matrix.shape[1]

    num_contexts = matrix.shape[0]
    context_sums = zeros(num_contexts, dtype=int)
    for feature_index in range(matrix.shape[1]):
        data_slice = matrix[:, feature_index]
        context_sums[data_slice.indices] += data_slice.data

        if sum(context_sums > 0) > max_moves:
            return context_sums > 0, feature_index

    raise RuntimeError('Loop should have terminated. Error in stopping condition.')
