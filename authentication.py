"""
UbuntuSSO OpenID support

No extra configurations are needed to make this work.
"""
from social_auth.backends import OpenIDBackend, OpenIdAuth


UBUNTU_OPENID_URL = 'https://login.ubuntu.com/'


class UbuntuSSOBackend(OpenIDBackend):
    """UbuntuSSO OpenID authentication backend"""
    name = 'yahoo'


class UbuntuSSOAuth(OpenIdAuth):
    """UbuntuSSO OpenID authentication"""
    AUTH_BACKEND = UbuntuSSOBackend

    def openid_url(self):
        """Return UbuntuSSO OpenID service url"""
        return UBUNTU_OPENID_URL


# Backend definition
BACKENDS = {
    'ubuntu': UbuntuSSOAuth,
}
