import  sys
import  datetime as d
import  os
import  logging
import  time
import  re
import  pandas as pd
import  smtplib
from    email.message import EmailMessage
from    email.mime.multipart import MIMEMultipart
from    email.headerregistry import Address
import  mimetypes
from    email.mime.audio import MIMEAudio
from    email.mime.base import MIMEBase
from    email.mime.image import MIMEImage
from    email.mime.text import MIMEText
from    email import encoders
from    dictionary_list import mfr_table
from    config import *
from    sqlalchemy import create_engine
from    sqlalchemy import types as clm_type
import  numpy as np


def send_email(subject,content,to,files):
    msg = MIMEMultipart()
    #msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = "do_not_reply@insight.com" #Address("Do Not Reply", "do_not_reply", "insight.com")
    msg['To'] =   to
    msg.attach(MIMEText(content))
    if files is not None:
        for f in files:
            a=attachment(f)
            msg.attach(a)
    s = smtplib.SMTP('mailna.insight.com')
    s.send_message(msg)
    s.quit()
    return 

def attachment(fileToSend):
    fn=os.path.basename(fileToSend)
    type = mimetypes.guess_type(fileToSend)
    ctype=type[0] if type[0] is not None else "application/octet-stream"
    encoding =type[1]

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fn)

    return attachment

def push(table,stg_table,store_procedure):
    #Update parts table
    table.to_sql(con=engine,if_exists="replace",schema="pm_na",index=False,name=stg_table,chunksize=100)
    connection = engine.raw_connection()
    
    if  store_procedure: 
        #close connection stored proc fails
        try:
            cursor = connection.cursor()
            cursor.execute(store_procedure)          
            cursor.close()
            connection.commit()
        finally:
            connection.close()

    return

def runCTO():
    
    to = 'yunior.rosellruiz@insight.com'
    try:

        for s in mfr_table:
            mfr_id = mfr_table.get(s)
            connection = engine.connect()
            trans = connection.begin() 
            if mfr_id['cto_flag']==True:
                    #stored procedure to update prod table
                    query=mfr_id['cto_str_proc'].replace("'","''")                
                    store_procedure ="EXEC [dbo].[pm_categories] @query={q}".format(q="'"+ query +"'")                
                    try:
                        #cursor = connection.cursor()
                        connection.execute(store_procedure) 
                        trans.commit()
                        connection.close()

                    except Exception as e:
                        logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
                        logging.warning(str(e))
                        content = "Something went wrong when running the daily PM CTO scripts for {s} \n{e}".format(e=str(e),s=s)
                        subject = "Error: Daily PM CTO Partner"       
                        send_email(subject,content,to,None)
                    finally:
                        #close connection stored proc fails
                        connection.close()
    except Exception as e:
        logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
        logging.warning(str(e))
        content = "Something went wrong when running the daily PM CTO scripts\n {e}".format(e=str(e))
        subject = "Error: Daily PM CTO"       
        send_email(subject,content,to,None)

    content = "Success!"
    subject = "Success: Daily PM CTO "
    send_email(subject,content,to,None)

    return

def main():
    #if len(sys.argv)>1:
    subject=sys.argv[2] 
    files=sys.argv[4] 
    sender=sys.argv[6]
    #to="yunior.rosellruiz@insight.com"
    #send_email("FILES Mapping",files,to,None)
    #else:
    #    mfr_id=sys.argv[0] 

    ####testing
    #subject="mapping=standard"
    #files='pm_categories_stnd.xlsx'
    #sender='yunior.rosellruiz@insight.com'
    mp_rgx=re.search("mapping\s?=\s?(.+)",subject,re.RegexFlag.IGNORECASE) 
    mapping= mp_rgx.group(1) if mp_rgx else None
    to = sender

    
    for f in files.strip().replace(' ','').split(","): 

        if not mapping:
            subject="Check mapping in subject line. Sample mapping=standard "
            content="Error"
            send_email(subject,content,to,None)
            break

        try:           
                parts=pd.read_excel(f,'parts',index_col=False).astype(str)
                parts=parts.replace('nan',np.nan)
                parts['sender']=sender
                parts['append_date']= d.datetime.now()
        
                stg_table = "pm_categories_stg" if mapping=="standard" else "pm_categories_comp_stg" if mapping=="component" else None
                store_procedure="EXEC [dbo].[pm_categories]" if mapping=="standard" else None 

                #pushes parts from stg to prd
                push(parts,stg_table,store_procedure)

                mfr_ids= parts['mfr_id'].unique() if mapping=="standard" else parts['Component_mfr_id'].unique() if mapping=="component" else None

                for mfr_id in mfr_ids: 
            
                    sr_table=mfr_table.get(mfr_id)

                    if sr_table and sr_table['cto_flag']:
                        connection = engine.raw_connection()

                        #stored procedure to update prod table
                        query=sr_table['cto_str_proc'].replace("'","''") if mapping=="standard" else sr_table['cto_str_proc']
                
                        store_procedure ="EXEC [dbo].[pm_categories] @query={q}".format(q="'"+ query +"'" if query else "NULL") if mapping=="standard" else query if mapping=="component" else None                
                        try:
                            cursor = connection.cursor()
                            cursor.execute(store_procedure)          
                            cursor.close()
                            connection.commit()
                        finally:
                            #close connection stored proc fails
                            connection.close()


                content = "Success!"
                subject = "Partner Categories\n FILE:{_f}".format(_f=f)
                to= sender
                send_email(subject,content,to,None)
                    
        except Exception as e:
            logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
            logging.warning(str(e))
            content = "Something went wrong please reach out to the BI Team\n{e}".format(e=str(e))
            subject = "Error"
            send_email(subject,content,to,None)

    return

if __name__ == '__main__':
    if len(sys.argv)>1 :
        main()
    else:
        runCTO()


