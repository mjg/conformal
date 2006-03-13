#!/usr/bin/env python

#   Gimp-Python - allows the writing of Gimp plugins in Python.
#   Copyright (C) 1997  James Henstridge <james@daa.com.au>
#
#    This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import math, cmath
from math import *
from cmath import *
# allow access through module and without
from array import array
from gimpfu import *
try:
	from fpconst import *
	import scipy.special
except ImportError:
	pass

#import psyco
#psyco.full()

def python_conformal(code, xl, xr, yt, yb, grid, width, height):
	image = gimp.Image(width, height, RGB)
	drawables = [ gimp.Layer(image, "Argument", width, height, RGBA_IMAGE, 100, NORMAL_MODE),
	              gimp.Layer(image, "Log. modulus", width, height, RGBA_IMAGE, 35, DARKEN_ONLY_MODE),
		      gimp.Layer(image, "Grid", width, height, RGBA_IMAGE, 10, DARKEN_ONLY_MODE)]
        image.disable_undo()
	l = 1
        for drawable in drawables:
		image.add_layer(drawable, l)
		l = -1

        bpp = drawables[0].bpp

        gimp.tile_cache_ntiles(2 * (width + 63) / 64)

        dest_rgns = [ drawable.get_pixel_rgn(0, 0, width, height, TRUE, FALSE) for drawable in drawables ]
	#desta = drawables[0].get_pixel_rgn(0, 0, width, height, TRUE, FALSE)
	#destm = drawables[1].get_pixel_rgn(0, 0, width, height, TRUE, FALSE)
#	src_rgn = drawable.get_pixel_rgn(0, 0, width, height, FALSE, FALSE)
#        bg_colour = gimp.get_background()
#	bg_pixel = struct.pack('BBB', bg_colour[0], bg_colour[1], bg_colour[2])
#	if drawable.has_alpha:
#        	bg_pixel=bg_pixel + chr(0)
	gradient = gimp.context_get_gradient()
        progress = 0
        max_progress = width * height
        gimp.progress_init("Conformally Mapping...")
	sx = (width-1.0)/(xr-xl)
	sy = (height-1.0)/(yt-yb)
	w = complex(0.0)
	z = complex(0.0) # typedef
	cx, cy = 0, 0
	ml2 = 2.0*math.log(2) # no need to do this 500*500 times...
	compiled=compile(code, "compiled code", "exec", 0, 1)

	for row in range(0, height):
        	# top_p = ''
		args = ()
		mods = ()
		sqrs = ()
	# could use map or coll. instead of for, but it's no faster
        	for col in range(0, width):
		# z = complex(col/sx + xl, yt - row/sy) # 3s
			z = col/sx + xl + 1j*( yt - row/sy) # only 1s
			exec(compiled)	
			arg = math.atan2(w.imag, w.real)
			if arg<0.0:
				arg = arg + 2*math.pi
			args = args + ( arg/(2*math.pi) ,)
			try:
				mod = ( math.log(w.imag**2+w.real**2)/ml2 ) % 1.0
			except OverflowError:
				mod=0.0
			mods = mods + ( mod ,)
			sqrs = sqrs + (bpp-1)*( 255*(((int)(w.imag/grid % 2.0) + (int)(w.real/grid % 2.0)) % 2) ,) + (255, )

	        samples = gimp.gradient_get_custom_samples(gradient, args)
		top_p = array("B", [ ((int)(255*samples[col][i]+0.5)) for col in range(0, width) for i in range(bpp) ] )

	        dest_rgns[0][0:width, row] = top_p.tostring()
	
		samples = gimp.gradient_get_custom_samples("Default", mods)
		top_p = array("B", [ ((int)(255*samples[col][i]+0.5)) for col in range(0, width) for i in range(bpp) ] )
		dest_rgns[1][0:width, row] = top_p.tostring()

		top_p = array("B", sqrs )
		dest_rgns[2][0:width, row] = top_p.tostring()
	
        	progress = progress + width 
        	gimp.progress_update(float(progress) / max_progress)

        for drawable in drawables:
        	drawable.flush()
        	#drawable.merge_shadow(TRUE)
        	drawable.update(0,0,width,height)	
	pdb.plug_in_edge(image,drawables[2], 10, 0, 0) # amount, WRAP, SOBEL
	pdb.plug_in_vinvert(image,drawables[2])

	image.enable_undo()
	gimp.Display(image)



register(
        "python_fu_conformal",
        "Colour representation of a conformal map",
        "Colour representation of a conformal map",
        "Michael J Gruber",
        "Michael J Gruber",
        "2005",
        "<Toolbox>/Xtns/Python-Fu/_Conformal",
        "RGB*, GRAY*, INDEXED*",
        [
		(PF_TEXT, "code", "code", "w=z"),
                (PF_FLOAT, "xl", "x left", -1.0),
                (PF_FLOAT, "xr", "x right", 1.0),
                (PF_FLOAT, "yt", "y top", 1.0),
		(PF_FLOAT, "yb", "y bottom", -1.0),
		(PF_FLOAT, "grid", "grid", 1.0),
		(PF_INT, "width", "width", 256),
		(PF_INT, "height", "height", 256)
        ],
        [],
        python_conformal)

main()
