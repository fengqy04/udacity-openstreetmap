
# coding: utf-8

# In[1]:

# Imports

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict


# In[2]:

FILENAME = 'sample.osm'


# In[3]:

st_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# In[4]:

# List of expected street types

expected_st_types = ['Street', 'Avenue', 'Boulevard', 'Drive', 'Court', 'Place',                     'Square', 'Lane', 'Road', 'Trail', 'Parkway', 'Commons',                     'Terrace', 'Broadway', 'Center', 'Circle', 'Expressway',                     'Highway', 'Way']


# In[5]:

# Define the function to audit street type

def audit_st_type(st_types, st_name):
    m = st_type_re.search(st_name)
    if m:
        st_type = m.group()
        if st_type not in expected_st_types:
            st_types[st_type].add(st_name)


# In[6]:

# Define the function to audit street names

def audit_st(filename):
    st_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == "way" or elem.tag == 'node':
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:street':
                    audit_st_type(st_types, tag.attrib['v'])
    return st_types


# In[7]:

st_types = audit_st(FILENAME)
pprint.pprint(dict(st_types))


# In[8]:

# From the audit results of the sample, I create the mapping dictionary for updating the street names.
# I am not going to change street names like "South Avenue D" because they are correct.

mapping = {'St': 'Street',
           'St.': 'Street',
           'Ave': 'Avenue',
           'Rd.': 'Road',
           'Trl': 'Trail',
           'Ct': 'Court',
           'Dr': 'Drive'
            }


# In[9]:

# Define the function to update the street names.

def update_st_name(name):
    for old_type in mapping:
        if name.endswith(old_type):
            new_type = mapping[old_type]
            name = name[:(len(name) - len(old_type))] + new_type
    return name


# In[10]:

# Take a look at the updated street names

for st_type, ways in st_types.iteritems():
    for name in ways:
        better_name = update_st_name(name)
        if better_name != name:
            print name, "=>", better_name


# In[ ]:



