import datetime
import os
import re

from datetime import datetime as createdatetime

def generate_tree(path):
    """
        Recurses down a path, returning all valid directories and files inside
        that path.
    """
    tree = {}
    dir_items = os.listdir(path)
    for item in dir_items:
        new_path = "%s/%s" % (path, item)
        if os.path.isdir(new_path) and is_valid_dir(new_path):
            sub = generate_tree(new_path)
            if sub:
                tree[item] = sub
        elif os.path.isfile(new_path) and is_valid_file(new_path):
            tree[os.path.splitext(item)[0]] = new_path
        else:
            continue
    return tree

def is_valid_dir(path):
    """
        Tests whether a provided path belongs to the date-based directory
        scheme.
    """
    year = 1
    month = 1
    day = 1

    day_match = re.match(r'.*?/([0-9]{1,4})/([0-9]{2,2})/([0-9]{2,2})$', path)
    if day_match:
        try:
            year = int(day_match.group(1))
            month = int(day_match.group(2))
            day = int(day_match.group(2))
        except:
            return False
    else:
        month_match = re.match(r'.*?\/([0-9]{1,4})/([0-9]{2,2})$', path)
        if month_match:
            try:
                year = int(month_match.group(1))
                month = int(month_match.group(2))
            except:
                return False
        else:
            year_match = re.match(r'.*?\/([0-9]{1,4})$', path)
            if year_match:
                try:
                    year = int(year_match.group(1))
                except:
                    return False
            else:
                return False

    # test if it corresponds with an actual date/time
    try:
        createdatetime(year, month, day)
    except:
        return False

    return True

def is_valid_file(path):
    """
        Tests whether a provided file path fits in the date-based
        directory scheme and is a valid image file.
    """
    acceptable_exts = [".jpg", ".jpeg", ".gif", ".png", ".tiff", ".bmp"]
    if os.path.splitext(path)[1] not in acceptable_exts:
        return False

    file_match = re.match(r'.*?/([0-9]{1,4})/([0-9]{2,2})/([0-9]{2,2})/([0-9]{2,2})\.[a-zA-Z]+$', path)
    if file_match:
        try:
            year = int(file_match.group(1))
            month = int(file_match.group(2))
            day = int(file_match.group(3))
            hour = int(file_match.group(4))
        except:
            return False

        try:
            createdatetime(year, month, day, hour)
        except:
            return False

        return True
    else:
        return False
