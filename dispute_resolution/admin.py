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


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    inlines = [
        UserInfoInline,
    ]

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'family_name', 'admin', 'judge',
                    'eth_account', 'org_name', 'taxnum', 'paynum')
    list_filter = ('admin', 'judge', 'staff')
    list_select_related = (
        'info',
    )

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

    def taxnum(self, obj):
        return getattr(obj.info, 'tax_num', None)

    def paynum(self, obj):
        return getattr(obj.info, 'payment_num', None)

    def org_name(self, obj):
        return getattr(obj.info, 'organization_name', None)


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
    model = ContractStage


admin.site.register(ContractStage, ContractStageAdmin)


class ContractCaseAdmin(admin.ModelAdmin):
    inlines = [
        ContractStageInline,
    ]

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('name', 'user_link', 'files', 'stage_link')
    list_filter = ('finished',)

    fieldsets = (
        (None, {'fields': ('name', 'files')}),
    )
    search_fields = ('files', 'stages__dispute_start_allowed',
                     'stages__owner__name',
                     'stages__owner__info__eth_account')

    def parties(self, obj):
        return '\n'.join(map(str, obj.party.all()))

    @admin_link('party', 'Users', True)
    def user_link(self, user):
        return str(user)

    @admin_link('stages', 'Stages', True)
    def stage_link(self, stage):
        return str(stage)


admin.site.register(ContractCase, ContractCaseAdmin)


class NotifyEventAdmin(admin.ModelAdmin):
    pass


admin.site.register(NotifyEvent, NotifyEventAdmin)
