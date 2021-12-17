# -*- coding: utf-8 -*-
"""

@author: Elaine
"""

def print_tree(tree, prefix = '', bend = '', answer = ''):
    """Recursively print a 20 Questions tree in a human-friendly form.
       TREE is the tree (or subtree) to be printed.
       PREFIX holds characters to be prepended to each printed line.
       BEND is a character string used to print the "corner" of a tree branch.
       ANSWER is a string giving "Yes" or "No" for the current branch."""
    text, left, right = tree
    if len(left) >= 50 and  len(right) >= 20:
        print(f'{prefix}{bend}{answer}It is {text} food')
        print(f'{prefix}  rating>=4.0 restaurants: {left[0]["name"]}, {left[1]["name"]}...')
        print(f'{prefix}  rating<4.0 restaurants: {right[0]["name"]}, {right[1]["name"]}...')
    else:
        print(f'{prefix}{bend}{answer}{text}')
        if bend == '+-':
            prefix = prefix + '| '
        elif bend == '`-':
            prefix = prefix + '  '
        print_tree(left, prefix, '+-', "Yes: ")
        print_tree(right, prefix, '`-', "No:  ")
