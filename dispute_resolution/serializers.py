import logging
from rest_framework import serializers

from dispute_resolution.models import UserInfo, User, ContractCase, \
    ContractStage, NotifyEvent


logger = logging.getLogger(__name__)


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        extra_kwargs = {'user': {'required': False}}
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    info = UserInfoSerializer()

    class Meta:
        model = User
        fields = ('id', 'name', 'family_name', 'email', 'info', 'judge',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('info')
        _ = profile_data.pop('user', None)
        _ = validated_data.pop('user', None)
        _ = validated_data.pop('staff', None)
        _ = validated_data.pop('admin', None)
        _ = validated_data.pop('judge', None)
        pwd = validated_data.pop('password')
        logger.info('Creating user %s', validated_data['email'])
        user = User.objects.create(**validated_data)
        if pwd:
            logger.debug('Set password for %s', user)
            user.set_password(pwd)
        logger.debug('Create info object for %s', user)
        UserInfo.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        _ = validated_data.pop('password', None)
        return super().update(instance, validated_data)


class ContractStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractStage
        exclude = ('contract',)


class ContractCaseSerializer(serializers.ModelSerializer):
    stages = ContractStageSerializer(many=True)
    in_party = UserSerializer(many=True, read_only=True, source='party')
    party = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                               many=True, write_only=True,
                                               allow_empty=False)

    class Meta:
        model = ContractCase
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        stages_data = validated_data.pop('stages')
        contract = super().create(validated_data)
        for data in stages_data:
            ContractStage.objects.create(contract=contract, **data)
        return contract


class NotifyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyEvent
        fields = '__all__'

    def create(self, validated_data):
        stage_num = validated_data.pop('stage')
        contract_id = validated_data.pop('contract')
        case = ContractCase.objects.get(id=contract_id)
        stage_id = case.stages[stage_num].id
        user_to = validated_data.pop('user_to')
        user_to.extend(User.objects.filter(judge=True).all())
        event = NotifyEvent.objects.create(contract=contract_id,
                                           stage=stage_id, user_to=user_to,
                                           **validated_data)
        return event
