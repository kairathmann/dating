#  -*- coding: UTF8 -*-

import copy
from random import randint

from sys_base.entity.renderable import HeliosEntityRenderable
from sys_base.schema.form import ffield
from sys_base.schema.query import qfield
from sys_util.geodata.name import render_name_chain_deferred

from django.db.models.expressions import RawSQL
from django.db.models.fields import BooleanField
from silo_user.user.db import User
from sys_base.api import parse_search_string


class UserAsBase(HeliosEntityRenderable):
    COLUMNS = [

        qfield.ColumnField(

            desc='Avatar Set',
            column='avatar_set',
            ops=[''],
            form_field=ffield.BooleanFormField(),
            cardinal=True
        ),

        qfield.ColumnField(

            desc='Avatar Size',
            column='avatar_size',
            ops=['', '__ne', '__gt', '__lt', '__gte', '__lte'],
            form_field=ffield.IntegerFormField(max_val=None, min_val=0)
        ),

        qfield.ColumnField(

            desc='Job Set',
            column='job_set',
            ops=[''],
            form_field=ffield.BooleanFormField(),
            cardinal=True
        ),

        qfield.ColumnField(

            desc='Location Set',
            column='location_set',
            ops=[''],
            form_field=ffield.BooleanFormField(),
            cardinal=True
        ),

        qfield.ColumnField(

            desc='Roles',
            column='roles',
            ops=['__in'],

            form_field=ffield.SelectFormField(

                generator=lambda d: [(1, 'Members'), (2, 'Owners')],
                validator=lambda d, v: True,
                multiselect=True
            ),
            cardinal=True
        ),

        qfield.ColumnField(

            desc='Segments',
            column='segments',
            ops=['__in'],

            form_field=ffield.SelectFormField(

                generator=lambda d: [(1, 'Members'), (2, 'Owners')],
                validator=lambda d, v: True,
                multiselect=True
            ),
            cardinal=True
        ),

        qfield.ColumnField(

            desc='Last Login',
            column='last_login',
            ops=['__date__gt', '__date__lt', '__date__gte', '__date__lte'],
            form_field=ffield.DateTimeFormField()
        ),

        qfield.AnnotationField(

            desc='Viewer Follows User',
            column='viewer_follows',
            ops=[''],
            form_field=ffield.BooleanFormField(),
            cardinal=True
        ),

        qfield.AnnotationField(

            desc='Target Follows User',
            column='target_follows',
            ops=[''],
            form_field=ffield.BooleanFormField(),
            cardinal=True
        ),

        # qfield.AnnotationField(
        #
        #     desc = 'Location Overlap',
        #     column = 'location_overlap',
        #     ops = ['__gt', '__lt', '__gte', '__lte'],
        #     form_field = ffield.FloatFormField(max_val=None, min_val=0)
        # ),
        #
        # qfield.AnnotationField(
        #
        #     desc = 'Topic Overlap',
        #     column = 'topic_overlap',
        #     ops = ['__gt', '__lt', '__gte', '__lte'],
        #     form_field = ffield.FloatFormField(max_val=None, min_val=0)
        # ),
        #
        # qfield.AnnotationField(
        #
        #     desc = 'Follow Overlap',
        #     column = 'follow_overlap',
        #     ops = ['__gt', '__lt', '__gte', '__lte'],
        #     form_field = ffield.FloatFormField(max_val=None, min_val=0)
        # )
    ]

    def annotate_data(self, viewed_user_id):
        """
            :return:
        """

        viewer_id = self.viewer.id if self.viewer else 0

        data = {

            'target_follows': RawSQL(

                # language=SQL --INTELLIJ
                """
                    EXISTS (

                        SELECT id
                        FROM silo_user_follow
                        WHERE silo_user_follow.target_id = silo_user_user.id
                        AND "silo_user_follow"."source_id" = %s
                    )
                """,
                (viewed_user_id,),
                output_field=BooleanField()
            ),

            'follows_target': RawSQL(

                # language=SQL --INTELLIJ
                """
                    EXISTS (

                        SELECT id
                        FROM silo_user_follow
                        WHERE silo_user_follow.source_id = silo_user_user.id
                        AND "silo_user_follow"."target_id" = %s
                    )
                """,
                (viewed_user_id,),
                output_field=BooleanField()
            ),

            'viewer_follows': RawSQL(

                # language=SQL --INTELLIJ
                """
                    EXISTS (

                        SELECT id
                        FROM silo_user_follow
                        WHERE silo_user_follow.target_id = silo_user_user.id
                        AND "silo_user_follow"."source_id" = %s
                    )
                """,
                (viewer_id,),
                output_field=BooleanField()
            ),
        }

        return {self.prefix + '__' + col: rule for col, rule in data} if self.prefix else data

    def build_avatar(self, user):
        """
            Returns the 'avatar' URL for a rendered item
        """

        return user.get_avatar_url(

            req_x=self.avatar_req_x,
            req_y=self.avatar_req_y
        )

    def build_job(self, user):
        """
            Builds the 'job' dict for a rendered item
        """

        return {

            'TITLE': user.job.title if user.job else None,
            'EMPLOYER': user.job.employer if user.job else None
        }

    def build_location(self, user):
        """
            Builds the 'location' string for a rendered item
        """

        return render_name_chain_deferred(user.location)

    def build_actions(self, user):
        """
            Builds the 'actions' dict for a rendered item
        """

        return {

            'HAS_FOLLOWED': bool(user.id in self.followed_ids),
            'CAN_FOLLOW': bool(self.viewer and (user.id not in self.followed_ids))
        }

    def build_stats(self):
        """
            Placeholder function that generates stats data for testing
        """

        return {

            'GEO': str(randint(27, 95)) + '%',
            'TOPICS': str(randint(27, 95)) + '%',
            'FRIENDS': str(randint(27, 95)) + '%',
        }

    # ##############################################################################################################

    def get_as_query(self, query_obj, start, end, items_order_by=None):

        # Deep copy the filter and ordering dicts to guard against the additional constraints we add to
        # them being accidentally saved to the schema due to object reuse

        incl = copy.deepcopy(query_obj.rules['include'])
        excl = copy.deepcopy(query_obj.rules['exclude'])
        ordr = copy.deepcopy(query_obj.rules['order_by'])  # ('-avatar_set', '-last_login')

        # Handle the Pivot Table view
        # -----------------------------------------------------------------------------------

        if items_order_by:
            ordr = self.parse_orderby_token(items_order_by, ordr)

        pre = self.select_related_cols()
        cols = self.only_cols()

        # ADDITIONAL CONSTRAINTS
        # -----------------------------------------------------------------------------------

        incl['status'] = User.STATUS_ACTIVE  # Remove hidden and deleted users
        incl['universes__overlap'] = [self.universe.id]  # Limit query scope to current universe to improve speed

        # If querying in the context of an Org, force listed people to be a member of THIS org

        if self.org is not None:
            # NOTE: cannot add this safety check this way because it overwrites the roles__overlap
            # filter set in the rules dict

            # incl['roles__overlap'] = [self.org.role_member_id]

            items = list(
                User.objects.select_related(*pre).only(*cols).filter(**incl).exclude(**excl).order_by(*ordr)[start:end])
            total = User.objects.select_related(*pre).filter(**incl).exclude(**excl).count()

        if getattr(self, 'viewed_user', None):
            anno = self.annotate_data(self.viewed_user.id)

            items = list(
                User.objects.annotate(**anno).select_related(*pre).only(*cols).filter(**incl).exclude(**excl).order_by(
                    *ordr)[start:end])
            total = User.objects.annotate(**anno).select_related(*pre).filter(**incl).exclude(**excl).count()

        return total, items

    def query_as_html(self, target, query_obj, items_page, items_per_page, items_order_by):

        start, end = self.calc_db_offsets(items_page, items_per_page)

        total_items, items = self.get_as_query(query_obj, start, end, items_order_by=items_order_by)

        return self.render_iframe_html(

            target=target,
            items_page=items_page,
            total_items=total_items,
            items=items
        )

    def get_as_search(self, search_str, start, end, items_order_by=None):

        # Sanitize search_name
        # =========================================================================

        incl = {

            'universes__overlap': [self.universe.id],  # Limit query scope to current universe to improve speed
            'status': User.STATUS_ACTIVE,  # Remove hidden and deleted users
        }

        # If an empty search string is passed, return ALL item. This greatly simplifies the frontend JS code,
        # and makes the system easier to use by showing the user what query results will look like

        parsed_search_str = parse_search_string(search_str)

        if parsed_search_str:
            incl['text_tsv__ft_expression'] = parsed_search_str

        excl = {}
        ordr = ('-avatar_set', '-last_login')

        # Handle the Pivot Table view
        # -----------------------------------------------------------------------------------

        if items_order_by:
            ordr = self.parse_orderby_token(items_order_by, ordr)

        pre = self.select_related_cols()
        cols = self.only_cols()

        # ADDITIONAL CONSTRAINTS
        # -----------------------------------------------------------------------------------

        # If querying in the context of an Org, force listed people to be a member of THIS org

        if self.org is not None:
            incl['roles__overlap'] = [self.org.role_member_id]

            items = list(
                User.objects.select_related(*pre).only(*cols).filter(**incl).exclude(**excl).order_by(*ordr)[start:end])

            # from django.db import connection
            # print connection.queries

            total = User.objects.select_related(*pre).filter(**incl).exclude(**excl).count()

        if getattr(self, 'viewed_user', None):
            anno = self.annotate_data(self.viewed_user.id)

            items = list(
                User.objects.annotate(**anno).select_related(*pre).only(*cols).filter(**incl).exclude(**excl).order_by(
                    *ordr)[start:end])
            total = User.objects.annotate(**anno).select_related(*pre).filter(**incl).exclude(**excl).count()

        return total, items

    def search_as_html(self, target, search_str, items_page, items_per_page, items_order_by=None):

        start, end = self.calc_db_offsets(items_page, items_per_page)
        total_items, items = self.get_as_search(search_str, start, end, items_order_by=items_order_by)

        return self.render_iframe_html(

            target=target,
            items_page=items_page,
            total_items=total_items,
            items=items
        )
