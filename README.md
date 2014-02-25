hourlyimage
===========
A simple database-free website engine that displays time-sensitive images by regularly scanning a directory and its subdirectories -- which have a specific file structure -- for images. Images are displayed with pretty URLs. RSS feeds are available for posts by day or by hour.

How it works
------------
Once the site is installed and running, content is provided via FTP (or any other method that gets the images into the appropriate directories) using the following file structure:

    base directory
    `-year
      `-month
      `-month
      `-month
        `-day
          `-hour.jpg
          `-hour.jpg
          `-hour.jpg
        `-day
      `-month
      `-month
    `-year
      `-month
        `-day
          `-hour.jpg
          `-hour.jpg
      `-month
    `-year

For example, if in your settings, your base directory is `/myimages` and you wanted to put in images for 1pm, 2pm and 3pm on December 21 of 2011, your structure would look like this:

    my images
    `-2011
      `-12
        `-21
          `- 13.jpg
          `- 14.jpg
          `- 15.jpg

This would create the following available pages on your site:

* **A summary for 2011:** `http://yoursite.com/images/2011/`
* **A summary for December of 2011:** `http://yoursite.com/images/2011/12/`
* **All images for December 21, 2011:** `http://yoursite.com/images/2011/12/21/`
* **The image for 1pm on December 21, 2011:** `http://yoursite.com/images/2011/12/21/13/`
* **The image for 2pm on December 21, 2011:** `http://yoursite.com/images/2011/12/21/14/`
* **The image for 3pm on December 21, 2011:** `http://yoursite.com/images/2011/12/21/15/`

It would also update the daily RSS feed, adding the new images to the December 21 entry, and the hourly RSS feed with 3 new entries, one for each hour.

Installation
------------

1. Install hourlyimage
2. Create config file with the following required configuration values:
 * `IMAGE_LOCATION_DIR` - The full file path to where your images are stored.
 * `IMAGE_LOCATION_URL` - The relative URL path to where your images should be displayed on the site. I recommend putting a symlink inside your `/static` directory to where `IMAGE_LOCATION_DIR` is.
 * `TIMEZONE` - The pytz-formatted timezone where you are.
 * `OFFSET_HOURS` - The number of hours to wait before displaying an image. For example, `OFFSET_HOURS = 24` means the latest image shown would be from exactly one day ago.
 * `SITE_DOMAIN` - Your website's domain name.
 * `STATIC_PAGE_DIR` - The location to where your static page HTML files live.
 * `DEFAULT_THEME` - The name of the theme you want to use. Usually corresponds with the name of a directory inside `hourlyimage/hourlyimage/themes/`. More information on Flask-Themes [here](http://packages.python.org/Flask-Themes/).
3. Create an environment variable `HOURLYIMAGE_SETTINGS` pointing to your config file:

   `$ export HOURLYIMAGE_SETTINGS=/path/to/your/config.py`
4. Install dependencies.

   `$ cd path/to/hourlyimage`

   `$ pip install -r requirements.txt`

### To run your website in test/development mode ###
    $ cd path/to/hourlyimage/hourlyimage
    $ python hourlyimage.py

### To run in a production environment ###
See [Flask's description of deployment options](http://flask.pocoo.org/docs/deploying/).

TODOs
-----
* Pretty 404 and 500 error pages
* "Latest image" view.
* Daily RSS feed doesn't publish current day until it's over (keeping timezone and offset in mind)
* Add titles to images
* Add open-source license


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/JoshMock/hourlyimage/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

