from flask import Flask, request, redirect
from twilio import twiml
from twilio.rest import TwilioRestClient
import wikipedia
import wikia

ACC_SID = "AC6f6a9dd829c0b0ac45030ba3b0d5a05d"#CHECK YOUR LIVE ACC_SID
AUTH_TOKEN = "670a2fb01d2361e03f330c7265cdd18e"#CHECK YOUR LIVE AUTH_TOKEN
PHONE_NUMBER = "+4697700002" #YOUR NUMBER

ERROR = "Ambiguous query. Please use the search command if you cannot find your query."

app = Flask(__name__)

#Please don't kill me for this
resp = twiml.Response()

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
            message = ERROR
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
    elif( context.lower() == "full" ):
        try:
            message = wikipedia.page(query).content
        except:
            message = ERROR
    elif( context.lower() == "image" ):
        try:
            x = ""
            img_list = wikipedia.page(query).images
            # Removing first letter to remove capital because wikipedia
            # is anal about uppercase and lowercase
            for i, x in enumerate(img_list):
                if query[1:] in x:
                    break
            if x == "":
                message = "Image could not be found."
            else:
                resp.message().media(x)
        except:
            ERROR
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
    elif( context.lower() == "full" ):
        try:
            message = wikia.page(wiki, query).content
        except:
            message = ERROR
    elif( context.lower() == "image" ):
        try:
            x = ""
            img_list = wikipedia.page(query).images
            # Removing first letter to remove capital because wikipedia
            # is anal about uppercase and lowercase
            for i, x in enumerate(img_list):
                if query[1:] in x:
                    break
            if x == "":
                message = "Image could not be found."
            else:
                resp.message().media(x)
        except:
            ERROR
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

    if( context.lower() == "image"):
        return str(resp)

    #client = TwilioRestClient(ACC_SID, AUTH_TOKEN)
    # Cuts messages so that they don't exceel twilio MMS 1600 character limit.
    i = 0
    while( len(message) > 1280 ):
        # 1280 is 160 (max SMS message) times 8.
        client = TwilioRestClient(ACC_SID, AUTH_TOKEN)
        sms = client.messages.create(
            to=request.values.get('From', None), 
            from_=PHONE_NUMBER, 
            body=message[:1280]+ "\n PAGE: " + str(i+1), 
        )
        message = message[1280:]
        print(str(i+1))
        i+=1#time.sleep(60)
    print("Returning")
    if (i > 0):
        message += "\n LAST PAGE"
    resp.message(message)    
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
