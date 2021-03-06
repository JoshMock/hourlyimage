import datetime
import os
import re
import pytz

from datetime import (
    datetime as createdatetime,
    timedelta
)


class FileTree():
    def __init__(self, timezone, offset_hours):
        self.timezone = timezone
        self.offset_hours = offset_hours

        self.acceptable_exts = [
            ".jpg",
            ".jpeg",
            ".gif",
            ".png",
            ".tiff",
            ".bmp"
        ]


    def generate_tree(self, path):
        """
            Recurses down a path, returning all valid directories and files
            inside that path.
        """
        tree = {}
        dir_items = os.listdir(path)

        for item in dir_items:
            new_path = "%s/%s" % (path, item)

            if os.path.isdir(new_path) and self.is_valid_dir(new_path):
                sub = self.generate_tree(new_path)
                if sub:
                    tree[item] = sub

            elif os.path.isfile(new_path) and self.is_valid_file(new_path):
                tree[os.path.splitext(item)[0]] = new_path

            else:
                continue
        return tree


    def is_valid_dir(self, path):
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
            except ValueError:
                return False
        else:
            month_match = re.match(r'.*?\/([0-9]{1,4})/([0-9]{2,2})$', path)
            if month_match:
                try:
                    year = int(month_match.group(1))
                    month = int(month_match.group(2))
                except ValueError:
                    return False
            else:
                year_match = re.match(r'.*?\/([0-9]{1,4})$', path)
                if year_match:
                    try:
                        year = int(year_match.group(1))
                    except ValueError:
                        return False
                else:
                    return False

        # test if it corresponds with an actual date/time
        try:
            local_dt = self.timezone.localize(createdatetime(year, month, day))
        except TypeError:
            return False
        except ValueError:
            return False
        utc_time = pytz.utc.localize(datetime.datetime.utcnow())
        tz_time = utc_time.astimezone(self.timezone) - timedelta(hours=self.offset_hours)
        if local_dt > tz_time:
            return False

        return True


    def is_valid_file(self, path):
        """
            Tests whether a provided file path fits in the date-based
            directory scheme and is a valid image file.
        """
        if os.path.splitext(path)[1] not in self.acceptable_exts:
            return False

        file_match = re.match(r'.*?/([0-9]{1,4})/([0-9]{2,2})/([0-9]{2,2})/' +\
                r'([0-9]{2,2})\.[a-zA-Z]+$', path)

        if not file_match:
            return False

        try:
            year = int(file_match.group(1))
            month = int(file_match.group(2))
            day = int(file_match.group(3))
            hour = int(file_match.group(4))
        except ValueError:
            return False

        # test if it corresponds with an actual date/time
        try:
            local_dt = self.timezone.localize(createdatetime(year, month, day,
                    hour))
        except TypeError:
            return False
        except ValueError:
            return False

        utc_time = pytz.utc.localize(datetime.datetime.utcnow())
        time_change = timedelta(hours=self.offset_hours)
        tz_time = utc_time.astimezone(self.timezone) - time_change

        if local_dt > tz_time:
            return False

        return True

