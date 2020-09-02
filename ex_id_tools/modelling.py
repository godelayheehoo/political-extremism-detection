def reg_summary_table(vectorizer, estimator):
    '''
    Given a fitted tfidfvectorizer and binary classifier that supports feature_log_prob, returns a table summarizing
    the important features of the data, sorted per-class.
    :param vectorizer:
    An instance of an sklearn tf-idf vectorizer or similar
    :param estimator:
    A classifier that reports .feature_log_prob
    :return:
    a dataframe consisting of 8 columns.  The first four show the idf, feature name, and log-probability of that
    attribtue conditioned with class 0 or class 1, organized by log-probability with respect to class 1.  The second
    four do the same, but organized with respect to class 0.
    '''
    q = pd.concat([
        pd.DataFrame({'fn': vectorizer.get_feature_names(),
                      'given 0': estimator.feature_log_prob_[0]
                         , 'given 1': estimator.feature_log_prob_[1]}).sort_values(by='given 1').reset_index().drop(
            columns=['index']),

        pd.DataFrame({'fn': vectorizer.get_feature_names(), 'given 0': estimator.feature_log_prob_[0]
                         , 'given 1': estimator.feature_log_prob_[1]}).sort_values(by='given 0').reset_index().drop(
            columns=['index'])]
        , axis=1, keys=['sorted by 1', 'sorted by 0'])
    q[('sorted by 0', 'idf')] = q.loc[:, ('sorted by 0', 'fn')].apply(
        lambda word: vectorizer.idf_[(vectorizer.vocabulary_[word])])
    q[('sorted by 1', 'idf')] = q.loc[:, ('sorted by 1', 'fn')].apply(
        lambda word: vectorizer.idf_[(vectorizer.vocabulary_[word])])
    q = q[[('sorted by 1', 'idf'), ('sorted by 1', 'fn'), ('sorted by 1', 'given 0'), ('sorted by 1', 'given 1'),
           ('sorted by 0', 'idf'), ('sorted by 0', 'fn'), ('sorted by 0', 'given 0'), ('sorted by 0', 'given 1')]]

    return (q)

