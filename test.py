from flask import Flask, request, redirect
import twilio.twiml
import wikipedia
 
app = Flask(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def get_wiki():
    """Respond and greet the caller by name."""

    sent_message = request.values.get('Body', None)
    wiki = wikipedia.page(sent_message)
    message = wiki.url
    
    resp = twilio.twiml.Response()
    resp.message(message)
 
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
