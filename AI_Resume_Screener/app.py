from flask import Flask, render_template, request
import spacy
from PyPDF2 import PdfReader
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


nlp = spacy.load("en_core_web_md")


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def calculate_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)


@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    if request.method == 'POST':
        job_description = request.form['job_description']
        uploaded_files = request.files.getlist('resumes')

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        for file in uploaded_files:
            if file and file.filename.endswith('.pdf'):
                path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(path)

                resume_text = extract_text_from_pdf(path)
                score = calculate_similarity(job_description, resume_text)

            
                status = "Selected" if score >= 0.75 else "Rejected"

                results.append({
                    "filename": file.filename,
                    "score": round(score * 100, 2),
                    "status": status
                })

        # Sort resumes by highest score
        results.sort(key=lambda x: x['score'], reverse=True)

    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)

