# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 13:49:31 2021

@author: Elaine
"""
# =============================================================================
# Restaurant data source -- Data Structure: Tree
# =============================================================================
# parent: is asian food? 
#   child(yes):is Chinese food?
#       leaf(yes):Chinese
#       child(no):is japanese food?
#           leaf(yes):japanese
#           leaf(no): thai
#   child(no):is burger food?
#       leaf(yes):burger
#       child(no):is mexcian food?
#           leaf(yes):mexican
#           leaf(no):italian 
tree_rest = ['Is it Asian food?',['Is it Chinese food?',['Chinese',None,None],['Is it Japanese food?',['Japanese',None,None],['Thai',None,None]]],['Is it Burger food?',['Burger',None,None],['Is it Mexican food?',['Mexican',None,None],['Italian',None,None]]]]

def parent(key):
    if key.lower() in ['chinese','burger']:
        return True
def isleaf(key):
    if key.lower() in ['thai','italian']:
        return True
def tree_type(data,tree):
    '''
    Paramter:the dictionary that contains all restaurants information
    Determine which node in the tree the restaurant type is on.
    Return: a list that is a tree data structure based on restaurant type
    '''
    asian_type =['chinese','japanese','thai']
    for key,val in data.items():
        if key.lower() in asian_type:
            if parent(key):
                rating = rating_tree(key, val)
                tree[1][1] = rating .rating_info()
            elif isleaf(key):
                rating = rating_tree(key, val)
                tree[1][2][2] = rating .rating_info()
            else:
                rating = rating_tree(key, val)
                tree[1][2][1] = rating .rating_info()         
        if key.lower() not in asian_type:
            if parent(key):   
                rating = rating_tree(key, val)
                tree[2][1] = rating .rating_info()
            elif isleaf(key):
                rating = rating_tree(key, val)
                tree[2][2][2] = rating .rating_info()
            else:
                rating = rating_tree(key, val)
                tree[2][2][1] = rating .rating_info()
    return tree


class rating_tree:
    '''
    The structure of the tree is applied again to the restaurants of each node, which are divided into binary trees by restaurant rating
    '''
    def __init__(self,val,data):
        self.data = data
        self.val = val
    
    def rating_info(self):
        rat=[self.val,[],[]]
        for i in self.data:
            if float(i['rating']) >= 4.0:
                rat[1].append(i)
            else:
                rat[2].append(i)
        return rat


