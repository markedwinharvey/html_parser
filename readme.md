<h4>html_parser</h4>

<h5>Installation:</h5>

	python setup.py install

<h5>Usage:</h5>

	import html_parser
	data = html_parser.parse(doc)

where `doc` is some html text. 

For instance:

	import requests
	import html_parser

	url = 'https://en.wikipedia.org/wiki/Special:Random'
	r = requests.get(url)
	doc = r.text

	data = html_parser.parse(doc)

The data structure can be accessed via its class attributes. 

`data.info` returns a brief overview of the structure and node attributes: 


	#--Accessing tree data--#
	head:       complete raw html head
	body:       complete raw html body
	shell:      everything that is not head or body
	tree:       html node-based data structure 			
	node_dict:  dict of html tags as cumulative lists
	info:       display this information
	raw:        unchanged from original input
	classes:    class dict, each dict entry a list of corresponding nodes
	
	#--Properties of all nodes--#
		tag:      html tag/element
		attr:     attributes defined in html tag
		parent:   parent node
		children: child nodes (as list) in order
		html:     innerHTML exclusive to each tag (no nested content), as list

	#--node_dict lookup:  e.g. node_dict['div'] == [node1,node2,node3,...]