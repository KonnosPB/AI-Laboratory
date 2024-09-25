# Unter WSL Linux ausführen
import os
import shutil
import pypandoc
import subprocess

# Pfade anpassen
source_directory = "/home/konnos/github/api-erp"
destination_directory = "/home/konnos/gematik-erp-docs"

# Liste der zu kopierenden Dateiendungen
file_extensions = [".pdf", ".png", ".puml", ".adoc", ".docx"]

def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

def convert_adoc_to_md(adoc_file, md_file):
    try:
        # Schritt 1: Konvertiere AsciiDoc zu HTML mit asciidoctor
        html_file = adoc_file.replace('.adoc', '.html')
        subprocess.run(['asciidoctor', '-o', html_file, adoc_file], check=True)

        # Schritt 2: Konvertiere HTML zu Markdown mit pandoc
        output = pypandoc.convert_file(html_file, 'markdown', format='html')
        with open(md_file, 'w') as f:
            f.write(output)

        print(f"Converted {adoc_file} to {md_file}")
    except Exception as e:
        print(f"Error converting {adoc_file}: {e}")

def copy_and_convert_files(source_dir, dest_dir):
    for root, _, files in os.walk(source_dir):
        for file in files:
            #print(f"Handling file {file}")
            if any(file.endswith(ext) for ext in file_extensions):
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                dest_path = os.path.join(dest_dir, relative_path)
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                if file.endswith('.adoc'):
                    md_file = os.path.splitext(file)[0] + '.md'
                    dest_file = os.path.join(dest_path, md_file)
                    convert_adoc_to_md(source_file, dest_file)
                else:
                    dest_file = os.path.join(dest_path, file)
                    shutil.copy2(source_file, dest_file)
                    print(f"Copied {source_file} to {dest_file}")

# Zielverzeichnis säubern
clear_directory(destination_directory)

# Dateien kopieren und konvertieren
copy_and_convert_files(source_directory, destination_directory)