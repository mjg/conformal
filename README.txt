conformal.py
============
:Author: Michael J. Gruber
:Email:  conformal@drmicha.warpmail.net
:Revision: 0.2

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
directory, usually `/usr/lib/gimp/2.*/plug-ins/` or (similar) on Linux,
and make sure that it is executable (`chmod a+rx conformal.py`).

=== Usage
After starting The Gimp, you find the conformal plug-in in the `Create`
submenu of the `File` menu. From the dialogue, you can adjust these parameters:

`width`, `height`::
	The dimensions of the new image.
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
`gradient`::
	The gradient representing the argument of the complex number.

The plugin-in then creates a new image with three layers:

`Grid`::
	This layer paints the conformally transformed coordinate grid.
	
`Log. modulus`::
	This layer adds a shading corresponding to the absolute value on
	a logarithmic scale, i.e. one cycle (from white to black) of the
	shading means doubling the modulus: the fractional part of `lb |w|`
	is used as an index into the default white-black gradient.
	 
`Argument`::
	This layer is coloured using the value of the gradient
	at an index corresponding to `arg w`.

The two topmost layers have transparency and layer mode set
appropriately, but feel free to experiment with these, as well as
turning some layers off, depending on your goal: produce instructive
illustrations, or simply beautiful pictures!

== License
`conformal.py` is copy righted by {author} and is available
under the GNU General Public License Version 2.
