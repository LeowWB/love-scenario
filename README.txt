This is the README file for A0184415E and ________ submission
Email(s): e0311210@u.nus.edu, ________

== Python Version ==

We're using Python Version 3.8.10 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Our indexing is performed using SPIMI. As the Tembusu cluster has a large amount of memory, we simulate insufficient memory by placing a limit on the number of files that can be read at once. This limit can be configured as a constant in the file index.py. 

For preprocessing, all documents are first tokenized by sentence, then by words. All words are case-folded to lower case and stemmed using a Porter stemmer. Words which are entirely non-alphanumeric (e.g. punctuations) are removed.   

Our implementation of SPIMI works by reading in as many files as possible (based on the abovementioned constant). The files are then converted to (term, docID) pairs, which are then hashed into a dictionary. This dictionary forms an index block, which will be temporarily stored on disk. This is done in the form of a dictionary file and a postings file for each index. 

When all the index blocks have been generated, we will perform merging of the index blocks to obtain a single index, comprising of a dictionary file and a postings file. Merging is done on a pairwise basis, where we merge two indices together to obtain one larger index. As we assume that memory is limited, we will only store the dictionary in memory. The postings lists are stored on disk and the necessary information is read only when it is needed for the merge.

The dictionary is stored in pickled format. When unpickled, the result is a Python dictionary where the keys are the terms, and the values are 2-tuples where the first element is the document frequency and the second element is the byte offset in the postings file. This byte offset can be used with the seek() function and the postings file to obtain a list of documents which contain the relevant term. 

<arun pls continue>

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py - performs indexing of corpus, outputs a dictionary file and a postings file

<arun pls continue>

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0184415E and _______, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
