from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.forms.models import model_to_dict


class WhoAmIView(APIView):
    """ Simple endpoint to test auth """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """ Return request.user and request.auth """
        return Response({
            'request.user': model_to_dict(request.user),
            'request.auth': request.auth
        })
