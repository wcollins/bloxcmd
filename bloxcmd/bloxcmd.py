# -*- coding: utf-8 -*-

from sys import argv
from sys import exit
from time import strftime
from csv import reader
from os.path import expanduser
from .ipam import IPAM

def session():

    ''' Resource for InfoBlox IPAM REST requests '''

    login = './bloxcmd/auth'

    with open(login, 'r') as f:
        for line in f.readlines():
            data = line.strip().split(':')
            hostname = data[0]
            version = data[1]
            username = data[2]
            password = data[3]
            url = 'https://%s' % hostname

            ipam = IPAM(url,
                        username,
                        password,
                        version)

            return ipam

def get_next(s, subnet, number):

    ''' Get a list of available IPs on a given subnet '''

    print 'Getting next %s IPs from %s' % (number, subnet)

    # build ip list
    ip_list = s.get_next(subnet, number)

    # loop through ip list
    for ip in ip_list['ips']:
        print ip

def create_host(s):

    ''' Create a new host record '''

    # record type
    record_type = 'HOST'

    # hostname
    name = raw_input('Hostname - e.g. host1.domain.com: ')
    hostname = name.lower()

    # ip address
    ipaddr = raw_input('IP Address: ')

    # comment
    comment = raw_input('Comment: ')

    try:
        s.create_record(record_type, hostname, ipaddr, comment)

    except Exception, e:
        print e

    else:
        entry = 'post,%s,%s,%s' % (hostname, ipaddr, comment)
        log(entry, comment)
        print entry

def delete_host(s):

    ''' Delete a given host record '''

    # record type
    record_type = 'host'

    # hostname
    name = raw_input('Hostname - e.g. host1.domain.com: ')
    hostname = name.lower()

    # comment
    comment = raw_input('Comment: ')

    try:
        s.delete_record(hostname, record_type)

    except Exception, e:
        print e

    else:
        entry = 'delete,%s,%s' % (hostname, comment)
        log(entry, comment)
        print entry

def bulk_post(post_csv):

    d = post_csv

    # loop through data
    with open(d, 'r') as in_data:
        data = reader(in_data)
        next(data, None)
        for row in data:
            d = row
            s = session()
            record_type = 'HOST'
            hostname = d[0].lower() + '.' + d[1]
            ipaddr = d[2]
            comment = d[3]

            try:
                s.create_record(record_type, hostname, ipaddr, comment)

            except Exception, e:
                print e

            else:
                entry = 'post,%s,%s,%s' % (hostname, ipaddr, comment)
                log(entry, comment)
                print entry

def bulk_delete(delete_csv):

    d = delete_csv

    # loop through data
    with open(d, 'r') as in_data:
        data = reader(in_data)
        next(data, None)
        for row in data:
            d = row
            s = session()
            record_type = 'host'
            hostname = d[0].lower() + '.' + d[1]
            comment = d[3]

            try:
                s.delete_record(hostname, record_type)

            except Exception, e:
                print e

            else:
                entry = 'delete,%s,%s' % (hostname, comment)
                log(entry, comment)
                print entry

def log(entry, comment):

    ''' Log all changes to ~/Engineering/changes/ '''

    change_dir = expanduser('~/engineering/changes/%s_%s') % (date(), comment)
    change_file = open(change_dir, 'a')

    # append change to file
    print>>change_file, entry

def date():

    ''' Date - ISO 8601 - (YYY-MM-DD) '''

    current_date = (strftime("%Y-%m-%d"))

    return current_date


def main():

    a = argv[1:]
    option = a[0]
    s = session()

    if option == 'get':

        if a[1] == '-a':
            subnet = a[2]
            number = int(a[3])
            get_next(s, subnet, number)

    elif option == 'post':

        if a[1] == '-h':
            create_host(s)

    elif option == 'delete':

        if a[1] == '-h':
            delete_host(s)

    elif option == 'bulk':
        kind = raw_input('Type - post/delete: ')
        
        if kind == 'post':
            post_csv = a[1]
            bulk_post(post_csv)

        elif kind == 'delete':
            delete_csv = a[1]
            bulk_delete(delete_csv)
