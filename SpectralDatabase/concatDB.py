#!/usr/bin/python3
import pandas as pd
import glob

loc         = 'tab'
# Define the path to your files
files_path  = '/data/Campaign/'+loc.upper()+'/Spectral_DB/HRspDB*_v2.dat'  # Replace with the actual path and file extension
outout_file = '/data/Campaign/'+loc.upper()+'/Spectral_DB/HRspDB_concat_v2.dat' 

# Get a list of file names matching the pattern
file_list = glob.glob(files_path)
file_list.sort()

#file_list = ['HRspDB_tab_2015_v2.dat', 'HRspDB_tab_2016_v2.dat', 'HRspDB_tab_2017_v2.dat', 'HRspDB_tab_2018_v2.dat', 'HRspDB_tab_2019_v2.dat', 'HRspDB_tab_2020_v2.dat', 'HRspDB_tab_2021_v2.dat', 'HRspDB_tab_2022_v2.dat']

# Initialize an empty DataFrame to store the concatenated data
concatenated_df = pd.DataFrame()

# Loop through the files and concatenate them
for file_name in file_list:
    # Read each file into a DataFrame
    current_df = pd.read_csv(file_name)
    
    # Append the current DataFrame to the concatenated DataFrame
    concatenated_df = concatenated_df.append(current_df, ignore_index=True)

# Save the concatenated DataFrame to a new file
concatenated_df.to_csv(outout_file, index=False)  # Replace with the desired output path