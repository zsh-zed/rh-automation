# =============================================================
#  prompts.py
#  Os prompts são os "comandos" enviados ao LLM.
#  Usamos {variáveis} que serão preenchidas dinamicamente.
#  {format_instructions} é preenchido automaticamente pelo
#  PydanticOutputParser para dizer ao LLM como formatar a resposta.
# =============================================================

ANALYSIS_PROMPT = """
Você é um especialista em recrutamento técnico.

Analise o currículo abaixo e extraia:

- Nome do candidato
- Nível (Sem Experiencia, Estagio,Júnior, Pleno ou Sênior)
- Anos estimados de experiência
- Lista de skills técnicas
- Lista de soft skills
- Um resumo profissional objetivo

Currículo:
{resume_text}

{format_instructions}
"""

JOB_DESCRIPTION_PROMPT = """
Você é um especialista em recrutamento técnico.

Analise a descrição de vaga abaixo e extraia:

- Título da vaga
- Nível esperado (Sem Experiencia, Estagio,Júnior, Pleno ou Sênior)
- Anos mínimos de experiência exigidos
- Lista de skills técnicas obrigatórias
- Lista de skills técnicas desejáveis
- Formação mínima exigida

Descrição da vaga:
{job_text}

{format_instructions}
"""
