import os
import shutil
import subprocess

# Setze die Quell- und Zielverzeichnisse
source_dir = "/workspace/source"
target_dir = "/workspace/target"

# Leere das Zielverzeichnis
if os.path.exists(target_dir):
    shutil.rmtree(target_dir)
os.makedirs(target_dir)

# Definiere die zu kopierenden Dateitypen
file_types = [".png", ".puml", ".pdf", ".adoc"]

# Funktion zum Kopieren und Konvertieren von Dateien
def copy_and_convert_files(src, dest):
    for root, dirs, files in os.walk(src):
        for file in files:
            if any(file.endswith(ext) for ext in file_types):
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, src)
                destination_file = os.path.join(dest, relative_path)

                # Erstelle das Zielverzeichnis falls es nicht existiert
                os.makedirs(os.path.dirname(destination_file), exist_ok=True)

                if file.endswith(".adoc"):
                    # Konvertiere adoc zu markdown
                    markdown_file = os.path.splitext(destination_file)[0] + ".md"
                    subprocess.run(["asciidoctor", "-b", "pandoc", "-r", "asciidoctor-pandoc", "-o", markdown_file, source_file])
                else:
                    shutil.copy2(source_file, destination_file)

# Kopiere die Dateien rekursiv
copy_and_convert_files(source_dir, target_dir)