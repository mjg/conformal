conformal.py
============
:Author: Michael J. Gruber
:Email:  conformal@drmicha.warpmail.net
:Revision: 0.1

== Introduction
`conformal.py` is a plugin-in for http://gimp.org[The Gimp] which allows
visualisation of conformal maps.

== Requirements
You need `gimp` and the python scripting extension to Gimp. It is
included in newer versions of Gimp, before it was available in packages
named `gimp-python` or similar.

== Installation
You can install `conformal.py` as a local user or system wide:

=== Local User
Copy `conformal.py` to the `plug-ins` subdirectory of your Gimp
directory, usually `$HOME/.gimp-2.*/plug-ins/` on Linux, and make sure
that it is executable (`chmod +x conformal.py`).

=== System wide
Copy `conformal.py` to the `plug-ins` subdirectory of your system Gimp
directory, usually `/usr/lib/gimp/2.0/plg-ins/` or (similar) on Linux,
and make sure that it is executable (`chmod a+rx conformal.py`).

=== Usage
After starting The Gimp, you find the conformal plug-in in the `Render`
submenu of the `Filters` menu. Just like any other render filter it
operates on the current image and takes its dimensions as input. After
choosing the plug-in from the submenu you can adjust other parameters:

`code`::
	The python code which is executed for every single pixel of the
	image. The code can use the value of the complex number `z`
	(which represents the current pixel) and should assign a value
	to `w` which will be considered the (mapping) image of `z`.
`x left`, `x-right`::
	The range of x-values (real parts) which is mapped to the horizontal image axis.
`y top`, `y bottom`::
	The range of y-values (imaginary parts) which is mapped to the vertical image axis.
`grid`::
	The spacing of the generated coordinate grid.

As an additional input, the currently active gradient will be used. The
plug-in then replaces the currently active layer with three new layers:

`Grid`::
	This layer paints the conformally transformed coordinate grid.
	
`Log. modulus`::
	This layer adds a shading corresponding to the absolute value on
	a logarithmic scale, i.e. one cycle (from white to black) of the
	shading means doubling the modulus: the fractional part of `lb |w|`
	is used as an index into the default white-black gradient.
	 
`Argument`::
	This layer is coloured using the value of the the active gradient
	at an index corresponding to `arg w`.

The two topmost layers have transparency and layer mode set
appropriately, but feel free to experiment with these, as well as
turning some layers off, depending on your goal: produce instructive
illustrations, or simply beautiful pictures!

== License
`conformal.py` is copy righted by {author} and is available
under the GNU General Public License Version 2.
