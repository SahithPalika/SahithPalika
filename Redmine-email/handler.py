from redminelib import Redmine
import boto3

def lambda_handler(event, context):
    get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
    s3 = boto3.client('s3')
    
    objs = s3.list_objects(Bucket='redmine-ticket-create-2')['Contents']
    length = len(objs)-1
    last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified)][length]

    file_content = s3.get_object( Bucket='redmine-ticket-create-2', Key=last_added)["Body"].read()
    content = file_content.decode('UTF-8')
    
    content_array = content.split("\n")

    lengt = len(content_array)

    
    #Finding the start line number of the description
    for lines in range(len(content_array)):
        word_one = "text/plain;"
        if word_one in content_array[lines]:
            lowercount = lines            
     
    #Finding the end line number of the description       
    for lines in range(len(content_array)):
        word_two="text/html"
        if word_two in content_array[lines]:
            uppercount=lines  
            
    # parsing the description according to the line numbers
    print('Description : \n')
    body_1 = ' '
    for i in range(lowercount+1,uppercount-1):
        body_1=body_1+content_array[i]
    print(body_1,'\n')
        
    # Findig the sender_domain  
    for lines in content_array:
        line_array = lines.split(" ")
        if line_array[0] == "Return-Path:":
            at=lines.split('@')
            if at[-1]=='bizcloudexperts.com>\r':
                sender_domain = 2
            else:
                sender_domain= 1
            print(sender_domain)
    
            
    #Finding the sender
    for lines in content_array:
        line_array = lines.split("\n")
        word="From:"
        for i in range(len(line_array)):
            if word in line_array[i]:
                sender=line_array[i]
            break
    print(sender)
    c=0
    for i in sender:
        c=c+1
        if i=='<':
            index=c
    print(index)
    to_address=sender[index:len(sender)-2]
    
                       
    #Finding the subject of the mail
    for lines in content_array:
        line_array = lines.split(" ")
        if line_array[0] == "Subject:":
            subject=' '
            for i in range(1,len(line_array)):
                subject=subject+line_array[i]+' '
            
    #addidng sender to description 
    body=body_1+"\n"+sender
            
            
    #Default Priority
    default_priority = 5
    
    redmine = Redmine('https://agiledev.bizcloudexperts.com', key='46f2b42985f276af85d8acc47e59445a4b2f1671')
    user = redmine.auth()
        
    new_ticket=redmine.issue.create(
        project_id=72,
        subject=subject,
        description=body,
        priority_id=default_priority,
        custom_fields=[{'id':1,'value':2}] )
        
    ticket_id = new_ticket.id            #ticket_id

    ticket_id=str(ticket_id)
    
    #sending email as a response
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                to_address,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": "Thanks for reaching out to Bizcloud Support Desk. We have create a ticket to follow up on the issue you raised. Please refer this ticket number when you call us for follow-ups. We will keep you posted about the progress of the ticket. \n\n Ticket number:"+ticket_id+"\n\nTitle:"+subject+"\n\nDescription:"+body_1,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Details on issue",
            },
        },
        Source="no-reply@testsupport.bizcloudexperts.com",
        )