#!/usr/bin/env python
# coding: utf-8

# # Train, promote and deploy Boston house prices prediction model

# This notebook contains steps and code to demonstrate support of AI Lifecycle features in Cloud Pak for Data. 
# It contains steps and code to work with [`cpdctl`](https://github.com/IBM/cpdctl) CLI tool available in IBM github repository. 
# It also introduces commands for getting model and training data, persisting model, deploying model
# and promoting it between deployment spaces.
# 
# Some familiarity with Python is helpful. This notebook uses Python 3.7.
# 

# In[1]:


# import base64
import json
import os
# import platform
# import requests
# import tarfile
# import zipfile
# from IPython.core.display import display, HTML
from decouple import config
from simple_term_menu import TerminalMenu


# ## CPD Credentials

# In[2]:
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CPD_USER_NAME =  config('WKCUSER')
CPD_USER_PASSWORD =  config('PASSWORD')
CPD_URL =  config('TZHOSTNAME')

version_r = os.popen('cpdctl version').read()

CPDCTL_VERSION = version_r
CPDCTL_VERSION=CPDCTL_VERSION.strip()

print("cpdctl version: {}".format(CPDCTL_VERSION))


# ### Add CPD profile and context configuration

# Add "cpd_user" user to the `cpdctl` configuration

# In[6]:

os.system('cpdctl config user set cpd_user --username '+CPD_USER_NAME+ ' --password '+CPD_USER_PASSWORD)


# Add "cpd" profile to the `cpdctl` configuration

# In[7]:


os.system('cpdctl config profile set cpd --url ' +CPD_URL+' --user cpd_user')


# Add "cpd" context to the `cpdctl` configuration

# In[8]:


os.system('cpdctl config context set cpd --profile cpd --user cpd_user')


# List available contexts

# In[9]:

os.system('cpdctl config context list')


# In[10]:


os.system('cpdctl config context use cpd')


# List available projects in current context

# In[11]:

#####################Function to select an existing project#####################
def existing_projects():
    options = []
    service_info = {}
    data = json.loads(os.popen("cpdctl project list --output json").read())
    # print(data)
    entries=data['total_results']
    # print(entries)
    if(entries>1): #incase there are more than one existing project
        for i in range(0,len(data)):
            #########creating list of existing projects#########
            options.append(data['resources'][i]['entity']['name'])
            service_info[i] = {
                "name": data['resources'][i]['entity']['name'],
                "guid": data['resources'][i]['metadata']['guid']
            }
        #########Printing the menu in the terminal#########
        terminal_menu = TerminalMenu(options,title = "\nSelect a Project to export\n", menu_cursor_style = ("fg_cyan", "bold"), menu_highlight_style =("bold",))
        menu_entry_index = terminal_menu.show()
        return service_info[menu_entry_index]['guid']  # return guid of selected project
    else: #incase there is only one existing project 
        return data['resources'][0]['metadata']['guid']  # return guid of the single existing project
#####################End of function existing_projects#####################



## Access the selected project assets

# Get cpdctl-demo project ID and show details

# In[12]:

PROJECT_ID=existing_projects()   #function call to list the existing projects and returning the selected project guid
# print(PROJECT_ID)


# In[13]:

PROJECT_ID=PROJECT_ID.strip()
os.system(' cpdctl project get --project-id '+PROJECT_ID)


# Get project details in JSON format and extract it's name

# In[14]:


os.system(' cpdctl project get --project-id '+PROJECT_ID+' --output json')


# In[15]:


result = os.popen('cpdctl project get --project-id '+PROJECT_ID+' --output json --jmes-query "entity.name" --raw-output').read()
PROJECT_NAME = result
print("{}project ID is: {}".format(PROJECT_NAME, PROJECT_ID))

EXPORT = {
    "all_assets": True
}
EXPORT_JSON = json.dumps(EXPORT)
print(EXPORT_JSON)
result = os.popen('cpdctl asset export start --project-id '+PROJECT_ID+ ' --assets \''+EXPORT_JSON+'\' --name demo-project-assets --output json --jmes-query "metadata.id" --raw-output').read()
EXPORT_ID = result
print('Export ID: {}'.format(EXPORT_ID))
EXPORT_ID=EXPORT_ID.strip()
os.system('cpdctl asset export download --project-id '+PROJECT_ID+' --export-id '+EXPORT_ID+' --output-file project-assets.zip --progress')
