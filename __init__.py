import logging
import warnings

warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=r".*google\._upb\._message\..*uses PyType_Spec.*",
)

from . import models
from . import wizard
from . import controllers

# Silence the XML-RPC deprecation warning which is noisy in Odoo 19
logging.getLogger('odoo.addons.rpc.controllers.xmlrpc').setLevel(logging.ERROR)

def post_init_hook(env):
    """Refined Command: Update configuration parameters after module installation."""
    pass


