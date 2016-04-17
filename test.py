from flask import Flask, request, redirect
import twilio.twiml
from twilio.rest import TwilioRestClient
import wikipedia
import wikia
import requests
import time

ACC_SID = "AC7012eb334ad3587d202faede0290ccc3"
AUTH_TOKEN = "b787bc83f51ce068eaf36046866993c8"
PHONE_NUMBER "+15005550006"

ERROR = "Ambiguous query. Please use the search command if you cannot find your query."

app = Flask(__name__)

# Named oddly so that functions don't conflict
def wiki_pedia(context, query):
    # Initialize
    message = ""
    
    if( context.lower() == "search" ):
        message = ",  \n".join(wikipedia.search(query))
    elif( context.lower() == "summary" ):
        try:
            message = wikipedia.summary(query)
        except:
            message = ERROR
    elif( context.lower() == "toc" ):
        try:
            sec_list = wikipedia.page(query).sections
            # Throws together a list of numbered sections for section use below
            message = sec_list[0] + " (1)"
            x = 1
            for i, x in enumerate(sec_list[1:]):
                message += ",  \n" + x + " (" + str(i+2) + ")"
        except:
            message = "poop"
    elif( context.lower() == "section" ):
        try:
            # Uses the secton number to return query
            sec_list = wikipedia.page(query).sections
            store = query.split(" ",1)
            sec_num = int(store[0])
            query = store[1]
            message = wikipedia.page(query).section(sec_list[sec_num])
        except:
            message = ERROR
    elif( context.lower() == "content" ):
        try:
            message = wikipedia.page(query).content
        except:
            message = ERROR
    elif( context.lower() == "url" ):
        try:
            message = wikipedia.page(query).url
        except:
            message = ERROR
    else:
        message = "Invalid context. Type '?' for help."
        
    return message

def wiki_a(wiki, context, query):
    # Initialize
    message = ""
    
    if( context.lower() == "search" ):
        message = ",  \n".join(wikia.search(wiki, query))
    elif( context.lower() == "summary" ):
        try:
            message = wikia.summary(wiki, query)
        except:
            message = ERROR
    elif( context.lower() == "toc" ):
        try:
            sec_list = wikia.page(wiki, query).sections
            # Throws together a list of numbered sections for section use below
            message = sec_list[0] + " (1)"
            x = 1
            for i, x in enumerate(sec_list[1:]):
                message += ",  \n" + x + " (" + str(i+2) + ")"
        except:
            message = ERROR
    elif( context.lower() == "section" ):
        try:
            # Uses the secton number to return query
            sec_list = wikipedia.page(query).sections
            store = query.split(" ",1)
            sec_num = int(store[0])
            query = store[1]
            message = wikipedia.page(query).section(sec_list[sec_num])
            if( message == NONE ):
                # This will happen often because the API is pretty shit
                message = "Unable to grab the section text."
        except:
            message = ERROR
    elif( context.lower() == "content" ):
        try:
            message = wikia.page(wiki, query).content
        except:
            message = ERROR
    elif( context.lower() == "url" ):
        try:
            message = wikia.page(wiki, query).url
        except:
            message = ERROR
    else:
        message = "Invalid context. Type '?' for help."
        
    return message
 
@app.route("/", methods=['GET', 'POST'])
def get_wiki():
    sent_message = request.values.get('Body', None)
    resp = twilio.twiml.Response()

    # Initialize
    args = sent_message.split(" ",2);
    wiki = args[0]
    context = ""
    query = ""
    message = ""

    # If the user only types one word, this catches it and won't break the script
    if( len(args) > 1 ):
        context = args[1]
        if( len(args) > 2 ):
            query = args[2]
            

    # Dummy-free if statement
    # ? is used instead of help because the twilio trial doesn't allow access to help
    if( sent_message.lower() == "?" or sent_message.lower() == "'?'" ):
        message = """To search wikis, enter one of the following commands:
  'wiki' search 'query',
  'wiki' summary 'query',
  'wiki' toc 'query',
  'wiki' section 'toc' 'query',
  'wiki' full 'query',
  'wiki' url 'query'. 
'wiki' is the wiki you are searching in, for example wikipedia or marvel. 
'query' is the string you are searching for.
'toc' is the specific table of contents to read.
Please note that text over 1000 characters will be split into multiple messages. Sections are case-sensitive."""
    elif( wiki.lower() == "wikipedia" ):
        message = wiki_pedia(context, query)
    else:
        try:
            # Now this is what I call a true hack. This will check to see if a wiki exists
            # by searching for the common letter 'e'. If it cannot find it, then it is very
            # likely that the wikia either does not exist or is so small it's irrevelant.
            # There may be an edge case where a wikia purposefully never uses the letter 'e'.
            wikia.search(wiki, "e")
            
            message = wiki_a(wiki, context, query)
        except:
            message = "Invalid wiki. Type '?' for help."

    # Cuts messages so that they don't exceel twilio MMS 1600 character limit.
    while( len(message) != 0 ):
        # 1280 is 160 (max SMS message) times 8.
        resp.message(message[:1280])
        message = message[1280:]
    client = TwilioRestClient(ACC_SID, AUTH_TOKEN)
    
    sms = client.messages.create(
    to=request.values.get('From', None), 
    from_=PHONE_NUMBER, 
    body="testing", 
    )
    print(sms.sid)
    time.sleep(1)

    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
