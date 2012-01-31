#!/usr/local/bin/python
'''
Created on Jan 22, 2010

@author: rgs
'''

import os
import time
import string

dbInstances = ['PRODDB','XYTHOSD','XYTHOSP']

log_files = {
'PRODDB':'/d01/app/oracle/admin/proddb/bdump/alert_proddb.log',
'XYTHOSD':'/oracle/diag/rdbms/xythosd/xythosd/trace/alert_xythosd.log',
'XYTHOSP':'/oracle/diag/rdbms/xythosp/xythosp/trace/alert_xythosp.log'
}

temp_files = {
'PRODDB':'/d01/app/oracle/admin/proddb/bdump/alert_proddb.tmp',
'XYTHOSD':'/oracle/diag/rdbms/xythosd/xythosd/log_archive/alert_xythosd.tmp',
'XYTHOSP':'/oracle/diag/rdbms/xythosp/xythosp/log_archive/alert_xythosp.tmp'
}

archive_files = {
'PRODDB':'/d01/app/oracle/admin/proddb/bdump/alert_proddb.arc',
'XYTHOSD':'/oracle/diag/rdbms/xythosd/xythosd/log_archive/alert_xythosd.arc',
'XYTHOSP':'/oracle/diag/rdbms/xythosp/xythosp/log_archive/alert_xythosp.arc'
}

#log_files = {'PRODDB':'/app/oracle/admin/scripts/test/alert_proddb.log'}
#temp_files = {'PRODDB':'/app/oracle/admin/scripts/test/alert_proddb.tmp'}
#archive_files = {'PRODDB':'/app/oracle/admin/scripts/test/alert_proddb.arc'}

# Email Variables
To = ['stauffer@swarthmore.edu']
From = 'oracle@swarthmore.edu'
Server = 'smtp.swarthmore.edu'
Subject = 'Errors in %s Alert Log'

def checklogs(db):
    process_files(db)
    errors, trace_file_list = process_errors(db)
    if errors <> '':
#        attach_list = process_attachments(trace_file_list)
        attach_list = [] 
        mail(To, From, Server, Subject % db, errors, attach_list)
#    else:
#        print "No Errors Found for %s" % db

def process_attachments(file_list):
    import gzip
    compressed_file_list = []
    for file in file_list:
	try:
            filename = file[file.index('/'):file.index(':')]
            zipfile = filename + '.gz'
            file_in = open(filename,'rb')
            file_out = gzip.open(zipfile,'wb')
            file_out.writelines(file_in)
            file_out.close
            file_in.close
            compressed_file_list.append(zipfile)
        except:
            pass
    return compressed_file_list
    
def mail(To,From,Server='localhost',Subject='',Message='',Attachments=[]):
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.utils import COMMASPACE, formatdate
    from email import Encoders
    
    To = ','.join(To)
    msg = MIMEMultipart()
    msg['From'] = From
    msg['To'] = To
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = Subject
    
    msg.attach(MIMEText(Message))
    
    if Attachments:
        for file in Attachments:
            part = MIMEBase('application','octet-stream')
            part.set_payload(open(file,'rb').read())
            part.add_header('Content-Disposition','attachment; filename=%s' % os.path.basename(file))
            msg.attach(part)
    
    smtp = smtplib.SMTP(Server)
    smtp.sendmail(From,To,msg.as_string())
    smtp.close()
                         
def process_errors(db):
    trace_file_list = []
    error_buffer = ''
    infile = open(temp_files[db],'r')
    for line in infile:
#	print line
        if line.startswith('Errors'):
            trace_file_list.append(line) 
            error_buffer += line
        elif line.startswith('ORA-'):
            error_buffer += line
        elif line.startswith('Linux'):
            error_buffer += line
    return error_buffer, trace_file_list    

def process_files(db):
    if os.path.exists(temp_files[db]):
        os.remove(temp_files[db])
    os.rename(log_files[db],temp_files[db])
    infile = open(temp_files[db],'r')
    outfile = open(archive_files[db],'a')
    outfile.write(infile.read())
    infile.close()
    outfile.close()

def check_logfile_exists(db_list):
    import os.path
    process_list = []
    for database in db_list:
        if os.path.exists(log_files[database]):
            process_list.append(database)
    return process_list

if __name__ == '__main__':

    process_list = check_logfile_exists(dbInstances)
    for dbname in process_list:
        checklogs(dbname)
