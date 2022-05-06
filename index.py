'''
dictionary entry for each term is a tuple with 2 elements. first element is doc frequency, second element is byte offset.
'''

#!/usr/bin/python3
import re
import nltk
import pickle
import sys
import os
import getopt
import shutil

NUM_FILES_UNTIL_NO_MEMORY = 2500 # to simulate insufficient memory. how many files we can read until there is not enough memory. 
INTERMEDIATE_FILES_DIR = '_temp_spimi' # directory for storing intermediate index files

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    remove_all_files(INTERMEDIATE_FILES_DIR)
    corpus_files = os.listdir(in_dir)
    corpus_filepaths = list(map(lambda fname: os.path.join(in_dir, fname), corpus_files))
    intermediate_file_count = 0

    while (len(corpus_filepaths) > 0):
        corpus_filepaths, index_block = make_index_until_no_memory(corpus_filepaths)
        intermediate_file_count += 1
        write_temporary_index(INTERMEDIATE_FILES_DIR, index_block, intermediate_file_count)
    
    print('finished reading all corpus files.')

    while (intermediate_file_count > 1):
        merge_two_intermediate_files(INTERMEDIATE_FILES_DIR, intermediate_file_count-1, intermediate_file_count)
        intermediate_file_count -= 1

    save_final_intermediate_files(INTERMEDIATE_FILES_DIR, out_dict, out_postings)
    
    print('done.')

def save_final_intermediate_files(intermediate_dir, out_dict, out_postings):
    '''
    saves the final results to the dictionary and postings files
    '''
    shutil.copy(os.path.join(intermediate_dir, '1dict'), out_dict)
    shutil.copy(os.path.join(intermediate_dir, '1post'), out_postings)

def merge_two_intermediate_files(directory, f1, f2):
    '''
    reads two intermediate files, merges them, and writes back into directory.
    the contents of f2 (both the dictionary and the postings) will be merged into f1.
    then deletes f2 (dictionary and postings)
    '''
    print(f'merging temporary indices {f1}, {f2}')

    dict1_file_name = os.path.join(directory, f'{f1}dict')
    dict2_file_name = os.path.join(directory, f'{f2}dict')
    post1_file_name = os.path.join(directory, f'{f1}post')
    post2_file_name = os.path.join(directory, f'{f2}post')
    
    temp_post_file_name = os.path.join(directory, f'_temp_post')

    with open(dict1_file_name, 'rb') as f:
        dict1 = pickle.load(f)

    with open(dict2_file_name, 'rb') as f:
        dict2 = pickle.load(f)

    merged_dict = {}
    terms = set(dict1.keys()).union(set(dict2.keys()))
    bytes_so_far = 0

    for term in sorted(terms):
        p1 = []
        p2 = []
        if term in dict1.keys():
            _, p1_offset = dict1[term]
            with open(post1_file_name, 'rb') as f:
                f.seek(p1_offset)
                p1 = pickle.load(f)
        if term in dict2.keys():
            _, p2_offset = dict2[term]
            with open(post2_file_name, 'rb') as f:
                f.seek(p2_offset)
                p2 = pickle.load(f)

        merged_posting = list(sorted(set(p1 + p2)))

        merged_dict[term] = (len(merged_posting), bytes_so_far)
        bytes_to_write = pickle.dumps(merged_posting)
        bytes_so_far += len(bytes_to_write)
        with open(temp_post_file_name, 'ab') as f:
            f.write(bytes_to_write)
        
    # delete the unneeded files
    os.unlink(dict2_file_name)
    os.unlink(post2_file_name)
    os.unlink(post1_file_name)

    os.rename(temp_post_file_name, post1_file_name)
    with open(dict1_file_name, 'wb') as f:
        pickle.dump(merged_dict, f)

def write_temporary_index(directory, index_block, intermediate_file_count):
    '''
    writes the index to disk as a temporary file. 
    '''
    print(f'writing temporary index {intermediate_file_count}')

    sorted_terms = sorted(index_block.keys())
    dict_file_name = os.path.join(directory, f'{intermediate_file_count}dict')
    post_file_name = os.path.join(directory, f'{intermediate_file_count}post')
    dict_file_contents = {}
    post_file_contents = b''
    for term in sorted_terms:
        next_bytes = pickle.dumps(index_block[term])
        dict_file_contents[term] = (len(index_block[term]), len(post_file_contents))
        post_file_contents += next_bytes
        
    with open(dict_file_name, 'wb') as f:
        pickle.dump(dict_file_contents, f)

    with open(post_file_name, 'wb') as f:
        f.write(post_file_contents)

def make_index_until_no_memory(filepaths, num_files_until_no_memory=NUM_FILES_UNTIL_NO_MEMORY):
    '''
    we will use spimi, so we will read files and build the index until there is no memory.
    but tembusu cluster has a lot of memory, so we will instead pretend that it has
    less memory. we will assume that there is only enough memory to store a certain number of files' worth
    at one time
    '''
    filepaths_until_no_memory = filepaths[:num_files_until_no_memory]
    filepaths = filepaths[num_files_until_no_memory:]
    term_doc_pairs = []

    for filepath in filepaths_until_no_memory:
        with open(filepath, 'r') as f:
            file_text = f.read()
        terms = process_file_text(file_text)
        file_name = os.path.basename(filepath)
        term_doc_pairs += list(map(
            lambda term: (term, file_name),
            terms
        ))

    index_block = make_index_block(term_doc_pairs)
    return filepaths, index_block

def make_index_block(term_doc_pairs):
    '''
    takes in a list of (term, docId) pairs as input. generates an index "block".
    although spimi does not use blocks, we have divided the set of corpus files
    into blocks so as to simulate limited memory space
    '''
    dictionary = {}
    for (term, doc) in term_doc_pairs:
        if term not in dictionary.keys():
            dictionary[term] = []
        if doc not in dictionary[term]:
            dictionary[term].append(doc)
    return dictionary

def process_file_text(file_text):
    '''
    input: raw file text
    output: list of terms, with necessary preprocessing performed
    '''
    stemmer = nltk.stem.porter.PorterStemmer()
    sentences = nltk.sent_tokenize(file_text)
    terms = []
    for sent in sentences:
        terms += [
                stemmer.stem(word).lower()  # porter stemming and case folding
                for word
                in nltk.word_tokenize(sent) # split sentence into words
                if re.match('\w', word)     # remove punctuation
        ]
    return terms

def remove_all_files(directory):
    '''
    deletes all files in a directory.
    used for removing temp files
    '''
    if directory not in os.listdir('.'):
        os.mkdir(directory)
        return

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        os.unlink(filepath)

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
