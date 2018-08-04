from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import User, ContractCase, UserInfo, ContractStage, NotifyEvent


class UserInfoInline(admin.StackedInline):
    model = UserInfo


class CaseInline(admin.TabularInline):
    model = ContractCase.party.through


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    inlines = [
        UserInfoInline,
        CaseInline
    ]

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'family_name', 'admin', 'judge', 'staff',
                    'eth_account', 'org_name', 'taxnum', 'paynum')
    list_filter = ('admin', 'judge', 'staff')
    list_editable = ('name', 'family_name', 'admin', 'staff')
    list_select_related = (
        'info',
    )

    readonly_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'name', 'family_name', 'password')}),
        ('Permissions', {'fields': ('admin', 'judge', 'staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'family_name',
                       'password1', 'password2')}
         ),
    )
    search_fields = ('email', 'name', 'family_name', 'info__payment_num',
                     'info__tax_num', 'info__organization_name',
                     'info__eth_account')
    ordering = ('email',)
    filter_horizontal = ()

    def eth_account(self, obj):
        return getattr(obj.info, 'eth_account', None)
    eth_account.admin_order_field = 'info__eth_account'

    def taxnum(self, obj):
        return getattr(obj.info, 'tax_num', None)
    taxnum.admin_order_field = 'info__tax_num'

    def paynum(self, obj):
        return getattr(obj.info, 'payment_num', None)
    paynum.admin_order_field = 'info__payment_num'

    def org_name(self, obj):
        return getattr(obj.info, 'organization_name', None)
    org_name.admin_order_field = 'info__organization_name'


admin.site.register(User, UserAdmin)

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


class ContractStageInline(admin.StackedInline):
    model = ContractStage


def admin_change_url(obj):
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse('admin:{}_{}_change'.format(
        app_label, model_name
    ), args=(obj.pk,))


def admin_link(attr, short_description, many=False, empty_description="-"):
    """Decorator used for rendering a link to a related model in
    the admin detail page.
    attr (str):
        Name of the related field.
    short_description (str):
        Name if the field.
    empty_description (str):
        Value to display if the related field is None.
    The wrapped method receives the related object and should
    return the link text.
    Usage:
        @admin_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    """

    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            if many:
                return mark_safe('<br/>'.join(
                    [format_html(
                        '<a href="{}">{}</a>',
                        admin_change_url(relobj),
                        func(self, relobj)
                    ) for relobj in related_obj.all()]))
            else:
                url = admin_change_url(related_obj)
                return format_html(
                    '<a href="{}">{}</a>',
                    url,
                    func(self, related_obj)
                )

        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func

    return wrap


class ContractStageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner_link', 'case_link',
                    'dispute_started', 'dispute_finished',
                    'dispute_starter')
    list_filter = ('start', 'dispute_start_allowed', 'dispute_started',
                   'dispute_finished')

    readonly_fields = ('owner', 'dispute_started', 'contract',
                       'dispute_start_allowed', 'start', 'dispute_starter',
                       'dispute_finished', 'result_file')

    fieldsets = (
        (None, {'fields': ('owner', 'start', 'contract',
                           'dispute_start_allowed')}),
        ('State', {'fields': ('dispute_started', 'dispute_starter',
                              'dispute_finished', 'result_file')}),
    )
    search_fields = ('start', 'dispute_start_allowed',
                     'contract__party__email',
                     'contract__party__info__organization_name',
                     'contract__party__family_name', 'contract__party__name',
                     'contract__name',
                     'contract__party__info__eth_account',
                     'dispute_started', 'dispute_finished',
                     'dispute_starter__name',
                     'result_file')

    @admin_link('owner', 'Owner')
    def owner_link(self, user):
        return str(user)

    @admin_link('contract', 'Case')
    def case_link(self, case):
        return str(case)


admin.site.register(ContractStage, ContractStageAdmin)


class UserInline(admin.StackedInline):
    model = ContractCase.party.through


class ContractCaseAdmin(admin.ModelAdmin):
    inlines = [
        UserInline,
        ContractStageInline,
    ]

    list_display = ('id', 'name', 'party_link', 'files', 'stage_link')
    list_filter = ('finished',)
    list_editable = ('name',)
    list_display_links = ('id', 'files')

    readonly_fields = ('party', 'files', 'stages', 'finished')

    fieldsets = (
        (None, {'fields': ('name', 'files')}),
    )
    search_fields = ('files', 'name',
                     'stages__dispute_start_allowed',
                     'party__name', 'party__family_name',
                     'party__email', 'party__info__organization_name',
                     'party__info__tax_num', 'party__info__payment_num',
                     'party__info__eth_account')

    @admin_link('party', 'Participants', True)
    def party_link(self, user):
        return str(user)

    @admin_link('stages', 'Stages', True)
    def stage_link(self, stage):
        return str(stage)


admin.site.register(ContractCase, ContractCaseAdmin)


class NotifyEventAdmin(admin.ModelAdmin):
    list_display = ('pk', 'event_type', 'case_link', 'stage_link',
                    'user_by_link', 'user_to_link', 'seen')
    list_display_links = ('pk', 'event_type')
    list_filter = ('event_type', 'seen')

    readonly_fields = ('user_by', 'user_to', 'event_type', 'contract', 'stage')

    fieldsets = (
        (None, {'fields': ('event_type', 'user_by', 'user_to', 'seen')}),
        ('Case', {'fields': ('contract', 'stage')}),
    )
    search_fields = ('event_type',
                     'contract__id',
                     'stage__id',
                     'contract__party__email',
                     'contract__party__info__organization_name',
                     'contract__party__family_name', 'contract__party__name',
                     'contract__name',
                     'contract__party__info__eth_account',
                     'creation_date')

    @admin_link('user_by', 'Sender')
    def user_by_link(self, user):
        return str(user)
    user_by_link.admin_order_field = 'user_by'

    @admin_link('user_to', 'Recipient')
    def user_to_link(self, user):
        return str(user)
    user_to_link.admin_order_field = 'user_to'

    @admin_link('contract', 'Case')
    def case_link(self, case):
        return str(case)
    case_link.admin_order_field = 'contract'

    @admin_link('stage', 'Stage')
    def stage_link(self, stage):
        return str(stage)
    stage_link.admin_order_field = 'stage'


admin.site.register(NotifyEvent, NotifyEventAdmin)
