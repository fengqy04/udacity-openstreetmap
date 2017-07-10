
# coding: utf-8

# In[28]:

# Imports

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

import csv
import codecs
import cerberus
import schema


# In[29]:

# Import functions from audit files

from audit_street_name import update_st_name
from audit_tiger import is_tiger, is_not_in


# In[30]:

FILENAME = 'sample.osm'


# In[31]:

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"


# In[32]:

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# In[33]:

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# In[34]:

# Create schema

SCHEMA = schema.schema


# In[35]:

# Define the function to shape the elements into Python dictionary

def shape_elem(elem, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    
    if is_tiger(elem) and (not is_not_in(elem)): # eliminate the IN data
        return None
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    
    for t in elem.iter('tag'):
        tag = {}
        key = t.attrib['k']
        if re.search(problem_chars, key) == None: # exclude keys with problematic characters
            tag['id'] = elem.attrib['id']
            tag['type'] = default_tag_type
            if is_tiger(elem) and key == 'name':
                tag['value'] = update_st_name(t.attrib['v']) # use updated street names for Tiger data
            elif key == 'addr:street':
                tag['value'] = update_st_name(t.attrib['v']) # use updated street names for regular data
            else:
                tag['value'] = t.attrib['v']
            if key.find(':') == -1:
                tag['key'] = key
            else:
                colon_pos = key.find(':')
                tag['type'] = key[:colon_pos]
                tag['key'] = key[(colon_pos + 1):]
        tags.append(tag)
                
    if elem.tag == 'node':
        for attr in elem.attrib:
            if attr in node_attr_fields:
                node_attribs[attr] = elem.attrib[attr]
        return {'node': node_attribs, 'node_tags': tags}
    
    elif elem.tag == 'way':
        position = 0
        for attr in elem.attrib:
            if attr in way_attr_fields:
                way_attribs[attr] = elem.attrib[attr]
        for nd in elem.iter('nd'):
            way_node = {}
            way_node['id'] = elem.attrib['id']
            way_node['node_id'] = nd.attrib['ref']
            way_node['position'] = position
            way_nodes.append(way_node)
            position += 1
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# In[36]:

# Define the function to yield elements (from case study)

def get_elem(filename, tags=('node', 'way', 'relation')):
    context = ET.iterparse(filename, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


# In[37]:

# Define the function to raise validation errors if element does not match schema (from case study)

def validate_elem(elem, validator, schema=SCHEMA):
    if validator.validate(elem, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


# In[38]:

# Extend csv.DictWriter to handle Unicode input (from case study)

class UnicodeDictWriter(csv.DictWriter, object):

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[39]:

# Iteratively process each XML element and write to csv(s) (from case study)

def process_map(filename, validate):

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for elem in get_elem(filename, tags=('node', 'way')):
            el = shape_elem(elem)
            if el:
                if validate is True:
                    validate_elem(el, validator)

                if elem.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif elem.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


# In[40]:

process_map(FILENAME, validate=True)


# In[ ]:



