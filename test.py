from flask import Flask, request, redirect
import twilio.twiml
import wikipedia
 
app = Flask(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def get_wiki():
    sent_message = request.values.get('Body', None)
    resp = twilio.twiml.Response()
    
    args = sent_message.split(" ",1);
    context = args[0]
    query = ""
    message = ""
    if( len(args) != 1 ):
        query = args[1]

    if( sent_message.lower() == "?" or sent_message.lower() == "'?'" ):
        message = """To search on wikipedia, enter one of the following commands:
  search 'query',
  summary 'query',
  content 'query',
  url 'query'.
Please note that text over 1000 characters will be split into multiple messages."""
    elif( context.lower() == "search" ):
        message = wikipedia.search(query)
    elif( context.lower() == "summary" ):
        message = wikipedia.summary(query)
    elif( context.lower() == "content" ):
        message = wikipedia.page(query).content
    elif( context.lower() == "url" ):
        message = wikipedia.page(query).url
    else:
        message = "Invalid query. Type '?' for help."

    while( len(message) != 0 ):
        resp.message(message[:1000])
        message = message[1000:]
 
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
