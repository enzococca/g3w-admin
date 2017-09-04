from core.api.base.views import BaseVectorOnModelApiView
from core.utils.structure import mapLayerAttributesFromModel
from core.utils.models import create_geomodel_from_qdjango_layer, get_geometry_column
from .api.serializers import QGISLayerSerializer, QGISGeoLayerSerializer
from .models import Layer

# add form impout type based on qgis edittypes
FORM_FIELD_TYPE_QGIS_CHECK = 'check'
FORM_FIELD_TYPE_QGIS_DATETIME = 'datetime'
FORM_FIELD_TYPE_QGIS_RANGE = 'range'
FORM_FIELD_TYPE_QGIS_UNIQUE_VALUE = 'unique_value'

class QGISLayerVectorViewMixin(object):

    def get_layer_by_params(self, params):

        layer_id = params['layer_name']
        project_id = params['project_id']

        # get layer object from qdjango model layer
        return Layer.objects.get(project_id=project_id, qgs_layer_id=layer_id)

    def get_geoserializer_kwargs(self):

        return {'model': self.metadata_layer['model'], 'using': self.database_to_use}

    def set_relations(self):

        self.relations = {r['id']: r for r in eval(self.layer.project.relations)}

    def set_metadata_relations(self, request, **kwargs):

        for idr, relation in self.relations.items():

            # get relation layer object
            relation_layer = Layer.objects.get(qgs_layer_id=relation['referencingLayer'], project=self.layer.project)

            geomodel, database_to_use, geometrytype = create_geomodel_from_qdjango_layer(relation_layer)

            self.metadata_relations[relation['referencingLayer']] = {
                'model': geomodel,
                'serializer': QGISGeoLayerSerializer if geometrytype else QGISLayerSerializer,
                'geometryType': geometrytype,
                'clientVar': relation_layer.origname,
                'relation_id': idr
            }

    def set_metadata_layer(self, request, **kwargs):

        self.layer = self.get_layer_by_params(kwargs)

        # set layer_name
        self.layer_name = self.layer.origname

        geomodel, self.database_to_use, geometrytype = create_geomodel_from_qdjango_layer(self.layer)

        # set bbox_filter_field with geomentry model field
        self.bbox_filter_field = get_geometry_column(geomodel).name

        # create model and add to editing_layers
        self.metadata_layer = {
            'model': geomodel,
            'geoSerializer': QGISGeoLayerSerializer,
            'geometryType': geometrytype,
            'clientVar': self.layer.origname,
        }


class LayerVectorView(QGISLayerVectorViewMixin, BaseVectorOnModelApiView):

    mapping_layer_attributes_function = mapLayerAttributesFromModel

    def get_forms(self):
        """
        Check if edittype is se for layer and build inputtype
        """

        fields = super(LayerVectorView, self).get_forms()

        if hasattr(self.layer, 'edittypes') and self.layer.edittypes:

            fields = dict()

            # reduild edittypes
            edittypes = eval(self.layer.edittypes)

            for edittype in edittypes:
                pass

        return fields


