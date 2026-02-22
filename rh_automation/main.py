# =============================================================
#  main.py
#  Orquestra todo o fluxo: lê arquivos, chama os serviços,
#  evita reprocessamento e salva os resultados.
# =============================================================

import json
from pathlib import Path

from services.analyzer import analyze_job, analyze_resume, calculate_score
from services.file_loader import extract_text, generate_file_hash

RESUME_DIR = Path("resumes")  # Pasta com os currículos
OUTPUT_DIR = Path("output")  # Pasta de saída dos JSONs
OUTPUT_DIR.mkdir(exist_ok=True)  # Cria a pasta se não existir


def get_resume_files() -> list[Path]:
    """Retorna todos os arquivos PDF e DOCX da pasta de currículos."""
    return [
        file
        for file in RESUME_DIR.iterdir()
        if file.suffix.lower() in [".pdf", ".docx"]
    ]


def main():
    output_file = OUTPUT_DIR / "analysis_results.json"  # Resultados dos candidatos
    job_output_file = OUTPUT_DIR / "job_analysis.json"  # Análise da vaga

    # --- Passo 1: Analisa a vaga ---
    job_text = Path("vaga.txt").read_text(encoding="utf-8")
    job = analyze_job(job_text)

    with open(job_output_file, "w", encoding="utf-8") as f:
        json.dump(job.model_dump(), f, indent=4, ensure_ascii=False)
    print(f"\n💾 Vaga salva em: {job_output_file}")

    # --- Passo 2: Carrega resultados anteriores (se existirem) ---
    # Permite rodar o script várias vezes sem reprocessar currículos já analisados
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = []

    # Conjunto de hashes já processados para lookup rápido (O(1))
    processed_hashes = {item["file_hash"] for item in results}

    # --- Passo 3: Processa cada currículo ---
    for file in get_resume_files():
        file_hash = generate_file_hash(file)

        # Pula se o arquivo já foi processado (mesmo conteúdo = mesmo hash)
        if file_hash in processed_hashes:
            print(f"⏭️  {file.name} já analisado. Pulando.")
            continue

        print(f"📄 Processando: {file.name}")

        text = extract_text(file)
        if not text.strip():
            print("   ⚠️  Texto vazio, ignorando...")
            continue

        # Extrai dados estruturados do currículo via LLM
        analysis = analyze_resume(text)

        # Calcula score de compatibilidade com a vaga
        score_data = calculate_score(analysis, job)

        results.append(
            {
                "arquivo": file.name,
                "file_hash": file_hash,  # Salvo para evitar reprocessamento futuro
                "analise": analysis.model_dump(),
                "score": score_data,
            }
        )

    # --- Passo 4: Salva todos os resultados ---
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Análise concluída! Resultados em: {output_file}")


if __name__ == "__main__":
    main()
