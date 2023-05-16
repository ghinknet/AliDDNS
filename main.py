import re
import time
import json
import threading

import requests

from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest

class AliDDNS(object):
    def __init__(self,
                 domain, record, 
                 id, secret,
                 sleep = 600,
                 ipv4 = True, ipv6 = True,
                 v4api = "http://ipv4.ipv6-test.ch/ip/",
                 v6api = "http://ipv6.ipv6-test.ch/ip"):
    
        assert domain.count(".") == 1 and \
               not domain.startswith(".") and \
               not domain.endswith(".")

        self.domain = domain
        self.record = record
        self.sleep = sleep
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.v4api = v4api
        self.v6api = v6api
        self.v4re = re.compile(r"(((\d{1,2})|(1\d{2})|(2[0-4]\d)|(25[0-5]))\.){3}((\d{1,2})|(1\d{2})|(2[0-4]\d)|(25[0-5]))")
        self.v6re = re.compile(r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))")

        self.__client = AcsClient(id, secret, 'cn-hangzhou')

        daemon = threading.Thread(target=self.__daemon, name="Daemon Thread")
        daemon.daemon = True
        daemon.start()

    def __daemon(self):
        while True:
            self.refresh()
            time.sleep(self.sleep)

    def refresh(self):
        # Get local public ipv4 address
        if self.ipv4:
            try:
                self.__v4 = re.search(self.v4re, requests.get(self.v4api).text).group(0)
            except Exception as e: 
                print("Failed to get local public ipv4 address,", e)
            else:
                print("Your ipv4 address is:", self.__v4)

                try:
                    describe_v4 = DescribeDomainRecordsRequest()
                    describe_v4.set_accept_format('json')

                    describe_v4.set_DomainName(self.domain)
                    describe_v4.set_RRKeyWord(self.record)
                    describe_v4.set_TypeKeyWord("A")

                    describeback_v4 = self.__client.do_action_with_exception(describe_v4)

                    recordlist_v4 = json.loads(describeback_v4)
                    recordid_v4 = recordlist_v4['DomainRecords']['Record'][0]['RecordId']
                    value_v4 = recordlist_v4['DomainRecords']['Record'][0]['Value']

                    if value_v4 != self.__v4:
                        print('Your ipv4 address has been changed, update now.')
                        update_v4 = UpdateDomainRecordRequest()
                        update_v4.set_accept_format('json')

                        update_v4.set_RecordId(recordid_v4)
                        update_v4.set_Value(self.__v4)
                        update_v4.set_Type("A")
                        update_v4.set_RR(self.record)

                        self.__client.do_action_with_exception(update_v4)
                        print('Your ipv4 record has been updated successfully.')
                except Exception as e: 
                    print("Failed to update your ipv4 record,", e)

        
        # Get local public ipv6 address
        if self.ipv6:
            try:
                self.__v6 = re.search(self.v6re, requests.get(self.v6api).text).group(0)
            except Exception as e: 
                print("Failed to get local public ipv6 address,", e)
            else:
                print("Your ipv6 address is:", self.__v6)

                try:
                    describe_v6 = DescribeDomainRecordsRequest()
                    describe_v6.set_accept_format('json')

                    describe_v6.set_DomainName(self.domain)
                    describe_v6.set_RRKeyWord(self.record)
                    describe_v6.set_TypeKeyWord("AAAA")

                    describeback_v6 = self.__client.do_action_with_exception(describe_v6)

                    recordlist_v6 = json.loads(describeback_v6)
                    recordid_v6 = recordlist_v6['DomainRecords']['Record'][0]['RecordId']
                    value_v6 = recordlist_v6['DomainRecords']['Record'][0]['Value']

                    if value_v6 != self.__v6:
                        print('Your ipv6 address has been changed, update now.')
                        update_v6 = UpdateDomainRecordRequest()
                        update_v6.set_accept_format('json')

                        update_v6.set_RecordId(recordid_v6)
                        update_v6.set_Value(self.__v6)
                        update_v6.set_Type("AAAA")
                        update_v6.set_RR(self.record)

                        self.__client.do_action_with_exception(update_v6)
                        print('Your ipv6 record has been updated successfully.')
                except Exception as e: 
                    print("Failed to update your ipv6 record,", e)
            
if __name__ == "__main__":
    dns = AliDDNS("MainDomain.com", "SubDomain", "AccessKey ID", "AccessKey Secret")
    
    while True:
        cmd = input()
        if cmd == "exit":
            break
        elif cmd == "refresh":
            dns.refresh()
        else:
            print("Unknown command.")
        