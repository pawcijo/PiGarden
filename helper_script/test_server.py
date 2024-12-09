from flask import Flask, render_template
import time

app = Flask(__name__)

def generate_data():
    while True:
        yield f"data: {time.time()}\n\n"
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def events():
    return app.response_class(generate_data(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
