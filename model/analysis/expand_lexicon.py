from utilities.analysis import svd_embeddings, get_nearest_neighbours
from scipy.cluster.vq import whiten, kmeans
from scipy.linalg import norm
from scipy.spatial.distance import euclidean
from numpy import percentile, argmin
from nltk.corpus import wordnet

x_key, y_key = 'euclidean_distances', 'cosine_distances'


def cluster_neighbours(neighbours, refined=False, target=None):
    """ Calculate the cluster of embeddings around a given word """
    # Normalize data
    neighbours = neighbours.iloc[1:]
    normed_data = whiten(neighbours[[x_key, y_key]].values)

    # Threshold data
    e_distances = normed_data[:, 0]
    threshold = percentile(e_distances, 20)
    normed_data = normed_data[e_distances < threshold]

    # Cluster
    distortion = 2
    num_centroids = 1
    while distortion > (.25 if refined else 1):
        num_centroids += 1
        centroids, distortion = kmeans(normed_data, num_centroids)

    # Split data by centroid
    target_index = argmin([norm(centroid) for centroid in centroids])
    term_indexes = [
        ind + 1 for ind, point in enumerate(normed_data)
        if argmin([euclidean(centroid, point) for centroid in centroids]) == target_index
    ]

    close_bois = neighbours.iloc[term_indexes]
    if target is not None:
        close_bois['dist'] = close_bois.iloc[:, 1:-3].apply(lambda doc: euclidean(target, doc), axis=1)

    return list(neighbours['words'].iloc[term_indexes].values), close_bois[['words', 'euclidean_distances', 'cosine_distances', 'dist']]


def wordnet_expansion(lexicon, n_words=None):
    """ Expand lexicon using wordnet """
    if n_words is None:
        n_words = 5

    looker = wordnet.synsets
    expanded_lexicon = [
        [str(synonym.lemmas()[0].name()) for synonym in looker(word)[:n_words]]
        for word in lexicon
    ]

    return expanded_lexicon


def embedding_expansion(lexicon, embeddings, simple_expand=None):
    """
    Expand lexicon using trained word embeddings
    :param lexicon: List of word embeddings
    :param embeddings: Pandas DataFrame of words and their embeddings
    :param simple_expand: Specify number of terms to take 'blindly' from around the target word, (default, don't use)
    :return: List of words in the expanded lexicon
    """
    # Normalize embeddings and expand lexicon
    embeddings = svd_embeddings(embeddings)
    if not simple_expand:
        expanded_lexicon = [
            cluster_neighbours(
                get_nearest_neighbours(embeddings, word)[0]
            )
            for word in lexicon
        ]
    else:
        expanded_lexicon = []
        for ind, word in enumerate(lexicon):
            new_terms = get_nearest_neighbours(embeddings, word, n_words=(simple_expand + 1))[0]

            if len(new_terms) < 1:
                continue

            new_terms = new_terms['words'].values[1:]
            expanded_lexicon.append(new_terms)

            print('Adding', new_terms, ' - ', round((ind + 1) / len(lexicon) * 10000) / 100, '% complete')

    return expanded_lexicon


def expand_lexicon(lexicon, embeddings=None, simple_expand=None):
    """ Expand lexicon using either wordnet expansion or word embeddings """
    if embeddings is None:
        return wordnet_expansion(lexicon, simple_expand)
    else:
        return embedding_expansion(lexicon, embeddings, simple_expand)
