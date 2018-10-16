from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from core.api.serializers import GroupSerializer, Group, update_serializer_data
from core.api.permissions import ProjectPermission
from core.signals import perform_client_search, post_serialize_project
from core.models import GeneralSuiteData


class ClientConfigApiView(APIView):
    """
    APIView to get data Project and layers
    """

    permission_classes = (ProjectPermission,)

    def get(self, request, format=None, group_slug=None, project_type=None, project_id=None):

        # get serializer
        projectAppModule = __import__('{}.api.serializers'.format(project_type))
        projectSerializer = projectAppModule.api.serializers.ProjectSerializer

        project = projectAppModule.models.Project.objects.get(pk=project_id)

        ps = projectSerializer(project)

        # add wms_url to project metadata il user i anonynous

        if request.user.is_anonymous and 'metadata' in ps.data and not ps.data['metadata']['onlineresource']:
            ps.data['metadata']['wms_url'] = '{}://{}/ows/{}/{}/{}/'.format(
                request._request.META['wsgi.url_scheme'],
                request._request.META['HTTP_HOST'],
                project.group.slug,
                project_type,
                project_id
            )
        elif 'onlineresource' in ps.data['metadata']:
            ps.data['metadata']['wms_url'] = ps.data['metadata']['onlineresource']

        if 'onlineresource' in ps.data['metadata']:
            del(ps.data['metadata']['onlineresource'])

        # signal after serialization project
        ps_data = ps.data
        for singnal_receiver, data in post_serialize_project.send(ps, app_name=project_type, request=self.request):
            if data:
                update_serializer_data(ps_data, data)

        return Response(ps_data)


class ClientSearchApiView(APIView):
    """
    APIView to perform a search on a project layer
    """

    permission_classes = (ProjectPermission,)

    def get(self, request, format=None, group_slug=None, project_type=None, project_id=None, widget_id=None):

        resSearch = perform_client_search.send(request, app_name=project_type, project_id=project_id,
                                               widget_id=widget_id)

        # build response from modules
        # todo:: to build response
        response = [res[1].asJSON() for res in resSearch]
        return Response(response)


class GroupConfigApiView(APIView):
    """
    APIView to get data Project and layers
    """

    permission_classes = (ProjectPermission,)

    def get(self, request, format=None, group_slug=None, project_type=None, project_id=None):
        group = get_object_or_404(Group, slug=group_slug)
        groupSerializer = GroupSerializer(group, projectId=project_id, projectType=project_type, request=self.request)
        baseurl = "/{}".format(settings.SITE_PREFIX_URL if settings.SITE_PREFIX_URL else '')
        generaldata = GeneralSuiteData.objects.get()

        initconfig = {
          "staticurl": settings.STATIC_URL,
          "client": "client/",
          "mediaurl": settings.MEDIA_URL,
          "baseurl": baseurl,
          "vectorurl": settings.VECTOR_URL,
          "group": groupSerializer.data,
          "g3wsuite_logo_img": settings.CLIENT_G3WSUITE_LOGO,
          "main_map_title": generaldata.main_map_title
        }

        # add frontendurl if frontend is set
        if settings.FRONTEND:
            initconfig.update({
                'frontendurl': baseurl
            })

        u = request.user

        # add user login data
        initconfig['user'] = {'i18n': get_language()}
        if not u.is_anonymous():
            initconfig['user'].update({
                'username': u.username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'groups': [g.name for g in u.groups.all()],
                'logout_url': reverse('logout'),
                'admin_url': reverse('home')
            })


        return Response(initconfig)
