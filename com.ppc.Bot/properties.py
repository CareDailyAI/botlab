"""
Created on April 27, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""


def get_property(botengine, name, complain_if_missing=True):
    """
    Extract a property 'the right way' to allow organization properties to override the local bot properties.
    :param botengine: BotEngine environment
    :param name: Property name
    :param complain_if_missing: Issue a warning to the developer if this property is missing, default is True
    :return: Property value, or None if it doesn't exist
    """
    # Organization properties override local properties
    if botengine is not None:
        if name in botengine.organization_properties:
            property = (
                str(botengine.organization_properties[name])
                .replace("null", "None")
                .replace("false", "False")
                .replace("true", "True")
            )
            botengine.get_logger(f"{__name__}").debug(
                "properties.py: Using organization property '{}' {}.".format(
                    name, property
                )
            )
            try:
                return eval(property)
            except Exception:
                return botengine.organization_properties[name]

    # Attempt to extract the local property
    import domain

    try:
        property = getattr(domain, name)

        if botengine is not None:
            botengine.get_logger(f"{__name__}").debug(
                "properties.py: Using domain property '{}' {}.".format(name, property)
            )
        return property
    except Exception:
        # Couldn't find it locally, return None
        if complain_if_missing:
            if botengine is not None:
                botengine.get_logger(f"{__name__}").warning(
                    "properties.py: Please define property '{}' in your domain.py file.".format(
                        name
                    )
                )
    return None
