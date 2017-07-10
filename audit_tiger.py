
# coding: utf-8

# In[9]:

# Imports

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

from audit_street_name import audit_st_type
from audit_postal_code import audit_citypc


# In[10]:

FILENAME = 'sample.osm'


# In[11]:

# Define the function to find out Tiger data

def is_tiger(elem):
    for tag in elem.iter('tag'):
        if tag.attrib['k'].startswith('tiger:'):
            return True
    return False


# In[12]:

# Define the function to audit street names in Tiger data

def audit_tiger(filename):
    st_types_tiger = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == "way" or elem.tag == 'node':
            if is_tiger(elem):
                for tag in elem.iter('tag'):
                    if tag.attrib['k'] == 'name':
                        audit_st_type(st_types_tiger, tag.attrib['v'])
    return st_types_tiger


# In[17]:

st_types_tiger = audit_tiger(FILENAME)
pprint.pprint(dict(st_types_tiger))

# No need to update street name for Tiger data in the sample - there is no abbreviation


# In[14]:

# Define the function to audit postal codes in Tiger data

def audit_pc_tiger(filename):
    city_pcs_tiger = defaultdict(dict)
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            if is_tiger(elem):
                city = ''
                pc = ''
                for tag in elem.iter('tag'):
                    if tag.attrib['k'] == 'tiger:county':
                        city = tag.attrib['v']
                    if tag.attrib['k'].startswith('tiger:zip'):
                        pc = tag.attrib['v']
                if city != '' or pc != '':
                    audit_citypc(city_pcs_tiger, city, pc)
    return city_pcs_tiger


# In[15]:

city_pcs_tiger = audit_pc_tiger(FILENAME)
pprint.pprint(dict(city_pcs_tiger))


# In[16]:

# Tiger data includes some data from Lake county and Porter county of IN
# Define the function to eliminate IN data

def is_not_in(elem):
    for tag in elem.iter('tag'):
        if tag.attrib['k'] == 'tiger:county':
            if tag.attrib['v'].endswith(', IN'):
                return False
    return True


# In[ ]:



