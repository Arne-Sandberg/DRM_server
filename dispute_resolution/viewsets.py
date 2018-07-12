from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from url_filter.integrations.drf import DjangoFilterBackend

from dispute_resolution.models import User, ContractCase, ContractStage, \
    NotifyEvent, UserInfo
from dispute_resolution.serializers import UserSerializer, \
    ContractCaseSerializer, ContractStageSerializer, NotifyEventSerializer, \
    UserInfoSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name', 'family_name', 'email', 'judge',
                     'info__eth_address', 'info__organization_name']

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['get'], detail=True)
    def get_contracts(self, request, pk=None):
        user = self.get_object()
        return Response({
            'contracts': ContractCaseSerializer(data=user.contracts,
                                                many=True).initial_data
        })

    @action(methods=['get'], detail=False)
    def self(self, request):
        if request.user.is_authenticated:
            return Response({
                'self': UserSerializer(data=request.user).initial_data
            })
        else:
            return Response({'errors': {'auth': 'You are not authorized'}},
                            status=401)


class ContractCaseViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    ordering_fields = ('id', 'finished', 'party')
    ordering = ('finished',)

    filter_backends = [DjangoFilterBackend]
    filter_fields = ['party', 'files', 'finished']

    queryset = ContractCase.objects.all()
    serializer_class = ContractCaseSerializer


class ContractStageViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    filter_backends = [DjangoFilterBackend]
    filter_fields = ['owner', 'dispute_starter']

    queryset = ContractStage.objects.all()
    serializer_class = ContractStageSerializer


class NotifyEventViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    filter_backends = [DjangoFilterBackend]
    filter_fields = ['user_to', 'user_by', 'contract', 'stage']

    queryset = NotifyEvent.objects.all()
    serializer_class = NotifyEventSerializer


class UserInfoViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    filter_backends = [DjangoFilterBackend]
    filter_fields = ['eth_address', 'organization_name', 'tax_num',
                     'payment_num', 'user', 'files']

    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
