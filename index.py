from flask import Flask, request, render_template_string, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

app = Flask(__name__)

# Codice HTML/CSS per il modulo di input (Con Checkbox Toggle)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generatore CV Sezionato</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .section-header {
            border-bottom: 2px solid theme('colors.indigo.400');
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        .section-box {
            background-color: theme('colors.gray.50');
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid theme('colors.gray.200');
        }
        textarea {
            transition: all 0.2s;
            resize: vertical;
        }
        textarea:focus {
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.4);
        }
        /* Stile per l'interruttore/checkbox */
        .toggle-switch {
            display: flex;
            align-items: center;
            cursor: pointer;
            user-select: none;
        }
        .toggle-switch input {
            display: none;
        }
        .toggle-slider {
            width: 44px;
            height: 24px;
            background-color: #ccc;
            border-radius: 24px;
            position: relative;
            transition: background-color 0.4s;
        }
        .toggle-slider:before {
            content: "";
            position: absolute;
            left: 2px;
            bottom: 2px;
            width: 20px;
            height: 20px;
            background-color: white;
            border-radius: 50%;
            transition: transform 0.4s;
        }
        .toggle-switch input:checked + .toggle-slider {
            background-color: theme('colors.indigo.500');
        }
        .toggle-switch input:checked + .toggle-slider:before {
            transform: translateX(20px);
        }
    </style>
</head>
<body class="bg-gray-100 p-4 sm:p-8 flex items-start justify-center min-h-screen">
    <div class="bg-white p-6 sm:p-10 rounded-xl shadow-2xl w-full max-w-5xl border border-gray-200 mt-8 mb-8">
        <header class="text-center mb-10">
            <h1 class="text-3xl font-extrabold text-gray-800 tracking-tight sm:text-4xl">Generatore CV & Lettera Flessibile 📄</h1>
            <p class="text-lg text-gray-500 mt-2">
                Inserisci i dati e usa gli **interruttori** per includere le sezioni nel PDF.
            </p>
        </header>

        <form action="/generate-cv" method="post" class="space-y-8">
            
            {% macro section_toggle(name) %}
            <label class="toggle-switch mr-4">
                <span class="text-sm font-medium text-gray-600 mr-2">Includi Sezione:</span>
                <input type="checkbox" name="include_{{ name }}" checked>
                <span class="toggle-slider"></span>
            </label>
            {% endmacro %}

            <div class="section-box space-y-6">
                <div class="flex justify-between items-center mb-4">
                    <div class="section-header border-none p-0 m-0">
                        <svg class="w-6 h-6 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        <h2 class="text-xl font-semibold text-gray-700">Informazioni Base</h2>
                    </div>
                    {{ section_toggle('personal_data') }}
                </div>
                
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <label for="personal_data" class="block text-sm font-medium text-gray-700 mb-1">Dati Personali (Contatti, Data di nascita, etc.)</label>
                        <textarea id="personal_data" name="personal_data" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="📍 Indirizzo...&#10;📞 Telefono...&#10;✉️ Email..."></textarea>
                    </div>
                    <div>
                        <label for="profile" class="block text-sm font-medium text-gray-700 mb-1">Profilo / Sommario Professionale</label>
                        <textarea id="profile" name="profile" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="Professionista serio e preciso, con esperienza nella gestione di attività di back office..."></textarea>
                    </div>
                </div>
            </div>
            
            <div class="section-box space-y-4">
                <div class="flex justify-between items-center mb-4">
                    <div class="section-header border-none p-0 m-0">
                        <svg class="w-6 h-6 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.324-.877-9-2.245M12 21v-7m0 0l3-3m-3 3l-3-3"></path></svg>
                        <h2 class="text-xl font-semibold text-gray-700">Esperienza Professionale</h2>
                    </div>
                    {{ section_toggle('experience') }}
                </div>
                <label for="experience" class="sr-only">Esperienza Professionale</label>
                <textarea id="experience" name="experience" rows="6" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="Back Office Team Leader&#10;2017 – 2018&#10;- Coordinamento e supporto a un team..."></textarea>
            </div>

            <div class="section-box space-y-4">
                <div class="flex justify-between items-center mb-4">
                    <div class="section-header border-none p-0 m-0">
                        <svg class="w-6 h-6 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.467 9.576 5 8.25 5c-2.404 0-4.408 1.484-5.176 3.565M12 6.253C13.168 5.467 14.424 5 15.75 5c2.404 0 4.408 1.484 5.176 3.565m-5.176-3.565A20.307 20.307 0 0112 10.755m0 0l-1.637 1.637m1.637-1.637L13.637 12.392m-1.637-1.637l-4.25-4.25"></path></svg>
                        <h2 class="text-xl font-semibold text-gray-700">Formazione e Titoli di Studio</h2>
                    </div>
                    {{ section_toggle('education') }}
                </div>
                <label for="education" class="sr-only">Formazione</label>
                <textarea id="education" name="education" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="Diploma di Maturità in Economia e Sviluppo – ITC Germano Sommeiller, 2016"></textarea>
            </div>

            <div class="section-box space-y-6">
                <div class="flex justify-between items-center mb-4">
                    <div class="section-header border-none p-0 m-0">
                        <svg class="w-6 h-6 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L19.5 7.25M17 9.75L7.25 19.5m0 0l-5-5m5 5l5-5"></path></svg>
                        <h2 class="text-xl font-semibold text-gray-700">Competenze (Tecniche, Personali, Lingue)</h2>
                    </div>
                    {{ section_toggle('skills') }}
                </div>
                <div class="grid md:grid-cols-3 gap-6">
                    <div>
                        <label for="tech_skills" class="block text-sm font-medium text-gray-700 mb-1">Informatiche e Tecniche</label>
                        <textarea id="tech_skills" name="tech_skills" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="Microsoft Office (Word, Excel, Outlook)"></textarea>
                    </div>
                    <div>
                        <label for="soft_skills" class="block text-sm font-medium text-gray-700 mb-1">Personali (Soft Skills)</label>
                        <textarea id="soft_skills" name="soft_skills" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="Precisione e serietà&#10;Capacità organizzative"></textarea>
                    </div>
                    <div>
                        <label for="languages" class="block text-sm font-medium text-gray-700 mb-1">Lingue Straniere</label>
                        <textarea id="languages" name="languages" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="Italiano – Madrelingua&#10;Inglese – C2"></textarea>
                    </div>
                </div>
            </div>

            <div class="section-box space-y-4">
                <div class="flex justify-between items-center mb-4">
                    <div class="section-header border-none p-0 m-0">
                        <svg class="w-6 h-6 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8m-9 13h9a2 2 0 002-2V5a2 2 0 00-2-2H3a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
                        <h2 class="text-xl font-semibold text-gray-700">Lettera di Presentazione</h2>
                    </div>
                    {{ section_toggle('cover_letter') }}
                </div>
                <label for="cover_letter" class="sr-only">Lettera di Presentazione</label>
                <textarea id="cover_letter" name="cover_letter" rows="8" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm placeholder-gray-400" placeholder="Oggetto: Candidatura per posizione di...&#10;&#10;Gentile Selezionatore,..."></textarea>
            </div>
            
            <div class="flex justify-center pt-4">
                <button type="submit" class="w-full md:w-96 px-8 py-4 text-lg font-bold rounded-xl shadow-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300 transform hover:scale-[1.01] flex items-center justify-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    Genera e Scarica PDF
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
    # Uso render_template_string per servire l'HTML con il macro Jinja
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate-cv', methods=['POST'])
def generate_cv():
    """Route per la generazione del PDF, che ora controlla i toggle."""
    
    # 1. Ottiene i dati del testo dai campi del modulo
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

    # 2. Ottiene lo stato dei toggle (checkbox)
    # Se il campo include_X è 'on' (spuntato), il valore è True, altrimenti è None/False
    toggles = {
        'personal_data': request.form.get('include_personal_data') == 'on',
        'profile': request.form.get('include_personal_data') == 'on', # Profilo usa lo stesso toggle di Personal Data
        'experience': request.form.get('include_experience') == 'on',
        'education': request.form.get('include_education') == 'on',
        'skills': request.form.get('include_skills') == 'on',
        'cover_letter': request.form.get('include_cover_letter') == 'on'
    }

    # Creazione del PDF in memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, bottomMargin=30) 
    story = []

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    
    # Stili PDF (come prima, per la professionalità)
    style_section = ParagraphStyle(
        'section', parent=styleN, spaceBefore=14, spaceAfter=4, fontSize=12, leading=15,
        fontName='Helvetica-Bold', textColor='#374151'
    )
    style_content = ParagraphStyle(
        'content', parent=styleN, spaceBefore=0, spaceAfter=12, fontSize=10, leading=14,
        textColor='#1F2937'
    )
    styleH_CV = ParagraphStyle(
        'HeadingCV', parent=styles["Heading1"], fontSize=24, spaceBefore=0, spaceAfter=18,
        alignment=1, fontName='Helvetica-Bold'
    )
    styleH_Letter = ParagraphStyle(
        'HeadingLetter', parent=styles["Heading1"], fontSize=18, spaceBefore=30, spaceAfter=15,
        alignment=0, fontName='Helvetica-Bold', textColor='#4B5563'
    )

    # --- Costruzione del CV (Solo se il toggle è ON e il campo non è vuoto) ---
    
    cv_content_present = any(
        (toggles[key] and data.get(key) and key != 'cover_letter') or # controlla i toggle individuali
        (toggles['skills'] and (data['tech_skills'] or data['soft_skills'] or data['languages'])) # caso speciale per skills
        for key in toggles if key != 'cover_letter' and key != 'skills'
    )

    if cv_content_present:
        story.append(Paragraph("CURRICULUM VITAE", styleH_CV))
        
        # Dati Personali
        if toggles['personal_data'] and data['personal_data']:
            story.append(Paragraph("DATI PERSONALI", style_section))
            story.append(Paragraph(data['personal_data'].replace('\n', '<br/>'), style_content))
            
        # Profilo (Stesso toggle dei Dati Personali)
        if toggles['personal_data'] and data['profile']:
            story.append(Paragraph("PROFILO", style_section))
            story.append(Paragraph(data['profile'].replace('\n', '<br/>'), style_content))

        # Esperienza Professionale
        if toggles['experience'] and data['experience']:
            story.append(Paragraph("ESPERIENZA PROFESSIONALE", style_section))
            # Logica per mettere in grassetto la prima riga
            experience_html = ""
            lines = data['experience'].split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    if i == 0 or (i > 0 and not lines[i-1].strip()): # Rileva l'inizio di un nuovo blocco di testo (1a riga o dopo riga vuota)
                         experience_html += f"<b>{line.strip()}</b><br/>"
                    else:
                        experience_html += f"{line.strip()}<br/>"
            story.append(Paragraph(experience_html, style_content))

        # Formazione
        if toggles['education'] and data['education']:
            story.append(Paragraph("FORMAZIONE", style_section))
            story.append(Paragraph(data['education'].replace('\n', '<br/>'), style_content))

        # Competenze (un unico toggle per le tre sottosezioni)
        if toggles['skills'] and (data['tech_skills'] or data['soft_skills'] or data['languages']):
            story.append(Paragraph("COMPETENZE", style_section))
            
            skills_list = []
            if data['tech_skills']:
                skills_list.append("<b>Informatiche/Tecniche:</b> " + data['tech_skills'].replace('\n', ' / '))
            if data['soft_skills']:
                skills_list.append("<b>Personali:</b> " + data['soft_skills'].replace('\n', ' / '))
            if data['languages']:
                skills_list.append("<b>Lingue:</b> " + data['languages'].replace('\n', ' / '))
            
            story.append(Paragraph('<br/>'.join(skills_list), style_content))

    # --- Costruzione della Lettera di Presentazione ---
    if toggles['cover_letter'] and data['cover_letter']:
        # Aggiunge un salto pagina/spazio se il CV ha contenuto
        if cv_content_present:
             story.append(Spacer(1, 48))
             
        story.append(Paragraph("Lettera di Presentazione", styleH_Letter))
        
        # Formattazione paragrafi
        letter_html = data['cover_letter'].replace('\n\n', '@@PARAGRAPH@@').replace('\n', '<br/>').replace('@@PARAGRAPH@@', '<br/><br/>')
        story.append(Paragraph(letter_html, style_content))
        
        # Clausola GDPR (se non è già menzionata)
        if "autorizzo" not in data['cover_letter'].lower():
             story.append(Spacer(1, 12))
             style_privacy = ParagraphStyle('privacy', parent=styleN, fontSize=8, leading=10)
             story.append(Paragraph("Autorizzo il trattamento dei miei dati personali ai sensi del Regolamento UE 2016/679 (GDPR).", style_privacy))


    # Costruisce il PDF
    if story:
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name='Curriculum_Flessibile.pdf',
            mimetype='application/pdf'
        )
    else:
        # Gestisce il caso in cui non sia stato selezionato nulla
        return "Nessun contenuto selezionato o inserito per la generazione del PDF.", 400


if __name__ == '__main__':
    app.run(debug=True)