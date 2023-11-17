import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType

# See https://django-auth-ldap.readthedocs.io/en/latest/index.html

AUTH_LDAP_SERVER_URI = 'ldap://X.Y.Z.389'

AUTH_LDAP_BIND_DN = 'uid=XXXX,dc=X,dc=Y,dc=Z'
AUTH_LDAP_BIND_PASSWORD = 'my-super-secure-ldap-password'
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "cn=users,dc=X,dc=Y,dc=Z",
    ldap.SCOPE_SUBTREE,
    "(|(uid=%(user)s)(mail=%(user)s))",
)

# AUTH_LDAP_REQUIRE_GROUP = 'cn=GGGGGG,cn=groups,dc=X,dc=Y,dc=Z'

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    'cn=groups,dc=X,dc=Y,dc=Z',
    ldap.SCOPE_SUBTREE
)
AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType(name_attr="cn")

AUTH_LDAP_USER_QUERY_FIELD = "username"
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "uid",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache distinguished names and group memberships for 15min to minimize
# LDAP traffic.
AUTH_LDAP_CACHE_TIMEOUT = 900

AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
]
