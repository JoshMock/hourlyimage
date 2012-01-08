import datetime
import os

from datetime import datetime as createdatetime

def list_directories(path, year=None, month=None):
    """
        Lists all directories in configured IMAGE_LOCATION_DIR path. If the
        `year` or `year` and `month` arguments are provided, it only returns
        directories that correspond to valid dates.  Raises a ValueError
        exception if `month` is provided but `year` is not.
    """
    if month and not year:
        raise ValueError("'year' argument not provided")

    if year:
        try:
            year = int(year)
        except:
            raise ValueError("'year' is not a valid year")
        if year < datetime.MINYEAR or year > datetime.MAXYEAR:
            raise ValueError("'year' is not a valid year")

        if month:
            try:
                intmonth = int(month)
            except:
                raise ValueError("'month' is not a valid month")
            if intmonth < 1 or intmonth > 12:
                raise ValueError("'month' is not a valid month")

            path = "%s/%s/%s" % (path, year, month)
        else:
            path = "%s/%s" % (path, year)

    dir_items = os.listdir(path)
    dirs = []
    for item in dir_items:
        if os.path.isdir("%s/%s" % (path, item)):
            # test if directory accurately portrays a date or part of a date
            try:
                intitem = int(item)
            except ValueError:
                continue
            if year:
                if month:
                    try:
                        createdatetime(year, intmonth, intitem)
                    except ValueError:
                        continue
                else:
                    try:
                        createdatetime(year, intitem, 1)
                    except ValueError:
                        continue

            dirs.append(item)

    return dirs

def list_images(path, url, year, month, day, hour=None):
    """
        Takes a path, year, month and day and lists all available images
        matching the file naming convention for that dated directory. Only
        returns results for a set of arguments that correspond to a valid date.
    """
    # test all params to ensure valid date
    try:
        year = int(year)
    except:
        raise ValueError("'year' is not a valid ")
    try:
        intmonth = int(month)
    except:
        raise ValueError("'month' is not a valid month")
    try:
        intday = int(day)
    except:
        raise ValueError("'day' is not a valid day")
    if hour:
        try:
            inthour = int(hour)
        except:
            raise ValueError("'hour' is not a valid hour")
        try:
            createdatetime(year, intmonth, intday, inthour)
        except:
            raise ValueError("Parameters do not correspond to a real date.")
    else:
        try:
            createdatetime(year, intmonth, intday)
        except:
            raise ValueError("Parameters do not correspond to a real date.")

    # ensure parameters will map to directories with leading zero for <10
    if isinstance(month, int):
        month = "0%s" % month if month < 10 else str(month)
    if isinstance(day, int):
        day = "0%s" % day if day < 10 else str(day)
    if hour and isinstance(hour, int):
        hour = "0%s" % hour if hour < 10 else str(hour)

    acceptable_exts = [".jpg", ".jpeg", ".gif", ".png", ".tiff", ".bmp"]

    if hour:
        acceptable_names = [hour]
    else:
        acceptable_names = ["00", "01", "02", "03", "04", "05", "06", "07", "08",
                "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
                "20", "21", "22", "23"]

    path = "%s/%s/%s/%s" % (path, year, month, day)
    url = "%s/%s/%s/%s" % (url, year, month, day)

    items = os.listdir(path)
    images = []
    for item in items:
        ext = os.path.splitext(item)[1]
        name = item.replace(ext, '')
        fullpath = "%s/%s" % (path, item)
        fullurl = "%s/%s" % (url, item)
        if os.path.isfile(fullpath) \
                and ext in acceptable_exts \
                and name in acceptable_names:
            images.append(fullurl)

    return images
