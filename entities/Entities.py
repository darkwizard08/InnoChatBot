__author__ = 'darkwizard'
from pony.orm import *

db = Database()


class LinkEntity(db.Entity):
    name = Required(str)
