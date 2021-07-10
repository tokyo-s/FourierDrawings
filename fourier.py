import cmath
import sys
from flask import Blueprint, render_template, request, jsonify, current_app
from scipy import integrate
import numpy as np
import matplotlib.pyplot as plt
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import SubmitField, IntegerField
from svgpathtools import svg2paths
from svg2paths_ext import svg_file2paths
from xml.dom.minidom import parse
import svgutils
import os
from werkzeug.utils import secure_filename
from svgpathtools import smoothed_path

fourier_blueprint = Blueprint('fourier', __name__)

class FourierForm(FlaskForm):
    svg_file = FileField(u"SVG to plot", validators=[
        FileRequired(),
        FileAllowed(['svg'], 'svgs only!')
    ])
    canvas_width = IntegerField(u"The canvas width to plot on")
    canvas_height = IntegerField(u"The canvas height to plot on")
    number_of_circles = IntegerField(u"How many circles to draw")
    submit = SubmitField("Plot")


@fourier_blueprint.route("/")
def fourier_index():
    print('fdfsdfds')
    return render_template('fourier.html', form=FourierForm())


@fourier_blueprint.route('/fourier/get_constants', methods=['PUT', 'POST'])
def get_fourier_constants_post():
    form = FourierForm()
    if form.validate_on_submit():
        f = form.svg_file.data
        file = request.files['file']
        print(file)
        # f.save(os.getcwd())
        # svg = svgutils.transform.fromfile(f.filename)
        #f.rotate()
        #f.save("D:\\programming\\ML\\graphimages\\FourierFromSVG-master\\FourierFromSVG-master")
        #doc = parse(f)
        number_of_circles = form.number_of_circles.data
        canvas_width = form.canvas_width.data
        canvas_height = form.canvas_height.data
        current_app.logger.debug('Calculating fourier constants for %s with %d circles', f.filename, number_of_circles)
        fourier_constants = calculate_fourier_for_svg(form,f, number_of_circles, canvas_width, canvas_height)
        return jsonify(convert_fourier_constants_for_js(fourier_constants))
    return jsonify(data=form.errors)


def convert_fourier_constants_for_js(constants):
    result = []
    for constant in constants:
        result.append(convert_fourier_constant_for_js(constant))
    return result


def convert_fourier_constant_for_js(constant):
    radius, angle = cmath.polar(constant['C'])
    return {
        's': constant['speed'],
        'r': radius,
        'a': angle
    }


def calculate_fourier_for_svg_path(svg_path, count):
    paths, _ = svg2paths(svg_path)
    return calculate_fourier_for_path(paths[count], count, 600, 600)


def calculate_fourier_for_svg(form,svg_file, count, canvas_width, canvas_height):
    paths, attributes = svg_file2paths(svg_file)
    return calculate_fourier_for_path(form,paths, count, canvas_width, canvas_height)


def complex_integrate(func, *args):
    result = integrate.fixed_quad(func, 0, 1, n=500, args=args)[0]
    return result


def scale_svg(path, x, y):
    orig_bbox = path.bbox()
    path = path.translated(-(orig_bbox[0] - 20) - (orig_bbox[2] - 20) * 1j)
    y_diff = orig_bbox[3] - orig_bbox[2]
    x_diff = orig_bbox[1] - orig_bbox[0]
    scale_factor = min(x / x_diff, y / y_diff)
    scaled = path.scaled(scale_factor, scale_factor)
    return scaled


def calculate_fourier_for_path(form,paths, count, canvas_width, canvas_height):
    result = []
    maxx= -999999999
    maxy = -99999999
    minx = 99999999
    miny = 99999999
    for path in paths:
        #path = path.rotated(180)
        maxx = max(maxx,path.bbox()[1])
        minx = min(minx,path.bbox()[0])
        miny = min(miny,path.bbox()[2])
        maxy = max(maxy,path.bbox()[3])

    print("x - ",minx,' ',maxx)
    print("y - ",miny,' ',maxy)
    # form.canvas_width.data = (maxx-minx)/10
    # form.canvas_height.data = (maxy-miny)/10

    if (maxx-minx)<(maxy-miny):
        canvas_width = (maxx-minx)/((maxy-miny)/1450)  #################
        canvas_height = (maxy-miny)/((maxy-miny)/1450) ##########
    else:
        canvas_width = (maxx-minx)/((maxx-minx)/1450)  #################
        canvas_height = (maxy-miny)/((maxx-minx)/1450) ##########
    # print('########################################################################################3')
    # print(canvas_width,canvas_height)
    # print('########################################################################################3')
    for i,path in enumerate(paths):
        #path = path.rotated(180)
        #print(path.getBoundig)
        #print(path.getBoundingClientRect().width)
        xmin, xmax, ymin, ymax = path.bbox()
        
        height = ymax - ymin
        width = xmax - xmin
        print(i)
        print("xmin = ",xmin)
        print("ymin = ",ymin)
        widthpercent=width/(maxx-minx)
        heightpercent = height/(maxy-miny)
        path = scale_svg(path,widthpercent*canvas_width,heightpercent*canvas_height) # path = scale_svg(path,widthpercent*canvas_width,heightpercent*canvas_height)
        
        #path = path.translated()#+xmin/(maxx-minx)*canvas_width+ymin/(maxy-miny)*canvas_height*1j
        


        
        #path = path.translated(-(xmin - 20) - (ymin - 20) * 1j)
        _get_path_point = np.vectorize(lambda x: path.point(x))
        def _func(x, n):
            return np.exp(-n * 2 * np.pi * x * 1j) * _get_path_point(x)

        result.append({'speed': 0, 'C': complex_integrate(_func, 0)+(xmin)/(maxx-minx)*canvas_width+(ymin+(1500-canvas_height))/(maxy-miny)*canvas_height*1j+1500*1j})#+xmin/maxx*canvas_width+ymin/(maxy/canvas_height)*1j
        for i in range(1, count):
            result.append({'speed': i, 'C': complex_integrate(_func, i)})
            result.append({'speed': -i, 'C': complex_integrate(_func, -i)})
    return result


# def plot_svg_path(svg):
#     paths, _ = svg2paths(svg)

#     def _func(x):
#         return paths[0].point(x)

#     vct = np.vectorize(_func)
#     line = np.linspace(0, 1, num=5000)
#     cnums = vct(line)
#     X = [x.real for x in cnums]
#     Y = [x.imag for x in cnums]
#     # plt.scatter(X,Y, color='black')
#     plt.plot(line, X)
#     plt.plot(line, Y)
#     plt.show()


if __name__ == "__main__":
    # plot_svg_path(sys.argv[1])
    print(convert_fourier_constants_for_js(
        calculate_fourier_for_svg_path(sys.argv[1], int(sys.argv[2]))))
