# -*- coding: utf-8 -*-

from sys_base.exceptions import HeliosException


def deduplicate_list(items):
    """
        The fastest known algorithm for deduplicating an ordered list in Python while preserving the order
        of the list. Runs in O(N) time. See: https://www.peterbe.com/plog/uniqifiers-benchmark
    """

    seen = set()
    seen_add = seen.add

    return [x for x in items if not (x in seen or seen_add(x))]


def reorder_object_list(obj_list, attr_name, ordr_list):
    """
        Returns a list of objects, ordered by 'attr_name', in the order specified by 'ordr_list'. The value of
        'attr_name' must be unique across 'obj_list', and the values in 'ordr_list' must map one-to-one with the
        values of 'attr_name' in 'obj_list'.

        :param obj_list: a list of objects, containing attribute 'attr_name', to reorder
        :param attr_name: string name of the attribute to reorder based on
        :param ordr_list: a list of 'attr_name' values ordered in the way 'obj_list' should be ordered

        EXAMPLE:

            obj_a = object()
            obj_a.foo = 'x'
            obj_a.bar = '1'

            obj_b = object()
            obj_b.foo = 'y'
            obj_b.bar = '2'

            obj_c = object()
            obj_c.foo = 'z'
            obj_c.bar = '3'

            result = reorder_object_list(

                obj_list = [obj_a, obj_b, obj_c],
                attr_name = 'foo',
                ordr_list = ['z', 'y', 'x']
            )

            print [item.bar for item in result]

            >> '3', '2', '1'
    """

    mapped = {

        # This will raise an exception if the object is missing attr_name
        getattr(obj, attr_name): obj for obj in obj_list
    }

    if len(mapped) != len(obj_list):
        raise HeliosException(

            desc='obj_list contains two or more items with the same attr_name value',
            code='duplicate_obj_attr'
        )

    if set(mapped.keys()) != set(ordr_list):
        diff = str(set(mapped.keys()) ^ set(ordr_list))

        raise HeliosException(

            desc='the values in ordr_list do not map one-to-one to the attr_name values in obj_list ' + diff,
            code='not_one_to_one'
        )

    return [mapped[key] for key in ordr_list]
