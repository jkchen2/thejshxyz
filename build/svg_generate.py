# Python 3.5+
# Generates an SVG version of the resume PDF.
# This also embeds the Roboto font, adds links, and optimizes the SVG

import base64
import subprocess
import sys
import yaml

from os.path import realpath, dirname
from lxml import etree

import logger
LOGGER = logger.new_logger(name='SVG')

path = dirname(realpath(__file__))
if 'dev' in sys.argv:
    LOGGER.debug('Development: writing SVG to src/assets')
    gen_type = 'src'
else:
    gen_type = 'dist'
assets = f'{path}/../{gen_type}/assets'

# Convert PDF to basic, unoptimized SVG
# inkscape -l "{assets}/resume.svg" "{assets}/resume.pdf"
completed = subprocess.run(
    ['inkscape', '-l', f'{assets}/resume.svg', f'{assets}/resume.pdf'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if completed.returncode != 0:
    print(completed.stdout.decode('utf-8'), '\n')
    print(completed.stderr.decode('utf-8'), file=sys.stderr)
    LOGGER.error("Inkscape returned non-zero status code: {}".format(completed.returncode))
    sys.exit(1)

# Optimize SVG
# svgo "{assets}/resume.svg"
completed = subprocess.run(
    ['svgo', f'{assets}/resume.svg'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if completed.returncode != 0:
    print(completed.stdout.decode('utf-8'), '\n')
    print(completed.stderr.decode('utf-8'), file=sys.stderr)
    LOGGER.error("SVG optimizer returned non-zero status code: {}".format(completed.returncode))
    sys.exit(1)

# Load and encode the Roboto font
with open(f'{path}/font/Roboto-Regular.ttf', 'rb') as font_file:
    encoded_font = base64.b64encode(font_file.read()).decode('utf-8')
style_text = (
    'svg a{{font-weight:normal!important}}svg a:hover{{cursor:pointer;'
    'font-weight:normal!important;text-decoration:none!important;}}'
    '@font-face{{font-family:"Roboto";src:url("data:application/font-woff;charset=utf-8;'
    'base64,{encoded_font}");}}'.format(encoded_font=encoded_font)
)

# Load optimized SVG and add embedded font style
tree = etree.parse(f'{assets}/resume.svg')
root = tree.getroot()
style_element = etree.Element('style')
style_element.text = style_text
root.insert(0, style_element)

# Fix viewbox properties
root.attrib['viewBox'] = f"0 0 {root.attrib['width']} {root.attrib['height']}"

# Need xlink spec for valid href
XLINK_HREF = '{http://www.w3.org/1999/xlink}href'

# Load replacements
with open(f'{path}/svg_config.yaml', 'r') as config_file:
    replacements = yaml.load(config_file)

def recurse(element):
    for child in element:
        recurse(child)

    # Replace Inkscape's font guesses with 'Roboto'
    if element.attrib.get('font-family'):
        element.attrib['font-family'] = 'Roboto'

    # Remove -inkscape-font-specification in style attributes
    if element.attrib.get('style'):
        del element.attrib['style']

    # Remove the white fill background so that the SVG can be properly inverted
    if element.attrib.get('fill') == '#fff':
        element.attrib['fill'] = 'none'

    # Detect necessary link additions
    if element.text:
        cleaned = element.text.replace('\u200b', '').strip()
        if cleaned in replacements:
            LOGGER.debug('Adding link for: %s', cleaned)
            a = etree.Element('a')
            a.attrib[XLINK_HREF] = replacements[cleaned]
            a.attrib['target'] = '_blank'
            to_replace = element.getparent()
            parent = to_replace.getparent()
            index = parent.index(to_replace)
            parent.remove(to_replace)
            a.append(to_replace)
            parent.insert(index, a)

recurse(root)

tree.write(f'{assets}/resume.svg')
LOGGER.debug('Wrote resume.svg')
