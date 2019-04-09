#  -*- coding: UTF8 -*-

import os, random, shutil
import newrelic.agent
from datetime import date

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.core.urlresolvers import reverse
from django.db import models
from datetime import datetime

from sys_base.exceptions import HeliosException
from sys_base.fields.field_fulltext import VectorField
from sys_base.hsm.model import SecureModel
from sys_base.profile.image import ProfileImage
from django.contrib.auth.models import PermissionsMixin

from silo_user.user.imgix_service import ImgixService
from silo_user.user.gender_id import GenderId

class UserManager(BaseUserManager):
    """
        Provides Django's QueryManager with create_user and create_superuser methods so that it can use our
        custom User user data model
    """

    def create_user(self, email, password, first_name, last_name, dob=None, gid_is=None, gid_seeking=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(

            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            gid_is=gid_is,
            gid_seeking=gid_seeking,
            hid=User.generate_hid(),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, *options):
        first_name = 'Admin'
        last_name = 'Admin'

        user = self.create_user(

            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dob=date.today(),
            gid_is=GenderId.ID_MALE,
            gid_seeking=GenderId.ID_FEMALE
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(ProfileImage, SecureModel, AbstractBaseUser, PermissionsMixin):
    """
        A custom Django user model that extends our platform base Entity. Remember to change
        AUTH_USER_MODEL in settings.py to silo_user.User
    """

    # The user's email address. Used as their login name. Required by Django.
    email = models.EmailField(blank=False, unique=True, db_index=True)

    # When this profile was created
    created = models.DateTimeField(default=datetime.now)

    # When this profile was last updated
    updated = models.DateTimeField(default=datetime.now)

    # Token account for this User
    token_account = models.OneToOneField('plant_hermes.TokenAccount', related_name='owner', on_delete=models.SET_NULL,
                                         null=True)

    INCOMPLETE = 1
    ACTIVE = 2
    DISABLED = 3
    DELETED = 4

    USER_STATES = (
        (INCOMPLETE, "INCOMPLETE"),
        (ACTIVE, "ACTIVE"),
        (DISABLED, "DISABLED"),
        (DELETED, "DELETED")
    )

    state = models.SmallIntegerField(db_index=True, choices=USER_STATES, default=INCOMPLETE)

    # Images
    # =====================================================================================================

    # HeliosID - A 4-byte hexadecimal string used as a GUID and as a sharding key for storing the User's
    # media item path. This allows up to 255^4 = 4,228,250,625 People per server. Even with 40 million users
    # on the site, the odds of a hash key collision are 1 in 100, and all we have to do is generate a new
    # random value and try again.

    hid = models.CharField(max_length=8, unique=True, db_index=True)

    # The prefix of the square avatar image of this entity, used throughout the site.
    avatar_prefix = models.CharField(max_length=8, null=True)

    # The id of the largest size of avatar image available
    avatar_size = models.PositiveSmallIntegerField(null=True)

    # True if the profile's avatar image is set. This is used push profile cards with no avatar image to
    # the bottom of a list, and is the ONLY way to accomplish this within the limits of Django's ORM.

    avatar_set = models.BooleanField(db_index=True, default=False)

    # Relationships
    # =====================================================================================================

    # True if the user has HELIOS ROOT access. This column is also required by Django.
    is_staff = models.BooleanField(default=False, db_index=True)

    # Roles that the user has within the Helios platform. Used to give non-root staff various
    # abilities needed to manage and maintain the platform - deleting spam profiles, for example

    roles = ArrayField(models.PositiveIntegerField(unique=True), db_index=True, default=list)

    # Matching
    # =====================================================================================================

    # Date of Birth
    dob = models.DateField(db_index=True, null=True)

    # Gender identity is/seeking. This is going to be a *lot* of work to implement properly. A "good" implementation
    # would probably involve a system table of named gender ID's like "male", "female", "trans->male", and a many<>many
    # table mapping People to genders, with a weight for each mapping.

    GID_IS_IDS = (

        (GenderId.ID_MALE, "ID_MALE"),
        (GenderId.ID_FEMALE, "ID_FEMALE"),
        (GenderId.ID_OTHER, "ID_OTHER")
    )

    VALID_GID_IS = [GenderId.ID_MALE, GenderId.ID_FEMALE, GenderId.ID_OTHER]

    GID_SEEKING_IDS = (

        (GenderId.ID_MALE, "ID_MALE"),
        (GenderId.ID_FEMALE, "ID_FEMALE"),
        (GenderId.ID_BOTH, "ID_BOTH")
    )

    VALID_GID_SEEKING = [GenderId.ID_MALE, GenderId.ID_FEMALE, GenderId.ID_BOTH]

    # Gender ID this User identifies with
    gid_is = models.SmallIntegerField(db_index=True, choices=GID_IS_IDS, null=True)

    # Gender ID this User is seeking
    gid_seeking = models.SmallIntegerField(db_index=True, choices=GID_SEEKING_IDS, null=True)

    # Preferred age range from, this User is seeking
    seeking_age_from = models.PositiveSmallIntegerField(default=18, db_index=True)

    # Preferred age range to, this User is seeking
    seeking_age_to = models.PositiveSmallIntegerField(default=45, db_index=True)

    # Text
    # =====================================================================================================

    # The User's Location, if any. This field avoids having to run subqueries in the User list and Org member
    # manager. People can only have one location. Building the UI necessary to handle anything more than that is far
    # too much work and provides very little benefit. Yes, people can live in 3 different cities at once or commute
    # to another city for work, but 99.999% of the population lives and works in a single city.

    location = models.OneToOneField('silo_user.Location', related_name='owner', blank=True, null=True, on_delete=models.SET_NULL)

    # True if the profile's Location is set. This is used push Users with no Location to the bottom of a list,
    # and is the ONLY way to accomplish this within the limits of Django's ORM.

    location_set = models.BooleanField(db_index=True, default=False)

    # Text
    # =====================================================================================================

    # The user's first name. This field is REQUIRED for Django's base models.
    first_name = models.CharField(max_length=40, null=True)

    # The user's last name. This field is REQUIRED for Django's base models.
    last_name = models.CharField(max_length=40, blank=True, null=True)

    # Sum yourself up in 255 characters or less
    tagline = models.TextField(blank=True, default='', null=True)

    # Text blob containing the user's biography
    bio = models.TextField(blank=True, default='', null=True)

    # Search
    # =====================================================================================================

    # TSVector for name of a User
    name_tsv = VectorField(db_index=True, null=True)

    # TSVector for email of a User
    email_tsv = VectorField(db_index=True, null=True)

    # TSVector for tagline of a User
    tagline_tsv = VectorField(db_index=True, null=True)

    # TSVector for bio of a User
    bio_tsv = VectorField(db_index=True, null=True)

    # TSVector for all of the above fields
    text_tsv = VectorField(db_index=True, null=True)

    # HIDDEN FIELD INHERITED FROM AbstractBaseUser CLASS
    # last_login = models.DateTimeField(_('last login'), default=timezone.now)

    # =====================================================================================================

    # [HSM] The HSM signature for this record. Used to detect if the record has been tampered with.
    hsm_sig = models.TextField(blank=True, null=True)

    # These parameters are required by Django for user creation

    objects = UserManager()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    def generate_hsm_hash(self):
        """
            Concatenates all HSM controlled columns in a record into a string, for processing by the HSM
        """

        return ''.join([

            str(self.id),
            str(self.email),
            str(self.created),
            str(self.token_account_id),
            str(self.hid),
            str(self.is_staff),
            str(self.roles)
        ])

    @property
    def name(self):
        """ Required by Django """
        return self.first_name

    def get_full_name(self):
        """ Required by Django """
        return self.first_name if not self.last_name else ' '.join(self.first_name, self.last_name)

    def get_short_name(self):
        """ Required by Django """
        return self.first_name

    @property
    def profile_name(self):
        return self.get_full_name()

    @property
    def age(self):
        today = date.today()
        if self.dob is None:
            return 0
        else:
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    @property
    def is_deleted(self):
        return self.state in (User.DISABLED, User.DELETED)

    @classmethod
    def generate_hid(cls):
        """
            Generates a globally-unique shard key for this User. The shard key is used to generate
            a unique filepath for storing the User's media assets.
        """

        while True:

            # Generate a completely random string of HEX PAIRS, which is ~4 billion possibilities. This is
            # not a security-critical algorithm, all we're doing is creating a balanced file tree

            key = ''.join([random.choice('0123456789abcdef') for x in range(8)])

            if not cls.objects.filter(hid=key).exists():
                return key

    @classmethod
    def validate_hid(cls, key):
        """
            Validates a shard key
        """

        if not len(key) == 8:
            return False

        return not bool(set(key) - set('0123456789abcdef'))

    @classmethod
    def _cdn_path(cls, hid):
        """
            Returns the path to this User's CDN folder. The first 2 bytes of the User's hid are the
            hid of the Helios that owns the User. This lets us get the full asset path with a single query.
        """

        assert settings.H1_CDN_ROOT, 'No H1_CDN_ROOT value configured in settings.py'

        result = settings.H1_CDN_ROOT + 'p/'
        result += hid[0:2] + '/'
        result += hid[2:4] + '/'
        result += hid[4:6] + '/'
        result += hid[6:]

        return result

    @classmethod
    def _cdn_url(cls, hid):
        """
            Returns the URL to this User's CDN folder
        """

        assert settings.H1_CDN_URL, 'No H1_CDN_URL value configured in settings.py'

        result = settings.H1_CDN_URL + 'p/'
        result += hid[0:2] + '/'
        result += hid[2:4] + '/'
        result += hid[4:6] + '/'
        result += hid[6:]

        return result

    @property
    def _assets_path(self):
        """
            Returns the path to this Org's assets folder
        """

        return User._cdn_path(self.hid) + '/a/'

    @newrelic.agent.function_trace()
    def _get_img_url(self, prefix, sizes, img_key, largest_img_size, req_x, req_y):
        """
            Returns the URL to a given size of an image owned by a cls. The function will return the closest
            image size greater than or equal to the target size, if it exists, otherwise it will return the largest
            size available. If the profile does not have an image matching the specified prefix set, it will return
            an equivalent default image.

            :param prefix: The image prefix, eg "avatar_"
            :param sizes: A list of sizes to evaluate. Each size is an object of the form {'id':<ID>,'x':<X>,'y':<Y>}.
            :param img_key:
            :param largest_img_size: Largest image size available as reported by the profile
            :param req_x: Requested x-pixels size to retrieve an image for.
            :param req_y: Requested y-pixels size to retrieve an image for.

            :return: URL to image file
        """

        if not img_key:

            for size in sizes:

                best_size = size

                if req_x and size['x'] >= req_x or req_y and size['y'] >= req_y:
                    break

            return settings.H1_IMG_SRC_URL + 'user/{}_{}.jpg'.format(prefix, best_size['id'])


        else:

            base_path = User._cdn_url(hid) + '/a/'

            for size in sizes:

                # Current size exceeds requested values in at least one axis
                size_exceeds_axis = req_x and size['x'] >= req_x or req_y and size['y'] >= req_y

                # Requested size exceeds largest size available
                reached_max_size = (size['id'] == largest_img_size)

                if size_exceeds_axis or reached_max_size:
                    return base_path + '{}_{}_{}.jpg'.format(img_key, prefix, str(size['id']))

    @classmethod
    def delete_cdn_assets(cls, hid):
        """
            Removes all files and folders owned by this User from the CDN
        """

        assert settings.H1_CDN_ROOT, 'No H1_CDN_ROOT value configured in settings.py'

        level_1 = settings.H1_CDN_ROOT + 'p/' + hid[0:2] + '/'
        level_2 = level_1 + hid[2:4] + '/'
        level_3 = level_2 + hid[4:6] + '/'
        level_4 = level_3 + hid[6:] + '/'

        # At 32,000 users, each level_1 folder will have an average of 128 level_2 folders inside it, and each
        # level_2 folder has 50% odds of having two or more level_3 folders inside it. Since filesystem calls
        # delay completing the operation, we only make calls that are likely to be useful.

        try:

            if os.path.exists(level_4):
                shutil.rmtree(level_4)

                if len(os.listdir(level_3)) == 0:
                    os.rmdir(level_3)

                    if len(os.listdir(level_2)) == 0:
                        os.rmdir(level_2)

                        if len(os.listdir(level_1)) == 0:
                            os.rmdir(level_1)

        except:

            # This is a rare occasion where we need to ignore an exception. Even if this method partially
            # completes, there's no undo. In the future we will log this so manual cleanup is possible.
            pass

    @classmethod
    def create_cdn_folder(cls, hid):
        """
            Creates the assets folder for a Post
        """

        try:
            os.makedirs(User._cdn_path(hid) + '/', 0755)
            os.makedirs(User._cdn_path(hid) + '/a', 0755)  # Asset

        except:
            raise HeliosException(desc='Error creating assets folder', code='error_creating_assets_folder')

    def get_relative_url(self):
        """
            Returns the url to a user's root page RELATIVE to the root domain
        """

        return reverse('AppHelios.User.Home', kwargs={'hid': self.hid})

    def get_absolute_url(self):
        """
            Returns the ABSOLUTE url to a User's root page
        """

        return settings.SITE_PROTOCOL + settings.SITE_DOMAIN + self.get_relative_url()

    @newrelic.agent.function_trace()
    def get_notifications_url(self):
        """
            Returns the absolute URL to the User's notifications settings screen

            :return: (string) URL to notifications settings URL
        """

        base = settings.SITE_PROTOCOL + settings.SITE_DOMAIN

        return base + reverse('AppHelios.User.Notifications', kwargs={'hid': self.hid})

    @newrelic.agent.function_trace()
    def get_avatar_url(self, req_x=None, req_y=None):
        """
            Returns the URL to a given size of profile avatar image.
            It returns a default image if no profile avatar image set.

            :param req_x: (opt) Requested x-pixels size to retrieve an image for.
            :param req_y: (opt) Requested y-pixels size to retrieve an image for.

            :return: (string) URL to the avatar image
        """

	imgix_service = ImgixService()
	return imgix_service.build_avatar_url(self, req_x, req_y)
