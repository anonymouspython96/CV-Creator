
from flask import Flask, request, render_template_string, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

app = Flask(__name__)

# Codice HTML/CSS per il modulo di input
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generatore di CV</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-100 p-8 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-4xl">
        <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">Crea il tuo CV e Lettera di Presentazione</h1>
        <p class="text-gray-600 mb-8 text-center">
            Inserisci i tuoi dati qui sotto per generare un file PDF pronto all'uso.
        </p>

        <form action="/generate-cv" method="post" class="space-y-6">
            <div class="grid md:grid-cols-2 gap-6">
                <!-- Dati Personali -->
                <div>
                    <label for="personal_data" class="block text-sm font-medium text-gray-700">Dati Personali</label>
                    <textarea id="personal_data" name="personal_data" rows="4" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;📍 Via Paruzzaro, 5 – Italia&#10;📞 +39 350 8324707&#10;✉️ timofeiemilian9000@gmail.com&#10;📅 Data di nascita: 18/08/1996"></textarea>
                </div>

                <!-- Profilo -->
                <div>
                    <label for="profile" class="block text-sm font-medium text-gray-700">Profilo</label>
                    <textarea id="profile" name="profile" rows="4" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;Professionista serio e preciso, con esperienza nella gestione di attività di back office e supporto a team commerciali..."></textarea>
                </div>
            </div>

            <!-- Esperienza Professionale -->
            <div>
                <label for="experience" class="block text-sm font-medium text-gray-700">Esperienza Professionale</label>
                <textarea id="experience" name="experience" rows="5" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;Back Office Team Leader (esperienza pro bono)&#10;2017 – 2018&#10;- Coordinamento e supporto a un team di venditori..."></textarea>
            </div>

            <!-- Formazione -->
            <div>
                <label for="education" class="block text-sm font-medium text-gray-700">Formazione</label>
                <textarea id="education" name="education" rows="3" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;Diploma di Maturità in Economia e Sviluppo – ITC Germano Sommeiller, 2016"></textarea>
            </div>

            <!-- Competenze -->
            <div class="grid md:grid-cols-3 gap-6">
                <div>
                    <label for="tech_skills" class="block text-sm font-medium text-gray-700">Competenze Informatiche</label>
                    <textarea id="tech_skills" name="tech_skills" rows="3" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;Microsoft Office (Word, Excel, Outlook, PowerPoint)&#10;CRM e strumenti di gestione anagrafiche..."></textarea>
                </div>
                <div>
                    <label for="soft_skills" class="block text-sm font-medium text-gray-700">Competenze Personali</label>
                    <textarea id="soft_skills" name="soft_skills" rows="3" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;Precisione e serietà&#10;Capacità organizzative&#10;Puntualità e affidabilità..."></textarea>
                </div>
                <div>
                    <label for="languages" class="block text-sm font-medium text-gray-700">Lingue</label>
                    <textarea id="languages" name="languages" rows="3" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;Italiano – Madrelingua&#10;Inglese – C2&#10;Romeno – C2"></textarea>
                </div>
            </div>

            <!-- Lettera di Presentazione -->
            <div>
                <label for="cover_letter" class="block text-sm font-medium text-gray-700">Lettera di Presentazione</label>
                <textarea id="cover_letter" name="cover_letter" rows="8" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Es:&#10;Oggetto: Candidatura per posizione di Impiegata/o Front e Back Office – Torino&#10;&#10;Gentile Selezione Lavoropiù,..."></textarea>
            </div>
            
            <div class="flex justify-center">
                <button type="submit" class="w-full md:w-auto px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300 transform hover:scale-105">
                    Genera PDF
                </button>
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Route principale per servire il modulo di input HTML."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate-cv', methods=['POST'])
def generate_cv():
    """Route per la generazione del PDF dal testo del modulo."""
    # Ottiene i dati dal modulo
    data = {
        'personal_data': request.form.get('personal_data', ''),
        'profile': request.form.get('profile', ''),
        'experience': request.form.get('experience', ''),
        'education': request.form.get('education', ''),
        'tech_skills': request.form.get('tech_skills', ''),
        'soft_skills': request.form.get('soft_skills', ''),
        'languages': request.form.get('languages', ''),
        'cover_letter': request.form.get('cover_letter', '')
    }

    # Creazione del PDF in memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH = styles["Heading1"]
    style_section = ParagraphStyle('section', parent=styleN, spaceBefore=10, spaceAfter=4, fontSize=11, leading=14)

    # Aggiunge i contenuti al PDF se i campi non sono vuoti
    if any(data.values()):
        story.append(Paragraph("Curriculum Vitae", styleH))
        story.append(Spacer(1, 12))

    if data['personal_data']:
        story.append(Paragraph("<b>Dati personali</b>", style_section))
        story.append(Paragraph(data['personal_data'].replace('\n', '<br/>'), styleN))
        
    if data['profile']:
        story.append(Paragraph("<b>Profilo</b>", style_section))
        story.append(Paragraph(data['profile'].replace('\n', '<br/>'), styleN))

    if data['experience']:
        story.append(Paragraph("<b>Esperienza Professionale</b>", style_section))
        story.append(Paragraph(data['experience'].replace('\n', '<br/>'), styleN))

    if data['education']:
        story.append(Paragraph("<b>Formazione</b>", style_section))
        story.append(Paragraph(data['education'].replace('\n', '<br/>'), styleN))

    if data['tech_skills']:
        story.append(Paragraph("<b>Competenze Informatiche</b>", style_section))
        story.append(Paragraph(data['tech_skills'].replace('\n', '<br/>'), styleN))

    if data['soft_skills']:
        story.append(Paragraph("<b>Competenze Personali</b>", style_section))
        story.append(Paragraph(data['soft_skills'].replace('\n', '<br/>'), styleN))

    if data['languages']:
        story.append(Paragraph("<b>Lingue</b>", style_section))
        story.append(Paragraph(data['languages'].replace('\n', '<br/>'), styleN))

    # Aggiunge la lettera di presentazione se presente
    if data['cover_letter']:
        if any(data.values()):
            story.append(Spacer(1, 20))
            story.append(Paragraph("Lettera di Presentazione", styleH))
            story.append(Spacer(1, 12))
        story.append(Paragraph(data['cover_letter'].replace('\n', '<br/>'), styleN))

    # Costruisce il PDF
    doc.build(story)

    # Riporta il puntatore del buffer all'inizio
    buffer.seek(0)
    
    # Invia il file PDF come risposta
    return send_file(
        buffer,
        as_attachment=True,
        download_name='Curriculum_Vitae.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
