from numpy import all, asarray, logical_not, ndarray, any, abs
from config import confidence_increment

midpoint = 0.5


def get_consensus(current_labels, *label_deltas):
    """
    Ensures consensus between label sources and produces new array of labels

    :param ndarray current_labels: Current array of labels
    :param ndarray label_deltas: Array of label changes from each learner
    :return ndarray: New array of labels with changes applied
    """
    if len(label_deltas) < 1:
        raise AttributeError('No labels provided to get consensus.')
    elif len(label_deltas) < 2:
        ResourceWarning('Only provided a single list of labels, so consensus has no function.')
        return label_deltas[0]

    # Get mask of documents with requested shifts
    label_deltas = asarray([label_set - current_labels for label_set in label_deltas])

    positive_shift = any(label_deltas > 0, axis=0)
    negative_shift = any(label_deltas < 0, axis=0)

    # Checks whether a document has both a positive and negative shift
    non_solid = abs(midpoint - current_labels) < midpoint
    no_conflict = logical_not(
        all([positive_shift, negative_shift], axis=0)
    )

    # Gets mask of documents to be shifted positive and negatively (only if there is no conflict)
    positive = all([non_solid, no_conflict, positive_shift], axis=0)
    negative = all([non_solid, no_conflict, negative_shift], axis=0)

    # Apply shift in labels (based on confidence)
    current_labels = current_labels.copy()
    current_labels[positive] += confidence_increment
    current_labels[negative] -= confidence_increment

    # Bound labels to [0, 1]
    current_labels[current_labels < 0] = 0
    current_labels[current_labels > 1] = 1

    return current_labels
