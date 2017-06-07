#!/usr/bin/env python
# coding: utf-8
import sys
import os
import json
import glob
import re
import traceback
from pprint import pprint
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from random import randint
import nltk.data
import copy

# eventually fetch from online
#mycroft_core_skills = "https://github.com/MycroftAI/mycroft-core/tree/dev/mycroft/skills"
#community_skills = "https://github.com/MycroftAI/mycroft-skills.git"


def permute_model(json_dict):
    # Load the pretrained neural net
    tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')

    print "Finding permutations for:"
    total = [json_dict]
    print total
    sentance = json_dict["utterance"]

    # Tokenize the text
    tokenized = tokenizer.tokenize(sentance)

    # Get the list of words from the entire text
    words = word_tokenize(sentance)
    output = ""
    # Identify the parts of speech
    tagged = nltk.pos_tag(words)
    # try to find 3 alternatives to the sentance
    for k in range(3):
        for i in range(0, len(words)):
            replacements = []

            # Find synsets for each word
            for syn in wn.synsets(words[i]):

                # Only replace Nouns and verbs, skip proper nouns, determiners,
                # and wh determiners
                if tagged[i][1] == 'NNP' or tagged[i][1] == 'DET' or tagged[i][1] == 'WH' or tagged[i][1] == 'PRON':
                    break
                # The tokenizer returns strings like NNP, VBP etc
                # but the wordnet synonyms has tags like .n.
                # So we extract the first character from NNP ie n
                # then we check if the dictionary word has a .n. or not
                word_type = tagged[i][1][0].lower()
                if syn.name().find("." + word_type + "."):
                    # extract the word only
                    r = syn.name()[0:syn.name().find(".")]
                    replacements.append(r)
            # no permutations of sentance found
            if len(replacements) > 0:
                # Choose a random replacement
                replacement = replacements[randint(0, len(replacements) - 1)]
                output = output + " " + replacement
        # add new permutation to total array
        if len(output) > 1:
            output.replace("_", " ")
            new_json_dict = copy.copy(json_dict)
            json_dict["utterance"] = output
            total.append(new_json_dict)

    return total


def main(args):
    #a_dict = {}
    print "Adding local files..."
    training_data = args[0]
    try:
        if not os.path.exists(traning_data):
            os.makedirs(training_data)
    except:
        print "training_data folder already exists, creating more files there...."

    for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
        print "Finding all .json files in " + root
        print dirs
        sample_no = 0
        for new_file in files:
            a_corpus = []
            if new_file.lower().endswith((".json")):
                with open(os.path.join(root, new_file), 'r') as json_file:
                    try:
                        json_data = json.load(json_file)
                        print new_file + " added!"
                    except Exception as e:
                        print "File " + new_file + " failed to open"
                        print e
                    a_corpus.extend(permute_model(json_data))


            for example in a_corpus:
                folder_name = training_data +"/" + example["intent_type"]
                print "writing to " + folder_name
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                with open(folder_name + "/" + str(sample_no), 'w') as output:
                    sample_no += 1
                    print "Writing out to " + folder_name
                    utterance = example["utterance"]
                    output.write(utterance)
                    output.close()


if __name__ == "__main__":
    main(sys.argv[1:])
