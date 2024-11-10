import os
import re
import subprocess
import shutil

# Configuration
input_file = 'test.tex'
# Chemin vers le dépôt Git
github_repo_dir = '/Users/nicolasogier/workspaces/Latex/GithubPage'
github_page_url = 'https://opware2000.github.io/TestGithubPageLatex/'

# Fonction pour extraire les corrections


def extract_corrections(input_file):
    corrections = []

    with open(input_file, 'r') as file:
        content = file.read()

    # Trouver tous les environnements Exercice
    exercises = re.findall(
        r'\\begin\{Exercice\}\[.*?\](.*?)\\end\{Exercice\}', content, re.DOTALL)

    for i, exercise in enumerate(exercises):
        # Trouver l'environnement Correction dans l'Exercice
        correction = re.findall(
            r'\\begin\{Correction\}\{(.*?)\}(.*?)\\end\{Correction\}', exercise, re.DOTALL)
        if correction:
            filename = f'correction_exercice{i + 1}.tex'
            # Contenu de la correction
            correction_content = correction[0][1].strip()

            # Créer un fichier .tex pour la correction
            with open(filename, 'w') as corr_file:
                corr_file.write(r'\documentclass{standalone}' + '\n')
                corr_file.write(r'\usepackage{amsmath}' + '\n')
                corr_file.write(r'\begin{document}' + '\n')
                corr_file.write(r'\begin{minipage}{\textwidth}' + '\n')
                corr_file.write(
                    r'\textbf{Correction:}\newline ' + correction_content.replace('\n', r'\\') + '\n')
                corr_file.write(r'\end{minipage}' + '\n')
                corr_file.write(r'\end{document}' + '\n')

            # Stocker le nom du PDF
            corrections.append((filename, f'correction_exercice{i + 1}.pdf'))

    return corrections

# Fonction pour compiler les corrections


def compile_corrections(corrections):
    for filename, _ in corrections:
        try:
            subprocess.check_call(['pdflatex', filename],
                                  stderr=subprocess.STDOUT)
            print(f"Compilation réussie pour: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la compilation de {
                  filename}: {e.output.decode()}")

# Fonction pour compiler le fichier d'énoncé


def compile_statement(input_file):
    try:
        subprocess.check_call(['pdflatex', input_file],
                              stderr=subprocess.STDOUT)
        print(f"Compilation réussie pour: {input_file}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la compilation de {
              input_file}: {e.output.decode()}")

# Fonction pour copier les fichiers PDF


def copy_files(corrections):
    for filename, _ in corrections:
        pdf_filename = filename.replace('.tex', '.pdf')
        if os.path.exists(pdf_filename):
            # Copie le fichier PDF vers le dossier GitHub Pages
            shutil.copy(pdf_filename, github_repo_dir)
            print(f"Fichier copié vers GitHub Pages: {pdf_filename}")
        else:
            print(f"Avertissement: Le fichier {pdf_filename} n'existe pas.")


def insert_qr_codes(input_file, corrections):
    with open(input_file, 'r') as file:
        content = file.readlines()

    with open(input_file, 'w') as file:
        for line in content:
            file.write(line)
            if r'\begin{Exercice}' in line:
                for filename, _ in corrections:
                    pdf_filename = filename.replace('.tex', '.pdf')
                    base_filename = os.path.basename(pdf_filename)
                    # Ajouter le QR code pour chaque PDF
                    file.write(r'\begin{center}' + '\n')
                    file.write(
                        r'\qrcode{' + github_page_url + base_filename + '}' + '\n')
                    file.write(r'\end{center}' + '\n')

# Fonction pour commiter les fichiers copiés et faire un push


def commit_and_push_changes():
    os.chdir(github_repo_dir)  # Changer de répertoire vers le dépôt
    try:
        # Ajouter tous les nouveaux fichiers
        subprocess.check_call(['git', 'add', '.'])
        # Commiter les changements
        subprocess.check_call(
            ['git', 'commit', '-m', 'Ajout des fichiers de correction avec les QR codes.'])
        subprocess.check_call(['git', 'push'])  # Pousser les modifications
        print("Changements poussés vers le dépôt Git.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'opération Git: {e.output.decode()}")


# Main
if __name__ == '__main__':
    corrections = extract_corrections(input_file)
    compile_corrections(corrections)

    # Copier les fichiers PDF vers le répertoire GitHub Pages
    copy_files(corrections)

    # Insérer les QR codes dans le fichier d'énoncé
    insert_qr_codes(input_file, corrections)

    # Compiler le fichier d'énoncé après l'insertion des QR codes
    compile_statement(input_file)

    # Commiter et pousser les fichiers
    commit_and_push_changes()

    # Nettoyer les fichiers temporaires
    for filename, _ in corrections:
        aux_file = filename.replace('.tex', '.aux')
        log_file = filename.replace('.tex', '.log')
        if os.path.exists(aux_file):  # Supprimer le fichier .aux
            os.remove(aux_file)
        if os.path.exists(log_file):  # Supprimer le fichier de log
            os.remove(log_file)
        if os.path.exists(filename):  # Supprimer le fichier de correction
            os.remove(filename)

    # Nettoyer aussi le fichier d'énoncé
    aux_file = input_file.replace('.tex', '.aux')
    log_file = input_file.replace('.tex', '.log')
    if os.path.exists(aux_file):
        os.remove(aux_file)
    if os.path.exists(log_file):
        os.remove(log_file)

    print('Compilation réussie !')