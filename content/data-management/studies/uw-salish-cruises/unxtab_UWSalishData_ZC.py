# %%
#!/usr/bin/env python
# unxtab_salish_cfg_file_generation.ipynb
#
# PURPOSE
#   Loop through the "Salish_Cruises" directory to read in all UW salish ctd/bottle data and create a .cfg file for each file.  
#   Also will execute the un-xtab.py cmd line script to successfully flip all original data into long useable format
#
# PROJECT
#   6983: phyto indicator PS partnership
#
# NOTES
#   1. Originally ran on zach caslers local computer with "Salish_Cruises" directory. Check requirements.txt to replicate.
#   2. There are two sections built into this script to handle the different groupings of source data.  SECTION 1 handles all the older data,
#       The original csv files from 1998 to 2015 both upcase and downcast files are the same format.  SECTION 2 handles all the newer data,
#       The original xlsx files from 2016 to 2023. But processes upcast and downcast differently due to the data templates being different.
#   3. This script creates multiple intermediary files in order to get to the unxtabbed final result as long as the source data is a csv 
#       it will process file for the old data in section 1, in section 2 it converts the <filename.xlsx> to <filename.csv> then:
#       - first it creates the <filename>_m.csv version of the file to add the metadata like the source file etc.
#       - next it creates the <filename_m>.cfg
#       - and finally it will create a untabbed_<filename_m>.csv that will be what we use to join the data in the sql loading script
#
# AUTHOR(S)
#   Zach Casler (ZC)
#
# HISTORY
#  Date      Remarks
# ---------- -------------------------------------------------------------
# 2024-06-27 script completed everything ran successfully on ZC's personal computer
# 2024-08-10 script converted to run off of server paths and ran successfully
# ==========================================================================


#generate un-tab.py cfg files for all uw salish data
#import pandas as pd
import polars as pl
from pathlib import Path
import subprocess
#import re
from xlsx2csv import Xlsx2csv
import sys

pl.Config.set_fmt_str_lengths(45)


#important function to get proper path format to run subprocess un-xtab.py
def cmd_format_path(path_obj):
    posix_path = path_obj.as_posix()               # Convert to POSIX path
    windows_path = posix_path.replace('/', '\\')   # Replace forward slashes with backslashes
    formatted_path = f'.\\{windows_path}'          # Prepend .\ for relative path notation
    return formatted_path

#set salish data path directory
directory = Path('../../../../Data_Inventory/_University_of_Washington/Salish_Cruises')

## BELOW is the working subprocess in a loop for all csvs

# %%
# Looping for creating all un-xtab.py cmd line statements in a format to use for subprocesses 
# WORKING RUNS THROUGH ALL CSVS AND UNTABBS CURRENT FILE WITH A SUBPROCESS CMD LINE
#
#   20240613 -- Successfully ran through all pre 2016 data files took approx 8 minutes to unxtab all of the files
#   20240617 -- Running again, added 'None' station filtering, strip() header and data for white spaces, Ran successfully took about 11 minutes
#   20240703 -- caleb and zach fixed filepaths to work with salish data directory and un subprocesses successfully

#### SECTION 1 ####

# csv handling
# Get a list of directories in the specified directory
folders = [f for f in directory.iterdir() if f.is_dir() and f.name.endswith("Data")]

# Filter folders where the year in the name is 2016 or greater
filtered_folders = []
for folder in folders:
    folder_parts = folder.name.split('-')
    year = int(folder_parts[1].split('_')[0])
    # Debug: Print each folder and the extracted year
    # print(f"Folder: {folder.name}, Extracted Year: {year}")
    if year is not None and year <= 2015:
        filtered_folders.append(folder)

folder_count = 0
file_count = 0
# Print the list of filtered directories
# print("\nFiltered directories (2015 or less):")
for folder in filtered_folders:  #gets all pre 2016 folders
    folder_count += 1

    for file in folder.glob("*.csv"): # only checks the files that end in ".csv"
        
        if file.name.endswith(("downcast.csv","upcast.csv")): #only checks upcast and downcast csvs
            file = file.resolve()

            #init cmd line run for current file
            cmd = ['~/houston-dc-jobs/data-management/bin/un-xtab.py','-c']

            file_count += 1
            print(f'folder_count {folder_count}')
            print(f'file count {file_count}')
            print(f'curr filename {file.name}')

            #read and insert meta data
            curr_df = pl.read_csv(file)

            # Determine cast based on file name
            if 'downcast' in file.name.lower():
                cast_type = 'downcast'
            elif 'upcast' in file.name.lower():
                cast_type = 'upcast'
            else:
                cast_type = 'N/A'
            curr_df = curr_df.insert_column(0, pl.Series('cast_type', [cast_type]*len(curr_df)))

            # insert source filename and path as new columns
            curr_df = curr_df.insert_column(0, pl.Series('source_filename', [file.name]*len(curr_df)))
            curr_df = curr_df.insert_column(0, pl.Series('source_path', [str(file)]*len(curr_df)))

            # strip column heaeders of any white spaces
            curr_df = curr_df.rename({col: col.strip() for col in curr_df.columns})

            # Strip whitespace from each cell in the DataFrame
            curr_df = curr_df.with_columns([pl.col(col).str.strip_chars().alias(col) for col in curr_df.columns])

            # filter out any "None" Stations to be ignored on import
            metadata_rows = curr_df.head(2) #get the meta data rows
            curr_df = curr_df.slice(2) # remove the meta data rows so we dont duplicate them
            curr_df = curr_df.filter(pl.col('Station') != 'None') # filter out any rows with a 'None' station to be ignored on import
            curr_df = pl.concat([metadata_rows,curr_df])

            curr_file_new_name = file.parent / f'{file.stem}_m.csv'
            # EXPORT INTO NEW CSV SO WE CAN RUN UNXTAB ON THIS VERSION OF FILE W Orig filepath 
            # and file name and cast type NEW FILE = same name + "_m" for metadata
            curr_df.write_csv(curr_file_new_name)

            curr_cfg_filepath = file.parent / f'{file.stem}_m.cfg' # save proper cfg file name

            # CFG file generation below
            if 'Pressure' in curr_df.columns:
                if (curr_df.get_column_index('Pressure') + 1) != 11: # +1 because index is 0 based
                    print(f'CURRENT FILE: {file.name} Does not have PRESSURE at expected INDEX, using value of 11 anyway. PLEASE CHECK FILE')
                data_cols_start = 11
                if (curr_df.get_column_index('Depth') + 1) != 12: # +1 because index is 0 based
                    print(f'CURRENT FILE: {file.name} Does not have DEPTH at expected INDEX, using value of 11 anyway. PLEASE CHECK FILE')
                data_cols_start = 11
            else:
                print(f'CURRENT FILE: {file.name} Does not have PRESSURE in the HEADERS at all, using value of 11 anyway. PLEASE CHECK FILE')
                data_cols_start = 11
                if 'Depth' not in curr_df.columns: # check for depth as well
                    print(f'CURRENT FILE: {file.name} Does not have DEPTH in the HEADERS at all, using value of 11 anyway. PLEASE CHECK FILE')
                    data_cols_start = 11
           
            print('start col    ',data_cols_start)
            data_cols_end = curr_df.width
            print('end col      ',data_cols_end)
            data_rows_start = 4 #SET MANUALLY
            print('start row    ', data_rows_start)
            data_rows_end = len(curr_df) + 1 # +1 to account for header being a row in excel
            print('end row      ',data_rows_end)
            #SET MANUALLY (Should be same value as start col if pressure is first col) --we want pressure in the row header and data to include as primary key
            row_headers_end = data_cols_start + 1 # add one to get depth in the row headers but still pull pressure and depth as variables
            print('row hdr end  ',row_headers_end)

            #cfg generation for all csv (up and downcasts are in same data structure) (pre 2016 data ONLY)
            if file.suffix == '.csv':
                with open(curr_cfg_filepath, 'w') as cfg_file:
                    cfg_file.write(f"[{file.stem}_m]\n")
                    cfg_file.write(f"data_columns={data_cols_start}-{data_cols_end}\n")
                    cfg_file.write(f"data_rows={data_rows_start}-{data_rows_end}\n")
                    cfg_file.write(f"row_headers=1-{row_headers_end}\n")
                    cfg_file.write(f"row_headers_row=1\n")
                    cfg_file.write(f"column_header_rows=1-3\n") # known that there are only 3 SET MANUALLY
                    cfg_file.write(f"column_group_count=1\n")
                    cfg_file.write(f"column_header_label_1=result_value\n")
                    cfg_file.write(f"header_as_column_1=1,1,col_name\n")
                    cfg_file.write(f"header_as_column_2=2,1,units\n")
                    cfg_file.write(f"header_as_column_3=3,1,ctd_status")
            else:
                print(f"file:{file.name} failed, filetype not csv")
            
            # # building cmd line to pass into subprocess
            cmd.append(f"'{curr_cfg_filepath.as_posix()}'")
            cmd.append(f"'{curr_file_new_name.as_posix()}'")
            cmd.append(f"'{(curr_file_new_name.parent / ('untabbed_' + curr_file_new_name.name)).as_posix()}'")
            cmd = [' '.join(cmd)]
            print('curr cmd list: ', cmd)
            
            unxtab_run = subprocess.run(cmd, shell=True)

            # Print the output of current subprocess
            print('direct output:', unxtab_run)
            print("stdout:", unxtab_run.stdout)
            print("stderr:", unxtab_run.stderr)
            print("Return code:", unxtab_run.returncode)

            print('-----------------end------------------')



# %%
## BELOW IS EVERYTHING FOR 2016 and up files where downcast and upcast are different formats and all are stored in xlsx

# successfully converted all xlsx files to csv only clean ones that end in downcast or upcast # DO NOT NEED TO RUN AGAIN
# DO NOT NEED TO RUN AGAIN UNLESS we have new data to convert then just uncomment the below code chunk


# folders = [f for f in directory.iterdir() if f.is_dir() and f.name.endswith("Data")]
# # Filter folders where the year in the name is 2016 or greater to get just the new .xlsx data
# filtered_folders = []
# for folder in folders:
#     folder_parts = folder.name.split('-')
#     year = int(folder_parts[1].split('_')[0])
#     # Debug: Print each folder and the extracted year
#     # print(f"Folder: {folder.name}, Extracted Year: {year}")
#     if year is not None and year >= 2016:
#         filtered_folders.append(folder)

# # Print the list of filtered directories
# # print("\nFiltered directories (2016 or greater):")
# for folder in filtered_folders:
#     #print(folder.name)
#     for file in folder.glob("*.xlsx"):
#         if file.name.endswith(("downcast.xlsx","upcast.xlsx")):
#             curr_filepath = file
#             print(curr_filepath)
#             csv_output = str(file.parent / f'{file.stem}.csv')
#             print(csv_output)
#             Xlsx2csv(curr_filepath, outputencoding="utf-8").convert(outfile=csv_output, sheetid=1)
#             # Xlsx2csv().convert() redundant line dont need


# SUCCESSFUlly RAN ALL XLSX CONVERTED TO CSVS if name ended in upcast or downcast


# %%

#### SECTION 2 ####

# xlsx handling post 2015 data
# 20240619 - ran without untabbing and successfully created all metata data versions of csv up and down casts
# 20240621 - ran through all 2016+ upcast and downcast files, created cfg files and successfully untabbed all files

#init counter variables
folder_count = 0
file_count = 0

# Loop through each file in the directory

folders = [f for f in directory.iterdir() if f.is_dir() and f.name.endswith("Data")]

# Filter folders where the year in the name is 2016 or greater
filtered_folders = []
for folder in folders:
    folder_parts = folder.name.split('-')
    year = int(folder_parts[1].split('_')[0])
    # Debug: Print each folder and the extracted year
    # print(f"Folder: {folder.name}, Extracted Year: {year}")
    if year is not None and year >= 2016:
        filtered_folders.append(folder)


#init list to store filenames that need to be checked
files_to_check = []
for folder in filtered_folders:
    folder_count += 1
    print(f'folder_count {folder_count}')
    print(f'folder name: {folder.name}')

    for file in folder.glob("*.csv"): # only checks the files that end in ".csv"
        
        if file.name.endswith(("downcast.csv","upcast.csv")): #only checks upcast and downcast csvs
        #if file.name.endswith(("April2016_labupcast.csv")): # Testing statement for just 1 file
            file = file.resolve()
            #init cmd line run for current file
            cmd = ['~/houston-dc-jobs/data-management/bin/un-xtab.py','-c']

            file_count += 1
            print(f'file count {file_count}')
            print(f'curr filename {file.name}')

            #read and insert meta data
            curr_df = pl.read_csv(file,infer_schema_length=0)
            # drop null rows that are appended to the end for some reason
            curr_df = curr_df.filter(~pl.all_horizontal(pl.all().is_null()))
            # Determine cast based on file name
            if 'downcast' in file.name.lower():
                cast_type = 'downcast'
            elif 'upcast' in file.name.lower():
                cast_type = 'upcast'
            else:
                cast_type = 'N/A'

            curr_df = curr_df.insert_column(0, pl.Series('cast_type', [cast_type]*len(curr_df)))

            # insert source filename and path as new columns
            curr_df = curr_df.insert_column(0, pl.Series('source_filename', [file.name]*len(curr_df)))
            curr_df = curr_df.insert_column(0, pl.Series('source_path', [str(file)]*len(curr_df)))

            # strip column heaeders of any white spaces
            curr_df = curr_df.rename({col: col.strip() for col in curr_df.columns})
            # change cast to cast_no so it doesnt break sql
            curr_df = curr_df.rename({col: col.replace("Cast", "cast_no") for col in curr_df.columns if "Cast" in col})

            # Strip whitespace from each cell in the DataFrame
            curr_df = curr_df.with_columns([pl.col(col).str.strip_chars().alias(col) for col in curr_df.columns])
            
            curr_cfg_filepath = file.parent / f'{file.stem}_m.cfg' # save proper cfg file name

            if file.name.endswith('downcast.csv'):
                # filter out any "None" Stations to be ignored on import
                metadata_rows = curr_df.head(1) #get the meta data rows
                curr_df = curr_df.slice(1) # remove the meta data rows so we dont duplicate them
                curr_df = curr_df.filter(pl.col('Station') != 'None') # filter out any rows with a 'None' station to be ignored on import
                curr_df = pl.concat([metadata_rows,curr_df])

                # CFG file generation below
                if 'prDM: Pressure  Digiquartz' in curr_df.columns: #checks to see if pressure is in the columns
                    if (curr_df.get_column_index('prDM: Pressure  Digiquartz') + 1) != 14: # +1 for zero index in cols
                        print(f'CURRENT FILE: {file.name} Does not have PRESSURE at expected INDEX, using value of 14 anyway. PLEASE CHECK FILE')
                        files_to_check.append(file.name)
                    if (curr_df.get_column_index('depSM: Depth') + 1) != 15: # +1 for zero index in cols
                        print(f'CURRENT FILE: {file.name} Does not have DEPTH at expected INDEX, using value of 14 anyway. PLEASE CHECK FILE')
                        files_to_check.append(file.name) 
                    data_cols_start = 14
                elif 'prdM: Pressure  Strain Gauge' in curr_df.columns: # alt check for files where they named it pressure strain gauge...
                    if (curr_df.get_column_index('prdM: Pressure  Strain Gauge') + 1) != 14: # +1 for zero index in cols
                        print(f'CURRENT FILE: {file.name} Does not have PRESSURE at expected INDEX, using value of 14 anyway. PLEASE CHECK FILE')
                        files_to_check.append(file.name)
                    data_cols_start = 14
                else:
                    print(f'CURRENT FILE: {file.name} Does not have PRESSURE in the column HEADERS, using value of 14 anyway. PLEASE CHECK FILE')
                    files_to_check.append(file.name)
                    data_cols_start = 14
                    if 'depSM: Depth' not in curr_df.columns: # check for depth as well
                        print(f'CURRENT FILE: {file.name} Does not have DEPTH in the column HEADERS, using value of 14 anyway. PLEASE CHECK FILE')
                        files_to_check.append(file.name)
                        data_cols_start = 14
                
                print('start col    ',data_cols_start)
                data_cols_end = curr_df.width
                print('end col      ',data_cols_end)
                data_rows_start = 3 #SET MANUALLY
                print('start row    ', data_rows_start)
                data_rows_end = len(curr_df) + 1 # +1 to account for header being a row in excel
                print('end row      ',data_rows_end)
                #SET MANUALLY (Should be same value as start col if pressure is first col) --we want pressure in the row header and data to include as primary key
                row_headers_end = data_cols_start + 1 # add one to get depth in the row headers but still pull pressure and depth as variables
                print('row hdr end  ',row_headers_end)

                #check if col 'flag:flag'

                #cfg generation for post 2015 DOWNCAST data ONLY
                if file.suffix == '.csv':
                    with open(curr_cfg_filepath, 'w') as cfg_file:
                        cfg_file.write(f"[{file.stem}_m]\n")
                        cfg_file.write(f"data_columns={data_cols_start}-{data_cols_end}\n")
                        cfg_file.write(f"data_rows={data_rows_start}-{data_rows_end}\n")
                        cfg_file.write(f"row_headers=1-{row_headers_end}\n") ## col 'flag:flag' ??
                        cfg_file.write(f"row_headers_row=1\n")
                        cfg_file.write(f"column_header_rows=1-2\n") # known that there are only 2 SET MANUALLY
                        cfg_file.write(f"column_group_count=1\n")
                        cfg_file.write(f"column_header_label_1=result_value\n")
                        cfg_file.write(f"header_as_column_1=1,1,col_name\n")
                        cfg_file.write(f"header_as_column_2=2,1,units\n")
                else:
                    print(f"file:{file.name} failed, filetype not csv")
                    
            # IF UPCAST write a DIFFERENT CFG FILE
            elif file.name.endswith('upcast.csv'):
                curr_df = curr_df.filter(pl.col('STATION_NO') != 'None') # remove all rows with no station logged
                
                # CFG file generation below
                if 'CTDPRS_DBAR' in curr_df.columns: #checks to see if pressure is in the columns
                    if (curr_df.get_column_index('CTDPRS_DBAR') + 1) != 17: # +1 for zero index in cols
                        print(f'CURRENT FILE: {file.name} Does not have PRESSURE at expected INDEX, using value of 17 anyway. PLEASE CHECK FILE')
                        files_to_check.append(file.name) 
                    if (curr_df.get_column_index('DEPTH (M)') + 1) != 18: # +1 for zero index in cols
                        print(f'CURRENT FILE: {file.name} Does not have DEPTH at expected INDEX, using value of 17 anyway. PLEASE CHECK FILE')
                        files_to_check.append(file.name)
                    data_cols_start = 17
                else:
                    print(f'CURRENT FILE: {file.name} Does not have PRESSURE in the column HEADERS, using value of 17 anyway. PLEASE CHECK FILE')
                    files_to_check.append(file.name)
                    data_cols_start = 17
                    if 'DEPTH (M)' not in curr_df.columns: #checks to see if depth exists in the cols
                        print(f'CURRENT FILE: {file.name} Does not have DEPTH in the column HEADERS, using value of 17 anyway. PLEASE CHECK FILE')
                        files_to_check.append(file.name)
                        data_cols_start = 17
                
                print('start col    ',data_cols_start)
                data_cols_end = curr_df.width
                print('end col      ',data_cols_end)
                data_rows_start = 2 #SET MANUALLY
                print('start row    ', data_rows_start)
                data_rows_end = len(curr_df) + 1 # +1 to account for header being a row in excel
                print('end row      ',data_rows_end)
                #SET MANUALLY (Should be same value as start col if pressure is first col) --we want pressure in the row header and data to include as primary key
                row_headers_end = data_cols_start + 1 # add one to get depth in the row headers but still pull pressure and depth as variables
                print('row hdr end  ',row_headers_end)


                #cfg generation for post 2015 UPCAST data ONLY
                if file.suffix == '.csv':
                    with open(curr_cfg_filepath, 'w') as cfg_file:
                        cfg_file.write(f"[{file.stem}_m]\n")
                        cfg_file.write(f"data_columns={data_cols_start}-{data_cols_end}\n") # manually adding all the flag and comment columns to header
                        cfg_file.write(f"data_rows={data_rows_start}-{data_rows_end}\n")
                        cfg_file.write(f"row_headers=1-{row_headers_end},21,22,25,26,32,33,39,40,44,51,56,60,62,64\n")
                        cfg_file.write(f"row_headers_row=1\n")
                        cfg_file.write(f"column_header_rows=1\n") # known that there are only 2 SET MANUALLY
                        cfg_file.write(f"column_group_count=1\n")
                        cfg_file.write(f"column_header_label_1=result_value\n")
                        cfg_file.write(f"header_as_column_1=1,1,col_name\n")
                else:
                    print(f"file:{file.name} failed, filetype not csv")

            # EXPORT INTO NEW CSV SO WE CAN RUN UNXTAB ON THIS VERSION OF FILE W Orig filepath 
            # file name and cast type. NEW FILE = same filename name + "_m" for metadata
            curr_file_new_name = file.parent / f'{file.stem}_m.csv'
            curr_df.write_csv(curr_file_new_name)

            # building cmd line to pass into subprocess
            cmd.append(f"'{curr_cfg_filepath.as_posix()}'")
            cmd.append(f"'{curr_file_new_name.as_posix()}'")
            cmd.append(f"'{(curr_file_new_name.parent / ('untabbed_' + curr_file_new_name.name)).as_posix()}'")
            cmd = [' '.join(cmd)]
            print('curr cmd list: ', cmd)
            
            unxtab_run = subprocess.run(cmd, shell=True)

            # Print the output of current subprocess
            print('direct output:', unxtab_run)
            print("stdout:", unxtab_run.stdout)
            print("stderr:", unxtab_run.stderr)
            print("Return code:", unxtab_run.returncode)

            print('-----------------end------------------')
print('files to check:', files_to_check)

# End of script
