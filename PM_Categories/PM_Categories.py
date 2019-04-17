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
from  dictionary_list import sr_tables
from    config import *
from    sqlalchemy import create_engine

stg_table="pm_categories_stg"

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

def push(table):
        #Update parts table
    table.to_sql(con=engine,if_exists="replace",schema="pm_na",index=False,name=stg_table)

    #stored procedure to update prod table
    store_procedure="EXEC [dbo].[pm_categories]"

    connection = engine.raw_connection()
        
    #close connection stored proc fails
    try:
        cursor = connection.cursor()
        cursor.execute(store_procedure)          
        cursor.close()
        connection.commit()
    finally:
        connection.close()

    return

def main():
            #if len(sys.argv)>1:
    subject=sys.argv[2] 
    files=sys.argv[4] 
    sender=sys.argv[6]
    #else:
    #    sr_soldto=sys.argv[0] 

    ####testing
    #subject="None"
    #files='pm_categories.xlsx'
    #sender='yunior.rosellruiz@insight.com'
   

    try:
        parts=pd.read_excel(files,'parts',index_col=False).astype(str) 
        parts['sender']=sender
        parts['append_date']= d.datetime.now()  
        push(parts)

        sr_soldtos= parts['sr_soldto'].unique()

        for sr_soldto in sr_soldtos: 
            
            sr_table=sr_tables.get(sr_soldto)

            if sr_table and sr_table['cto_flag']:
                connection = engine.raw_connection()

                #stored procedure to update prod table
                query=sr_table['cto_str_proc'].replace("'","''")
                
                store_procedure ="EXEC [dbo].[pm_categories_sp] @sr_soldto = N'{s}', @query = N'{q}'".format(s=sr_soldto,q=query)                                
                try:
                    cursor = connection.cursor()
                    cursor.execute(store_procedure)          
                    cursor.close()
                    connection.commit()
                finally:
                    #close connection stored proc fails
                    connection.close()
 
        content = "The parts have been updated!"
        subject = "Partner Categories"
        to= sender
        send_email(subject,content,to,None)
                    
    except Exception as e:
        logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
        logging.warning(str(e))
        content = "Something went wrong please reach out to the BI Team\n{e}".format(e=str(e))
        subject = "Error"
        to = sender
        send_email(subject,content,to,None)

    return

if __name__ == '__main__':
    main()


