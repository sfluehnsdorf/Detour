"""Detour."""


# =============================================================================
# Module Imports


from Products.Detour.Detour import (
    Detour, add_and_edit_Detour, add_Detour_form, add_Detour)


# =============================================================================
# Zope Registry


def initialize(context):
    """Register Product."""
    context.registerClass(
        Detour,
        meta_type="Detour",
        permission="Add Detours",
        constructors=(
            ('add_Detour_form', add_Detour_form),
            ('add_Detour', add_Detour),
            ('add_and_edit_Detour', add_and_edit_Detour),
        ),
        legacy=(
            ('add_Detour', add_Detour),
            ('add_and_edit_Detour', add_and_edit_Detour),
        ),
        icon='resources/icon.png',
    )
