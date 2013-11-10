#!/usr/bin/python

import email
from email.parser import HeaderParser
import imaplib
import mimetypes
import getpass
import sys
import os
from config import email_id, assignments_folder

class Mailbox(object):
    
    def __init__(self, email_id, password, server='imap.gmail.com'):
        self.mbox = imaplib.IMAP4_SSL(server)
        self.mbox.login(email_id, password)
        self.header_parser = HeaderParser()
    
    def select(self, folder_name):
        self.mbox.select(folder_name)
    
    def print_headers(self, msg_part):
        print(msg_part)
        for item in msg_part.items():
            print(item[0], item[1])

    def fetch_messages(self, folder, unread=True):
        search_str = "ALL"
        if unread:
            search_str = "(UNSEEN)"
        
        result, data = self.mbox.uid('search', None, search_str)
        email_ids = data[0].split()
        
        i = 1
        for email_id in email_ids:
            result, data = self.mbox.uid('fetch', email_id, '(RFC822)')
            
            raw_email = data[0][1]
            email_message = email.message_from_string(str(raw_email))
            headers = self.header_parser.parsestr(raw_email)
            
            #print(email_message.is_multipart())
            payloads = email_message.get_payload()
            save_folder = os.path.join(folder, email_id)
            
            print("Saving email received from: " + headers['From'])
            self.save(email_message, headers, save_folder)
    
    def save(self, msg, headers, folder):
        
        if not os.path.exists(folder):
            os.mkdir(folder)

        email_text = "Subject: {e_subject}\nFrom: {e_from}\nDate: {e_date}\n\n".format(
            e_subject=headers['Subject'],
            e_from=headers['From'],
            e_date=headers['Date']
        )
        
        for part in msg.walk():
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                continue
            # Applications should really sanitize the given filename so that an
            # email message can't be used to overwrite important files
            filename = part.get_filename()
            #print("Filename " + str(filename))
            if not filename:
                ext = mimetypes.guess_extension(part.get_content_type())
                #print(ext)
                if '.ksh' == ext:
                    email_text += part.get_payload(decode=True)
                    #print(part.get_payload(decode=True))
            else:
                fp = open(os.path.join(folder, filename), 'wb')
                fp.write(part.get_payload(decode=True).strip())
                fp.close()
        
        open(os.path.join(folder, '_email.txt'), 'wb').write(email_text)


if '__main__' == __name__:
    
    if len(sys.argv) != 2:
        print("Usage:\n\n\t %s email_save_folder" % sys.argv[0])
        sys.exit()

    password = getpass.getpass("Enter password for %s: " % email_id)
    M = Mailbox(email_id, password)
    M.select(assignments_folder)
    M.fetch_messages(folder=sys.argv[1])
    