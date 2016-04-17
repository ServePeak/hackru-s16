from flask import Flask, request, redirect
import twilio.twiml
import wikipedia
import wikia

ERROR = "Ambiguous query. Please use the search command."


app = Flask(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def get_wiki():
    sent_message = request.values.get('Body', None)
    resp = twilio.twiml.Response()

    #Initialize
    args = sent_message.split(" ",1);
    context = args[0]
    query = ""
    message = ""

    #If the user only types one word, this catches it and won't break the script
    if( len(args) != 1 ):
        query = args[1]

    #Dummy-free if statement
    if( sent_message.lower() == "?" or sent_message.lower() == "'?'" ):
        message = """To search on wikipedia, enter one of the following commands:
  search 'query',
  summary 'query',
  toc 'query',
  section 'query',
  full 'query',
  url 'query'.
Please note that text over 1000 characters will be split into multiple messages. Sections are case-sensitive."""
    elif( context.lower() == "search" ):
        message = ",  \n".join(wikipedia.search(query))
    elif( context.lower() == "summary" ):
        try:
            message = wikipedia.summary(query)
        except:
            message = ERROR
    elif( context.lower() == "toc" ):
        try:
            message = ",  \n".join(wikipedia.page(query).sections)
        except:
            message = ERROR
    elif( context.lower() == "section" ):
        try:
            store = query.split(" ",1)
            section = store[0]
            query = store[1]
            message = wikipedia.page(query).section(section)
        except:
            message = ERROR
    elif( context.lower() == "full" ):
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
        message = "Invalid query. Type '?' for help."

    while( len(message) != 0 ):
        #1280 is 160 (max SMS message) times 8. Maximum size of a twilio MMS is 1600 characters.
        resp.message(message[:1280])
        message = message[1280:]
 
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
