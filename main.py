"""
Michael Josten
TCSS 554 Information Retrieval 
Assignment 1

Requires natural language toolkit to run. main.py must be run 
in a directory with a subdirectory of 'transcripts' which contains files with
text for processing.
"""

#imports
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import os
import re
import math

"""
Text Processing Operations Procedures
1. Remove stopwords
2. remove special characters
3. user porter or snowball stemming

Goals:
1. number of word tokens in the database(before and after text processing)
2. The number of unique words in the database
3. the number of words that occur only once in the database
4. the average number of word tokens per document
5. For the 30 most frequent words in the database provide:
    TF, scaled TF(1+log(tf)), IDF, TF*IDF, and probabilities
    In a tabular format(rows=terms, columns=values)
"""
def main():
    # get the stopwords into a list
    # Iterate over the database and make a dictionary out of the tokenized words
    stopwords = getStopwords()
    wordDict, docFreq = getDatabaseDictionary()

    nWordsBeforeProcessing = countDict(wordDict)

    # process the text of the wordDict and the docFrequency
    wordDict, docFreq = textProcessing(wordDict, docFreq, stopwords)
    calcMetrics(wordDict, docFreq, nWordsBeforeProcessing)

    return

#function that will calculate metrics of the database based on the wordDictionary
def calcMetrics(wordDict, docFreq, nWordsBeforeProcessing):
    freqWordsDict = get30MostFrequent(wordDict)

    nDocs = len(os.listdir('./transcripts'))
    # nDocs = 1
    nWords = countDict(wordDict)
    nUniqueWords = len(wordDict.keys())

    nOnceOcurrence = 0
    for key in wordDict.keys():
        if wordDict[key] == 1:
            nOnceOcurrence += 1
    
    avgWordsPerDoc = nWords / nDocs
    

    #calc metrics of freq terms
    #{term: [TF, scaled TF(1+log(tf)), IDF, TF*IDF, probability]}
    resultDict = {}
    for word, count in freqWordsDict.items():
        # calc metrics
        tf = count
        scaledTF = math.log1p(count)
        df = docFreq[word]
        idf = math.log(nDocs / df)
        tfidf = tf * idf
        probOfTerm = count/nWords
        
        resultDict[word] = [tf, scaledTF, df, idf, tfidf, probOfTerm]   

    # print results
    print("Number of word tokens before text processing: ", nWordsBeforeProcessing)
    print("Number of word tokens after text processing: ", nWords)
    print("Number of unique words: ", nUniqueWords)
    print("Number of words that occur only once: ", nOnceOcurrence)
    print("Average number of word tokens per document: ", avgWordsPerDoc)
    print("-------30 Most Frequent Terms-------------------")
    print("# term :  [Tf, Tf(weight), df, IDF, tf*idf, p(term)]")
    i = 1
    for k, v in resultDict.items():
        print("#" + str(i), k, ":", v)
        i += 1

    #makeCSV(resultDict)

    return

def makeCSV(dct):
    fout = open("output.csv", 'w')
    fout.write("term,TF,TF(Weight),DF,IDF,TF*IDF,P(Term)\n")
    for k, v in dct.items():
        result = k + ','
        for value in v:
            result += str(value) + ','
        result += '\n'
        fout.write(result)
    fout.close()
    return



#helper function to return a dictionary of the 30 most frequent terms in the db
def get30MostFrequent(wordDict):
    result = []

    x = sorted(((v, k) for k, v in wordDict.items()), reverse=True)
    if len(x) > 30:
        result = x[:30]
    else:
        result = x
    
    resultDct = {}
    for (v, k) in result:
        resultDct[k]=v
    return resultDct

#function that will process the word dictionary
def textProcessing(wordDict, docFreq, stopwords):
    """
    Text Processing Operations Procedures
    1. Remove stopwords
    2. remove special characters
    3. use porter stemming
    """
    #remove stopwords
    for sw in stopwords:
        if sw in wordDict:
            del wordDict[sw]
        if sw in docFreq:
            del docFreq[sw]
    
    #remove special characters
    specRegex = re.compile(r"\W+")
    specWords = []
    #cant remove from dict while iterating so need to collect first then delete
    for key in wordDict.keys():
        if specRegex.match(key):
            specWords.append(key)
    for sw in specWords:
        if (sw in wordDict):
            del wordDict[sw]
        if (sw in docFreq):
            del docFreq[sw]

    # wasn't caught by regex for some reason
    del wordDict['n\'t']
    del docFreq['n\'t']
    
    #Porter Stemming
    stemmer = PorterStemmer()
    stemWordDict = {}
    stemDocFreq = {}
    for key in wordDict.keys():
        stemWord = stemmer.stem(key)
        if stemWord not in stemWordDict:
            stemWordDict[stemWord] = wordDict[key]
        else:
            stemWordDict[stemWord] += wordDict[key]
        
        if stemWord not in stemDocFreq:
            stemDocFreq[stemWord] = docFreq[key]
        else:
            stemDocFreq[stemWord] = max(stemDocFreq[stemWord], docFreq[key])
        
        
    
    return stemWordDict, stemDocFreq



# function that will get a list of stopwords from the stopwords file
def getStopwords():
    fStopwords = open('stopwords.txt', 'r')
    contents = fStopwords.read()
    stopList = word_tokenize(contents)
    fStopwords.close()
    return stopList

# function that will get a dictionary from the files
def getDatabaseDictionary():
    #transcripts file needs to be in same folder as main.py
    fileList = os.listdir('./transcripts')
    path = "transcripts/"
    wordDict = {}
    docFreq = {}
    docFreqFlag = {}

    #Whole database 
    for fileName in fileList:
        file = open(path+fileName, 'r')
        wordList = word_tokenize(file.read().lower())
        for word in wordList:
            if word not in wordDict:
                wordDict[word] = 1
            else:
                wordDict[word] += 1
            
            #document frequency calc
            if word not in docFreq:
                docFreq[word] = 1
                docFreqFlag[word] = 1
            elif word in docFreq and docFreqFlag[word] == 0:
                docFreq[word] += 1
                docFreqFlag[word] = 1
        
        for key in docFreqFlag.keys():
            docFreqFlag[key] = 0
        
    return wordDict, docFreq

#Function that will count the total number of words
def countDict(wordDict):
    total = 0
    for word in wordDict.keys():
        total += wordDict[word]
    return total

#helper function to print out a dictionary object
def printDict(d):
    for k, v in d.items():
        print(k, ': ', v)
        
#run main
if __name__ == "__main__":
    main()