#  -*- coding: UTF8 -*-


def render_name_chain_dict(location):
    """
        Generates a pleasing name-chain for everything from a "point" to a "country" based on the supplied dicts

        :param location: A location dict
        :return: (string) composited name chain
    """

    # If we were passed a place name, simply combine it with the admin1 name, because every Place in our
    # datastore has an admin1 record.

    if location['place_name']:

        # If the location is in Canada or the USA, we can use the short name (code column) for the admin 1. This
        # produces results like "New York City, NY, USA" instead of "New York City, New York, USA"

        if location['country_alpha3'] in ['USA', 'CAN']:

            return location['place_name'] + u", " + location['admin1_code'] + u", " + location['country_alpha3']

        elif location['admin1_code']:

            return location['place_name'] + u", " + location['admin1_name'] + u", " + location['country_alpha3']

    # Otherwise, descend through the admin hierarchy until an admin4 -> admin2 record is found, then append
    # the admin1 record's name to it. This produces results like "Bronx County, New York"

    base_name = u""
    no_match = True

    if location['admin4_name']:
        no_match = False

        base_name += location['admin4_name']

    if location['admin3_name'] and no_match:
        no_match = False

        sep = u", " if len(base_name) > 0 else u""

        base_name += sep + location['admin3_name']

    if location['admin2_name'] and no_match:
        sep = u", " if len(base_name) > 0 else u""

        base_name += sep + location['admin2_name']

    if location['admin1_name']:
        sep = u", " if len(base_name) > 0 else u""

        base_name += sep + location['admin1_name']

    sep = u", " if len(base_name) > 0 else u""

    if location['country_alpha3']:

        return base_name + sep + location['country_alpha3']

    else:
        return "No Location"


def render_name_chain_deferred(location):
    """
        Generates a pleasing name-chain for everything from a "point" to a "country" based on the supplied dicts

        :param location: A location dict
        :return: (string) composited name chain
    """

    if not location:
        return 'No Location'

    # If we were passed a place name, simply combine it with the admin1 name, because every Place in our
    # datastore has an admin1 record.

    if location.place and location.place.name:

        # If the location is in Canada or the USA, we can use the short name (code column) for the admin 1. This
        # produces results like "New York City, NY, USA" instead of "New York City, New York, USA"

        if location.country and location.country.alpha3 in ['USA', 'CAN']:

            return location.place.name + u", " + location.admin1.code + u", " + location.country.alpha3

        elif location.admin1 and location.admin1.code:

            return location.place.name + u", " + location.admin1.name + u", " + location.country.alpha3

    # Otherwise, descend through the admin hierarchy until an admin4 -> admin2 record is found, then append
    # the admin1 record's name to it. This produces results like "Bronx County, New York"

    base_name = u""
    no_match = True

    if location.admin4 and location.admin4.name:
        no_match = False

        base_name += location.admin4.name

    if location.admin3 and location.admin3.name and no_match:
        no_match = False

        sep = u", " if len(base_name) > 0 else u""

        base_name += sep + location.admin3.name

    if location.admin2 and location.admin2.name and no_match:
        sep = u", " if len(base_name) > 0 else u""

        base_name += sep + location.admin2.name

    if location.admin1 and location.admin1.name:
        sep = u", " if len(base_name) > 0 else u""

        base_name += sep + location.admin1.name

    sep = u", " if len(base_name) > 0 else u""

    if location.country and location.country.alpha3:

        return base_name + sep + location.country.alpha3

    else:
        return "No Location"


def render_name_chain_obj(base_name, location):
    """
        Generates a pleasing name-chain for everything from a "point" to a "country" based on the objects
        supplied.

        :param base_name: A name string for a place
        :param location: A location object

        :return: (string) composited name chain
    """

    # If we were passed a place name, simply combine it with the admin1 name, because every Place in our
    # datastore has an admin1 record. This produces results like "New York City, New York".

    if len(base_name) > 0:

        if location.admin1:
            sep = u", " if len(base_name) > 0 else ""

            base_name += sep + location.admin1.name

        return base_name

    # Otherwise, descend through the admin hierarchy until an admin4 -> admin2 record is found, then append
    # the admin1 record's name to it. This produces results like "Bronx County, New York"

    else:

        no_match = True

        if location.admin3:
            no_match = False

            sep = u", " if len(base_name) > 0 else ""

            base_name += sep + location.admin3.name

        if location.admin2:
            no_match = False

            sep = u", " if len(base_name) > 0 else ""

            base_name += sep + location.admin2.name

        if location.admin4 and no_match:
            base_name += location.admin4.name

        if location.admin1:
            sep = u", " if len(base_name) > 0 else ""

            base_name += sep + location.admin1.name

        return base_name
