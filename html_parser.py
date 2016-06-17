#!/usr/bin/env python
'''
html_parser generates a hierarchical tree structure by parsing html passed to function `parse`
'''
#--------imports--------#
import requests
import string
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
	def __init__(self,head,body,shell,tree,node_dict,info):
		self.head = head
		self.body = body
		self.shell = shell
		self.tree = tree
		self.node_dict = node_dict
		self.info = info		
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
#--------parse body--------#	

def parse_body(body):

	#----create tree root (body tag)----#
	el = body[1:body.find('>')]
	attr = el[el.find(' '):]
	body_tree = node(tag='body',parent=None,attr=attr)	
	curr_node_list = [body_tree]						#pointer stack for tracking parent nodes
	
	i = len(el)+2		#set html iterator
	last_pointer = i	#any offset from iterator 'i' will determine 'innerHTML' content
	#----create tree root (body tag)----#
	#
	#----definitions----#
	
	s = string.ascii_lowercase + string.ascii_uppercase 
	node_dict = {}		#dictionary organized by html tags (each dict entry will be node list)
	
	#----definitions----#
	#
	#----loop over html body----#
	
	while i < len(body):

		if body[i] == '<': 
			
			#----add innerHTML content, if available----#
			html_content = body[last_pointer:i].replace('\n','').replace('\t','').replace('\r','')
			if html_content:
				curr_node_list[-1].html.append(html_content)
			#----add innerHTML content, if available----#
			#
			#----handle comments----#
			if body[i+1:i+4] == '!--': 			
				com = body[i:body.find('-->',i)+3]
				if 'comment' in node_dict.iterkeys():
					node_dict['comment'].append(com)
				else:
					node_dict['comment'] = [com]
				
				i += len(com)	#iterator hop
			#----handle comments----#
			#
			#----found opening tag----#
			if body[i+1] in s:				
				el = body[i+1:body.find('>',i)]
				tag = el
				if ' ' in el:				
					tag = el[:el.find(' ')]
					attr = el[len(tag):].lstrip()
					
				n = node(tag, attr=attr, parent=curr_node_list[-1])
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
			elif body[i+1] == '/':	
				tag = body[i+2:body.find('>',i+2)].rstrip()
				curr_node_list.pop()
				
				i += (len(tag)+3)
			#----found closing tag----#
				
			last_pointer = i	#update last_pointer
			
		else:
			i+=1	#iterate over html content until '<'
	#----loop over html body----#
	
	return body_tree,node_dict
	
#--------parse body--------#
#
#--------get_info--------#
def get_info():
	return '''
	#--Accessing tree data--#
	head:  complete raw html head
	body:  complete raw html body
	shell: everything that is not head or body
	tree:  tree of html element nodes
				#--Properties of all nodes--#
					tag:      html tag/element
					attr:     attributes defined in html tag
					parent:   parent node
					children: child nodes (as list) in order
					html:     innerHTML exclusive to each tag (no nested content), as list
	node_dict:	tag dictionary, each dict item formulated as list of nodes	
	  e.g. node_dict['div'] == [n1,n2,n3,n4...]
	'''.replace('\t',' ')
#--------get_info--------#
#
#--------parse page--------#	
def parse(page):
	
	shell,head,body = excise_head_and_body(page)
	
	tree,node_dict = parse_body(body)
	
	info = get_info()

	data = data_obj(head,body,shell,tree,node_dict,info)
	
	return data
	
#--------parse page--------#		
#
#--------main--------#
def main():
	pass
	
if __name__ == '__main__':
	main()
#--------main--------#