# Python 3.5+
# Generates Open Graph meta tags for configured pages

import sys
import yaml
from os.path import realpath, dirname
from lxml import etree

import logger
LOGGER = logger.new_logger(name='OG')

path = dirname(realpath(__file__))

with open(f'{path}/og_config.yaml', 'r') as config_file:
    config = yaml.load(config_file)

# Script is in the build directory. Retrieve index.html from the dist directory and modify that.
tree = etree.parse(f'{path}/../dist/index.html', etree.HTMLParser())
head = tree.find('head')

# Fix app-root being a self-closing tag
approot = tree.find('body').find('app-root')
approot.text = ''

# Modify the index to include a description section
title_meta = None
for meta in head.findall('meta'):
    property_value = meta.attrib.get('property', '')
    if property_value == 'og:title':
        title_meta = meta
    elif property_value == 'og:description':  # Description already added
        title_meta = None
        break
if title_meta is not None:
    description_meta = etree.Element('meta', property='og:description')
    title_meta.addnext(description_meta)

# Write new Open Graph enabled pages
for name, data in config.items():
    for meta in head.findall('meta'):
        property_value = meta.attrib.get('property', '')
        replacement = data.get(property_value[3:])
        if replacement:
            meta.attrib['content'] = replacement
    tree.write(f'{path}/../dist/{name}.html', method='html')
    LOGGER.debug(f'Wrote tags for {name}.html')
