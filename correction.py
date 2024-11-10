import os
import re
import subprocess

# Nom du fichier d'entrée
input_file = 'test.tex'

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
            # Nom du fichier de correction
            correction_header = correction[0][0]

            # Créer un fichier .tex pour la correction
            with open(filename, 'w') as corr_file:
                corr_file.write(r'\documentclass{standalone}' + '\n')
                corr_file.write(r'\usepackage{amsmath}' + '\n')
                corr_file.write(r'\begin{document}' + '\n')
                corr_file.write(r'\begin{minipage}{\textwidth}' + '\n')
                corr_file.write(
                    r'\textbf{Correction:}\newline ' + correction_content + '\n')
                corr_file.write(r'\end{minipage}' + '\n')
                corr_file.write(r'\end{document}' + '\n')

            corrections.append((filename, correction_header))

    return corrections

# Fonction pour compiler les corrections


def compile_corrections(corrections):
    for filename, header in corrections:
        subprocess.run(['pdflatex', filename])
        print(f"Compiled {filename} to {header}")

# Fonction pour compiler le fichier d'énoncé


def compile_statement(input_file):
    subprocess.run(['pdflatex', input_file])
    print(f"Compiled {input_file}")


# Main
if __name__ == '__main__':
    corrections = extract_corrections(input_file)
    compile_corrections(corrections)

    # Compiler le fichier d'énoncé après avoir compilé les corrections
    compile_statement(input_file)

    # Nettoyer les fichiers temporaires
    for filename, _ in corrections:
        aux_file = filename.replace('.tex', '.aux')
        log_file = filename.replace('.tex', '.log')
        if os.path.exists(aux_file):
            os.remove(aux_file)
        if os.path.exists(log_file):
            os.remove(log_file)

    # Nettoyer aussi le fichier d'énoncé
    aux_file = input_file.replace('.tex', '.aux')
    log_file = input_file.replace('.tex', '.log')
    if os.path.exists(aux_file):
        os.remove(aux_file)
    if os.path.exists(log_file):
        os.remove(log_file)
