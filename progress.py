import os

from flask import Flask, make_response, redirect, render_template, request, send_from_directory
from fontTools.ttLib import TTFont

app = Flask(__name__)

def get_progress_color(progress, scale):
    ratio = progress / scale

    if ratio < 0.3:
        return "#d9534f"
    if ratio < 0.7:
        return "#f0ad4e"

    return "#5cb85c"


def get_template_fields(progress):
    font = TTFont('./fonts/Verdana.ttf')
    cmap = font['cmap']
    t = cmap.getcmap(3, 1).cmap
    s = font.getGlyphSet()
    units_per_em = font['head'].unitsPerEm
    padding = 8

    title = request.args.get("title")

    scale = 100
    try:
        scale = int(request.args.get("scale"))
    except (TypeError, ValueError):
        pass

    progress_width = 60 if title else 90
    try:
        progress_width = int(request.args.get("width"))
    except (TypeError, ValueError):
        pass

    def title_width(text, pointSize):
        total = 0
        for c in text:
            if ord(c) in t and t[ord(c)] in s:
                total += s[t[ord(c)]].width
            else:
                total += s['.notdef'].width
        total = total * float(pointSize) / units_per_em
        return total + padding

    return {
        "title": title,
        "title_width": title_width(title, 11) if title else 0,
        "title_color": request.args.get("color", "428bca"),
        "scale": scale,
        "progress": progress,
        "progress_width": progress_width,
        "progress_color": get_progress_color(progress, scale),
        "suffix": request.args.get("suffix", "%"),
    }


@app.route("/<int:progress>/")
def get_progress_svg(progress):
    template_fields = get_template_fields(progress)

    template = render_template("progress.svg", **template_fields)

    response = make_response(template)
    response.headers["Content-Type"] = "image/svg+xml"
    return response


@app.route("/fonts/<filename>")
def download(filename):
    return send_from_directory(directory="fonts", filename=filename)


@app.route("/")
def redirect_to_github():
    return redirect("https://github.com/tuchengpanghu/progress-bar", code=302)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
