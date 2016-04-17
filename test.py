from flask import Flask, request, redirect
import twilio.twiml
import wikipedia
 
app = Flask(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def get_wiki():
    """Respond and greet the caller by name."""
    sent_message = request.values.get('Body', None)
    args = sent_message.split(" ",1);
    if (args[0].lower() == "search"):
        result = wikipedia.search(args[1])
        message = '\n'.join(result)
    #need to send over 150chars
    elif (args[0].lower() == "content"):
        message = wikipedia.page(args[1]).content
    elif (args[0].lower() == "url"):
        page = wikipedia.page(args[1])
        message = page.url
    else:
        #default sends back summary of the search
		message = wikipedia.summary(sent_message)
	
	#message to send back
    #message = wiki.url
    
    resp = twilio.twiml.Response()
    resp.message(message)
 
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
