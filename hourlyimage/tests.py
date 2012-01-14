import os
import shutil
import unittest
import tempfile
import datetime
from datetime import timedelta
from pytz import timezone
import pytz

import hourlyimage
import utilities


class HourlyImageTestCase(unittest.TestCase):
    def setUp(self):
        hourlyimage.app.config['TESTING'] = True

        # set up directories and symlink for images
        hourlyimage.app.config["IMAGE_LOCATION_DIR"] = tempfile.mkdtemp()
        os.symlink(hourlyimage.app.config["IMAGE_LOCATION_DIR"],
                "static/zzz_test_images")
        hourlyimage.app.config["IMAGE_LOCATION_URL"] = \
                "/static/zzz_test_images"

        os.mkdir("%s/static_pages" % hourlyimage.app.config["IMAGE_LOCATION_DIR"])
        hourlyimage.app.config["STATIC_PAGE_DIR"] = "%s/static_pages" % \
                hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        self.app = hourlyimage.app.test_client()

    def tearDown(self):
        hourlyimage.app.config['TESTING'] = False

        # remove image directory and symlink
        shutil.rmtree(hourlyimage.app.config["IMAGE_LOCATION_DIR"],
                ignore_errors=True)
        os.unlink("static/zzz_test_images")

    def test_index_loads(self):
        rv = self.app.get("/")
        assert len(rv.data) > 0

    def test_years_display_accurately(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2011" % path)
        os.mkdir("%s/2011/01" % path)
        os.mkdir("%s/2011/01/01" % path)
        file1 = open("%s/2011/01/01/01.jpg" % path, "w")
        file1.write('a')
        file1.close()
        os.mkdir("%s/2012" % path)
        os.mkdir("%s/blah" % path)

        rv = self.app.get("/")
        assert "/2011/" in rv.data
        assert "/2012/" not in rv.data
        assert "/blah/" not in rv.data

    def test_years_page_displays_months_accurately(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2011" % path)
        os.mkdir("%s/2011/10" % path)
        os.mkdir("%s/2011/10/01" % path)
        file1 = open("%s/2011/10/01/01.jpg" % path, "w")
        file1.write('a')
        file1.close()
        os.mkdir("%s/2011/12" % path)
        os.mkdir("%s/2011/13" % path)
        os.mkdir("%s/2011/blah" % path)

        rv = self.app.get("/2011/")
        assert "/2011/10/" in rv.data
        assert "/2011/12/" not in rv.data
        assert "/2011/13/" not in rv.data
        assert "/2011/blah/" not in rv.data

        rv = self.app.get("/2010/")
        assert rv.status == "404 NOT FOUND"

        os.mkdir("%s/2012" % path)
        rv = self.app.get("/2012/")
        assert rv.status == "404 NOT FOUND"

    def test_months_page_displays_days_accurately(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2011" % path)
        os.mkdir("%s/2011/02" % path)
        os.mkdir("%s/2011/02/12" % path)
        os.mkdir("%s/2011/02/29" % path)
        os.mkdir("%s/2011/02/30" % path)
        os.mkdir("%s/2011/02/blah" % path)
        os.mkdir("%s/2008" % path)
        os.mkdir("%s/2008/02" % path)
        os.mkdir("%s/2008/02/29" % path)
        file1 = open("%s/2008/02/29/01.jpg" % path, "w")
        file1.write('a')
        file1.close()

        rv = self.app.get("/2011/02/")
        assert "/2011/02/12/" not in rv.data
        assert "/2011/02/29/" not in rv.data
        assert "/2011/02/30/" not in rv.data
        assert "/2011/02/blah/" not in rv.data
        rv = self.app.get("/2008/02/")
        assert "/2008/02/29/" in rv.data

        rv = self.app.get("/2010/01/")
        assert rv.status == "404 NOT FOUND"

        os.mkdir("%s/2009" % path)
        os.mkdir("%s/2009/01" % path)
        rv = self.app.get("/2009/01/")
        assert rv.status == "404 NOT FOUND"

    def test_day_page_displays_images_accurately(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2011" % path)
        os.mkdir("%s/2011/04" % path)
        os.mkdir("%s/2011/04/01" % path)
        file1 = open("%s/2011/04/01/01.jpg" % path, "w")
        file1.write('a')
        file1.close()
        file2 = open("%s/2011/04/01/31.jpg" % path, "w")
        file2.write('a')
        file2.close()
        file3 = open("%s/2011/04/01/blah.jpg" % path, "w")
        file3.write('a')
        file3.close()
        file4 = open("%s/2011/04/01/blah.txt" % path, "w")
        file4.write('a')
        file4.close()

        rv = self.app.get("/2011/04/01/")
        assert "/2011/04/01/01.jpg" in rv.data
        assert "/2011/04/01/01/" in rv.data
        assert "/2011/04/01/31.jpg" not in rv.data
        assert "/2011/04/01/31/" not in rv.data
        assert "/2011/04/01/blah.jpg" not in rv.data
        assert "/2011/04/01/blah.txt" not in rv.data
        assert "/2011/04/01/blah/" not in rv.data

        rv = self.app.get("/2010/01/01/")
        assert rv.status == "404 NOT FOUND"

        os.mkdir("%s/2009" % path)
        os.mkdir("%s/2009/02" % path)
        os.mkdir("%s/2009/02/01" % path)
        rv = self.app.get("/2009/02/01/")
        assert rv.status == "404 NOT FOUND"

    def test_hour_page(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2011" % path)
        os.mkdir("%s/2011/04" % path)
        os.mkdir("%s/2011/04/01" % path)
        file1 = open("%s/2011/04/01/01.jpg" % path, "w")
        file1.write('a')
        file1.close()
        file2 = open("%s/2011/04/01/02.png" % path, "w")
        file2.write('a')
        file2.close()

        rv = self.app.get("/2011/04/01/01/")
        assert "/2011/04/01/01.jpg" in rv.data
        assert "/2011/04/01/02.png" not in rv.data

        rv = self.app.get("/2011/04/01/02/")
        assert "/2011/04/01/02.png" in rv.data
        assert "/2011/04/01/01.png" not in rv.data

        rv = self.app.get("/2000/01/01/01/")
        assert rv.status == "404 NOT FOUND"

    def test_recursively_hidden_empty_directories(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/1999" % path)
        os.mkdir("%s/1999/09" % path)
        os.mkdir("%s/1999/09/09" % path)
        rv = self.app.get("/")
        assert "1999" not in rv.data

        os.mkdir("%s/1998" % path)
        os.mkdir("%s/1998/09" % path)
        rv = self.app.get("/")
        assert "1998" not in rv.data

        os.mkdir("%s/1997" % path)
        rv = self.app.get("/")
        assert "1997" not in rv.data

    def test_hide_future_datetimes(self):
        current_time = datetime.datetime.utcnow()
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/%s" % (path, str(current_time.year + 2)))
        rv = self.app.get("/%s/" % str(current_time.year + 2))
        assert rv.status == "404 NOT FOUND"

        os.mkdir("%s/%s/01" % (path, str(current_time.year + 2)))
        rv = self.app.get("/%s/01/" % str(current_time.year + 2))
        assert rv.status == "404 NOT FOUND"

        os.mkdir("%s/%s/01/01" % (path, str(current_time.year + 2)))
        rv = self.app.get("/%s/01/01/" % str(current_time.year + 2))
        assert rv.status == "404 NOT FOUND"

        file1 = open("%s/%s/01/01/01.jpg" % (path, str(current_time.year + 2)),
                "w")
        file1.write('a')
        file1.close()
        rv = self.app.get("/%s/01/01/01/" % str(current_time.year + 2))
        assert rv.status == "404 NOT FOUND"

    def test_timezone_setting(self):
        hourlyimage.app.config["OFFSET_HOURS"] = 0
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        eastern = timezone("US/Eastern")
        amsterdam = timezone("Europe/Amsterdam")

        utc_time = pytz.utc.localize(datetime.datetime.utcnow())
        eastern_time = utc_time.astimezone(eastern)
        amsterdam_time = utc_time.astimezone(amsterdam)

        file_month = "0%s" % amsterdam_time.month if amsterdam_time.month < 10\
                else str(amsterdam_time.month)
        file_day = "0%s" % amsterdam_time.day if amsterdam_time.day < 10 else\
                str(amsterdam_time.day)
        file_hour = "0%s" % amsterdam_time.hour if amsterdam_time.hour < 10\
                else str(amsterdam_time.hour)

        os.mkdir("%s/%s" % (path, amsterdam_time.year))
        os.mkdir("%s/%s/%s" % (path, amsterdam_time.year, file_month))
        os.mkdir("%s/%s/%s/%s" % (path, amsterdam_time.year, file_month,
                file_day))
        file1 = open("%s/%s/%s/%s/%s.jpg" % (path, amsterdam_time.year,
                file_month, file_day, file_hour), "w")
        file1.write('a')
        file1.close()

        e_month = "0%s" % eastern_time.month if eastern_time.month < 10 else\
                str(eastern_time.month)
        e_day = "0%s" % eastern_time.day if eastern_time.day < 10 else\
                str(eastern_time.day)
        e_hour = "0%s" % eastern_time.hour if eastern_time.hour < 10 else\
                str(eastern_time.hour)

        hourlyimage.app.config["TIMEZONE"] = eastern
        rv = self.app.get("/%s/%s/%s/%s/" % (eastern_time.year, e_month, e_day,
                e_hour))
        assert rv.status == "404 NOT FOUND"

        hourlyimage.app.config["TIMEZONE"] = amsterdam
        rv = self.app.get("/%s/%s/%s/%s/" % (amsterdam_time.year, file_month,
                file_day, file_hour))
        assert rv.status == "200 OK"

    def test_offset_hours(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]
        hourlyimage.app.config["OFFSET_HOURS"] = 2

        current_utc_time = pytz.utc.localize(datetime.datetime.utcnow())
        current_tz_time = current_utc_time.astimezone(hourlyimage.app.\
                config["TIMEZONE"])

        # create file for 3 hours into the future
        future_date = current_tz_time + timedelta(hours=3)
        month = str(future_date.month) if future_date.month > 9 else "0%s" %\
                future_date.month
        day = str(future_date.day) if future_date.day > 9 else "0%s" %\
                future_date.day
        hour = str(future_date.hour) if future_date.hour > 9 else "0%s" %\
                future_date.hour
        os.mkdir("%s/%s" % (path, future_date.year))
        os.mkdir("%s/%s/%s" % (path, future_date.year, month))
        os.mkdir("%s/%s/%s/%s" % (path, future_date.year, month, day))
        file1 = open("%s/%s/%s/%s/%s.jpg" % (path, future_date.year, month,
                day, hour), "w")
        file1.write('a')
        file1.close()
        # get URL for 3 hours into the future (should be 404)
        rv = self.app.get("/%s/%s/%s/%s/" % (future_date.year, month, day,
                hour))
        assert rv.status == "404 NOT FOUND"

        # create file for 3 hours in the past
        past_date = current_tz_time - timedelta(hours=3)
        month = str(past_date.month) if past_date.month > 9 else "0%s" %\
                past_date.month
        day = str(past_date.day) if past_date.day > 9 else "0%s" %\
                past_date.day
        hour = str(past_date.hour) if past_date.hour > 9 else "0%s" %\
                past_date.hour
        try:
            os.mkdir("%s/%s" % (path, past_date.year))
        except OSError:
            pass
        try:
            os.mkdir("%s/%s/%s" % (path, past_date.year, month))
        except OSError:
            pass
        try:
            os.mkdir("%s/%s/%s/%s" % (path, past_date.year, month, day))
        except OSError:
            pass
        file2 = open("%s/%s/%s/%s/%s.jpg" % (path, past_date.year, month, day,
                hour), "w")
        file2.write('a')
        file2.close()

        # get URL for 3 hours into the past (should be 200)
        rv = self.app.get("/%s/%s/%s/%s/" % (past_date.year, month, day, hour))
        assert rv.status == "200 OK"

    def test_rss_hourly(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2010" % path)
        os.mkdir("%s/2010/01" % path)
        os.mkdir("%s/2010/01/01" % path)
        file1 = open("%s/2010/01/01/01.jpg" % path, "w")
        file1.write('a')
        file1.close()
        file2 = open("%s/2010/01/01/02.jpg" % path, "w")
        file2.write('a')
        file2.close()
        file3 = open("%s/2010/01/01/03.jpg" % path, "w")
        file3.write('a')
        file3.close()

        rv = self.app.get("/feed/hourly/")
        assert "<link>http://example.com/2010/01/01/01/</link>" in rv.data
        assert "<link>http://example.com/2010/01/01/01/</link>" in rv.data
        assert "<link>http://example.com/2010/01/01/02/</link>" in rv.data
        assert "<link>http://example.com/2010/01/01/03/</link>" in rv.data
        assert "<link>http://example.com/2010/01/01/04/</link>" not in rv.data

    def test_rss_daily(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2010" % path)
        os.mkdir("%s/2010/01" % path)
        os.mkdir("%s/2010/01/01" % path)
        file1 = open("%s/2010/01/01/01.jpg" % path, "w")
        file1.write('a')
        file1.close()
        file2 = open("%s/2010/01/01/02.jpg" % path, "w")
        file2.write('a')
        file2.close()
        file3 = open("%s/2010/01/01/03.jpg" % path, "w")
        file3.write('a')
        file3.close()
        os.mkdir("%s/2010/01/02" % path)
        file4 = open("%s/2010/01/02/01.jpg" % path, "w")
        file4.write('a')
        file4.close()
        file5 = open("%s/2010/01/02/02.jpg" % path, "w")
        file5.write('a')
        file5.close()
        file6 = open("%s/2010/01/02/03.jpg" % path, "w")
        file6.write('a')
        file6.close()

        rv = self.app.get("/feed/daily/")
        assert "<link>http://example.com/2010/01/01/</link>" in rv.data
        assert "<img src=\"http://example.com%s/2010/01/01/01.jpg" % \
                hourlyimage.app.config["IMAGE_LOCATION_URL"] in rv.data
        assert "<link>http://example.com/2010/01/02/</link>" in rv.data
        assert "<img src=\"http://example.com%s/2010/01/02/01.jpg" % \
                hourlyimage.app.config["IMAGE_LOCATION_URL"] in rv.data
        assert "<link>http://example.com/2010/01/04/</link>" not in rv.data

    def test_static_pages(self):
        statics_dir = hourlyimage.app.config["STATIC_PAGE_DIR"]
        file1 = open("%s/about.html" % statics_dir, "w")
        file1.write("<h1>About us</h1><p>Stuff!</p>")
        file1.close()

        rv = self.app.get("/about")
        print rv.data
        assert "<h1>About us</h1><p>Stuff!</p>" in rv.data


if __name__ == '__main__':
    unittest.main()
