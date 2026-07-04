# -*- coding: utf8 -*-
u"""
===============================================================================

                       D e t o u r   B a s e   C l a s s

!TXT!

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
# Imports


from urllib import quote_plus

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view as view_permission
from AccessControl.Role import RoleManager
from Globals import DTMLFile, InitializeClass
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from OFS.History import Historical


# =============================================================================
# Definitions


prefix_types = ('none', 'acquired_prefix', 'absolute_url', 'get_site_url')

true_values = ('1', 'true', 'on', 'yes')


# =============================================================================
# Option Verification


def verify_options(errors, destination, prefix_type, acquired_prefix_id,
                   status_code, custom_status_code, truncate_url):
    """!!!."""
    #

    # verify prefix type settings
    if prefix_type not in prefix_types:
        errors['prefix_type'] = "Invalid prefix type specified!"
    elif prefix_type == 'none' and not str(destination).strip():
        errors['destination'] = ("You have to specify a destination for the "
                                 "redirect!")
    elif prefix_type == 'acquired_prefix' and not acquired_prefix_id.strip():
        errors['acquired_prefix_id'] = ("You have to specify a prefix for the "
                                        "selected prefix type!")

    # verify status code
    if status_code == 'custom':
        status_code = custom_status_code
    try:
        status_code = int(status_code)
    except:
        errors['status_code'] = ("Please provide a numeric (integer) HTTP "
                                 "response status code!")

    # verfiy truncate url option
    if truncate_url and str(truncate_url).lower() in true_values:
        truncate_url = True
    else:
        truncate_url = False

    return errors


# =============================================================================
# Detour Base Class

class Detour(SimpleItem, PropertyManager, RoleManager, Historical):
    """Detour Base Class."""

    security = ClassSecurityInfo()

    # -------------------------------------------------------------------------
    # Attributes

    meta_type = 'Detour'

    # The following definition is a hack to make Detour work properly with the
    # VirtualHostMonster as it expects a Folder like Product as a destination.
    isAnObjectManager = True

    destination = ''
    prefix_types = prefix_types
    prefix_type = 'none'
    prefix = ''
    status_code = 301
    truncate_url = None

    # -------------------------------------------------------------------------
    # Properties

    _properties = PropertyManager._properties + (
        {
            'id': 'destination',
            'type': 'string',
            'mode': 'w',
            'label': 'Destination URL or path',
        },
        {
            'id': 'prefix_type',
            'type': 'selection',
            'mode': 'w',
            'label': 'Prefix Type',
            'select_variable': 'prefix_types',
        },
        {
            'id': 'prefix',
            'type': 'string',
            'mode': 'w',
            'label': 'Custom Prefix String or Method',
        },
        {
            'id': 'truncate_url',
            'type': 'boolean',
            'mode': 'w',
            'label': 'Truncate URL and discard traverse_subpath',
        },
        {
            'id': 'status_code',
            'type': 'int',
            'mode': 'w',
            'label': 'HTTP Status Code'
        },
    )

    # -------------------------------------------------------------------------
    # ZMI Tabs

    manage_options = (
        {'label': 'Options', 'action': 'options_form'},
        {'label': 'Test', 'action': 'index_html'},
    ) +\
        PropertyManager.manage_options +\
        Historical.manage_options +\
        RoleManager.manage_options +\
        SimpleItem.manage_options

    # -------------------------------------------------------------------------
    # ZMI Find

    security.declareProtected(view_permission, 'SearchableText')

    def SearchableText(self):
        """Provide search data."""
        return '%s %s' % (self.prefix, self.destination)

    # -------------------------------------------------------------------------
    # Options

    options_form = DTMLFile('options', globals())

    def save_options(self, destination='', prefix_type='none',
                     acquired_prefix_id='', status_code=301,
                     custom_status_code=None, truncate_url=True, REQUEST=None):
        """Save options."""
        #

        # process parameters
        errors = verify_options(
            {},
            destination,
            prefix_type,
            acquired_prefix_id,
            status_code,
            custom_status_code,
            truncate_url
        )

        # handle errors
        if errors.keys():
            if REQUEST is not None:
                message = ("Your changes could not be saved because there was "
                           "a problem with your entries.")
                return self.options_form(client=self, REQUEST=REQUEST,
                                         errors=errors,
                                         manage_tabs_message=message)
            else:
                raise ValueError('\n'.join(errors.values()))

        # create instance
        self.destination = str(destination).strip()
        self.prefix_type = prefix_type
        self.acquired_prefix_id = str(acquired_prefix_id).strip()
        self.status_code = int(
            status_code == 'custom' and
            custom_status_code or
            status_code
        )
        self.truncate_url = str(truncate_url) in true_values and True or False

        # ZMI redirect
        if REQUEST is not None:
            message = 'Changes saved.'
            return self.options_form(client=self, REQUEST=REQUEST,
                                     manage_tabs_message=message)

    # -------------------------------------------------------------------------
    # Traversal

    def __before_publishing_traverse__(self, object, REQUEST):
        """End traversal and place request path to REQUEST."""
        path = REQUEST['TraversalRequestNameStack']

        # return, if path points to this object
        if path and hasattr(self.aq_base, path[-1]):
            return

        # process subpath and store in REQUEST
        subpath = path[:]
        for key in ['/', 'virtual_hosting']:
            while key in subpath:
                subpath.remove(key)
        path[:] = []
        subpath.reverse()

        REQUEST.set('traverse_subpath', subpath)

    # -------------------------------------------------------------------------
    # Call Handler

    def __call__(self, REQUEST, RESPONSE):
        """Redirect to the specified URL."""
        self.index_html(REQUEST, RESPONSE)

    def index_html(self, REQUEST, RESPONSE):
        """Redirect to the specified URL."""
        #

        # prepare URL
        url = self.destination

        # determine prefix according to prefix_type
        prefix_type = self.prefix_type
        if prefix_type == 'absolute_url':
            url = self.aq_parent.absolute_url() + '/' + url
        elif prefix_type == 'acquired_prefix':
            prefix = self.aq_acquire(self.acquired_prefix_id)
            if callable(prefix):
                prefix = prefix()
            url = prefix + (not(prefix.endswith('/')) and '/' or '') + url
        elif prefix_type == 'get_site_url':
            url = self.aq_acquire('get_site_url')() + '/' + url

        # append subpath
        if not self.truncate_url:
            subpath = REQUEST.get('traverse_subpath', [])
            url = url + (subpath and ('/' + '/'.join(subpath)) or '')

        # redirect with status code
        RESPONSE.redirect(url, status=self.status_code, lock=True)


# -----------------------------------------------------------------------------
# Class Initialization


InitializeClass(Detour)


# =============================================================================
# Constructor Form


add_Detour_form = DTMLFile('add', globals())


# =============================================================================
# Constructor Method


def add_Detour(self, id, title='', destination='', prefix_type='none',
               acquired_prefix_id='', status_code=301, custom_status_code=None,
               truncate_url=True, REQUEST=None):
    """ZMI constructor for Detour."""
    #

    # process parameters
    errors = {}
    id = str(id).strip()
    if not id:
        errors['id'] = "You have to specify an Id for the new object!"
    errors = verify_options(errors, destination, prefix_type,
                            acquired_prefix_id, status_code,
                            custom_status_code, truncate_url)

    # handle errors
    if errors.keys():
        if REQUEST is not None:
            REQUEST.set('errors', errors)
            return self.add_Detour_form(client=self, REQUEST=REQUEST)
        else:
            raise ValueError('\n'.join(errors.values()))

    # -------------------------------------------------------------------------
    # create instance

    instance = Detour(id)
    instance.id = id
    instance.title = str(title).strip()
    id = self._setObject(id, instance)
    instance = self._getOb(id)

    # -------------------------------------------------------------------------
    # save options

    instance.save_options(destination, prefix_type, acquired_prefix_id,
                          status_code, custom_status_code, truncate_url)

    # -------------------------------------------------------------------------
    # ZMI redirect

    if REQUEST is not None:
        try:
            base_url = self.DestinationURL()
        except:
            base_url = REQUEST['URL1']
        REQUEST.RESPONSE.redirect(
            '%s/manage_main?update_menu=1&manage_tabs_message=%s' % (
                base_url,
                quote_plus(u"""A new Detour with Id "%s" was created""" % id)
            )
        )
