from django.contrib.auth.models import User
from guardian.shortcuts import get_objects_for_user
from usersmanage.utils import get_users_for_object, get_groups_for_object, userHasGroups, get_viewers_for_object, get_user_groups_for_object
from usersmanage.configs import *


class G3WACLViewMixin(object):
    '''
    Mixins for Class FormView for get user initial values for editors and viewers
    Use self property editor_permission and viewer_permission
    '''

    def get_form_kwargs(self):
        kwargs = super(G3WACLViewMixin, self).get_form_kwargs()
        kwargs['request'] = self.request

        # get editor users
        editor_user_pk = None
        editor_users = get_users_for_object(self.object, self.editor_permission, [G3W_EDITOR2, G3W_EDITOR1])
        if editor_users:
            editor_user_pk = editor_users[0].id
            if self.request.user.is_superuser:
                kwargs['initial']['editor_user'] = editor_users[0].id

        # get viewer users
        viewers = get_viewers_for_object(self.object, self.request.user, self.viewer_permission)

        # get only user id and check if user is group or project editor
        kwargs['initial']['viewer_users'] = [o.id for o in viewers if o.id != editor_user_pk]

        # get initial editor user_groups
        group_editors = get_user_groups_for_object(self.object, self.request.user, self.editor_permission, 'editor')
        kwargs['initial']['editor_user_groups'] = [o.id for o in group_editors]

        group_viewers = get_user_groups_for_object(self.object, self.request.user, self.viewer_permission, 'viewer')
        kwargs['initial']['viewer_user_groups'] = [o.id for o in group_viewers]

        return kwargs