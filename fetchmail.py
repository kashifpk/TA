#!/usr/bin/python3

import email
import imaplib
import getpass
import sys
from config import email_id, assignments_folder

class Mailbox(object):
    
    def __init__(self, email_id, password, server='imap.gmail.com'):
        self.mbox = imaplib.IMAP4_SSL(server)
        self.mbox.login(email_id, password)
    
    def select(self, folder_name):
        self.mbox.select(folder_name)
    
    def fetch_messages(self, unread=True):
        search_str = "ALL"
        if unread:
            search_str = "(UNSEEN)"
        
        result, data = self.mbox.uid('search', None, search_str)
        #print(result)
        #print(data)
        email_ids = data[0].split()
        #print(email_ids)
        latest_email_uid = email_ids[-1]
        result, data = self.mbox.uid('fetch', latest_email_uid, '(RFC822)')
        print(data)
        raw_email = data[0][1]
        email_message = email.message_from_string(raw_email)
        print(email_message)
        print(dir(email_message))

if '__main__' == __name__:
    password = getpass.getpass("Enter password for %s: " % email_id)
    M = Mailbox(email_id, password)
    M.select(assignments_folder)
    M.fetch_messages()
    