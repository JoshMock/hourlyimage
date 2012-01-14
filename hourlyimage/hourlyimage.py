from datetime import datetime
import os
import re
from flask import abort, Flask, make_response, render_template
from utilities import generate_tree
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


@app.route("/")
def index():
    """
        Display available years.
    """
    tree = generate_tree(app.config["IMAGE_LOCATION_DIR"],
            app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    return render_template("home.html", years=tree.keys())


@app.route("/<year>/")
def year(year):
    """
        Display available months in selected year.
    """
    try:
        tree = generate_tree("%s/%s" % (app.config["IMAGE_LOCATION_DIR"],
                year), app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    except OSError:
        abort(404)
    if not tree:
        abort(404)

    kwargs = {
        "year": year,
        "months": tree.keys(),
    }
    return render_template("year.html", **kwargs)


@app.route("/<year>/<month>/")
def month(year, month):
    """
        Display available days in selected month.
    """
    try:
        tree = generate_tree("%s/%s/%s" % (app.config["IMAGE_LOCATION_DIR"],
                year, month), app.config["TIMEZONE"],
                app.config["OFFSET_HOURS"])
    except OSError:
        abort(404)
    if not tree:
        abort(404)

    kwargs = {
        "year": year,
        "month": month,
        "days": tree.keys(),
    }
    return render_template("month.html", **kwargs)


@app.route("/<year>/<month>/<day>/")
def day(year, month, day):
    """
        Display available images in selected day.
    """
    try:
        image_files = generate_tree("%s/%s/%s/%s" % (
                app.config["IMAGE_LOCATION_DIR"], year, month, day),
                app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
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
            "hour_name": "",
        })

    kwargs = {
        "year": year,
        "month": month,
        "day": day,
        "images": images,
    }
    return render_template("day.html", **kwargs)


@app.route("/<year>/<month>/<day>/<hour>/")
def hour(year, month, day, hour):
    """
        Display image for selected hour if it exists.
    """
    try:
        image_files = generate_tree("%s/%s/%s/%s" % (
                app.config["IMAGE_LOCATION_DIR"], year, month, day),
                app.config["TIMEZONE"], app.config["OFFSET_HOURS"])
    except OSError:
        abort(404)
    if not image_files:
        abort(404)

    kwargs = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "image": image_files[hour],
    }
    return render_template("hour.html", **kwargs)


@app.route("/feed/hourly/")
def rss_hourly():
    tree = generate_tree(app.config["IMAGE_LOCATION_DIR"],
            app.config["TIMEZONE"], app.config["OFFSET_HOURS"])

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
    domain = app.config["SITE_DOMAIN"]
    path = app.config["IMAGE_LOCATION_DIR"]
    url = app.config["IMAGE_LOCATION_URL"]
    tree = generate_tree(path, app.config["TIMEZONE"],
            app.config["OFFSET_HOURS"])

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
    print rss_items

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
