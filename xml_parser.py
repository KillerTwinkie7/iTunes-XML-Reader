import xmltodict
import xml.etree.ElementTree as ET
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import re

path = os.path.realpath(__file__)                        #| Gets the directory
directory = os.path.dirname(path)                        #| for the iTunes
dir_path = directory + '\\XML\\iTunes Music Library.xml' #| XML file.

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

def specify_artist(art_df, artist): # Show play counts associated with a specific artist.
    mask = art_df['Artist'] == artist
    filtered_df = art_df[mask]

    x_axis = filtered_df['Name']
    y_axis = filtered_df['Play Count']
    plt.bar(x_axis, y_axis)

    plt.xticks(rotation=45, ha='right')
    plt.title(f'{artist} Data')
    plt.tight_layout()
    plt.savefig(directory + '\\output\\Specific Artist.jpg')

def most_played_artist(play_df, top): # Done
    play_df = play_df.loc[play_df['Play Count'] > top]
    artists = play_df.groupby('Artist')['Play Count'].sum()
    artists = artists.sort_values(ascending=False)
    
    plt.close()
    artists.plot(kind='bar')

    plt.title(f'Most Played Artists (More than {top} collective plays)')
    plt.xticks(rotation=45, ha='right')
    plt.savefig(directory + '\\output\\Most Played Artists.jpg')

def most_skipped_artists(skip_df): # Done
    skips = skip_df.groupby('Artist')['Skip Count'].sum()
    skips = skips.sort_values(ascending=False)
    
    plt.close()
    skips.plot(kind='bar')

    plt.title('Most Skipped Artists')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(directory + '\\output\\Most Skipped Artists.jpg')

def highest_skip_pct(high_df): # Done
    '''
    I'll need to take the total amount of skips from all artists, add them together, and then find the percentage of skips each artist has.
    '''
    total_skips = high_df['Skip Count'].sum()

    artist_skip = high_df.groupby('Artist')['Skip Count'].sum()
    artist_skip = artist_skip.sort_values(ascending=False)
    artist_skip = (artist_skip / total_skips) * 100
    artist_skip = artist_skip.loc[artist_skip >= .15]

    plt.close()
    artist_skip.plot(kind='bar')

    plt.title(f'Skip Percentage by Artist (Out of {total_skips} Total Skips)')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Skip %')
    plt.savefig(directory + '\\output\\Most Skipped Artists (pct).jpg')

def release_year_to_play_count(rel_df): # Done
    group = rel_df.groupby('Release Year')['Play Count'].sum()
    group = group.loc[1:]
    group = group.loc[group > 10]
    
    plt.close()
    group.plot(kind='bar')

    plt.title(f'Play Count per Release Year')
    plt.ylabel('Play Count')
    plt.savefig(directory + '\\output\\Release Year to Play Count.jpg')

def skip_pct_genre(skip_pct_df): # Done
    total_skips = skip_pct_df['Skip Count'].sum()

    genre_skip = skip_pct_df.groupby('Genre')['Skip Count'].sum()
    genre_skip = genre_skip.sort_values(ascending=False)
    genre_skip = (genre_skip / total_skips) * 100
    genre_skip = genre_skip.loc[genre_skip >= .15]

    plt.close()
    genre_skip.plot(kind='bar')

    plt.title(f'Skip Percentage by Genre (Out of {total_skips} Total Skips)')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Skip %')
    plt.tight_layout()
    plt.savefig(directory + '\\output\\Most Skipped Genres (pct).jpg')

def ratings_vs_play_counts(rat_df): # Done
    '''
    I would like to see the average rating of the songs I listen to.
    '''
    plays = rat_df.groupby('Rating')['Play Count'].sum()

    plt.close()
    plays.plot(kind='bar')

    plt.title('Play Counts per Ratings')
    plt.xticks(rotation=0, ha='right')
    plt.savefig(directory + '\\output\\Ratings versus Play Counts.jpg')

def play_to_skip_ratio(play_skip_df): # Done
    '''
    I think it'd be interesting to see which songs have the most amount of plays and least amount of skips.
    I'd need to go through the dataframe, and compare each song's play count to their skip count, and get a percentage (probably).
    Shouldn't be too hard.
    '''
    # ratio = (num / denom)
    # ratio = ratio.where(~ratio.isin([np.inf, -np.inf]), num, inplace=False)
    # ratio.fillna(0, inplace=True)

    plt.close()
    plt.scatter(play_skip_df['Play Count'].astype(float), play_skip_df['Skip Count'].astype(float))
    plt.xlabel('Play Count')
    plt.ylabel('Skip Count')
    plt.savefig(directory + '\\output\\Play to Skip Ratio.jpg')

def song_length_to_skip_ratio(len_df): # Done
    '''
    Is there a correlation between the length of a song and the amount of skips it has?
    '''
    len_df['Song Length'] = pd.to_numeric(len_df['Song Length'], errors='coerce')   #| These few lines
    len_df['Skip Count'] = pd.to_numeric(len_df['Skip Count'], errors='coerce')     #| clean up our data 
                                                                            #| a bit so we can sort
    len_df = len_df.dropna(subset=['Song Length', 'Skip Count'])                    #| them and read the graph.

    song = len_df.sort_values(by=['Song Length'], ascending=False)
    skip = len_df.sort_values(by=['Skip Count'], ascending=False)

    slope, intercept = np.polyfit(song['Song Length'], skip['Skip Count'], 1)
    best_fit_line = slope * song['Song Length'] + intercept

    plt.close()
    plt.scatter(song['Song Length'], skip['Skip Count'])
    plt.plot(song['Song Length'], best_fit_line, color='red')

    plt.xlabel('Song Length')
    plt.ylabel('Skip Count')
    plt.title('Scatter Plot: Song Length vs. Skip Count')
    plt.savefig(directory + '\\output\\Song Length vs Skip Count.jpg')

def convert_date(date): # Converts the given date format into something more immediately readable.
    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

    formatted_date = date_obj.strftime("%m/%d/%Y")
    
    return formatted_date

def write_to_csv(df):

    specify_artist(df.copy(True), 'Bilmuri')
    most_played_artist(df.copy(True), 10)
    most_skipped_artists(df.copy(True))
    release_year_to_play_count(df.copy(True))
    skip_pct_genre(df.copy(True))
    highest_skip_pct(df.copy(True))
    ratings_vs_play_counts(df.copy(True))
    play_to_skip_ratio(df.copy(True))
    song_length_to_skip_ratio(df.copy(True))

    # Convert song length from ms to MM:SS
    df['Song Length'] = df['Song Length'].astype(int)
    df['Song Length'] = df['Song Length'] / 1000
    df['Song Length'] = pd.to_datetime(df['Song Length'], unit='s').dt.strftime('%M:%S')

    df.to_csv(directory + '\\output\\Music Data.csv', index=False)

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
                    temp_dict['Date Added'] = convert_date(combined_data[i][j][1])
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

    all_data_df = pd.DataFrame(dict_list) # Puts everything in one Dataframe.

    all_data_df['Play Count'] = all_data_df['Play Count'].astype(int)       #| These blocks convert some of the
    all_data_df['Rating'] = all_data_df['Rating'].astype(int)               #| data into more usable data types.
    all_data_df['Release Year'] = all_data_df['Release Year'].astype(int)   #|
    all_data_df['Skip Count'] = all_data_df['Skip Count'].astype(int)       #|

    ratings = [-1, 19, 39, 59, 79, 99, 101]                                             #| I've created bins to convert ratings from
    stars = [0, 1, 2, 3, 4, 5]                                                          #| 0, 20, 40, 60, 80, 100 into how many stars they       
    all_data_df['Rating'] = pd.cut(all_data_df['Rating'], bins=ratings, labels=stars)   #| pertain to.

    write_to_csv(all_data_df)

    itunes.close()

main()