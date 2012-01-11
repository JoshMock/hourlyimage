import os
from flask import abort, Flask, render_template
from utilities import generate_tree


app = Flask(__name__)
app.config["IMAGE_LOCATION_DIR"] = "/Users/joshmock/Documents/Code/hourlyimage_images" # TODO: change before release
app.config["IMAGE_LOCATION_URL"] = "/static/images" # TODO: change before release

@app.route("/")
def index():
    """
        Display available years.
    """
    tree = generate_tree(app.config["IMAGE_LOCATION_DIR"])
    return render_template("home.html", years=tree.keys())

@app.route("/<year>/")
def year(year):
    """
        Display available months in selected year.
    """
    try:
        tree = generate_tree("%s/%s" % (app.config["IMAGE_LOCATION_DIR"], year))
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
        tree = generate_tree("%s/%s/%s" % (app.config["IMAGE_LOCATION_DIR"], year,
                month))
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
                app.config["IMAGE_LOCATION_DIR"], year, month, day))
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
                app.config["IMAGE_LOCATION_DIR"], year, month, day))
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

if __name__ == "__main__":
    app.config["DEBUG"] = True # TODO: remove
    app.run()
