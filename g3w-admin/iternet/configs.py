from .models import *
from .api.serializers import *

ITERNET_LAYERS = {
    'elemento_stradale': {
        'model': ElementoStradale,
        'clientVar': 'strade', # variable name for client
        'geoSerializer': ElementoStradaleGeoSerializer,
        'geometryType': 'POINT'
    },
    'giunzione_stradale': {
        'model': GiunzioneStradale,
        'clientVar': 'giunzioni',  # variable name for client
        'geoSerializer': GiunzioneStradaleGeoSerializer,
        'geometryType': 'POINT'
    },
    'accesso': {
        'model': Accesso,
        'clientVar': 'accessi',  # variable name for client
        'geoSerializer': AccessoGeoSerializer,
        'geometryType': 'MULTILINESTRING'
    },

}