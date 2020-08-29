#!/usr/bin/env python3
import datetime
from bs4 import BeautifulSoup
import urllib.request
import os
from os import listdir
from os.path import isfile, join
import time

# deets
authorName = ["WPM Rowe", "W Rowe"]
scholarID = "sVMdRQMAAAAJ"
baseURL = "https://scholar.google.co.uk"
outFile = "./_data/googleScholar.yaml"


def printDetails(baseURL, scholarID, authorName, stats):
    timeStamp = datetime.datetime.now()
    lastUpdated = "%d.%d.%d" % (timeStamp.day, timeStamp.month, timeStamp.year)
    details = "%s citations, h-index %s. Please click on the abstract links for more information. Data last scraped from [Google Scholar](%s/citations?user=%s&hl=en) on %s." % (
        stats[0], stats[2], baseURL, scholarID, lastUpdated)
    return details


def parseScrape(soup):
    """
    parseScrape is adapted from: https://github.com/ayansengupta17/GoogleScholarParser/blob/master/GoogleScholarParser.py
    """
    paper_box = soup.find_all('a', attrs={'class': 'gsc_a_at'})
    papers = [paper.text.strip() for paper in paper_box]
    author_box = soup.find_all('div', attrs={'class': 'gs_gray'})
    authors = [author.text.strip() for author in author_box]
    year_box = soup.find_all(
        'span', attrs={'class': 'gsc_a_h gsc_a_hc gs_ibl'})
    years = [year.text.strip() for year in year_box]
    links = [paper['data-href'] for paper in paper_box]
    cited_box = soup.find_all('td', attrs={'class': 'gsc_rsb_std'})
    stats = [stat.text.strip() for stat in cited_box]
    return papers, authors, years, links, stats


if __name__ == "__main__":

    # scrape Google Scholar page
    scholarPage = baseURL + "/citations?hl=en&user=" + \
        scholarID + "&view_op=list_works&sortby=pubdate"
    page = urllib.request.urlopen(scholarPage)
    scrapedContent = BeautifulSoup(page, 'html.parser')

    # sift throught the scraped info and get the paper deets
    paperList, authorList, yearList, linkList, stats = parseScrape(
        scrapedContent)

    # write the papers to a yaml file
    with open(outFile, 'w', encoding='utf-8') as fh:
        fh.write("title: \"Papers\"\n")
        fh.write("introduction: \"%s\"\n" %
                 printDetails(baseURL, scholarID, authorName, stats))
        fh.write("papers:\n")
        for i in range(len(yearList)):
            fh.write("  - title: \"" + paperList.pop(0) + "\"\n")
            # put the author name in bold
            authors = authorList.pop(0)
            for name in authorName:
                authors = authors.replace(
                    name, "<strong>%s</strong>" % name)
            fh.write("    authors: \"" + authors + "\"\n")
            fh.write("    journal: \"" + authorList.pop(0) + "\"\n")
            fh.write("    year: \"" + yearList.pop(0) + "\"\n")
            fh.write("    link: \"" + baseURL + linkList.pop(0) + "\"\n")
