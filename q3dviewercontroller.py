# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Q3DControllerLive

                              -------------------
        begin                : 2016-02-10
        copyright            : (C) 2016 Minoru Akagi
        email                : akaginch@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import time
from qgis.core import QgsApplication

from .conf import DEBUG_MODE
from .build import ThreeJSBuilder
from .exportsettings import ExportSettings
from .qgis2threejstools import logMessage, pluginDir


class Q3DViewerController:

  def __init__(self, qgis_iface, settings=None):
    self.qgis_iface = qgis_iface

    if settings is None:
      defaultSettings = {}
      settings = ExportSettings()
      settings.loadSettings(defaultSettings)
      settings.setMapCanvas(qgis_iface.mapCanvas())

      err_msg = settings.checkValidity()
      if err_msg:
        logMessage("Invalid settings: " + err_msg)

    self.settings = settings
    self.exporter = ThreeJSBuilder(settings)

    self.iface = None
    self.previewEnabled = True    #TODO: rename to enabled
    self.aborted = False  # layer export aborted
    self.updating = False
    self.layersNeedUpdate = False

    self.message1 = "Press ESC key to abort processing"

  def connectToIface(self, iface):
    """iface: Q3DViewerInterface"""
    self.iface = iface

  def disconnectFromIface(self):
    self.iface = None

  def connectToMapCanvas(self):
    self.qgis_iface.mapCanvas().renderComplete.connect(self.canvasUpdated)
    self.qgis_iface.mapCanvas().extentsChanged.connect(self.canvasExtentChanged)

  def disconnectFromMapCanvas(self):
    self.qgis_iface.mapCanvas().renderComplete.disconnect(self.canvasUpdated)
    self.qgis_iface.mapCanvas().extentsChanged.disconnect(self.canvasExtentChanged)

  def abort(self):
    if self.updating:
      self.iface.showMessage("Aborting processing...")
      self.aborted = True

  def setPreviewEnabled(self, enabled):
    if self.iface is None:
      return

    self.previewEnabled = enabled
    self.iface.runString("app.resume();" if enabled else "app.pause();");
    if enabled:
      self.updateExtent()
      self.updateScene()

  def updateScene(self, update_scene_settings=True, update_layers=True, update_extent=True, base64=False):
    if not self.iface:
      return

    self.settings.base64 = base64
    self.updating = True
    self.layersNeedUpdate = self.layersNeedUpdate or update_layers
    self.iface.showMessage(self.message1)
    self.iface.progress(0, "Updating scene")

    if update_extent:
      self.exporter.settings.setMapCanvas(self.qgis_iface.mapCanvas())

    # build scene
    self.iface.loadJSONObject(self.exporter.buildScene(False))

    if update_scene_settings:
      # update background color
      sp = self.settings.sceneProperties()
      params = "{0}, 1".format(sp.get("colorButton_Color", 0)) if sp.get("radioButton_Color") else "0, 0"
      self.iface.runString("setBackgroundColor({0});".format(params))

      # coordinate display (geographic/projected)
      if sp.get("radioButton_WGS84", False):
        self.iface.loadScriptFile(pluginDir("js/proj4js/proj4.js"))
      else:
        self.iface.runString("proj4 = undefined;", "// proj4 not enabled")

    if update_layers:
      layers = self.settings.getLayerList()
      for idx, layer in enumerate(layers):
        self.iface.progress(idx / len(layers) * 100, "Updating layers")
        if layer.updated or (self.layersNeedUpdate and layer.visible):
          if not self._updateLayer(layer):
            break
      self.layersNeedUpdate = False

    self.updating = self.aborted = False
    self.iface.progress()
    self.iface.clearMessage()
    self.settings.base64 = False

  def updateLayer(self, layer):
    self.updating = True
    self.iface.showMessage(self.message1)
    self.iface.progress(0, "Building {0}...".format(layer.name))

    self._updateLayer(layer)

    self.updating = self.aborted = False
    self.iface.progress()
    self.iface.clearMessage()

  def _updateLayer(self, layer):
    if not (self.iface and self.previewEnabled):
      return False

    if layer.properties.get("comboBox_ObjectType") == "Model File":
      self.iface.loadModelLoaders()

    ts0 = time.time()
    tss = []
    for exporter in self.exporter.builders(layer):
      if self.aborted:
        return False
      ts1 = time.time()
      obj = exporter.build()
      ts2 = time.time()
      self.iface.loadJSONObject(obj)
      ts3 = time.time()
      tss.append([ts2 - ts1, ts3 - ts2])
      QgsApplication.processEvents()      # NOTE: process events only for the calling thread
    layer.updated = False
    if DEBUG_MODE:
      logMessage("updating {0} costed {1:.3f}s:\n{2}".format(layer.name, time.time() - ts0, "\n".join(["{:.3f} {:.3f}".format(ts[0], ts[1]) for ts in tss])))
    return True

  def updateExtent(self):
    self.exporter.settings.setMapCanvas(self.qgis_iface.mapCanvas())

  def canvasUpdated(self, painter):
    # update map settings
    self.exporter.settings.setMapCanvas(self.qgis_iface.mapCanvas())

    if self.iface and self.previewEnabled:
      self.updating = True
      self.iface.showMessage(self.message1)
      self.iface.progress(0, "Updating layers")
      layers = self.iface.controller.settings.getLayerList()
      for idx, layer in enumerate(layers):
        self.iface.progress(idx / len(layers) * 100)
        if layer.visible:
          if not self._updateLayer(layer):
            break
      self.layersNeedUpdate = False
      self.updating = self.aborted = False
      self.iface.progress()
      self.iface.clearMessage()

  def canvasExtentChanged(self):
    self.layersNeedUpdate = True
    self.updateScene(False, False)
