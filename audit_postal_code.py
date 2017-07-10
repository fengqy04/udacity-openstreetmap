
# coding: utf-8

# In[1]:

# Imports

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict


# In[2]:

FILENAME = 'sample.osm'


# In[3]:

def audit_citypc(city_pcs, city, pc):
    if city in city_pcs:
        if pc in city_pcs[city]:
            city_pcs[city][pc] += 1
        else:
            city_pcs[city][pc] = 1
    else:
        city_pcs[city][pc] = 1


# In[4]:

# Define the function to audit cities and postal codes

def audit_pc(filename):
    city_pcs = defaultdict(dict)
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            city = ''
            pc = ''
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:city':
                    city = tag.attrib['v']
                if tag.attrib['k'] == 'addr:postcode':
                    pc = tag.attrib['v']
            if city != '' or pc != '':
                audit_citypc(city_pcs, city, pc)
    return city_pcs


# In[5]:

city_pcs = audit_pc(FILENAME)
pprint.pprint(dict(city_pcs))


# In[6]:

# No need to update the postal codes - they are in the correct cities for Chicago area


# In[ ]:



