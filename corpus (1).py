''' IMPORTING LIBRARIES '''

''' DATA ACCESS '''
import glob
import json
import sys

''' DATA QUERY '''
from lxml import etree
parser = etree.XMLParser(collect_ids=False,encoding='utf-8')
nsmap = {'tei': 'http://www.tei-c.org/ns/1.0'} ### EPL Source

''' DATA STRUCTURING '''
import pandas as pd

''' PROGRESS BAR '''
from tqdm.notebook import tqdm

''' FUNCTION DEFINITION '''

''' root generator function:

    INPUT: File Path from your machine
    OUTPUT: A parseable xml element that is TEI encoded

    The purpose of this function is to simplify the steps needed to get an xml file in parseable state. Any file name that
    is XML encoded will work for this function. 

'''


def root_generator(file_path):
    #print (f"Printing from Root Generator: {file_path}")
    tree = etree.parse(file_path,parser)
    
    text_root = tree.getroot()
    
    return(text_root)

''' root generator function:

    INPUT: A text root
    OUTPUT: The TEI tag to identify this book

    The purpose of this function is to extract the unique TEI tag from the file. It will return a string with the TEI inside 

'''

def tei_finder(text_root):
    tei_tag = text_root.findall(".//tei:idno[@ type='DLPS']",namespaces=nsmap)
    tei = [tag.text for tag in tei_tag]
    #print (f"Printing from text_root: {tei[0]}")
    return (tei[0])

''' extract_all_words function:

    This function is intended to extract all of the words from the text file. 
    This will include the title, author, publisher, and all other metadata that may be included in the text. 
    
    INPUT: an xml tree tag
    OUTPUT: a list containing all of the words

'''
def extract_all_words(text_root):
    all_word_tags = text_root.findall(".//tei:w",namespaces=nsmap)
    
    all_words = [w.text for w in all_word_tags]
    
    return(all_words)


''' extract_all_modernized_words function:

    This function will generate a list of the modernized words generated by the NUIT Morphadorner. This function performs similarly
    to the orignal text function above, but just pulls a different XML tag.
    
    INPUT: an xml tree tag
    OUTPUT: a list containing all of the modernized words


'''

def extract_all_modernized_words(text_root):
    all_word_tags = text_root.findall(".//tei:w",namespaces=nsmap)
    
    regularized_words = [w.get('reg', w.text) for w in all_word_tags]
    
    
    return(regularized_words)

''' extract_all_lemmas function:

    This function will generate a list of the lemmatized words by EPL. It works in a similar fashion to those above.
    
    INPUT: an xml tree tag
    OUTPUT: a list containing all of the lemmatized words



'''

def extract_all_lemmas(text_root):
    all_word_tags = text_root.findall(".//tei:w",namespaces=nsmap)
    
    lemmas = [w.get('lemma') for w in all_word_tags]
    
    
    return(lemmas)


''' extract_all_pos function:

    This function will generate a list of the Parts of Speech Tags attributed to each individual word. These were generated
    
    INPUT: an xml tree tag
    OUTPUT: a list containing all of the POS tags for each respective word

'''

def extract_all_pos(text_root):
    all_word_tags = text_root.findall(".//tei:w",namespaces=nsmap)
    
    pos = [w.get('pos') for w in all_word_tags]
    
    return(pos)

''' extract_all_sentences function:

    INPUT: an xml text root
    OUTPUT: a list of strings that are each a sentence in the text
    
    This function is heavily adopted from the EPL documentation linked above. Naming conventions were changed from 'master'
    to 'main', and the code comments were changed as well to increased readability in this file. This function, like the word
    functions, will take an xml text root and geneare a split list based on the text provided. This function can take some
    time to run, as it iterates through the tags one by one.

'''

def extract_all_sentences(text_root):
    word_and_punctuation_tags = text_root.xpath("//tei:w|//tei:pc", namespaces=nsmap)
    
    
        ## Creating list storage containers for the working text
    all_sentences = []
    new_sentence = []
    
        ## Iterating through each tag
    
    for tag in word_and_punctuation_tags:
        ## First, we will test to see if the tag has the attribute to find the end of the sentence
        if 'unit' in tag.attrib and tag.get('unit') == 'sentence':
            if tag.text != None:
                ## Adding the punctuation to the sentence
                new_sentence.append(tag.text)
            
            joined_sentence = ' '.join([word for word in new_sentence if word is not None])
            ## Storing the sentences
            all_sentences.append(joined_sentence)
            ## Reinstantiating the working sentence storage container
            new_sentence = []
        # If the tag is not at the end of a sentence, we can simply add its contents to the list
        else:
            new_sentence.append(tag.text)
            
    
    return (all_sentences)


''' function: iterative dataframe maker'''
def by_word_dataframe_maker(files):
    text_data = [] # Empty list for data
    
    ## extracting the metadata from each file
    for file_name in files:
            ## Finding TEI and creating a parse object
        root = root_generator(file_name)
        tei = tei_finder(root)
        
            ## Parsing the object using the above functions

        words = extract_all_words(root)
        modernized = extract_all_modernized_words(root)
        lemmas = extract_all_lemmas(root)
        pos = extract_all_pos(root)

        current_text = {'TEI':tei,'words':words,'modernized':modernized,'lemmas':lemmas,'pos':pos}
        text_data.append(current_text)
          

    tei_data = pd.DataFrame(text_data)
    #word_data = tei_data.apply(pd.Series.explode).reset_index(inplace=True)
    
   
    
    repo_tei_code_first = tei_data.at[0,'TEI']
    repo_tei_code = repo_tei_code_first[0:3]

    text_file_name = str(repo_tei_code)+" FULL Text Data.csv"
    by_word_file_name = str(repo_tei_code)+ " SPLIT Word Data.csv"
    
    tei_data.to_csv(text_file_name)
    #word_data.to_csv(by_word_file_name)
    
    
    
''' function: sentence dataframe maker'''

def by_sentence_dataframe_maker(files):
    sentence_data = [] # Empty list for data
    teis = [] # Empty list for TCP IDs

    ## extracting the metadata from each file
    for file_name in files:
            ## Finding TEI and creating a parse object
        root = root_generator(file_name)
        tei = tei_finder(root)
        teis.append(tei)

            ## Parsing the object using the above functions
        sentences = extract_all_sentences(root)

        current_text = {'TEI':tei,'sentences':sentences}
        sentence_data.append(current_text)


    tei_full_sentences = pd.DataFrame(sentence_data)
    #tei_sentences = tei_full_sentences.explode(column='sentences')

    
    repo_tei_code_first = tei_full_sentences.at[0,'TEI']
    repo_tei_code = repo_tei_code_first[0:3]
    
    sentence_full_file_name = str(repo_tei_code)+" FULL Sentence Data.csv"
    sentence_file_name = str(repo_tei_code)+" SPLIT Sentence Data.csv"
    tei_full_sentences.to_csv(sentence_full_file_name)
    #tei_sentences.to_csv(sentence_file_name)
    

''' function: folder iteration and data generation '''
## naming the line aregument from the slurm script
folder_name = sys.argv[1]
folder_name = folder_name.strip()

with open("output.txt", 'w') as f:
    f.write(f"{folder_name} | using folder iterator")
    f.write(f" folder: {folder_name}")

def folder_iterator(folder_name):
    #folder_path = glob.glob(f"/projects/glimp/eebotcp/texts/{folder_name_test}")
    print (f"processing folder: {folder_name}")
    #xml_paths = folder_path+"/*.xml"
    
    #xml_files = glob.glob("/scratch/alpine/naca4005/texts/{folder_name_test}/*.xml")
    #xml_files = glob.glob(f"/scratch/alpine/naca4005/texts/A00/*.xml") ## this is a testing line to see if there is an issue with the file name  - when using this format it worked correctly
    current_path = f"/scratch/alpine/naca4005/texts/{folder_name}/*.xml"
    xml_files = glob.glob(current_path)
    
    print ("word dataframe processing")
    by_word_dataframe_maker(xml_files)
    print ("sentence dataframe processing")
    by_sentence_dataframe_maker(xml_files)
    
    print ("\n")
     
    
    
''' RUNNING THE FUNCTION '''

folder_iterator(folder_name)