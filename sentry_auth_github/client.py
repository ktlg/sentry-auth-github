from __future__ import absolute_import, print_function

from requests.exceptions import RequestException
from sentry import http
from sentry.utils import json

from .constants import API_DOMAIN


class GitHubApiError(Exception):
    def __init__(self, message='', status=0):
        super(GitHubApiError, self).__init__(message)
        self.status = status


class GitHubClient(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.http = http.build_session()

    def _request(self, path, access_token):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        headers = {
            'Authorization': 'token {0}'.format(access_token),
        }

        try:
            req = self.http.get('https://{0}/{1}'.format(API_DOMAIN, path.lstrip('/')),
                params=params,
                headers=headers,
            )
        except RequestException as e:
            raise GitHubApiError(unicode(e), status=getattr(e, 'status_code', 0))
        if req.status_code < 200 or req.status_code >= 300:
            raise GitHubApiError(req.content, status=req.status_code)
        return json.loads(req.content)

    def get_org_list(self, access_token):
        return self._request('/user/orgs', access_token)

    def get_user(self, access_token):
        return self._request('/user', access_token)

    def get_user_emails(self, access_token):
        return self._request('/user/emails', access_token)

    def is_org_member(self, access_token, org_ids):
        """
        Checks whether user is able to login via GitHub.

        :param access_token: User github token.
        :type access_token: str

        :param org_ids: Identificators of GitHub orgranizations.
        :type org_ids: list

        :return: True if user is allowed to login, False - otherwise
        :rtype: bool
        """
        # retrieve list of github org for a user by his access_token
        org_list = self.get_org_list(access_token)

        # check whether this user is able to login via github
        org_ids = [str(org) for org in org_ids]
        for org in org_list:
            if str(org['id']) in org_ids:
                return True
        return False
