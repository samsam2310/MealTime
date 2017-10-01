# -*- coding: utf-8 -*-

# DB - Collection User

from .base import Collection
from .base import Field


class User(Collection):
    _ORM_collection = 'User'

    # String - FB uid.
    uid = Field()
    # Array - The current cmd and args.
    cmd = Field([])
    # Int - The times of error input to the cmd.
    error_cnt = Field(0)
    # Object - FB user data cache.
    udata = Field({})
