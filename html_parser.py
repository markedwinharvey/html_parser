#!/usr/bin/env python
'''
html_parser generates a hierarchical tree structure by parsing html passed to function `parse`
'''
#--------imports--------#
import string
import sys
#--------imports--------#
#
#--------define classes--------#	
class node():
	def __init__(self,tag,attr,parent):
		self.tag = tag 
		self.attr = attr
		self.parent = parent
		self.children = []
		self.html = []
		
class data_obj():
	def __init__(self,head,body,shell,tree,node_dict,info,classes,raw):	
		self.head = head
		self.body = body
		self.shell = shell
		self.tree = tree
		self.node_dict = node_dict
		self.info = info		
		self.raw = raw
		self.classes=classes
#--------define classes--------#
#
#--------excise head and body--------#	

def excise_head_and_body(page):
	#----get head----#
	h1 = page.find('<head')
	h2 = page.find('</head',h1)
	h2 = page.find('>',h2)+1
	head = page[h1:h2]
	page = page[:h1]+page[h2:]	#remove head from page
	#----get head----#
	#
	#----get body----#
	b1 = page.find('<body')
	b2 = page.find('</body',b1)
	b2 = page.find('>',b2)+1
	body = page[b1:b2]
	shell = page[:b1]+page[b2:]	#remove body from page
	#----get body----#
	
	return shell,head,body
	
#--------excise head and body--------#		
#
#--------get classes--------#	
def get_classes(classes,el,n):
	#classes = class dict, el = html element attribute list, n = html node (just created)
	#scan each el for class list and add nodes to classes dict
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
		
#--------get classes--------#	
#
#--------parse section--------#	
def parse_section(section,section_name,tree,node_dict,classes):
	#----definitions----#
	i = 0
	last_pointer = i	
	s = string.ascii_lowercase + string.ascii_uppercase 
	curr_node_list = [tree]
	#----definitions----#
	#
	#----loop over html section----#	
	while i < len(section):

		if section[i] == '<': 
			
			#----add innerHTML content, if available----#
			html_content = section[last_pointer:i].replace('\n','').replace('\t','').replace('\r','')
			if html_content.replace(' ',''):
				curr_node_list[-1].html.append(html_content)
			#----add innerHTML content, if available----#
			#
			#----handle comments----#
			if section[i+1:i+4] == '!--': 			
				com = section[i:section.find('-->',i)+3]
				if 'comment' in node_dict.iterkeys():
					node_dict['comment'].append(com)
				else:
					node_dict['comment'] = [com]
				
				i += len(com)	#iterator hop
			#----handle comments----#
			#
			#----found opening tag----#
			if section[i+1] in s:				
				el = section[i+1:section.find('>',i)]
				tag = el
				attr=''
				if ' ' in el:				
					tag = el[:el.find(' ')]
					attr = el[len(tag):].lstrip()
				n = node(tag, attr=attr, parent=curr_node_list[-1])
				classes = get_classes(classes,el,n)
				curr_node_list[-1].children.append(n)
				
				#----handle self-closing tags (do not append to curr_node_list)----#
				for j in el[::-1]:		
					if j == ' ':
						continue
					elif j == '/':
						break
					else: 
						if tag != 'br': 
							curr_node_list.append(n)	#append node to curr_node_list pointer stack
						break
				#----handle self-closing tags (do not append to curr_node_list)----#
				#
				#----update node_dict with new tag----#		
				if tag in node_dict.iterkeys():	#node_dict is dictionary of html tags, represented as a list of nodes in order of appearance
					node_dict[tag].append(n)
				else:
					node_dict[tag] = [n]
				#----update node_dict with new tag----#	
							
				i += len(el)+2	#iterator hop
				
			#----found opening tag----#
			#
			#----found closing tag----#
			elif section[i+1] == '/':	
				tag = section[i+2:section.find('>',i+2)].rstrip()
				curr_node_list.pop()
				
				i += (len(tag)+3)
			#----found closing tag----#
				
			last_pointer = i	#update last_pointer
			
		else:
			i+=1	#iterate over html content until '<'
	#----loop over html body----#
	
	return tree,node_dict,classes
#--------parse body--------#
#
#--------get_info--------#
def get_info():
	return '''
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
	'''.replace('\t',' ')
#--------get_info--------#
#
#--------parse page--------#	
def parse(page):
	
	shell,head,body = excise_head_and_body(page)
	
	tree = node(tag='root',parent=None,attr=None)
	
	node_dict = {}
	classes = {}
	
	tree,node_dict,classes = parse_section(head,'head',tree,node_dict,classes)
	tree,node_dict,classes = parse_section(body,'body',tree,node_dict,classes)
	
	info = get_info()

	data = data_obj(head,body,shell,tree,node_dict,info,classes,raw=page)
	
	return data
	
#--------parse page--------#		
#
#--------main--------#
def main():
	pass
	
if __name__ == '__main__':
	main()
#--------main--------#