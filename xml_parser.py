import xmltodict
import xml.etree.ElementTree as ET
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

path = os.path.realpath(__file__)                        #| Gets the directory
directory = os.path.dirname(path)                        #| for the iTunes
dir_path = directory + '\\XML\\iTunes Music Library.xml' #| XML file.

'''
Create a new XML file that changes all of the integer and date keys to string, but also truncates the file when the word 'Playlists' is present.
'''

def prep_xml(dir_path): # Prepares the XML so that it can be read by the program.
    tree = ET.parse(dir_path)
    root = tree.getroot()

    tags_to_replace = ['integer', 'date'] # Replace all instances of the word 'integer' and 'date'...

    for elem in root.iter():            #| ... and replace them with 'string'. By default, the XML has all of these stored in
        if elem.tag in tags_to_replace: #| different categories, and trying to sort them would be a nightmare. By making them
            elem.tag = 'string'         #| all the same category, they're magically lined up and more easily parsible.

    tree.write(dir_path)

def countXMLelements(dir_path): # This was written by ChatGPT. I only used it to figure out how many elements I needed to loop through to get every element of an XML so that I know how much to loop through.
    
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

def specify_artist(df, artist): # Show play counts associated with a specific artist.
    mask = df['Artist'] == artist
    filtered_df = df[mask]

    print(filtered_df)

    x_axis = filtered_df['Name']
    y_axis = filtered_df['Play Count']
    plt.bar(x_axis, y_axis)

    plt.xticks(rotation=45, ha='right')
    plt.title(f'{artist} Data')
    plt.show()

def most_played_artist(df, top):
    df = df.loc[df['Play Count'] > top]
    artists = df.groupby('Artist')['Play Count'].sum()
    artists = artists.sort_values(ascending=False)
    
    artists.plot(kind='bar')

    plt.title(f'Most Played Artists (More than {top} collective plays)')
    plt.xticks(rotation=45, ha='right')
    plt.show()

def most_skipped_artists(df):
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
    genre_skip = df.groupby('Genre')['Skip Count'].sum()
    genre_skip = genre_skip.sort_values(ascending=False)

    genre_skip.plot(kind='bar')

    plt.title('Most Skipped Genres')
    plt.xticks(rotation=45, ha='right')
    plt.show()

def ratings_vs_play_counts(df):
    '''
    I would like to see the average rating of the songs I listen to. I'm expecting something skewed left.
    '''

def main():
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
        for j in range(len(combined_data[i])):                      #Go through each list inside the list pertaining to each song and it's info
            if combined_data[i][j][0] in interesting_data:  
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
    all_data_df['Play Count'] = all_data_df['Play Count'].astype(int) # Converts the playcounts column to integers.

    pprint(all_data_df)

    # specify_artist(all_data_df, 'Dance Gavin Dance')

    # most_played_artist(all_data_df, 10)
    # most_skipped_artists(all_data_df)
    # skip_pct_genre(all_data_df)


    itunes.close()

main()