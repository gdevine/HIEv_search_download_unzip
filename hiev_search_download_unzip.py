'''
Python script to perform a HIEv search api call (based on given query parameters) and then download the resultant 
files to local disk (if not already exisitng) 

Author: Gerard Devine
Date: August 2015


- Note: A valid HIEv API key is required  

'''

import os
import json
import urllib2
import zipfile
from datetime import datetime


# -- Set up global values
request_url = 'https://hiev.uws.edu.au/data_files/api_search'
# Either set your api key via an environment variable (recommended) or add directly below 
api_token = os.environ['HIEV_API_KEY']
#api_token = 'my_api_key'


# -- Set up parameters in which to do the HIEv API search call (see dc21 github wiki for full list of choices available)
experiment_ids = [43]
filenames = 'BMS_S39_.*\.zip$'


# --Open log file for writing and append date/time stamp into file for a new entry
logfile = 'log.txt'
log = open(os.path.join(os.path.dirname(__file__), logfile), 'a')
log.write('\n----------------------------------------------- \n')
log.write('------------  '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'  ------------ \n')
log.write('----------------------------------------------- \n')


# -- Set up the http request and handle the returned response
request_headers = {'Content-Type' : 'application/json; charset=UTF-8', 'X-Accept': 'application/json'}
request_data = json.dumps({'auth_token': api_token, 'experiments':experiment_ids, 'filename':filenames})
request  = urllib2.Request(request_url, request_data, request_headers)
response = urllib2.urlopen(request)
js = json.load(response)


# If there are returned results then proceed to download
log.write(' Number of search results returned = %s \n' %len(js))
if len(js):
    # -- Set up a directory to hold downloaded files and unzipped files (if not already existing)
    dest_dir = os.path.join(os.path.join(os.path.dirname(__file__), 'data'))
    unzipped_dir = os.path.join(os.path.dirname(__file__), 'data', 'unzipped')
    if not os.path.exists(unzipped_dir):
        os.makedirs(unzipped_dir)
        
    # --For each element returned pass the url to the download API and download
    for entry in js:
        # Check if the file already exists
        if not os.path.isfile(os.path.join(dest_dir, entry['filename'])):
            # download the file into memory
            download_url = entry['url']+'?'+'auth_token=%s' %api_token
            request = urllib2.Request(download_url)
            f = urllib2.urlopen(request)
            # -- Write the file to disk and close it
            with open(os.path.join(dest_dir, entry['filename']), 'w') as local_file:
                local_file.write(f.read())
            local_file.close()
            log.write(' Success: File Downloaded - %s \n' %entry['filename'])
            
    	    # If the current file is a zipped file, unzip it
    	    if entry['filename'].endswith(".zip"):
                # first check that an unzip directory for that zipped file hasn't already been created, otherwise create it
                zipname = os.path.splitext(entry['filename'])[0]
                if not os.path.join(unzipped_dir, zipname):
                    os.makedirs(unzipped_dir, zipname)
                zfile = zipfile.ZipFile(os.path.join(dest_dir, entry['filename']))		    
                zfile.extractall(os.path.join(unzipped_dir, zipname))
     	        log.write(' Success: File Unzipped - %s \n' %entry['filename'])
        else:
            log.write(' Warning: File Exists - %s \n' %entry['filename'])

    log.write('-- Complete \n')
else:
    log.write('No files matched the search params \n')
    log.write('\n')
    log.write('\n')


# --Close log file
log.close()
