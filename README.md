


Qgis2threejs plugin - version 2.2 (GIX version)
=================================

  This is a [QGIS](https://qgis.org/) plugin, which visualizes DEM data and vector data in 3D on web
browsers. You can build various kinds of 3D objects with simple settings panels and view them in web view of exporter.
If you want to share them in web, you can generate files to publish them to web in simple procedure. In addition, you can
save the 3D model in glTF format for 3DCG or 3D printing.

GIX version is a fork based on Minorua's https://github.com/minorua/Qgis2threejs

I simply added a GIX.js, GIX template so you can access easily objects inside Q3D Threejs Objects.


Documentation
-------------

  You can use GIX to access THREEJS (www.threejs.org) directly:
  
  ```
  layer1 = GIX.getLayerByName("my layer 1 name")
  ```
  then layer1 is the THREEJS bse object layer, so you can access THREEJS whole functionalities.
  
  
  Changing height of a layer, just type in the browser development console window:
  
  ```
  layer1 = GIX.getLayerByName("my layer 1 name")
  GIX.scaleLayer( layer1, 1.0, 1.0, 4.0 )
  ```

  Moving a layer, floating in the air (2.0 in the Z axe):

  ```
  layer1 = GIX.getLayerByName("my layer 1 name")
  GIX.moveLayer( layer1, 0.0, 0.0, 2.0 )
  ```

  
  Online documentation: https://qgis2threejs.readthedocs.org/

  You can download PDF version if you want.


Browser Support
---------------

  See [plugin wiki page](https://github.com/minorua/Qgis2threejs/wiki/Browser-Support).


Dependent JavaScript libraries and resources
--------------------------------------------

* [three.js](https://threejs.org)

* [Proj4js](https://trac.osgeo.org/proj4js/)

* [dat-gui](https://code.google.com/p/dat-gui/) for export based on 3DViewer(dat-gui) template

* [Font Awesome](https://fontawesome.com/) icons for export based on Mobile template

* JavaScript [polyfill](https://github.com/inexorabletash/polyfill) for glTF export function

License
=======

  Python modules of Qgis2threejs plugin are released under the GNU Public License (GPL) Version 2.

_Copyright (c) 2013 Minoru Akagi_
