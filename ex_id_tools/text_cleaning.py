import pandas as pd
import nltk

ENGLISH_STOPWORDS=set(nltk.corpus.stopwords.words('english'))
NON_ENGLISH_STOPWORDS=set(nltk.corpus.stopwords.words())-ENGLISH_STOPWORDS
ENGLISH_STOPWORDS=set(map(lambda r: r.replace("'",""),ENGLISH_STOPWORDS))
NON_ENGLISH_STOPWORDS=set(map(lambda r: r.replace("'",""),NON_ENGLISH_STOPWORDS))
#These are cached as sets now to speed up repeated function evaluations that use them.
#We strip apostrophes as they should be out of our data by this point.

from nltk.tokenize import RegexpTokenizer
reddit_tokenizer=RegexpTokenizer(r'http[s]*[:]*[\w_/]+|www[\w/_]+|[ur]/[\w]+|[a-z]{2,}')


regex_store={#Note, raw strings are used throughout here even where not needed.
    r'/clean':r'(?<![^\s])/(?=[ur]/[\w]+)',
#regex expression that looks for anything beginning with /letter/ and drops the first /.
# A character immediately prior prior to the first / must be some kind of spacer, to avoid
#messing with urls etc.
    r'tokenizer':r'http[s]*[:]*[\w_/]+|www[\w/_]|[ur]/[\w]+|[a-z0-9]{2,}',
#initial tokenizer, looks for websites, internal reddit links, or words of length greater than 1.  We assume lower-casing
#has already occurred.
    r'url_start':r'http[s]*[:]*[\w_/]+|www[\w/_]+',
    r'repetitions_in':r'(\w{1,3}\w{0,3})\1{3,}',
    r'repetitions_out': r'\g<1>\g<1>',
    r'html_tag_like_in':r'lt(\w*)gt',
    r'html_taglike_out':r'\g<1>',
    r'html_entities':r'|'.join([r'[\w]*nbsp[\w]*',r'\blt[\w]*',r'\bgt[\w]*',r'\bamp\b',r'\bquot\b',r'\bpos\b']),
    r'likely_url':r'\b\w*http(?:[^s\s]|(?:s\w))+\w*\b',
    r'http_end_in':r'(\w)http[s]*',
    r'http_end_out':r'\g<1>',
    r'image_endings':r'\w+(?:png|gif|jpg|jpeg)\w*',
    r'isolated_com':r'\bcom\b',
    r'isolated_www':r'\bwww\b'
}


def basic_reddit_preformatting(text_series):
    '''
    takes in a string of text, intended to be reddit posts, then lowercases them and replaces the leading /
    from /r/valid_name and /u/valid_name with a space
    :param text_series:
    series of strings
    :return:
    formatted series of strings
    '''
    text_series=text_series.str.lower()
    text_series=text_series.str.replace(regex_store[r'/clean'],' ')
    return text_series

def dumb_language_detect_tool(series):
    '''
    returns a series of the ratio of non-english stopwords per entry to (english-stopwords + 1).
    Intended use is to sort a dataframe for iterative, investigative work to find droppable foreign sources.
    Not recommended for blind use.
    :param series:
    series of strings
    :return:
    non-english stopword ratio, higher scores should roughly correspond to a higher chance of being non-english
    '''
    working_series=series.map(lambda z:
                              collections.Counter(['eng_stop' if s in ENGLISH_STOPWORDS else
                              'noneng_stop' if s in NON_ENGLISH_STOPWORDS else 'neutral' for
                              s in nltk.wordpunct_tokenize(z)]))
    return working_series.map(lambda z: z.get('noneng_stop',0)/(z.get('eng_stop',1)))

def clean_series(df, string_series_name='snapshot',subreddit_column_name='subreddit',foreign_list=None):
    '''
    Transforms a string series, following the steps used in the data_cleaning_work book.  Convenience and
    proof-of-concept only, inappopriate for general modular use without consideration or modification.

    Note: This repeatedly calls the .str. pandas method, which is nice for editing and readability but is therefore
    quite memory-intensive.  This may take longer than expected to run.

    :param string_series_name: the series to be transformed's name
    :param subreddit_column_name: we expect a column representing the subreddit, with that name, but can
    accept a different name.
    :param foreign_list: if supplied, purges those subreddits from the dataframe.  Intended for non-english subreddits.

    :return: the transformed (cleaned) string.
    '''

    df[string_series_name] = df[string_series_name].str.lower()
    # send all words to lowercase
    df[string_series_name] = df.snapshot.str.replace(regex_store[r'/clean'], ' ')
    # clean /x/yz-type strings
    if foreign_list:
        df.drop(df[df[subreddit_column_name].isin(foreign_list)].index, inplace=True)
    #drop non-english subs
    df[string_series_name]=df[string_series_name].map(reddit_tokenizer.tokenize)
    df[string_series_name]=df[string_series_name].map(lambda l: [s for s in l if s not in stopwords])
    df[string_series_name] = (df[string_series_name]).map(lambda s:
                                                              [word for word in s if
                                                               not re.match(regexp_store['url_start'], word)])

    df[string_series_name] = df[string_series_name].map(
        lambda s: list(
            map(
                (lambda w: re.sub(regexp_store['repetitions_in'], regex_store['\g<1>\g<1>'], w))
                , s)))
    #This will condense 1-and-2 letter repetitions

    df[string_series_name] = df[string_series_name].apply(lambda r: [w for w in r if len(w) <= 45])
    # Drop long strings
    df[string_series_name] = df[string_series_name].str.replace(regex_store['likely_url'], '')

    df[string_series_name] = df[string_series_name].str.replace(regex_store[r'http_end_in'], regex_store[r'http_end_out'])
    # 'http_end_in' and 'http_end_out' in regex_store

    df[string_series_name] = df[string_series_name].str.replace(regex_store['image_endings'], '')
    # image_endings in regex_store
    # drop likely image links, note this is a little more information-compromising
    # than might be expected due to the popularity of written out expressions like 'sad.jpg'

    df[string_series_name] = df[string_series_name].str.replace(regex_store[r'isoloted_com'], '')
    df[string_series_name] = df[string_series_name].str.replace(regex_store[r'isolated_www'], '')
    df[string_series_name] = df[string_series_name].str.replace(r'http[s]*(?=\s)', '')
    df[string_series_name] = df[string_series_name].str.replace(r'(?<=\s)http[s]*', '')
    # strings starting or ending with http
