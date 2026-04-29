import xmltodict
import xml.etree.ElementTree as ET
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

path = os.path.realpath(__file__)                        #| Gets the directory
directory = os.path.dirname(path)                        #| for the iTunes
dir_path = directory + '\\XML\\iTunes Music Library.xml' #| XML file.

plt.rcParams['font.family'] = 'DejaVu Serif' #Sets the font. This one was chosen to incorporate some missing Japanese characters.

def prep_xml(dir_path): # Prepares the XML so that it can be read by the program.
    tree = ET.parse(dir_path)
    root = tree.getroot()

    tags_to_replace = ['integer', 'date', 'true', 'false'] # Replace all instances of the word 'integer', 'date', 'true', and 'false'...

    for elem in root.iter():            #| ... and replace them with 'string'. By default, the XML has all of these stored in
        if elem.tag in tags_to_replace: #| different categories, and trying to sort them would be a nightmare. By making them
            elem.tag = 'string'         #| all the same category, they're magically lined up and more easily parsible.

    tree.write(dir_path)

def countXMLelements(dir_path): # This was written by ChatGPT. I only used it to figure out how many elements I needed to loop through to get every element of an XML so that I know how much to loop through.
    tree = ET.parse(dir_path)
    root = tree.getroot()

    def count_elements(element):
        count = 1  
        for child in element:
            count += count_elements(child)
        return count

    total_elements = count_elements(root)

    return total_elements

def tuple_to_dict(lst): # Passes a list of tuples and returns that list as a dictionary.
    dictionary = dict(lst)
    return dictionary

def milliseconds_to_dmhs(ms): # Converts milliseconds into a days/hours/minutes/seconds format.
    seconds = ms / 1000  # Convert milliseconds to seconds
    days = int(seconds // 86400)  # Calculate days
    seconds %= 86400  # Get the remainder of seconds after removing days
    hours = int(seconds // 3600)  # Calculate hours
    seconds %= 3600  # Get the remainder of seconds after removing hours
    minutes = int(seconds // 60)  # Calculate minutes
    seconds %= 60  # Get the remainder of seconds after removing minutes

    return f"{days}d {hours}h {minutes}m {int(seconds)}s"  # Format as "Xd Xh Xm Xs"

def milliseconds_to_ms(df): # Converts milliseconds into minutes/seconds format for dataframes.
    df['Total Listen Time'] = df['Total Listen Time'].astype(int)
    df['Total Listen Time'] = df['Total Listen Time'] / 1000
    df['Total Listen Time'] = pd.to_datetime(df['Total Listen Time'], unit='s').dt.strftime('%H:%M:%S')

    df['Total Time'] = df['Total Time'].astype(int)
    df['Total Time'] = df['Total Time'] / 1000
    df['Total Time'] = pd.to_datetime(df['Total Time'], unit='s').dt.strftime('%M:%S')

    return df

def total_time(time_df): # Calculate total time spent listening to music
    time_df['Total Time'] = pd.to_numeric(time_df['Total Time'], errors='coerce') #| Ensures the values are numeric before calculating- I ran into an issue
    time_df['Play Count'] = pd.to_numeric(time_df['Play Count'], errors='coerce') #| that seemed to be raising them to powers instead of multiplying otherwise.

    time_df['Total Listen Time'] = time_df['Total Time'] * time_df['Play Count']

    return time_df

def specify_artist(art_df, artist):  # Show play counts associated with a specific artist.
    mask = art_df['Artist'] == artist
    filtered_df = art_df[mask]

    filtered_df = filtered_df.sort_values(by='Play Count', ascending=False)

    plt.close()
    plt.figure(figsize=(12, 6))
    ax = filtered_df.set_index('Name')['Play Count'].plot(kind='bar')

    ax.set_xlabel('')
    plt.title(f'{artist} Data')
    plt.xticks(rotation=90, ha='center')
    plt.tight_layout()

    for p in ax.patches:
        height = p.get_height()
        num_str = f'{height:.0f}'
        if len(num_str) == 4:
            offset = -24
        elif len(num_str) == 3:
            offset = -18
        elif len(num_str) == 2:
            offset = -12
        elif len(num_str) == 1:
            offset = -6
        ax.annotate(num_str, (p.get_x() + p.get_width() / 2, height), 
                    ha='center', va='bottom', 
                    xytext=(1, offset), textcoords="offset points", 
                    rotation=90, color='white')

    plt.savefig(directory + '\\output\\Specific Artist.jpg')

def all_most_played_artists(play_df, top): # Done
    play_df = play_df.loc[play_df['Play Count'] > top]
    artists = play_df.groupby('Artist')['Play Count'].sum()
    artists = artists.sort_values(ascending=False)
    
    plt.close()
    artists.plot(kind='bar')

    plt.title(f'Shape of Most Played Artists')
    plt.xlabel('')
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xticklabels([])
    ax.set_xticks([])
    plt.savefig(directory + '\\output\\Most Played Artists.jpg')

def top_20_artists(ten_df): #Done
    ten_df = ten_df.groupby('Artist')['Play Count'].sum()
    ten_df = ten_df.sort_values(ascending=False)
    ten_df = ten_df.iloc[:20]

    plt.close()
    fig, ax = plt.subplots()

    #ax.imshow(plt.imread(directory + '\\Resources\\background.jpg'), extent=[0, 3000, 0, 2000])
    ax.bar(ten_df.index, ten_df.values)

    plt.title(f'Top 20 Most Played Artists')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('')
    plt.tight_layout()

    for p in ax.patches:
        height = p.get_height()
        num_str = f'{height:.0f}'
        offset = -24 if len(num_str) == 4 else -18  # adjust the offset based on the length of the number
        ax.annotate(num_str, (p.get_x() + p.get_width() / 2, height), ha='center', va='bottom', xytext=(1, offset), textcoords="offset points", rotation=90, color='white')

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.savefig(directory + '\\output\\Top 20 Artists.jpg')

def most_skipped_artists(skip_df): # Done
    skips = skip_df.groupby('Artist')['Skip Count'].sum()
    skips = skips.sort_values(ascending=False)
    skips = skips.nlargest(20)
    
    plt.close()
    ax = skips.plot(kind='bar')
    
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.title('Most Skipped Artists')
    plt.xticks(rotation=45, ha='right')
    # plt.tight_layout()
    plt.savefig(directory + '\\output\\Most Skipped Artists.jpg')

def highest_skip_pct(high_df): # Done
    total_skips = high_df['Skip Count'].sum()

    artist_skip = high_df.groupby('Artist')['Skip Count'].sum()
    artist_skip = artist_skip.sort_values(ascending=False)
    artist_skip = (artist_skip / total_skips) * 100
    artist_skip = artist_skip.loc[artist_skip >= .15]

    plt.close()
    ax = artist_skip.plot(kind='bar')

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.title(f'Skip Percentage by Artist (Out of {total_skips} Total Skips)')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Skip %')
    plt.savefig(directory + '\\output\\Most Skipped Artists (pct).jpg')

def release_year_to_play_count(rel_df): # Done
    group = rel_df.groupby('Year')['Play Count'].sum()
    group = group.loc[1:]
    group = group.loc[group > 10]
    
    plt.close()
    ax = group.plot(kind='bar')

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.title(f'Play Count per Release Year')
    plt.ylabel('Play Count')
    plt.savefig(directory + '\\output\\Release Year to Play Count.jpg')

def skip_pct_genre(skip_pct_df): # Done
    total_skips = skip_pct_df['Skip Count'].sum()

    genre_skip = skip_pct_df.groupby('Genre')['Skip Count'].sum()
    genre_skip = genre_skip.sort_values(ascending=False)
    genre_skip = (genre_skip / total_skips) * 100
    genre_skip = genre_skip.iloc[:20]

    plt.close()
    ax = genre_skip.plot(kind='bar')

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.title(f'Skip Percentage by Genre (Out of {total_skips} Total Skips)')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Skip %')
    plt.xlabel('')
    plt.tight_layout()
    plt.savefig(directory + '\\output\\Most Skipped Genres (pct).jpg')

def ratings_vs_play_counts(rat_df): # Done
    plays = rat_df.groupby('Rating', observed=True)['Play Count'].sum()

    plt.close()
    ax = plays.plot(kind='bar')

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.title('Play Counts per Ratings')
    plt.xticks(rotation=0, ha='right')
    plt.savefig(directory + '\\output\\Ratings versus Play Counts.jpg')

def play_to_skip_ratio(play_skip_df):
    plt.close()
    # Calculate Z-scores for play and skip counts
    play_z_scores = np.abs((play_skip_df['Play Count'].astype(float) - play_skip_df['Play Count'].mean()) / play_skip_df['Play Count'].std())
    skip_z_scores = np.abs((play_skip_df['Skip Count'].astype(float) - play_skip_df['Skip Count'].mean()) / play_skip_df['Skip Count'].std())
    
    # Define a threshold for outliers (e.g., 2 standard deviations)
    threshold = 3
    
    # Create a mask for outliers
    outlier_mask = (play_z_scores > threshold) | (skip_z_scores > threshold)

    max_x = max(play_skip_df.loc[outlier_mask, 'Play Count'].astype(float))  # Find the most played song by play count.
    max_y = max(play_skip_df.loc[outlier_mask, 'Skip Count'].astype(float))    # Find the most skipped song by skip count.

    # This chunk gets the name of the most *played* song to display on the scatterplot
    max_play_song = play_skip_df[play_skip_df['Play Count'] == max_x]['Name']
    max_play_song_name = play_skip_df.loc[play_skip_df[play_skip_df.columns[0]] == max_play_song.iloc[0], 'Name'].iloc[0]
    max_play_song_plays = play_skip_df.loc[play_skip_df[play_skip_df.columns[0]] == max_play_song.iloc[0], 'Play Count'].iloc[0]
    max_play_song_skips = play_skip_df.loc[play_skip_df[play_skip_df.columns[0]] == max_play_song.iloc[0], 'Skip Count'].iloc[0]

    # This chunk gets the name of the most *skipped* song to display on the scatterplot
    max_skip_song = play_skip_df[play_skip_df['Skip Count'] == max_y]['Name']
    max_skip_song_name = play_skip_df.loc[play_skip_df[play_skip_df.columns[0]] == max_skip_song.iloc[0], 'Name'].iloc[0]
    max_skip_song_plays = play_skip_df.loc[play_skip_df[play_skip_df.columns[0]] == max_skip_song.iloc[0], 'Play Count'].iloc[0]
    max_skip_song_skips = play_skip_df.loc[play_skip_df[play_skip_df.columns[0]] == max_skip_song.iloc[0], 'Skip Count'].iloc[0]

    # Plot only the outliers
    plt.scatter(play_skip_df.loc[outlier_mask, 'Play Count'].astype(float), play_skip_df.loc[outlier_mask, 'Skip Count'].astype(float))
    plt.annotate(max_play_song_name, xy=(max_play_song_plays, max_play_song_skips), xytext=(0,0), textcoords='offset points', ha='center')  # Label the most played song
    plt.annotate(max_skip_song_name, xy=(max_skip_song_plays, max_skip_song_skips), xytext=(0,0), textcoords='offset points', ha='center')  # Label the most skipped song
    plt.xlabel('Play Count')
    plt.ylabel('Skip Count')

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.savefig(directory + '\\output\\Play to Skip Ratio Outliers.jpg')

def convert_date(date): # Converts the given date format into something more immediately readable.
    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

    formatted_date = date_obj.strftime("%m/%d/%Y")
    
    return formatted_date

def write_to_csv(df):
    df = total_time(df.copy(True))
    total_play_time = milliseconds_to_dmhs(df['Total Listen Time'].sum())
    print(f"Total play time of library: {total_play_time}")

    artists = df['Artist'].to_list()
    artists = list(set(artists))
    artists.sort()

    cont = False
    while not cont:  # Data Validation Loop
        choice = input("Which artist do you want to see specific data about?: ")
        if choice in artists:
            cont = True
        else:
            data = input("Artist not found in list. Would you like to see a list of valid artist names? (Y/N): ")
            if data == 'Y' or data == 'y':
                pprint(artists)
            else:
                cont = False

    df = milliseconds_to_ms(df.copy(True))

    # List of functions to call with their respective arguments
    functions_to_call = [
        (specify_artist, (df.copy(True), choice)),
        (all_most_played_artists, (df.copy(True), 10)),
        (top_20_artists, (df.copy(True),)),
        (most_skipped_artists, (df.copy(True),)),
        (release_year_to_play_count, (df.copy(True),)),
        (skip_pct_genre, (df.copy(True),)),
        (highest_skip_pct, (df.copy(True),)),
        (ratings_vs_play_counts, (df.copy(True),)),
        (play_to_skip_ratio, (df.copy(True),))
    ]

    for func, args in tqdm(functions_to_call, desc="Generating...", unit="function"):  #| Generates the loading bar. Ran into issues with varied arguments,
        func(*args)  # Unpack the arguments for each function                          #| and this turned out to be the solution.

    df = df.rename(columns={'Total Time': 'Song Length', 'Year': 'Release Year', 'Name': 'Song Title'})

    df.to_csv(directory + '\\output\\_Music Data.csv', index=False)         #| General .csv filetype for viewing without excel.

    output_file_path = directory + '\\output\\_Music Data.xlsx'             #| Writes the file as
    with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:   #| an xlsx in case I want
        df.to_excel(writer, index=False, sheet_name='Music Data')           #| to implement conditional formatting later.

    print(f"Done! Files are located at {directory}\\output.")

def main():
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

    for i in range(len(combined_data)):
        try:
            dict_list.append(tuple_to_dict(combined_data[i]))
        except:
            break

    all_data_df = pd.DataFrame(dict_list) # Puts everything in one Dataframe.

    all_filtered_data = all_data_df[interesting_data]

    all_filtered_data = all_filtered_data.fillna(0).astype({'Year': 'int', 'Play Count': 'int', 'Skip Count': 'int', 'Rating': 'int'})

    ratings = [-1, 19, 39, 59, 79, 99, 101]                                                         #| I've created bins to convert ratings from
    stars = [0, 1, 2, 3, 4, 5]                                                                      #| 0, 20, 40, 60, 80, 100 into how many stars they       
    all_filtered_data['Rating'] = pd.cut(all_filtered_data['Rating'], bins=ratings, labels=stars)   #| pertain to.

    write_to_csv(all_filtered_data)

    itunes.close()

main()