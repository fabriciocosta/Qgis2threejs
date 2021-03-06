# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qgis2threejs Algorithm
        begin                : 2018-11-06
        copyright            : (C) 2018 Minoru Akagi
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
# Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/

import os
import qgis
from PyQt5.QtCore import QSize
from PyQt5.QtXml import QDomDocument
from qgis.core import (QgsCoordinateTransform,
                       QgsGeometry,
                       QgsMemoryProviderUtils,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterNumber,
                       QgsWkbTypes)

from .conf import DEBUG_MODE
from .export import ThreeJSExporter, ImageExporter, ModelExporter
from .q3dviewercontroller import Q3DViewerController
from .qgis2threejstools import logMessage
from .rotatedrect import RotatedRect


class AlgorithmBase(QgsProcessingAlgorithm):

  Exporter = ThreeJSExporter

  INPUT = "INPUT"
  SCALE = "SCALE"
  BUFFER = "BUFFER"
  TEX_WIDTH = "TEX_WIDTH"
  TEX_HEIGHT = "TEX_HEIGHT"
  TITLE_FIELD = "TITLE"
  CF_FILTER = "CF_FILTER"
  SETTINGS = "SETTINGS"
  OUTPUT = "OUTPUT"

  def createInstance(self):
    if DEBUG_MODE:
      logMessage("createInstance(): {}".format(self.__class__.__name__))
    return self.__class__()

  def flags(self):
    return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

  #def tags(self):
  #  return []

  def tr(self, string):
    return string
    #return QCoreApplication.translate("Qgis2threejsAlg", string)

  def addAdvancedParameter(self, param):
    param.setFlags(param.flags() | param.FlagAdvanced)
    self.addParameter(param)

  def initAlgorithm(self, config):
    if DEBUG_MODE:
      logMessage("initAlgorithm(): {}".format(self.__class__.__name__))

    self.addParameter(
      QgsProcessingParameterFolderDestination(
        self.OUTPUT,
        self.tr("Output Directory")
      )
    )

    self.addParameter(
      QgsProcessingParameterFeatureSource(  #TODO: VectorLayer
        self.INPUT,
        self.tr("Coverage Layer"),
        [QgsProcessing.TypeVectorAnyGeometry]
      )
    )

    self.addParameter(
      QgsProcessingParameterField(
        self.TITLE_FIELD,
        self.tr("Title Field"),
        None,
        self.INPUT,
        QgsProcessingParameterField.Any
      )
    )

    self.addParameter(
      QgsProcessingParameterBoolean(
        self.CF_FILTER,
        self.tr("Current Feature Filter")
      )
    )

    self.addAdvancedParameter(
      QgsProcessingParameterEnum(
        self.SCALE,
        self.tr("Scale Mode"),
        ["Fit to Geometry", "Fixed Scale (based on map canvas)"]
      )
    )

    self.addAdvancedParameter(
      QgsProcessingParameterNumber(
        self.BUFFER,
        self.tr("Buffer (%)"),
        defaultValue=10
      )
    )

    self.addAdvancedParameter(
      QgsProcessingParameterNumber(
        self.TEX_WIDTH,
        self.tr("Texture base width (px)"),
        defaultValue=1024
      )
    )

    self.addAdvancedParameter(
      QgsProcessingParameterNumber(
        self.TEX_HEIGHT,
        self.tr('Texture base height (px)\n'\
                '    Leave this zero to respect aspect ratio of buffered geometry bounding box (in "Fit to Geometry" scale mode)\n'\
                '    or map canvas (in "Fixed scale" scale mode).'),
        defaultValue=0
        #,optional=True
      )
    )

    self.addAdvancedParameter(
      QgsProcessingParameterFile(self.SETTINGS,
        self.tr('Export Settings File (.qto3settings)'),
        extension="qto3settings",
        optional=True
      )
    )

  def prepareAlgorithm(self, parameters, context, feedback):
    source = self.parameterAsSource(parameters, self.INPUT, context)
    source_layer = self.parameterAsLayer(parameters, self.INPUT, context)
    cf_filter = self.parameterAsBool(parameters, self.CF_FILTER, context)
    settings_path = self.parameterAsString(parameters, self.SETTINGS, context)

    self.transform = QgsCoordinateTransform(source.sourceCrs(),
                                            context.project().crs(),
                                            context.project())

    qgis_iface = qgis.utils.plugins["Qgis2threejs"].iface
    self.controller = Q3DViewerController(qgis_iface)
    self.controller.settings.loadSettingsFromFile(settings_path or None)

    if source_layer not in self.controller.settings.mapSettings.layers():
      msg = self.tr('Coverage layer must be visible when "Current Feature Filter" option is checked.')
      feedback.reportError(msg, True)
      return False

    self.exporter = self.Exporter(self.controller.settings)
    return True

  def processAlgorithm(self, parameters, context, feedback):
    if DEBUG_MODE:
      logMessage("processAlgorithm(): {}".format(self.__class__.__name__))

    source = self.parameterAsSource(parameters, self.INPUT, context)
    source_layer = self.parameterAsLayer(parameters, self.INPUT, context)
    title_field = self.parameterAsString(parameters, self.TITLE_FIELD, context)
    cf_filter = self.parameterAsBool(parameters, self.CF_FILTER, context)
    fixed_scale = self.parameterAsEnum(parameters, self.SCALE, context)   # == 1
    buf = self.parameterAsDouble(parameters, self.BUFFER, context)
    tex_width = self.parameterAsInt(parameters, self.TEX_WIDTH, context)
    orig_tex_height = self.parameterAsInt(parameters, self.TEX_HEIGHT, context)
    out_dir = self.parameterAsString(parameters, self.OUTPUT, context)

    mapSettings = self.controller.settings.mapSettings
    baseExtent = self.controller.settings.baseExtent
    rotation = mapSettings.rotation()
    orig_size = mapSettings.outputSize()

    if cf_filter:
      #TODO: FIX ME
      #cf_layer = QgsMemoryProviderUtils.createMemoryLayer("current feature",
      #                                                    source_layer.fields(),
      #                                                    source_layer.wkbType(),
      #                                                    source_layer.crs())

      doc = QDomDocument("qgis")
      source_layer.exportNamedStyle(doc)

      orig_layers = mapSettings.layers()

    total = source.featureCount()
    for current, feature in enumerate(source.getFeatures()):
      if feedback.isCanceled():
        break

      if cf_filter:
        cf_layer = QgsMemoryProviderUtils.createMemoryLayer("current feature",
                                                            source_layer.fields(),
                                                            source_layer.wkbType(),
                                                            source_layer.crs())
        cf_layer.startEditing()
        cf_layer.addFeature(feature)
        cf_layer.commitChanges()

        cf_layer.importNamedStyle(doc)

        layers = [cf_layer if lyr == source_layer else lyr for lyr in orig_layers]
        mapSettings.setLayers(layers)

      title = feature.attribute(title_field)
      feedback.setProgressText("({}/{}) Exporting {}...".format(current + 1, total, title))

      # extent
      geometry = QgsGeometry(feature.geometry())
      geometry.transform(self.transform)
      center = geometry.centroid().asPoint()

      if fixed_scale or geometry.type() == QgsWkbTypes.PointGeometry:
        tex_height = orig_tex_height or int(tex_width * orig_size.height() / orig_size.width())
        rect = RotatedRect(center, baseExtent.width(), baseExtent.width() * tex_height / tex_width, rotation).scale(1 + buf / 100)
      else:
        geometry.rotate(rotation, center)
        rect = geometry.boundingBox().scaled(1 + buf / 100)
        center = RotatedRect.rotatePoint(rect.center(), rotation, center)
        if orig_tex_height:
          tex_height = orig_tex_height
          tex_ratio = tex_width / tex_height
          rect_ratio = rect.width() / rect.height()
          if tex_ratio > rect_ratio:
            rect = RotatedRect(center, rect.height() * tex_ratio, rect.height(), rotation)
          else:
            rect = RotatedRect(center, rect.width(), rect.width() / tex_ratio, rotation)
        else:
          # fit to buffered geometry bounding box
          rect = RotatedRect(center, rect.width(), rect.height(), rotation)
          tex_height = tex_width * rect.height() / rect.width()

      rect.toMapSettings(mapSettings)
      mapSettings.setOutputSize(QSize(tex_width, tex_height))

      self.controller.settings.setMapSettings(mapSettings)

      self.export(title, out_dir, feedback)

      feedback.setProgress(int(current / total * 100))

    return {}

  def export(self, title):
    pass


class ExportAlgorithm(AlgorithmBase):

  TEMPLATE = "TEMPLATE"

  def initAlgorithm(self, config):
    super().initAlgorithm(config)

    templates = ["3DViewer.html", "3DViewer(dat-gui).html", "Mobile.html"]
    self.addParameter(
      QgsProcessingParameterEnum(
        self.TEMPLATE,
        self.tr("Template"),
        templates
      )
    )

  def name(self):
    return 'exportweb'

  def displayName(self):
    return self.tr("Export as Web Page")

  #def prepareAlgorithm(self, parameters, context, feedback):
    #TODO: template
  #  return True

  def export(self, title, out_dir, feedback):
    # scene title
    filename = "{}.html".format(title)
    filepath = os.path.join(out_dir, filename)
    self.controller.settings.setOutputFilename(filepath)

    err_msg = self.controller.settings.checkValidity()
    if err_msg:
      feedback.reportError("Invalid settings: " + err_msg)
      return False

    # export
    self.exporter.export()
    return True


class ExportImageAlgorithm(AlgorithmBase):

  Exporter = ImageExporter
  WIDTH = "WIDTH"
  HEIGHT = "HEIGHT"

  def initAlgorithm(self, config):
    super().initAlgorithm(config)

    self.addParameter(
      QgsProcessingParameterNumber(
        self.WIDTH,
        self.tr("Image Width"),
        defaultValue=2480,
        minValue=1)
    )

    self.addParameter(
      QgsProcessingParameterNumber(
        self.HEIGHT,
        self.tr("Image Height"),
        defaultValue=1748,
        minValue=1)
    )

  def name(self):
    return 'exportimage'

  def displayName(self):
    return self.tr("Export as Image")

  def prepareAlgorithm(self, parameters, context, feedback):
    if not super().prepareAlgorithm(parameters, context, feedback):
      return False

    width = self.parameterAsInt(parameters, self.WIDTH, context)
    height = self.parameterAsInt(parameters, self.HEIGHT, context)

    feedback.setProgressText("Preparing a web page for off-screen rendering...")
    self.exporter.initWebPage(self.controller, width, height)
    return True

  def postProcessAlgorithm(self, context, feedback):
    self.exporter.destroyWebPage()
    return {}

  def export(self, title, out_dir, feedback):
    # image path
    filename = "{}.png".format(title)
    filepath = os.path.join(out_dir, filename)

    err_msg = self.controller.settings.checkValidity()
    if err_msg:
      feedback.reportError("Invalid settings: " + err_msg)
      return False

    # export
    self.exporter.export(filepath)

    return True


class ExportModelAlgorithm(AlgorithmBase):

  Exporter = ModelExporter

  def initAlgorithm(self, config):
    super().initAlgorithm(config)

  def name(self):
    return 'exportmodel'

  def displayName(self):
    return self.tr("Export as 3D Model")

  def prepareAlgorithm(self, parameters, context, feedback):
    if not super().prepareAlgorithm(parameters, context, feedback):
      return False

    self.modelType = "gltf"

    feedback.setProgressText("Preparing a web page for 3D model export...")
    self.exporter.initWebPage(self.controller, 500, 500)
    return True

  def postProcessAlgorithm(self, context, feedback):
    self.exporter.destroyWebPage()
    return {}

  def export(self, title, out_dir, feedback):
    # model path
    filename = "{}.{}".format(title, self.modelType)
    filepath = os.path.join(out_dir, filename)

    err_msg = self.controller.settings.checkValidity()
    if err_msg:
      feedback.reportError("Invalid settings: " + err_msg)
      return False

    # export
    self.exporter.export(filepath)

    return True
