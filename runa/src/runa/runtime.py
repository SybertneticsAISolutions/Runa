"""
Runtime support for the Runa programming language.
This module provides functions and utilities used by generated Python code.
"""

def format_string(template, **kwargs):
    """Format a string with named placeholders."""
    return template.format(**kwargs)

def format_message(message, **kwargs):
    """Format a message with named placeholders."""
    return message.format(**kwargs)

def add_to_list(lst, item):
    """Add an item to a list and return the modified list."""
    lst.append(item)
    return lst

def remove_from_list(lst, item):
    """Remove an item from a list and return the modified list."""
    if item in lst:
        lst.remove(item)
    return lst

def get_list_length(lst):
    """Get the length of a list."""
    return len(lst)

def combine_lists(lst1, lst2):
    """Combine two lists and return the result."""
    return lst1 + lst2

def add_to_dictionary(dic, key, value):
    """Add a key-value pair to a dictionary and return the modified dictionary."""
    dic[key] = value
    return dic

def remove_from_dictionary(dic, key):
    """Remove a key from a dictionary and return the modified dictionary."""
    if key in dic:
        del dic[key]
    return dic

def get_dictionary_keys(dic):
    """Get the keys of a dictionary as a list."""
    return list(dic.keys())

def get_dictionary_values(dic):
    """Get the values of a dictionary as a list."""
    return list(dic.values())

def contains_key(dic, key):
    """Check if a dictionary contains a key."""
    return key in dic

def contains_value(lst, value):
    """Check if a list or dictionary contains a value."""
    return value in lst

def parse_number(s):
    """Parse a string as a number."""
    try:
        if '.' in s:
            return float(s)
        else:
            return int(s)
    except ValueError:
        return None

def to_string(value):
    """Convert a value to a string."""
    return str(value)

def to_number(value):
    """Convert a value to a number if possible."""
    if isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        return parse_number(value)
    else:
        return None

def to_boolean(value):
    """Convert a value to a boolean."""
    if isinstance(value, str):
        value = value.lower()
        if value in ('true', 'yes', '1'):
            return True
        elif value in ('false', 'no', '0'):
            return False
    return bool(value)