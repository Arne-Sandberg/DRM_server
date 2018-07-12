from rest_framework import serializers

from dispute_resolution.models import UserInfo, User, ContractCase, \
    ContractStage, NotifyEvent


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    info = UserInfoSerializer()

    class Meta:
        model = User
        fields = ('id', 'name', 'family_name', 'email', 'info', 'judge')
        # extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('info')
        _ = validated_data.pop('user')
        _ = validated_data.pop('staff')
        _ = validated_data.pop('admin')
        _ = validated_data.pop('judge')
        user = User.objects.create(**validated_data)
        UserInfo.objects.create(user=user, **profile_data)
        return user


class ContractStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractStage
        exclude = ('contract',)


class ContractCaseSerializer(serializers.ModelSerializer):
    stages = ContractStageSerializer(many=True)

    class Meta:
        model = ContractCase
        fields = '__all__'

    def create(self, validated_data):
        stages_data = validated_data.pop('stages')
        party = validated_data.pop('party')
        contract = ContractCase.objects.create(**validated_data)
        contract.party = party
        contract.save()
        for data in stages_data:
            ContractStage.objects.create(contract=contract, **data)
        return contract


class NotifyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyEvent
        fields = '__all__'
