from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser
)
from django.db.models import PROTECT


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    objects = UserManager()

    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=150, verbose_name='Name',
                            null=False, blank=False)
    family_name = models.CharField(max_length=150, verbose_name='Family',
                                   null=False, blank=False)

    active = models.BooleanField(default=True)
    judge = models.BooleanField(default=False)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser
    # notice the absence of a "Password field", that's built in.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    def get_full_name(self):
        # The user is identified by their email address
        return '{name} {family_name}'.format(name=self.name,
                                             family_name=self.family_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return self.staff or self.judge or self.admin

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return self.staff or self.judge or self.admin

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.staff

    @property
    def is_admin(self):
        """Is the user an admin member?"""
        return self.admin

    @property
    def is_admin(self):
        """Is the user a judge member?"""
        return self.judge

    @property
    def is_active(self):
        """Is the user active?"""
        return self.active


class UserInfo(models.Model):
    eth_account = models.CharField(max_length=65, verbose_name='ETH Address',
                                   unique=True, db_index=True)
    organization_name = models.CharField(max_length=45, default='Some org',
                                         verbose_name='Organization')
    tax_num = models.CharField(max_length=15, verbose_name='TAX Identity',
                               null=True, blank=True)
    payment_num = models.CharField(max_length=40, verbose_name='Payment card',
                                   default='not valid payment number')
    files = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, related_name='info', on_delete=PROTECT)

    def __str__(self):
        return '{user} ({eth_acc})'.format(eth_acc=self.eth_account,
                                           user=self.user)


class ContractCase(models.Model):
    party = models.ManyToManyField(User, related_name='contracts')
    files = models.TextField(blank=True, null=True)
    # 0 - false, 1 - pending, 2 - true
    finished = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return str(self.name) + ' ' + str(self.finished)


class ContractStage(models.Model):
    start = models.DateField(auto_now_add=False, null=False, blank=False)
    owner = models.ForeignKey(User, related_name='own_stages',
                              on_delete=PROTECT)
    dispute_start_allowed = models.DateField(auto_now_add=False,
                                             null=False, blank=False)
    dispute_started = models.DateField(auto_now_add=False, default=None,
                                       null=True, blank=True)
    dispute_starter = models.ForeignKey(User, related_name='started_disputes',
                                        null=True, blank=True,
                                        on_delete=PROTECT)
    contract = models.ForeignKey(ContractCase, related_name='stages',
                                 on_delete=PROTECT)
    result_file = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return 'Stage of {}'.format(self.contract)


class NotifyEvent(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    contract = models.ForeignKey(ContractCase, related_name='events',
                                 on_delete=PROTECT)
    stage = models.ForeignKey(ContractStage, related_name='events',
                              on_delete=PROTECT)
    user_by = models.ForeignKey(User, related_name='events_emitted',
                                on_delete=PROTECT)
    user_to = models.ManyToManyField(User, related_name='events_received')
    seen = models.BooleanField(default=False)
    event_type = models.CharField(max_length=10,
                                  default='open',
                                  choices=[('fin', 'Finished'),
                                           ('disp_open', 'Disput Opened'),
                                           ('open', 'Opened'),
                                           ('disp_close', 'Dispute Closed')])

    def __str__(self):
        return '{} by {} for {}'.format(self.event_type, self.user_by,
                                        self.contract.id)
