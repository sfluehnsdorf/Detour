# -*- coding: utf8 -*-
u"""
===============================================================================

                 D e t o u r   P r o d u c t   R e g i s t r y

Zope2 Product registry, which registers all Product classes, constructor,
online help and any other Product related resources.

===============================================================================
Copyright (c) 2007 - 2014, Sebastian Lühnsdorf - Web-Solutions
For more information see the README.txt file or visit www.zope.biz

-------------------------------------------------------------------------------
This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL).

A copy of the ZPL should accompany this distribution.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES
ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE,
MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

-------------------------------------------------------------------------------
"""


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
