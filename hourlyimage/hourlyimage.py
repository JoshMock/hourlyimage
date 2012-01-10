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
    years = list_directories(app.config["IMAGE_LOCATION_DIR"])
    return render_template("home.html", years=years)

@app.route("/<year>/")
def year(year):
    """
        Display available months in selected year.
    """
    months = list_directories(app.config["IMAGE_LOCATION_DIR"], year=year)
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
    days = list_directories(app.config["IMAGE_LOCATION_DIR"], year=year,
            month=month)
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
    path = app.config["IMAGE_LOCATION_DIR"]
    url = app.config["IMAGE_LOCATION_URL"]
    image_files = list_images(path, url, year, month, day)

    images = []
    for image in image_files:
        images.append({
            "url": image,
            "hour": os.path.splitext(os.path.split(image)[1])[0],
            "hour_name": None,
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
    path = app.config["IMAGE_LOCATION_DIR"]
    url = app.config["IMAGE_LOCATION_URL"]
    images = list_images(path, url, year, month, day, hour=hour)
    kwargs = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "images": images,
    }
    return render_template("hour.html", **kwargs)

if __name__ == "__main__":
    app.config["DEBUG"] = True # TODO: remove
    app.run()
