from datetime import datetime, timedelta
import os
import re
from flask import abort, Flask, make_response, Markup, render_template
from flaskext.themes import render_theme_template, setup_themes
from filetree import FileTree
from pytz import timezone
import pytz


app = Flask(__name__)

# TODO: change before release
app.config["IMAGE_LOCATION_DIR"] = \
        "/Users/joshmock/Documents/Code/hourlyimage_images"
app.config["IMAGE_LOCATION_URL"] = "/static/images"
app.config["TIMEZONE"] = pytz.utc
app.config["OFFSET_HOURS"] = 0
app.config["SITE_DOMAIN"] = "example.com"
app.config["STATIC_PAGE_DIR"] = "/Users/joshmock/Documents/Code/hourlyimage_pages"
app.config["DEFAULT_THEME"] = "default"

setup_themes(app, app_identifier="hourlyimage")


@app.route("/")
def index():
    """
        Display available years and current day's images.
    """
    ft = FileTree(app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    path = app.config["IMAGE_LOCATION_DIR"]
    tree = ft.generate_tree(path)

    utc_time = pytz.utc.localize(datetime.utcnow())
    tz_time = utc_time.astimezone(app.config["TIMEZONE"]) - \
            timedelta(hours=app.config["OFFSET_HOURS"])

    year = str(tz_time.year)
    month = "0%s" % tz_time.month if tz_time.month < 10 else str(tz_time.month)
    day = "0%s" % tz_time.day if tz_time.day < 10 else str(tz_time.day)

    current_day_images = None
    if tree.get(year, {}).get(month, {}).get(day):
        current_day_images = []
        for hour, image in tree[year][month][day].iteritems():
            hour = int(hour)
            date_hour = datetime(int(year), tz_time.month, tz_time.day, hour)
            current_day_images.append({
                "path": image.replace(path, app.config["IMAGE_LOCATION_URL"]),
                "name": date_hour.strftime("%I:00 %p"),
            })

    kwargs = {
        "years": tree,
        "current_day": current_day_images,
    }
    return render_theme_template(app.config["DEFAULT_THEME"], "home.html",
            **kwargs)


@app.route("/content/<page_name>")
def static_pages(page_name):
    """
        Enables user to create static content pages by placing partial-HTML
        files in a provided directory.
    """
    statics = app.config["STATIC_PAGE_DIR"]

    f = None
    if os.path.exists("%s/%s.html" % (statics, page_name)):
        f = open("%s/%s.html" % (statics, page_name))
    elif os.path.exists("%s/%s.htm" % (statics, page_name)):
        f = open("%s/%s.htm" % (statics, page_name))
    else:
        abort(404)
    html = f.read()
    f.close()

    kwargs = {
        "html": Markup(html),
    }
    return render_theme_template(app.config["DEFAULT_THEME"],
            "static_page.html", **kwargs)


@app.route("/images/<int:year>/")
def year(year):
    """
        Display available months in selected year.
    """
    ft = FileTree(app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    path = "%s/%s" % (app.config["IMAGE_LOCATION_DIR"], year)

    try:
        tree = ft.generate_tree(path)
    except OSError:
        abort(404)

    if not tree:
        abort(404)

    months = tree.keys()
    month_data = []
    for month in months:
        month_data.append({
            "value": month,
            "name": datetime(year, int(month), 1).strftime("%B"),
        })

    kwargs = {
        "year": year,
        "months": month_data,
    }
    return render_theme_template(app.config["DEFAULT_THEME"], "year.html",
            **kwargs)


@app.route("/images/<year>/<month>/")
def month(year, month):
    """
        Display available days in selected month.
    """
    ft = FileTree(app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    path = "%s/%s/%s" % (app.config["IMAGE_LOCATION_DIR"], year, month)

    try:
        tree = ft.generate_tree(path)
    except OSError:
        abort(404)

    if not tree:
        abort(404)

    kwargs = {
        "year": year,
        "month": {
            "value": month,
            "name": datetime(int(year), int(month), 1).strftime("%B"),
        },
        "days": tree.keys(),
    }
    return render_theme_template(app.config["DEFAULT_THEME"], "month.html",
            **kwargs)


@app.route("/images/<year>/<month>/<day>/")
def day(year, month, day):
    """
        Display available images in selected day.
    """
    ft = FileTree(app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    path = "%s/%s/%s/%s" % (app.config["IMAGE_LOCATION_DIR"], year, month, day)

    try:
        image_files = ft.generate_tree(path)
    except OSError:
        abort(404)

    if not image_files:
        abort(404)

    images = []
    for hour, image in image_files.iteritems():
        images.append({
            "url": image.replace(app.config["IMAGE_LOCATION_DIR"],
                    app.config["IMAGE_LOCATION_URL"]),
            "hour": hour,
            "hour_name": datetime(int(year), int(month), int(day),
                int(hour)).strftime("%I:00 %p"),
        })

    # find next/previous days
    days_tree = ft.generate_tree(app.config["IMAGE_LOCATION_DIR"])
    days = []
    for iter_year, year_data in days_tree.iteritems():
        for iter_month, month_data in year_data.iteritems():
            for iter_day, day_data in month_data.iteritems():
                days.append((iter_year, iter_month, iter_day))
    days = sorted(days)

    prev_day = None
    next_day = None
    for index, a_day in enumerate(days):
        if a_day == (year, month, day):
            if index - 1 >= 0:
                prev_day = days[index - 1]
                prev_day = {
                    "year": prev_day[0],
                    "month": prev_day[1],
                    "day": prev_day[2]
                }
            if index + 1 < len(days):
                next_day = days[index + 1]
                next_day = {
                    "year": next_day[0],
                    "month": next_day[1],
                    "day": next_day[2]
                }
            break

    kwargs = {
        "year": year,
        "month": {
            "value": month,
            "name": datetime(int(year), int(month), int(day)).strftime("%B")
        },
        "day": day,
        "images": images,
        "prev_day": prev_day,
        "next_day": next_day,
    }
    return render_theme_template(app.config["DEFAULT_THEME"], "day.html",
            **kwargs)


@app.route("/images/<year>/<month>/<day>/<hour>/")
def hour(year, month, day, hour):
    """
        Display image for selected hour if it exists.
    """
    ft = FileTree(app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    path = "%s/%s/%s/%s" % (app.config["IMAGE_LOCATION_DIR"], year, month, day)

    try:
        image_files = ft.generate_tree(path)
    except OSError:
        abort(404)

    if not image_files:
        abort(404)

    kwargs = {
        "year": year,
        "month": {
            "value": month,
            "name": datetime(int(year), int(month), int(day)).strftime("%B")
        },
        "day": day,
        "hour": hour,
        "hour_name": datetime(int(year), int(month), int(day),
                int(hour)).strftime("%I:00 %p"),
        "image": image_files[hour].replace(app.config["IMAGE_LOCATION_DIR"],
                app.config["IMAGE_LOCATION_URL"]),
    }
    return render_theme_template(app.config["DEFAULT_THEME"], "hour.html",
            **kwargs)


@app.route("/feed/hourly/")
def rss_hourly():
    """
        RSS feed of images, with a new feed item for each hourly image.
    """
    ft = FileTree(app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    tree = ft.generate_tree(app.config["IMAGE_LOCATION_DIR"])

    rss_items= []
    for years, year_data in tree.iteritems():
        for months, month_data in year_data.iteritems():
            for days, day_data in month_data.iteritems():
                for hours, hour_file in day_data.iteritems():
                    rss_items.append(hour_file)

    dir_re = re.compile(r'/([0-9]{1,4})/([0-9]{2,2})/([0-9]{2,2})/([0-9]{2,2})\.')
    rss_items = sorted(rss_items, reverse=True)[0:50]
    rss_data = []
    for item in rss_items:
        match = dir_re.search(item)
        year = match.group(1),
        month = match.group(2),
        day = match.group(3),
        hr = match.group(4),

        year = year[0]
        month = month[0]
        day = day[0]
        hr = hr[0]

        date = datetime(int(year), int(month), int(day), int(hr))
        date_name = date.strftime("%A, %B %d, %Y, %I:00 %p")
        pub_date = date.strftime("%a, %d %b %Y, %H:00:00")

        rss_data.append({
            "path": "http://%s%s" % (app.config["SITE_DOMAIN"],
                item.replace(app.config["IMAGE_LOCATION_DIR"],
                app.config["IMAGE_LOCATION_URL"])),
            "url": "http://%s/%s/%s/%s/%s/" % (app.config["SITE_DOMAIN"], year,
                month, day, hr),
            "date_name": date_name,
            "pub_date": pub_date,
        })

    kwargs = {
        "rss": rss_data,
        "pub_date": rss_data[0]["pub_date"],
        "link": "http://%s/" % app.config["SITE_DOMAIN"],
    }
    response = make_response(render_template("rss_hourly.xml", **kwargs))
    response.headers["Content-type"] = "application/xml"
    return response


@app.route("/feed/daily/")
def rss_daily():
    """
        RSS feed of images, with a new feed item for each available day.
    """
    domain = app.config["SITE_DOMAIN"]
    path = app.config["IMAGE_LOCATION_DIR"]
    url = app.config["IMAGE_LOCATION_URL"]
    ft = FileTree(app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    tree = ft.generate_tree(path)

    rss_items= []
    for years, year_data in tree.iteritems():
        for months, month_data in year_data.iteritems():
            for days, day_data in month_data.iteritems():
                images = []
                for hour, image_path in day_data.iteritems():
                    image = {
                        "path": "http://%s%s" % (domain,
                            image_path.replace(path, url)),
                        "name": "",
                    }
                    images.append(image)
                images = sorted(images)
                rss_items.append(images)

    rss_items = sorted(rss_items, key=lambda day: day[0]["path"], reverse=True)

    dir_re = re.compile(r'/([0-9]{1,4})/([0-9]{2,2})/([0-9]{2,2})/')
    rss_data = []

    for item in rss_items:
        match = dir_re.search(item[0]["path"])
        year = match.group(1),
        month = match.group(2),
        day = match.group(3),

        year = year[0]
        month = month[0]
        day = day[0]

        date = datetime(int(year), int(month), int(day))
        date_name = date.strftime("%A, %B %d, %Y")
        pub_date = date.strftime("%a, %d %b %Y, 00:00:00")

        rss_data.append({
            "images": item,
            "url": "http://%s/%s/%s/%s/" % (app.config["SITE_DOMAIN"], year,
                month, day),
            "date_name": date_name,
            "pub_date": pub_date,
        })

    kwargs = {
        "rss": rss_data,
        "pub_date": rss_data[0]["pub_date"],
        "link": "http://%s/" % app.config["SITE_DOMAIN"],
    }
    response = make_response(render_template("rss_daily.xml", **kwargs))
    response.headers["Content-type"] = "application/xml"
    return response


if __name__ == "__main__":
    app.config["DEBUG"] = True  # TODO: remove
    app.run()
