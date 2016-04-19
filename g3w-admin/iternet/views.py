from django.views.generic import TemplateView, FormView, View
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.db import IntegrityError, transaction
from django.db.models import Q
import copy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, APIException
from .forms import ConfigForm
from qdjango.utils.data import QgisPgConnection
from core.editing.structure import *
from core.editing.utils import LayerLock
from core.api.authentication import CsrfExemptSessionAuthentication
from core.api.filters import IntersectsBBoxFilter
from .configs import ITERNET_LAYERS
from .editing import *
from .api.serializers import NumeroCivicoSerializer, ToponimoStradaleSerializer


iternet_connection = copy.copy(settings.DATABASES[settings.ITERNET_DATABASE])


class EditingApiView(APIView):
    """
    APIView to get data Project and layers
    """

    authentication_classes = (
        CsrfExemptSessionAuthentication,
    )

    bbox_filter_field = 'the_geom'
    bbox_filter_include_overlapping = True

    def initial(self, request, *args, **kwargs):
        super(EditingApiView, self).initial(request, *args, **kwargs)

        if kwargs['layer_name'] not in ITERNET_LAYERS.keys():
            raise APIException('Only one of this: {}'.format(', '.join(ITERNET_LAYERS.keys())))

        # set layer model obejct to work
        self.layer = getLayerIternetIdByName(kwargs['layer_name'], object=True)

        # set lock object
        self.lock = LayerLock(
            appName='iternet',
            layer=self.layer,
            user=request.user,
            sessionid=request.COOKIES[settings.SESSION_COOKIE_NAME]
        )

    def get(self, request, format=None, layer_name=None):

        # check is editing mode ad inputs
        editingMode = 'editing' in request.GET
        configMode = 'config' in request.GET

        if editingMode and configMode:
            raise APIException('config and editing get parameters not allowed')

        # Instance bbox filter
        bboxFilter = IntersectsBBoxFilter()

        #   in_bbox=1627296.88291268446482718,4854554.72152963746339083,1628408.71542843640781939,4855197.11364984977990389
        #http://localhost:8000/it/iternet/api/editing/elemento_stradale/?in_bbox=1627296.88291268446482718,4854554.72152963746339083,1628408.71542843640781939,4855197.11364984977990389

        forms = getForms()
        relationForms = getRelationForms()

        if not configMode:
            featurecollection = {}
            for iternetLayer, dataLayer in ITERNET_LAYERS.items():
                if layer_name == iternetLayer:
                    featuresLayer = bboxFilter.filter_queryset(request, dataLayer['model'].objects.all(), self)
                    layerSerializer = dataLayer['geoSerializer'](featuresLayer, many=True)
                    featurecollection = layerSerializer.data


        # lock features
        featuresLocked = []
        if editingMode:
            # get feature locked:
            featuresLocked = self.lock.lockFeatures([str(f.gid) for f in featuresLayer])

        if configMode:
            vectorParams = {
                'geomentryType': ITERNET_LAYERS[layer_name]['geometryType'],
                'fields': mapLayerAttributes(
                    self.layer,
                    formField=True,
                    fields=forms[layer_name]['fields']
                ).values(),
                'pkField': ITERNET_LAYERS[layer_name]['model']._meta.pk.name
            }

            if layer_name in relationForms:
                vectorParams['relations'] = relationForms[layer_name]
        else:
            vectorParams = {
                'data': featurecollection,
                'geomentryType': ITERNET_LAYERS[layer_name]['geometryType'],
            }

        vectorParams['featureLocks'] = featuresLocked

        # instance new vectolayer
        vectorLayer = APIVectorLayerStructure(**vectorParams)
        return Response(vectorLayer.as_dict())


    def post(self, request, format=None):
        """
        Save data on database, clientsend data for every layer of iternet project.
        """
        data = request.data

        # start transaction
        try:
            with transaction.atomic():
                layerConfigData = ITERNET_LAYERS['layer_name']
                clientVar = layerConfigData['clientVar']
                if clientVar in data:
                    model = layerConfigData['model']

                    # save insert
                    for mode in (EDITING_POST_DATA_ADDED, EDITING_POST_DATA_UPDATED):
                        if mode in data[clientVar]:
                            for GeoJSONFeature in data[clientVar][mode]:
                                if mode == EDITING_POST_DATA_ADDED:
                                    serializer = layerConfigData['geoSerializer'](data=GeoJSONFeature)
                                else:
                                    feature = model.objects.get(pk=GeoJSONFeature['id'])
                                    serializer = layerConfigData['geoSerializer'](feature, data=GeoJSONFeature)
                                if serializer.is_valid():
                                    dato = serializer.save()
                                else:
                                    raise ValidationError({
                                        'result': False,
                                        'errors': serializer.errors
                                    })

                    # save delete
                    if EDITING_POST_DATA_DELETED in data[clientVar]:
                        features = model.objects.filter(pk__in=data[clientVar][EDITING_POST_DATA_DELETED])
                        for feature in features:
                            #feature.delete()
                            pass

                # now unlocked feature id
                # get feature locked and erase from lock table
                if 'lockids' in data:
                    LayerLock.unLockFeatures(data['lockids'])

                # unllock features by user and sessionid
                if 'unlock' in data and data['unlock']:
                    lock = LayerLock(
                        appName='iternet',
                        layer=self.layer,
                        user=request.user,
                        sessionid=request.COOKIES[settings.SESSION_COOKIE_NAME]
                    )


        except IntegrityError as e:
            return Response({
                'result': False,
                'errors': e.message
            })

        return Response({"result": True})


class NumeroCivicoApiView(APIView):
    """
    API get for numero_civico data.
    """
    def get(self, request):

        # check for cod_acc
        if 'cod_acc' not in request.GET or 'tip_acc' not in request.GET :
            raise APIException('You have to set cod_acc and/or tip_acc get parameter')
        cod_acc = request.GET['cod_acc']
        tip_acc = request.GET['tip_acc']

        # get numero civico
        # case 'interno'
        if tip_acc == '0501':
            q = Q(cod_acc_int=cod_acc)
        else:
            q = Q(cod_acc_est=cod_acc)
        numeriCivici = NumeroCivico.objects.filter(q)

        return Response(NumeroCivicoSerializer(numeriCivici, many=True).data)


class ToponimoStradaleApiView(APIView):
    """
    API get for toponimo_stradale data.
    """

    def get(self, request):

        # check for cod_acc
        if 'cod_top' not in request.GET:
            raise APIException('You have to set cod_top parameter')
        cod_top = request.GET['cod_top']

        # get toponimo
        toponimoStradale = ToponimoStradale.objects.filter(pk=cod_top)

        return Response(ToponimoStradaleSerializer(toponimoStradale, many=True).data)


class DashboardView(TemplateView):

    template_name = 'iternet/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        # set data iternet connection
        context['db_connection'] = iternet_connection

        # get report data from nodi accessi and elementi stradali
        '''
        context['n_accessi'] = len(Accesso.objects.all())
        context['n_elementi_stradali'] = len(ElementoStradale.objects.all())
        context['n_giunzioni_stradali'] = len(GiunzioneStradale.objects.all())
        '''
        context['n_accessi'] = 'n'
        context['n_elementi_stradali'] = 'n'
        context['n_giunzioni_stradali'] = 'n'
        return context




class ConfigView(FormView):

    form_class = ConfigForm
    template_name = 'iternet/config.html'


    def get_success_url(self):
        return reverse('iternet-dashboard')

    def get_object(self):
        self.object = Config.getData()

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        self.get_object()
        kwargs = super(ConfigView, self).get_form_kwargs()
        kwargs.update({'instance': self.object })
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super(ConfigView, self).form_valid(form)


class DownloadQgisPgConnectionView(View):

    def get(self, request, *args, **kwargs):

        qgisPgConnection = QgisPgConnection(
            host=iternet_connection['HOST'],
            username=iternet_connection['USER'],
            password=iternet_connection['PASSWORD'],
            port=iternet_connection['PORT'],
            name='G3W-ADMIN-ITERNET',
            database=iternet_connection['NAME'],
        )

        # get configuration data
        response = HttpResponse(qgisPgConnection.asXML(), content_type='text/xml')
        response['Content-Disposition'] = 'attachment; filename="g3w_iternet_qgis_connection.xml"'
        return response

