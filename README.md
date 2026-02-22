# Mini ATS — Analisador de Currículos com IA

Ferramenta de linha de comando que usa a API do Gemini para analisar currículos e calcular compatibilidade com uma vaga.

---

## Como funciona

1. Adicione seu currículo (PDF ou DOCX) na pasta `resumes/`
2. Cole a descrição da vaga no arquivo `vaga.txt`
3. Rode o projeto — a IA faz o resto

A API do Gemini estrutura os pontos principais da vaga, lê o currículo e retorna um score de compatibilidade entre os dois.

---

## Estrutura

```
.
├── main.py
├── models.py
├── prompts.py
├── config.py
├── services/
│   ├── analyzer.py
│   └── file_loader.py
├── resumes/
├── output/
└── vaga.txt
```

---

## Instalação

```bash
pip install -r requirements.txt
```

Configure sua chave no `config.py`:

```python
GOOGLE_API_KEY = "sua_chave"
MODEL_NAME = "gemini-1.5-flash"
```

Execute:

```bash
python3 main.py
```

---

## Stack

Python 3.10+ · LangChain · Gemini API · Pydantic

---

## Observações

- Persistência via JSON, sem banco de dados
- Sujeito ao limite diário da API do Gemini
- z
