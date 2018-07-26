import logging

from django.utils import timezone
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
        pwd = validated_data.pop('password', None)
        logger.info('Creating user %s', validated_data['email'])
        user = User.objects.create(**validated_data)
        if pwd:
            logger.debug('Set password for %s', user)
            user.set_password(pwd)
            user.save()
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
    stage_num = serializers.IntegerField(required=False)
    address_by = serializers.CharField(max_length=44, allow_blank=True, allow_null=True, required=False)
    filehash = serializers.CharField(max_length=250, allow_blank=True, allow_null=True, required=False)
    finished = serializers.BooleanField(default=False)

    class Meta:
        model = NotifyEvent
        fields = '__all__'
        extra_kwargs = {
            'user_to': {
                'required': False
            },
            'user_by': {
                'required': False
            },
            'stage': {
                'read_only': True,
                'required': False
            }
        }

    def create(self, validated_data):
        stage_num = validated_data.pop('stage_num')
        case = validated_data.pop('contract')
        case_stages = case.stages.all()
        stage_id = case_stages[stage_num].id
        user_to = validated_data.pop('user_to')
        address = validated_data.pop('address_by', None)
        if address:
            user_by = UserInfo.objects.filter(eth_account=address).user
        else:
            user_by = User.objects.get(id=1)
        user_to.extend(User.objects.filter(judge=True).all())
        event = NotifyEvent.objects.create(contract=case,
                                           stage=stage_id,
                                           user_to=user_to,
                                           user_by=user_by,
                                           **validated_data)
        # update cases
        if validated_data.get('event_type') == 'fin':
            if validated_data.get('finished'):
                case.finished = 2
            else:
                case.finished = 1
            case.save()
        elif validated_data.get('event_type') == 'disp_open':
            stage = case.stages[stage_num]
            stage.disputed = True
            stage.dispute_starter = user_by
            stage.dispute_started = timezone.now().date()
            stage.save()
        elif validated_data.get('event_type') == 'disp_close':
            stage = case.stages[stage_num]
            stage.dispute_finished = timezone.now().date()
            stage.result_files = validated_data.get('filehash')
            stage.save()

        return event
