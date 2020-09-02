import csv
import bz2
import json
import sqlite3
import pandas as pd



def unpack_zipped(source_file_name,target_file_stem,max_num_size=10**6,verbose=True,cutoff=100):
    '''

    :param source_file_name:
    the source .bz2 file's name
    :param target_file_stem:
    The default "stem" for the resulting csv file names, which will have an incremented number
    appended. e.g, "reddit_file_2017_09", which becomes "reddit_file_2017_09_01, reddit_file_2017_09_02", etc.
    :param max_num_size=10**6:
    maximum size for one csv befor starting a new one.
    :param verbose=True:
    if true, will print out counts as the function progresses, recommended as a sanity check as this process will take
    a long time.  It is recommended you turn on output scrolling if doing this in a jupyter notebook or jupyter lab.
    :param cutoff:
    a safety parameter that can be used to stop the process if something goes awry, recommended as internal formatting
    errors could lead to unpredicted results.  For the data in question, there's about 80 million entries and each
    file should take 1 million of them, so we'd expcct the counter to only rise to 80 *at most* if everything is going
    well (remember, some rows will be filtered out).
    :return:
    A message saying the process is complete.
    '''
    unwanted_keys = ['retrieved_on', 'parent_id', 'author_flair_text', 'score', 'author_flair_css_class', 'ups', 'downs'
                      'controversiality','score_hidden', 'link_id', 'subreddit_id', 'edited', 'distinguished',
                     'gilded', 'archived','removal_reason']
    #The keys we'll drop when reading lines
    full_keys = ['body', 'id', 'downs', 'author_flair_css_class', 'controversiality',
                 'score', 'link_id', 'distinguished', 'author', 'author_flair_text',
                 'created_utc', 'subreddit', 'gilded', 'retrieved_on', 'archived',
                 'parent_id', 'edited', 'score_hidden', 'name', 'subreddit_id', 'ups',
                 'removal_reason']
    #The full set of keys found in various pushshift data set
    fieldnames = [k for k in full_keys if k not in unwanted_keys]

    file_name = source_file_name
    new_file_name = target_file_stem
    bad_users = ['[deleted]', 'conspirobot', 'ModerationLog', 'AutoModerator', 'qkme_transcriber', 'pixis-4950',
                 'JiffyBot', 'ImagesOfNetwork',
                 'MovieGuide'',imguralbot', 'BitcoinAllBot']

    with bz2.open(file_name, mode='rb') as source_file:
        count = 0
        #Track the number of files written
        num_written = 0
        #track the number of lines written
        if verbose:
            print(f'counting {count}')
        while num_written < max_num_size and count < cutoff:
            #Begin the outer loop over different .csv files
            with open(f'{new_file_name}_{count}.csv', 'w', newline='', encoding='utf-8') as file:
                #Begin the inner loop, writing lines to the current .csv file
                writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for x in source_file:
                    #begin recording from the lines of the open source file
                    newline = json.loads(source_file.readline())
                    if newline['body'] != '[deleted]' and (not (newline['author'] in bad_users)):
                        writer.writerow(newline)
                        #write the new file only if it passes the filter, then record having written a new file
                        num_written += 1
                        if num_written % 10 ** 5 == 0 and verbose:
                            print(num_written)
                    if num_written >= max_num_size:
                        break
                    #stop writing lines when we've hit a pre-set amount, add one to the count, and restart the outer
                    #loop
            count += 1
            num_written = 0
            if verbose:
                print('>>>>>', count)
    return('done')

def database_create(database_name,source_files,verbose=False,make_new_table=False):
    '''
    Reads a list of csv files into a sql dataframe via pandas, using the columns "subreddit","body",and "author"
    :param database_name:
    file name for new database, remember the .db ending unless you have good reason not to!
    :param source_files
    list of source file names.  They should have the columns "subredddit","body",and "author"
    :param verbose=False:
    Speak every time a new file is added to the dataframe, useful if a large number of files are being written.
    :param make_new_table=False:
    assign "true" to make a new sql table.  Be sure you want to do this.  The function will prompt you prior
    to type "okay" as double-check.
    '''
    conn = sqlite3.connect(f'{database_name}')
    c = conn.cursor()
    if make_new_table:
        #creates a new file if needed
        u=input('type "okay" to proceed with new table creation ')
        if u!='okay':
            return('safety check')
        c.execute('''
        CREATE TABLE TEST_TABLE ([generated_id], INTEGER PRIMARY KEY, [subreddit] text, [body] text, [author] text)
        ''')
        conn.commit()
        print('table made')
    for f in file_names:
        try:
            read_df = pd.read_csv(f,
                                  usecols=['subreddit', 'body', 'author'])
            read_df.to_sql('POSTS', conn, if_exists='append', index=False)  # append for looping
            if verbose:
                try:
                    n-=1
                except:
                    n=len(source_files)
                print(fr'{f} written, {n} files remaining')
        except:
            print(f'failed at {f}')
    return('all done :)')

