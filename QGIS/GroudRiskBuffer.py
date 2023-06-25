# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsVectorLayer,
                       QgsFillSymbol)
from qgis import processing
from grb import GroundRiskBufferCalc


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    BUFFERSEGMENTE = 20
    BUFFERENDCAPSTYLE = 0
    BUFFERJOINSTYLE = 0
    BUFFERMITERLIMIT = 2
    BUFFERDISSOLVE = False
    input = 'input'
    ca = 'output_ca'
    grb = 'output_grb'
    vo = 'windspeed'
    cd = 'characteristicdimension'
    hfg = 'heightflightgeography'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        return 'GroundRiskBuffer'

    def displayName(self):
        return self.tr('GroundRiskBuffer')

    def group(self):
        return self.tr('digisky-tools')

    def groupId(self):
        return 'digisky-tools'

    def shortHelpString(self):
        return self.tr('Example algorithm short description')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.input,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.vo,
                'wind speed',
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                defaultValue=0.0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.cd,
                'characteristic dimension',
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                defaultValue=0.0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.hfg,
                'height flight geography',
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                defaultValue=0.0
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.ca,
                self.tr('Contingency area')
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.grb,
                self.tr('Ground Risk Buffer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        ca_polygon = self.parameterAsOutputLayer(parameters, self.ca, context)

        v0 = self.parameterAsDouble(parameters, self.vo, context)
        cd = self.parameterAsDouble(parameters, self.cd, context)
        hfg = self.parameterAsDouble(parameters, self.hfg, context)
        grb = GroundRiskBufferCalc()
        scv_size = grb.get_scv(v0)
        grb_size = grb.get_sgrb(v0, cd, hfg)
        feedback.pushInfo('Contingency area buffer size {:0.2f} [m]'.format(scv_size))
        feedback.pushInfo('Ground Risk Buffer {:0.2f} [m]'.format(grb_size))

        scv_buffered_layer = processing.run('native:buffer', {
            'INPUT': parameters['input'],
            'DISTANCE': scv_size,
            'SEGMENTS': self.BUFFERSEGMENTE,
            'END_CAP_STYLE': self.BUFFERENDCAPSTYLE,
            'JOIN_STYLE': self.BUFFERJOINSTYLE,
            'MITER_LIMIT': self.BUFFERMITERLIMIT,
            'DISSOLVE': self.BUFFERDISSOLVE,
            'OUTPUT': ca_polygon
        }, is_child_algorithm=True, context=context, feedback=feedback)['OUTPUT']

        grb_polygon = self.parameterAsOutputLayer(parameters, self.grb, context)
        grb_buffered_layer = processing.run('native:buffer', {
            'INPUT': parameters['input'],
            'DISTANCE': grb_size,
            'SEGMENTS': self.BUFFERSEGMENTE,
            'END_CAP_STYLE': self.BUFFERENDCAPSTYLE,
            'JOIN_STYLE': self.BUFFERJOINSTYLE,
            'MITER_LIMIT': self.BUFFERMITERLIMIT,
            'DISSOLVE': self.BUFFERDISSOLVE,
            'OUTPUT': grb_polygon
        }, is_child_algorithm=True, context=context, feedback=feedback)['OUTPUT']

        if context.willLoadLayerOnCompletion(scv_buffered_layer):
            context.layerToLoadOnCompletionDetails(scv_buffered_layer).setPostProcessor(ContingencyArea.create())

        if context.willLoadLayerOnCompletion(grb_buffered_layer):
            context.layerToLoadOnCompletionDetails(grb_buffered_layer).setPostProcessor(GroundRiskBuffer.create())

        return {}


class ContingencyArea(QgsProcessingLayerPostProcessorInterface):

    instance = None
    ALPHACHANNEL = '128'  # 50% transparenz
    FILLCOLOR = '221,176,39,{}'.format(ALPHACHANNEL)
    OUTLINECOLOR = '0,0,0,{}'.format(ALPHACHANNEL)
    OUTLINESTYPE = 'solid'
    OUTLINEWITHUNIT = 'MM'
    OUTLINEWITH = '1'
    LAYEROPACITY = '0.5'

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer):
            return

        renderer = layer.renderer().clone()

        # colors are in RGB and Alpha (opacity) 255 opaque 0 is transparent
        feedback.pushInfo(self.FILLCOLOR)
        props = {}
        props['color'] = self.FILLCOLOR
        props['outline_color'] = self.OUTLINECOLOR
        props['outline_style'] = self.OUTLINESTYPE
        props['outline_width'] = self.OUTLINEWITH
        props['outline_width_unit'] = self.OUTLINEWITHUNIT
        props['style'] = self.OUTLINESTYPE
        props['layerOpacity'] = self.LAYEROPACITY
        symbol = QgsFillSymbol.createSimple(props)
        renderer.setSymbol(symbol)
        layer.setRenderer(renderer)

    @staticmethod
    def create() -> 'ContingencyArea':
        ContingencyArea.instance = ContingencyArea()
        return ContingencyArea.instance


class GroundRiskBuffer(QgsProcessingLayerPostProcessorInterface):

    instance = None
    ALPHACHANNEL = '128'  # 50% transparenz
    FILLCOLOR = '221,57,39,{}'.format(ALPHACHANNEL)
    OUTLINECOLOR = '0,0,0,{}'.format(ALPHACHANNEL)
    OUTLINESTYPE = 'solid'
    OUTLINEWITHUNIT = 'MM'
    OUTLINEWITH = '1'
    LAYEROPACITY = '0.5'

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer):
            return

        renderer = layer.renderer().clone()

        # colors are in RGB and Alpha (opacity) 255 opaque 0 is transparent
        feedback.pushInfo(self.FILLCOLOR)
        props = {}
        props['color'] = self.FILLCOLOR
        props['outline_color'] = self.OUTLINECOLOR
        props['outline_style'] = self.OUTLINESTYPE
        props['outline_width'] = self.OUTLINEWITH
        props['outline_width_unit'] = self.OUTLINEWITHUNIT
        props['style'] = self.OUTLINESTYPE
        props['layerOpacity'] = self.LAYEROPACITY
        symbol = QgsFillSymbol.createSimple(props)
        renderer.setSymbol(symbol)
        layer.setRenderer(renderer)

    @staticmethod
    def create() -> 'GroundRiskBuffer':
        GroundRiskBuffer.instance = GroundRiskBuffer()
        return GroundRiskBuffer.instance
