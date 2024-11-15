import os
import re
import subprocess
import shutil
import argparse  # Importation du module argparse

# Fonction pour configurer et interpréter les arguments de la ligne de commande


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Générer des fichiers de corrections de LaTeX avec QR codes.')
    parser.add_argument('input_file', type=str,
                        help='Nom du fichier d\'énoncé en .tex')
    return parser.parse_args()


# Chemin vers le dépôt Git
github_repo_dir = '/Users/nicolasogier/workspaces/Latex/GithubPage'
github_page_url = 'https://opware2000.github.io/TestGithubPageLatex/'

# Fonction pour extraire les corrections


def extract_corrections(input_file):
    corrections = []
    # Nom de base du fichier d'énoncé sans extension
    base_name = os.path.splitext(input_file)[0]
    with open(input_file, 'r') as file:
        content = file.read()

    # Trouver tous les environnements Exercice
    exercises = re.findall(
        r'\\begin\{Exercice\}\[.*?\](.*?)\\end\{Exercice\}', content, re.DOTALL)

    for i, exercise in enumerate(exercises):
        # Trouver l'environnement Correction dans l'Exercice
        correction = re.findall(
            r'\\begin\{Correction\}\[(.*?)\](.*?)\\end\{Correction\}', exercise, re.DOTALL)
        if correction:
            filename = f'{base_name}_correction_exercice{i + 1}.tex'
            # Contenu de la correction
            correction_content = correction[0][1].strip()
            correction_header = correction[0][0].strip()

            # Créer un fichier .tex pour la correction
            with open(filename, 'w') as corr_file:
                corr_file.write(r'\documentclass{standalone}' + '\n')
                corr_file.write(r'\usepackage{amsmath}' + '\n')
                corr_file.write(r'\begin{document}' + '\n')
                corr_file.write(r'\begin{minipage}{\textwidth}' + '\n')
                corr_file.write(r'\textbf{Correction:}' + correction_header +
                                r'\newline ' + correction_content.replace('\n', r'\\') + '\n')
                corr_file.write(r'\end{minipage}' + '\n')
                corr_file.write(r'\end{document}' + '\n')

            # Stocker le nom du PDF
            corrections.append(
                (filename, f'{base_name}_correction_exercice{i + 1}.pdf'))

    return corrections

# Fonction pour compiler les corrections


def compile_corrections(corrections):
    for filename, _ in corrections:
        try:
            subprocess.check_call(['pdflatex', filename],
                                  stderr=subprocess.STDOUT)
            print(f"Compilation réussie pour: {filename}")
        except subprocess.CalledProcessError as e:
            print("Erreur lors de la compilation de"
                  + filename + ':' + e.output.decode())

# Fonction pour compiler le fichier d'énoncé


def compile_statement(input_file):
    try:
        subprocess.check_call(['pdflatex', input_file],
                              stderr=subprocess.STDOUT)
        print(f"Compilation réussie pour: {input_file}")
    except subprocess.CalledProcessError as e:
        print("Erreur lors de la compilation de"
              + input_file + ':' + e.output.decode())

# Fonction pour copier les fichiers PDF


def copy_files(corrections):
    for _, pdf_name in corrections:
        pdf_filename = pdf_name
        if os.path.exists(pdf_filename):
            # Copie le fichier PDF vers le dossier GitHub Pages
            shutil.copy(pdf_filename, github_repo_dir)
            print(f"Fichier copié vers GitHub Pages: {pdf_filename}")
        else:
            print(f"Avertissement: Le fichier {pdf_filename} n'existe pas.")


def insert_qr_codes(input_file, output_file, corrections):
    with open(input_file, 'r') as file:
        content = file.readlines()

    with open(output_file, 'w') as file:
        correction_count = 0
        for line in content:
            file.write(line)
            if r'\begin{Exercice}' in line:
                # Vérifiez s'il y a une correction disponible pour cet exercice
                if correction_count < len(corrections):
                    # Le nom du PDF correspondant
                    pdf_filename = corrections[correction_count][1]
                    file.write(
                        r'\begin{center} Correction\\\vspace*{2mm}' + '\n')
                    file.write(
                        r'\qrcode{' + github_page_url + pdf_filename + '}' + '\n')
                    file.write(r'\end{center}' + '\n')
                    correction_count += 1  # Incrémenter pour passer à la prochaine correction


def prof_version(input_file, prof_file):
    with open(input_file, 'r') as file:
        content = file.readlines()
    with open(prof_file, 'w') as file:
        for line in content:
            file.write(line.replace('\Proffalse', '\Proftrue'))


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


def clean_file(file_name):
    aux_file = file_name.replace('.tex', '.aux')
    log_file = file_name.replace('.tex', '.log')
    if os.path.exists(aux_file):
        os.remove(aux_file)
    if os.path.exists(log_file):
        os.remove(log_file)


# Main
if __name__ == '__main__':

    input_file = parse_arguments().input_file
    output_file = input_file.replace('.tex', '_qrcode.tex')
    prof_file = input_file.replace('.tex', '_prof.tex')
    corrections = extract_corrections(input_file)
    compile_corrections(corrections)

    # Copier les fichiers PDF vers le répertoire GitHub Pages
    copy_files(corrections)

    # Insérer les QR codes dans le fichier d'énoncé
    insert_qr_codes(input_file, output_file, corrections)
    # Générer la version prof
    prof_version(input_file, prof_file)
    # Compiler le fichier d'énoncé après l'insertion des QR codes
    compile_statement(output_file)
    compile_statement(prof_file)
    # Nettoyer les fichiers temporaires
    for filename, _ in corrections:
        clean_file(filename)

    # Nettoyer les fichiers d'énoncé et prof
    clean_file(output_file)
    clean_file(prof_file)
    # Commiter et pousser les fichiers
    commit_and_push_changes()
    print('Compilation réussie !')
