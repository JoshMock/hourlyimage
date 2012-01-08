import os
from flask import Flask, render_template
from utilities import list_directories, list_images


app = Flask(__name__)
app.config["IMAGE_LOCATION_DIR"] = "/Users/joshmock/Documents/Code/hourlyimage_images" # TODO: change before release
app.config["IMAGE_LOCATION_URL"] = "/static/images" # TODO: change before release

@app.route("/")
def index():
    """
        Display available years.
    """
    years = list_directories()
    return render_template("home.html", years=years)

@app.route("/<year>/")
def year(year):
    """
        Display available months in selected year.
    """
    months = list_directories(year=year)
    kwargs = {
        "year": year,
        "months": months,
    }
    return render_template("year.html", **kwargs)

@app.route("/<year>/<month>/")
def month(year, month):
    """
        Display available days in selected month.
    """
    days = list_directories(year=year, month=month)
    kwargs = {
        "year": year,
        "month": month,
        "days": days,
    }
    return render_template("month.html", **kwargs)

@app.route("/<year>/<month>/<day>/")
def day(year, month, day):
    """
        Display available images in selected day.
    """
    path = "%s/%s/%s/%s" % (app.config["IMAGE_LOCATION_DIR"], year, month, day)
    images = list_images(year, month, day)
    kwargs = {
        "year": year,
        "month": month,
        "day": day,
        "images": images,
    }
    return render_template("day.html", **kwargs)


if __name__ == "__main__":
    app.config["DEBUG"] = True # TODO: remove
    app.run()
