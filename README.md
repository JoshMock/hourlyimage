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

 * **A summary for 2011:** http://yoursite.com/2011/
 * **A summary for December of 2011:** http://yoursite.com/2011/12/
 * **All images for December 21, 2011:** http://yoursite.com/2011/12/21/
 * **The image for 1pm on December 21, 2011:** http://yoursite.com/2011/12/21/13/
 * **The image for 2pm on December 21, 2011:** http://yoursite.com/2011/12/21/14/
 * **The image for 3pm on December 21, 2011:** http://yoursite.com/2011/12/21/15/

It would also update the daily RSS feed, adding the new images to the December 21 entry, and the hourly RSS feed with 3 new entries, one for each hour.

Installation
------------
TODO: Finish this.


TODOs
-----
 * Separate user templating from Flask project folder.
 * Provide date/time offset config option (if you want things to show up 24 hours after actual time, 1 hour after actual time, etc.)
 * Complete templating in standards-compliant HTML5.
 * PEP8 ALL THE PYTHONS!
 * Ability to create static content pages (about, contact, etc.)
 * Make sure Flask routing lets user create directories and files of their own somewhere that they can link to.
 * RSS feeds.
 * "Latest image" view.
 * "Today" view.
 * Pretty 404 and 500 error pages
 * What to do if 01.jpg, 01.png, 01.gif, etc. all exist?
