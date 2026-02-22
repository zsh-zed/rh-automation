# =============================================================
#  services/file_loader.py
#  Responsável por ler arquivos PDF e DOCX e retornar
#  o texto puro, que será enviado ao LLM.
#  Também gera um hash MD5 para evitar reprocessar
#  o mesmo arquivo duas vezes.
# =============================================================

import hashlib
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def generate_file_hash(file_path: Path) -> str:
    """
    Gera uma 'assinatura' única para o arquivo (hash MD5).
    Se o arquivo não mudou, o hash será sempre o mesmo.
    Usado para pular currículos já processados.
    """
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        # Lê o arquivo em blocos de 4KB (eficiente para arquivos grandes)
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()  # Retorna uma string hexadecimal como "a1b2c3..."


def extract_text_from_pdf(file_path: Path) -> str:
    """Extrai todo o texto de um arquivo PDF, página por página."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # 'or ""' evita None se a página for vazia
    return text


def extract_text_from_docx(file_path: Path) -> str:
    """Extrai todo o texto de um arquivo Word (.docx), parágrafo por parágrafo."""
    doc = Document(str(file_path))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(file_path: Path) -> str:
    """
    Ponto de entrada: decide qual função usar com base na extensão do arquivo.
    Lança um erro se o formato não for suportado.
    """
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Formato não suportado: {suffix}")
