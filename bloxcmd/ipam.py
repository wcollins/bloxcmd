import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class IPAM(object):

    ''' A class that interfaces with the Infoblox IPAM system '''

    def __init__(self, hostname, username, password, version):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.version = version
        self.session = requests.session()
        self.url = '{0}/wapi/v{1}/'.format(hostname, version)
        self._RECORDS = ['A', 'AAA', 'CNAME', 'HOST', 'host', 'MX', 'PTR',
                         'SRV', 'TXT']

    def __repr__(self):

        return '<InfoBlox: {0}>'.format(self.url, self.version)

    def _request(self, obj, req, method):

        if method.upper() == 'GET':
            res = self.session.get(
                self.url + obj,
                data=json.dumps(req),
                verify=False,
                auth=(self.username, self.password)
            )
        elif method.upper() == 'POST':
            res = self.session.post(
                self.url + obj,
                data=json.dumps(req),
                verify=False,
                auth=(self.username, self.password)
            )
        elif method.upper() == 'DELETE':
            res = self.session.delete(
                self.url + obj,
                verify=False,
                auth=(self.username, self.password)
            )
        elif method.upper() == 'PUT':
            res = self.session.put(
                self.url + obj,
                data=json.dumps(req),
                verify=False,
                auth=(self.username, self.password)
            )

        if res.status_code == 200 or res.status_code == 201:
            if res.content.replace('"', '').startswith(obj):
                return True
            else:
                return res.json()
        elif res.status_code == 401:
            raise Exception('Unable to login to InfoBlox')
        else:
            raise Exception(json.loads(res.content)['text'])

    def get_record(self, record, record_type):

        if record_type in self._RECORDS:

            return self._request('record:' + record_type,
                                 {'name': record}, 'GET')
        else:
            raise Exception('unsupported record type {0}'.format(record_type))

    def get_network(self, network):

        ''' Return network details '''

        return self._request('network', {'network': network}, 'GET')

    def get_next(self, network, n=1):

        ''' Get available IP Addresses on a given subnet '''

        try:
            return self._request(
                self.get_network(network)[0]['_ref'] +
                '?_function=next_available_ip',
                {'num': n}, 'POST'
            )
        except IndexError:
            raise Exception('Unable to retrieve next available IP \
                            address for {0}'.format(network))

    def create_record(self, record_type, record, data, comment):

        ''' Creates a new record '''

        _options = {'A': {'name': record,
                          'ipv4addr': data},
                    'AAAA': {'name': record,
                             'ipv6addr': data},
                    'CNAME': {'name': record,
                              'canonical': data},
                    'HOST': {'name': record,
                             'ipv4addrs': [{'ipv4addr': data}],
                             'comment': comment},
                    'PTR': {'name': record,
                            'ipv4addr': data,
                            'ptrdname': record},
                    'TXT': {'name': record,
                            'text': data}}

        if record_type in self._RECORDS:
            return self._request('record:' + record_type.lower(),
                                 _options[record_type.upper()], 'POST')
        else:
            raise Exception('Unsupported record type {0}'.format(record_type))

    def delete_record(self, record, record_type):

        ref = self.get_record(record, record_type)

        if ref:
            return self._request(ref[0]['_ref'], {}, 'DELETE')
        else:
            raise Exception('Unable to delete {0}'.format(record))
