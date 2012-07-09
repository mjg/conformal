#!/usr/bin/env python

#   conformal.py
#   Copyright (C) 2006-2011  Michael J. Gruber <conformal@drmicha.warpmail.net>
#
#    This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

confversion = "0.3+"

# allow access through module and without
import math, cmath
from math import *
from cmath import *

from array import array
from gimpfu import *

# try importing typical math modules
try:
	from fpconst import *
	import scipy.special
except ImportError:
	pass

try:
	import mpmath
except ImportError:
	pass


def conformal_batch(width, height, code, constraint, xl, xr, yt, yb, grid, checkboard, gradient, filename):
	conformal_core(width, height, code, constraint, xl, xr, yt, yb, grid, checkboard, gradient, filename)


def conformal(width, height, code, constraint, xl, xr, yt, yb, grid, checkboard, gradient):
	conformal_core(width, height, code, constraint, xl, xr, yt, yb, grid, checkboard, gradient, None)


def conformal_core(width, height, code, constraint, xl, xr, yt, yb, grid, checkboard, gradient, filename):
	image = gimp.Image(width, height, RGB) 
	drawables = [ gimp.Layer(image, "Argument", width, height, RGBA_IMAGE, 100, NORMAL_MODE),
		      gimp.Layer(image, "Log. modulus", width, height, RGBA_IMAGE, 35, VALUE_MODE),
		      gimp.Layer(image, "Grid", width, height, RGBA_IMAGE, 10, DARKEN_ONLY_MODE)]
	image.disable_undo()
	l = 1
	for drawable in drawables:
		image.add_layer(drawable, l)
		l = -1

	bpp = drawables[0].bpp

	gimp.tile_cache_ntiles(2 * (width + 63) / 64)

	dest_rgns = [ drawable.get_pixel_rgn(0, 0, width, height, True, False) for drawable in drawables ]
	progress = 0
	max_progress = width * height
	if filename is None:
		gimp.progress_init("Conformally Mapping...")
	sx = (width-1.0)/(xr-xl)
	sy = (height-1.0)/(yt-yb)
	w = complex(0.0)
	z = complex(0.0)
	cx, cy = 0, 0
	mp2 = 2.0*math.pi # no need to do this 500*500 times...
	ml2 = 2.0*math.log(2) # no need to do this 500*500 times...
	ml = math.log(2) # no need to do this 500*500 times...
	compiled=compile(code, "compiled code", "exec", 0, 1)
	compiledconstraint=compile(constraint, "compiled constraint code", "exec", 0, 1)

	for row in range(0, height):
		args = []
		mods = []
		sqrs = []
		for col in range(0, width):
			z = col/sx + xl + 1j*( yt - row/sy)
			p = True
			try:
				exec(compiledconstraint)
			except (OverflowError, ValueError):
				p = False
			if not p:
				w = 0.0
			else:
				try:
					exec(compiled)
				except (OverflowError, ValueError):
					w = 0.0
			if isnan(w) or isinf(w):
				w = 0.0

			try:
				logw = cmath.log(w)
				arg = logw.imag
				if isnan(arg) or isinf(arg):
					arg = 0.0
				elif arg < 0.0:
					arg = arg + mp2
				mod = ( logw.real/ml ) % 1.0
				if isnan(mod) or isinf(mod):
					mod = 0.0
			except (OverflowError, ValueError):
				arg = 0.0
				mod = 0.0
			args.append( arg/mp2 )
			mods.append ( mod )

			try:
				sqr = int(w.imag/grid % 2.0) + int(w.real/grid % 2.0)
				if isnan(sqr) or isinf(sqr):
					sqr = 0.0
			except (OverflowError, ValueError):
				sqr = 0.0
			sqrs.extend( (bpp-1)*[ 255*(sqr % 2) ,] + [255, ] )

		samples = gimp.gradient_get_custom_samples(gradient, args)
		top_p = array("B", [ int(255*samples[col][i]+0.5) for col in range(0, width) for i in range(bpp) ] )

		dest_rgns[0][0:width, row] = top_p.tostring()
	
		samples = gimp.gradient_get_custom_samples("Default", mods)
		top_p = array("B", [ int(255*samples[col][i]+0.5) for col in range(0, width) for i in range(bpp) ] )
		dest_rgns[1][0:width, row] = top_p.tostring()

		top_p = array("B", sqrs )
		dest_rgns[2][0:width, row] = top_p.tostring()
	
		progress = progress + width 
		if filename is None:
			gimp.progress_update(float(progress) / max_progress)

	for drawable in drawables:
		drawable.flush()
		drawable.update(0,0,width,height)
	if not checkboard:
		pdb.plug_in_edge(image,drawables[2], 10, 0, 0) # amount, WRAP, SOBEL
		pdb.plug_in_vinvert(image,drawables[2])
	if image.parasite_find("gimp-comment"):
		image.parasite.detach("gimp-comment")
	image.attach_new_parasite("gimp-comment", PARASITE_PERSISTENT, """# conformal %s
code = \"\"\"
%s
\"\"\"
constraint = \"\"\"
%s
\"\"\"
xl = %f
xr = %f
yt = %f
yb = %f
grid = %f
checkboard = %d
gradient = "%s"
width = %d
height = %d
""" % (confversion, code, constraint, xl, xr, yt, yb, grid, checkboard, gradient, width, height))
	if filename is None:
		image.enable_undo()
		gimp.Display(image)
		gimp.displays_flush
	else:
		if filename.find('.xcf') > 0:
			pdb.gimp_xcf_save(1, image, drawables[0], filename, filename)
		else:
			flat_layer = pdb.gimp_image_flatten(image)
			pdb.gimp_file_save(image, flat_layer, filename, filename)


register(
	"conformal_batch",
	"Colour representation of a conformal map",
	"Colour representation of a conformal map",
	"Michael J Gruber",
	"Michael J Gruber",
	"2011",
	"",
	"",
	[
		(PF_INT, "width", "width", 512),
		(PF_INT, "height", "height", 512),
		(PF_TEXT, "code", "code", "w=z"),
		(PF_TEXT, "constraint", "constraint", "p=True"),
		(PF_FLOAT, "xl", "x left", -1.0),
		(PF_FLOAT, "xr", "x right", 1.0),
		(PF_FLOAT, "yt", "y top", 1.0),
		(PF_FLOAT, "yb", "y bottom", -1.0),
		(PF_FLOAT, "grid", "grid spacing", 1.0),
		(PF_BOOL, "checkboard", "checker board grid", 0),
		(PF_GRADIENT, "gradient", "gradient", "Full saturation spectrum CCW"),
		(PF_FILE, "file", "file", "out.xcf.bz2"),
	],
	[],
	conformal_batch)

register(
	"conformal",
	"Colour representation of a conformal map",
	"Colour representation of a conformal map",
	"Michael J Gruber",
	"Michael J Gruber",
	"2012",
	"<Toolbox>/File/Create/_Conformal ...",
	"",
	[
		(PF_INT, "width", "width", 512),
		(PF_INT, "height", "height", 512),
		(PF_TEXT, "code", "code", "w=z"),
		(PF_TEXT, "constraint", "constraint", "p=True"),
		(PF_FLOAT, "xl", "x left", -1.0),
		(PF_FLOAT, "xr", "x right", 1.0),
		(PF_FLOAT, "yt", "y top", 1.0),
		(PF_FLOAT, "yb", "y bottom", -1.0),
		(PF_FLOAT, "grid", "grid spacing", 1.0),
		(PF_BOOL, "checkboard", "checker board grid", 0),
		(PF_GRADIENT, "gradient", "gradient", "Full saturation spectrum CCW"),
	],
	[],
	conformal)

main()
