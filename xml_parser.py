import xmltodict
import xml.etree.ElementTree as ET
from pprint import pprint
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os

path = os.path.realpath(__file__)
directory = os.path.dirname(path)
dir_path = directory + '\\XML\\iTunes Music Library.xml'

# I have to get back to work, but here's what's on the roadmap:
# - A side program that automatically preps XML files to be used for data visualization (So that I don't forget how to do that in the future)
# - Default visualizations, and automatically spitting those out into a folder (rating vs play counts, etc)
# - Convert this into a Jupyter Notebook so I can actually see the data I'm dealing with somewhat


def prep_xml(dir_path):
    tree = ET.parse(dir_path)
    root = tree.getroot()

    # Define the tags you want to replace
    tags_to_replace = ['integer', 'date']

    # Iterate over all elements
    for elem in root.iter():
        if elem.tag in tags_to_replace:
            elem.tag = 'string'

    tree.write(dir_path)

def countXMLelements(dir_path): # This was written by ChatGPT. I only used it to figure out how many elements I needed to loop through to get every element of an XML by printing my counter value in the loop.
    
    # Parse the XML file
    tree = ET.parse(dir_path)
    root = tree.getroot()

    # Function to count elements recursively
    def count_elements(element):
        count = 1  # Count the current element
        for child in element:
            count += count_elements(child)  # Recursively count child elements
        return count

    # Count elements starting from the root
    total_elements = count_elements(root)

    #print("Total number of elements in the XML file:", total_elements)
    return total_elements

def most_played_artist(df, top):
    df['Play Count'] = df['Play Count'].astype(int)  # Converts the playcounts column to integers.
    df = df.loc[df['Play Count'] > top]
    artists = df.groupby('Artist')['Play Count'].sum()
    artists = artists.sort_values(ascending=False)
    
    artists.plot(kind='bar')

    plt.title(f'Most Played Artists (More than {top} collective plays)')
    plt.xticks(rotation=45, ha='right')
    plt.show()

def most_skipped_artists(df):
    df['Skip Count'] = df['Skip Count'].astype(int)  # Converts the playcounts column to integers.
    skips = df.groupby('Artist')['Skip Count'].sum()
    skips = skips.sort_values(ascending=False)
    
    skips.plot(kind='bar')

    plt.title('Most Skipped Artists')
    plt.xticks(rotation=45, ha='right')
    plt.show()

def highest_skip_pct(df):
    '''
    I'll need to take the total amount of skips from all artists, add them together, and then find the percentage of skips each artist has.
    '''

def release_year_to_play_count(df):
    '''
    I want to see if there's a correlation between when a song/album is released, and how much I listen to it.
    '''

def date_added_to_release_year(df):
    '''
    Do I tend to listen to a lot of music right when it's released, or do I primarily spend my time listening to older releases?
    '''

def skip_pct_genre(df):
    '''
    Is there a genre that I skip the most?
    This is not going to be so simple. By just counting the amount of skips each genre has, I'm really only seeing my most populous
    genres in my library. So, I likely need to break each genre down into a percentage (What genres make up the most of my music library)
    and then probably do the same for skip counts. Then, by comparing the percentage of genres and percentage of skip counts, I could
    find some more interesting data.
    '''
    df['Skip Count'] = df['Skip Count'].astype(int)
    genre_skip = df.groupby('Genre')['Skip Count'].sum()
    genre_skip = genre_skip.sort_values(ascending=False)

    genre_skip.plot(kind='bar')

    plt.title('Most Skipped Genres')
    plt.xticks(rotation=45, ha='right')
    plt.show()


temp_dict = {
    'Name': '',
    'Artist': '',
    'Album': '',
    'Genre': '',
    'Song Length': 0,
    'Release Year': 0,
    'Date Added': 0,
    'Play Count': 0,
    'Skip Count': 0,
    'Rating': 0
}

interesting_data = ['Name', 'Artist', 'Album', 'Genre', 'Total Time', 'Year', 'Date Added', 'Play Count', 'Skip Count', 'Rating']

combined_data = [] # List of lists storing tuples
dict_list = [] # Stores all of the dictionaries pertaining to each song and it's data.

prep_xml(dir_path) # Prepares the XML to be read in.

itunes = open(dir_path, 'r', encoding='UTF-8') # Opens the file
total = countXMLelements(dir_path) # Counts the total amount of entries in the XML
itunes_string = itunes.read()

entire_itunes_data = xmltodict.parse(itunes_string)

store = [entire_itunes_data['plist']['dict']['dict']['dict'] for i in entire_itunes_data] # Stores the multiple keys in the xml for cleaner code later

for i in range(total): #| Combine the lists from 'key' and 'string'                                                   
    try:               #| into a list containing tuples of the pairs
        combined_data.append(list(zip(store[0][i]['key'], store[0][i]['string'])))
    except:
        break

# For combined_data[i][j][k], we have a list of lists of tuples. So i is referring to which list to get info from,
# j is going to grab the specific tuple, and k is which element in that tuple (either 0 or 1). 

for i in range(len(combined_data)):
    for j in range(len(combined_data[i])):              #Go through each list inside the list pertaining to each song and it's info
        if combined_data[i][j][0] in interesting_data:  #If the first element of the tuple is something we want, do the following.
            if combined_data[i][j][0] == 'Name':
                temp_dict['Name'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Artist':
                temp_dict['Artist'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Album':
                temp_dict['Album'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Genre':
                temp_dict['Genre'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Total Time':
                temp_dict['Song Length'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Year':
                temp_dict['Release Year'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Date Added':
                temp_dict['Date Added'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Play Count':
                temp_dict['Play Count'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Skip Count':
                temp_dict['Skip Count'] = combined_data[i][j][1]
            elif combined_data[i][j][0] == 'Rating':
                temp_dict['Rating'] = combined_data[i][j][1]
        elif combined_data[i][j][0] == 'File Folder Count' and i != 0: #| We use File Folder Count to determine when we're looking at a different song,
            dict_list.append(temp_dict)                                #| and we skip the first time we do as we would have an empty dict as our
            temp_dict = {  #| This block reinitializes our dictionary  #| first element otherwise
                'Name': '',
                'Artist': '',
                'Album': '',
                'Genre': '',
                'Song Length': 0,
                'Release Year': 0,
                'Date Added': 0,
                'Play Count': 0,
                'Skip Count': 0,
                'Rating': 0
            }


all_data_df = pd.DataFrame(dict_list)
# most_played_artist(all_data_df, 10)
# most_skipped_artists(all_data_df)
skip_pct_genre(all_data_df)


itunes.close()
