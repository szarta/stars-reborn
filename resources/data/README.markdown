# resources/data #

The content of this directory is compressed data exported from Python.
The raw dictionaries containing the data are serialized with the jsonpickle
library and then gzipped with the gzip library.  It is then reversed to load in
the data module.

The contents:

 * technologies.dat - contains the structures for all of the built technologies 
   (armor, ship parts, etc) with their corresponding stat values
