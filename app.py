from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch

app = Flask(__name__)
CORS(app)

# Variable to store the text input
saved_text = ""

# Load Pegasus model and tokenizer
torch_device = 'cpu'
save_directory = './pegasus_model'  # Ensure this path is correct
tokenizer = PegasusTokenizer.from_pretrained(save_directory, local_files_only=True)
model = PegasusForConditionalGeneration.from_pretrained(save_directory, local_files_only=True).to(torch_device)

@app.route('/save', methods=['POST'])
def save_text():
    global saved_text
    data = request.json
    if 'text' not in data:
        return jsonify({"error": "No text field provided"}), 400
    saved_text = data.get('text', '')
    return jsonify({"message": "Text saved successfully!", "saved_text": saved_text}), 200

@app.route('/get', methods=['GET'])
def get_text():
    return jsonify({"saved_text": saved_text}), 200

@app.route('/summarize', methods=['GET'])
def summarize_text():
    global saved_text
    if not saved_text:
        return jsonify({"error": "No text has been saved yet"}), 400

    src_text = [saved_text]
    batch = tokenizer(src_text, truncation=True, padding='longest', return_tensors="pt")

    translated = model.generate(**batch, max_length=300, min_length=100, num_beams=5, length_penalty=1.0)

    tgt_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    cleaned_text = tgt_text.replace('<n>', '').strip()

    return jsonify({"summarized_text": cleaned_text}), 200

if __name__ == '__main__':
    app.run(debug=True)
