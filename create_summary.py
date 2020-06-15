#!/usr/bin/env python3


"""
Based on the output from the other functions, 
that is based on the file "reprint_counts.csv",
this function creates a summary for canonicity status.
"""


# Imports

import pandas as pd
import numpy as np


# Functions 

def read_countsfile(countsfile): 
    """
    Reads the "XXX_reprint_counts.csv" file. 
    Output: DataFrame
    """
    with open(countsfile, "r", encoding="utf8") as infile: 
        counts = pd.read_table(infile, sep=",")
        #print(counts.head())
        return counts


def read_metadatafile(metadatafile): 
    """
    Reads the "XXX_metadata.csv". 
    Output: DataFrame.
    """
    with open(metadatafile, "r", encoding="utf8") as infile: 
        metadata = pd.read_table(infile, sep="\t", index_col="xmlid")
        print(metadata.head())
        return metadata


def get_status(item): 
    """
    Calculates the canonicity status for a novel 
    based on the reprint count in the target period.
    The target period has been set to 1970-2009. 
    TODO: the minimum value could be made a parameter.
    Output: either string "high" or string "low"
    """
    print(item)
    if item > 1: 
        return "high"
    else: 
        return "low"


def create_summary(counts, metadata): 
    """
    Creates a summary from the full reprint count data. 
    Adds some metadata for better readability. 
    Columns: all reprints, reprints 1970-2009, author, title.
    Output: DataFrame. 
    """
    total_counts = np.sum(counts.iloc[:,1:], axis=0)
    canon_counts = np.sum(counts.iloc[131:171,1:], axis=0)    
    columns = ["total_counts", "canon_counts"]
    summary = pd.DataFrame([total_counts, canon_counts], index=columns).T
    summary["canon_status"] = summary.apply(lambda row: get_status(row.canon_counts), axis=1)
    summary["author"] = metadata.loc[:,"au-name"]
    summary["title"] = metadata.loc[:,"title"]
    print(summary.head())
    return summary
    

def save_summary(summary, lang): 
    """
    Saves the summary DataFrame to CSV.
    """
    summaryfile = str(lang) + "_summary.csv"
    with open(summaryfile, "w", encoding="utf8") as outfile: 
        summary.to_csv(outfile, sep="\t")


# Coordinating function.

def main(settingsdict): 
    countsfile = str(settingsdict["lang"]) + "_reprint_counts.csv"
    metadatafile = str(settingsdict["lang"]) + "_metadata.csv"
    counts = read_countsfile(countsfile)
    metadata = read_metadatafile(metadatafile)
    summary = create_summary(counts, metadata)
    save_summary(summary, settingsdict["lang"])
    
#main(settingsdict)
