from flask import Flask, request, jsonify

app = Flask(__name__)

# Variable to store the text input
saved_text = ""

@app.route('/save', methods=['POST'])
def save_text():
    global saved_text
    data = request.json  # Get JSON data from request
    saved_text = data.get('text', '')  # Extract 'text' from JSON
    return jsonify({"message": "Text saved successfully!", "saved_text": saved_text}), 200

@app.route('/get', methods=['GET'])
def get_text():
    return jsonify({"saved_text": saved_text}), 200

if __name__ == '__main__':
    app.run(debug=True)