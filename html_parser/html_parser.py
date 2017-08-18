#!/usr/bin/env python
'''
html_parser generates a hierarchical tree structure by parsing html passed to function `parse`

Usage:
	
	import requests
	import html_parser as hp

	url = 'https://en.wikipedia.org/wiki/Special:Random'
	r = requests.get(url)
	doc = r.text

	data = hp.parse(doc)
'''

import string
import sys
import re



#--------class declarations--------#	

class node(object):
	def __init__(self,tag,attr,parent,index):
		self.tag = tag 
		self.attr = attr
		self.attr_dict = gen_attr_dict(attr)
		self.parent = parent
		self.children = []
		self.html = []
		self.index = index
		self.content = ''

class html_obj(object):
	def __init__(self,content,index):
		self.content = content
		self.index = index
		
		
class data_obj(object):
	def __init__(self,head,body,shell,tree,node_dict,info,classes,text_node_list,id_dict,raw):	
		self.head = head
		self.body = body
		self.shell = shell
		self.tree = tree
		self.node_dict = node_dict
		self.info = info		
		self.raw = raw
		self.classes = classes
		self.text_node_list = text_node_list
		self.id_dict = id_dict
		
	def get(self,tags):
		'''accepts comma-separated string of tagnames and returns all requested tags in a single list'''
		taglist = []
		for tagname in [x.strip() for x in tags.split(',')]:
			if tagname:
				for each_node in self.node_dict[tagname]:					
					taglist.append(each_node)		
		return taglist


#--------data initialization--------#	
	
id_dict = {}


#--------function declarations--------#	

def rm_markup(text):
	'''Remove markup tags from text input for readability'''
	return re.sub('<.*?>','',text) 
	
	
def gen_attr_dict(attr):
	'''takes node attributes (as html string) and returns attr_dict, which becomes class attribute for node'''
	attr_dict = {}
	if not attr: 
		return attr_dict
	attr = attr.lstrip()
	
	last = 0
	i=0
	while i < len(attr):
		
		if attr[i] == '=':
			key = attr[last:i].strip()
			quote_type = attr[i+1]
			val_end = attr.find(quote_type,i+2)
			val = attr[i+2:val_end]
			last=val_end+2
			i=last
			attr_dict[key]=val
		else:
			i+=1
			
	return attr_dict
			

def excise_head_and_body(page):	
	'''excise and return head and body if available'''
	
	h1 = page.find('<head')
	h2 = page.find('</head',h1)
	h2 = page.find('>',h2)+1
	head = page[h1:h2]			#get head
	page = page[:h1]+page[h2:]	#remove head from page
	if not head: 
		head = 'NA'
	
	b1 = page.find('<body')
	b2 = page.find('</body',b1)
	b2 = page.find('>',b2)+1
	body = page[b1:b2]			#get body
	shell = page[:b1]+page[b2:]	#remove body from page
	if not body:
		body='NA'
		shell='NA'	
		
	return shell,head,body
	

def get_classes(classes,el,n):
	'''	classes = class dict, el = html element attribute list, n = html node (newly created)
		scan each el for class list and add appropriate nodes to classes dict'''
		
	c1 = el.find('class')
	if c1 == -1: 
		return classes
		
	for i in range(c1,len(el)):
		if el[i] == '"' or el[i] == "'":
			c1 = i
			quote_type = el[i]
			break
	class_list = el[c1+1:el.find(quote_type,c1+2)].split()
	for c in class_list:
		if c in classes.iterkeys():
			classes[c].append(n)
		else:
			classes[c] = [n]
	return classes
		

def update_id_dict(el,n):
	id1 = el.find('id=')
	if id1 == -1: return
	for i in range(id1,len(el)):
		if el[i] == '"' or el[i] == "'":
			id1=i
			quote_type = el[i]
			break
	id = el[id1+1:el.find(quote_type,id1+2)]
	id_dict[id] = n

text_node_list_accept_tags = 'a b h1 h2 h3 h4 h5 h6 li ol p ul'.split(' ')

def parse_section(section,tree,node_dict,classes,text_node_list):
	'''parse section (html text string); track/update tree, node_dict, and classes'''
	
	i = 0
	last_pointer = i	
	s = string.ascii_lowercase + string.ascii_uppercase 
	curr_node_list = [tree]
	
	while i < len(section):

		if section[i:i+2] == '<!' and section[i+2]!='-':		#ignore doctype declaration
			i=section.find('>',i)+1
			continue

		if section[i] == '<': 
			
			#----add innerHTML content, if found, to previous tag----#
			html_content = section[last_pointer:i].replace('\n','').replace('\t','').replace('\r','')
			if html_content.replace(' ',''):
				n = node(
					tag = 'html',
					attr = '',
					parent = curr_node_list[-1],
					index = last_pointer, 
				)
				n.content = html_content
				
				
				h = html_obj(html_content,last_pointer)
				curr_node_list[-1].html.append(h)
				
				##################
				curr_node_list[-1].children.append(n)
				
				this_tag = curr_node_list[-1].tag
				
				#if this_tag 
				#if curr_node_list[-1].tag in text_node_list_do_not_accept_tags:
					
				if curr_node_list[-1].tag in text_node_list_accept_tags:
					if html_content not in ['^'] and not re.search('\[\d+\]',html_content):
						text_node_list.append(n)
			
			#----handle comments----#
			if section[i+1:i+4] == '!--': 			
				com = section[i:section.find('-->',i)+3]
				if 'comment' in node_dict.iterkeys():
					node_dict['comment'].append(com)
				else:
					node_dict['comment'] = [com]
				
				i += len(com)	
			
			#----found opening tag----#
			if section[i+1] in s:				
				el = section[i+1:section.find('>',i)]
				tag = el
				attr=''
				if ' ' in el:				
					tag = el[:el.find(' ')]
					attr = el[len(tag):].lstrip()
				
				n = node(
					tag=tag, 
					attr=attr, 
					parent=curr_node_list[-1],
					index=i
				)
				
				classes = get_classes(classes,el,n)
				update_id_dict(el,n)
				
				
				curr_node_list[-1].children.append(n)
				#text_node_list.append(n)
				
				#----handle self-closing tags----#
				for j in el[::-1]:		
					if j == ' ':
						continue
					elif j == '/':
						break
					else: 
						if tag != 'br': 
							curr_node_list.append(n)	#append node to curr_node_list pointer stack
						break
				
				#----update node_dict with new tag----#		
				if tag in node_dict.iterkeys():	
					node_dict[tag].append(n)
				else:
					node_dict[tag] = [n]
							
				i += len(el)+2	#iterator hop
				
			#----found closing tag----#
			elif section[i+1] == '/':	
				tag = section[i+2:section.find('>',i+2)].rstrip()
				curr_node_list[-1].content = section[curr_node_list[-1].index:i+len(tag)+3]
				curr_node_list.pop()
				
				i += (len(tag)+3)
				
			last_pointer = i	
			
		else:
			i+=1	#iterate over html content until '<'
	
	
	return tree,node_dict,classes,text_node_list


#--------get_info--------#
def help():
	return '''
	#--Accessing tree data--#
	head:       complete raw html head
	body:       complete raw html body
	shell:      everything that is not head or body
	tree:       node-based data structure 			
	node_dict:  dict of html tags as cumulative lists
	info:       display this information
	raw:        unchanged from original input
	classes:    class dict, each dict entry a list of corresponding nodes
	id_dict:	id dict, element id (dict key) matched to node
	
	#--Properties of all nodes--#
		tag:      	html tag/element; the tag for innerHTML nodes is 'html'
		attr:     	attributes defined in tag (as string)
		attr_dict:	dict based on attr string
		parent:   	parent node
		children: 	child nodes (as list) in order
		html:     	innerHTML exclusive to each tag (no nested content), as list
		index:    	index of starting character of node, with respect to the entire document
		content:  	complete inner contents of tag (as string)

	#--node_dict lookup:  e.g.  node_dict['div'] == [node1,node2,node3,...]
	#--id_dict: 				id_dict['firstHeading'] = node_n
	
	#-- Use rm_markup(text) to remove markup and make text readable
	'''.replace('\t',' ')


#--------parse page--------#	
def parse(page):

	shell,head,body = excise_head_and_body(page)

	tree = node(tag='root',parent=None,attr=None,index='NA')
	
	node_dict = {}
	classes = {}
	text_node_list = []
	

	tree,node_dict,classes,text_node_list = parse_section(page,tree,node_dict,classes,text_node_list)

	info = get_info()

	data = data_obj(head,body,shell,tree,node_dict,info,classes,text_node_list,id_dict,raw=page)
	
	return data
	


def main():
	pass
	
if __name__ == '__main__':
	main()