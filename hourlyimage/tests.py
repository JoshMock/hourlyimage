import os
import shutil
import unittest
import tempfile

import hourlyimage
import utilities


class HourlyImageTestCase(unittest.TestCase):
    def setUp(self):
        hourlyimage.app.config['TESTING'] = True

        # set up directories and symlink for images
        hourlyimage.app.config["IMAGE_LOCATION_DIR"] = tempfile.mkdtemp()
        os.symlink(hourlyimage.app.config["IMAGE_LOCATION_DIR"],
                "static/zzz_test_images") # TODO: include path to this current Python file before "static/" so this file's code can be run from anywhere
        hourlyimage.app.config["IMAGE_LOCATION_URL"] = "/static/zzz_test_images"

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

    def test_months_page_displays_days_accurately(self):
        path = hourlyimage.app.config["IMAGE_LOCATION_DIR"]

        os.mkdir("%s/2011" % path)
        os.mkdir("%s/2011/02" % path)
        os.mkdir("%s/2011/02/12" % path)
        os.mkdir("%s/2011/02/29" % path)
        os.mkdir("%s/2011/02/30" % path)
        os.mkdir("%s/2011/02/blah" % path)
        os.mkdir("%s/2012" % path)
        os.mkdir("%s/2012/02" % path)
        os.mkdir("%s/2012/02/29" % path)
        file1 = open("%s/2012/02/29/01.jpg" % path, "w")
        file1.write('a')
        file1.close()

        rv = self.app.get("/2011/02/")
        assert "/2011/02/12/" not in rv.data
        assert "/2011/02/29/" not in rv.data
        assert "/2011/02/30/" not in rv.data
        assert "/2011/02/blah/" not in rv.data
        rv = self.app.get("/2012/02/")
        assert "/2012/02/29/" in rv.data

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


if __name__ == '__main__':
    unittest.main()
