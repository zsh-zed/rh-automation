# =============================================================
#  services/analyzer.py
#  Aqui está o coração do projeto: o uso do LangChain.
#
#  CONCEITOS IMPORTANTES:
#
#  1. PydanticOutputParser
#     Ensina o LLM a retornar dados no formato do nosso modelo.
#     Gera automaticamente as "format_instructions" que vão no prompt.
#
#  2. PromptTemplate
#     Um template de texto com {variáveis} que são preenchidas
#     antes de enviar para o LLM.
#
#  3. ChatGoogleGenerativeAI
#     O "cliente" que se conecta à API do Gemini.
#
#  4. Chain com o operador "|" (pipe)
#     Encadeia: prompt → llm → parser
#     Cada saída vira entrada do próximo passo.
#     Isso é o padrão LCEL (LangChain Expression Language).
# =============================================================

import re

from config import GOOGLE_API_KEY, MODEL_NAME
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from models import CandidateAnalysis, JobDescription
from prompts import ANALYSIS_PROMPT, JOB_DESCRIPTION_PROMPT

# --- Parsers: dizem ao LLM qual formato retornar ---

# Parser para análise de currículo
parser = PydanticOutputParser(pydantic_object=CandidateAnalysis)

# Parser para análise de vaga
job_parser = PydanticOutputParser(pydantic_object=JobDescription)

# --- LLM: conexão com o modelo Gemini ---
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=GOOGLE_API_KEY)

# --- Prompt Templates ---
# partial_variables preenche {format_instructions} automaticamente em todos os usos
prompt = PromptTemplate(
    template=ANALYSIS_PROMPT,
    input_variables=["resume_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

job_prompt = PromptTemplate(
    template=JOB_DESCRIPTION_PROMPT,
    input_variables=["job_text"],
    partial_variables={"format_instructions": job_parser.get_format_instructions()},
)

# --- Chains com LCEL (operador "|") ---
# Fluxo: formata o prompt → envia ao Gemini → faz parse da resposta
chain = prompt | llm | parser
job_chain = job_prompt | llm | job_parser


def analyze_resume(resume_text: str) -> CandidateAnalysis:
    """Envia o texto do currículo para o Gemini e retorna dados estruturados."""
    return chain.invoke({"resume_text": resume_text})


def analyze_job(job_text: str) -> JobDescription:
    """Envia o texto da vaga para o Gemini e retorna dados estruturados."""
    return job_chain.invoke({"job_text": job_text})


# --- Funções de Score (calculadas por código, não pelo LLM) ---


def normalize(text: str) -> str:
    """
    Normaliza texto para comparação:
    - Converte para minúsculas
    - Remove espaços extras
    Ex: "  Python 3  " → "python 3"
    """
    return re.sub(r"\s+", " ", text.lower().strip())


def skill_matches(candidate_skill: str, job_skill: str) -> bool:
    """
    Verifica se duas skills são equivalentes usando substring matching.
    Ex: "python 3.10" bate com "python", e vice-versa.
    Isso é mais flexível que comparação exata (==).
    """
    c = normalize(candidate_skill)
    j = normalize(job_skill)
    return j in c or c in j


def calculate_score(candidate: CandidateAnalysis, job: JobDescription) -> dict:
    """
    Calcula o quão compatível o candidato é com a vaga.

    Composição do score final:
      - 50% keyword_score     → skills obrigatórias que o candidato possui
      - 30% experience_score  → anos de experiência vs mínimo exigido
      - 20% hard_skills_score → skills desejáveis que o candidato possui

    Regra especial de experiência:
      Se o candidato tem menos de 30% das skills obrigatórias,
      a experiência não é contabilizada (evita inflar score de candidatos fora do perfil).
    """
    # Normaliza todas as listas para comparação consistente
    candidate_skills = [normalize(s) for s in candidate.skills_tecnicas]
    required_skills = [normalize(s) for s in job.skills_obrigatorias]
    optional_skills = [normalize(s) for s in job.skills_desejaveis]

    # --- Keyword Score: skills obrigatórias ---
    matched_required = 0
    for job_skill in required_skills:
        for candidate_skill in candidate_skills:
            if skill_matches(candidate_skill, job_skill):
                matched_required += 1
                break  # Encontrou match para esta skill, vai para a próxima

    keyword_score = (
        (matched_required / len(required_skills) * 100) if required_skills else 0
    )

    # --- Hard Skills Score: skills desejáveis ---
    matched_optional = 0
    for job_skill in optional_skills:
        for candidate_skill in candidate_skills:
            if skill_matches(candidate_skill, job_skill):
                matched_optional += 1
                break

    hard_skills_score = (
        (matched_optional / len(optional_skills) * 100) if optional_skills else 0
    )

    # --- Experience Score: anos de experiência ---
    # Só conta a experiência se o candidato tiver fit técnico mínimo (30%)
    if keyword_score < 30:
        experience_score = 0
    elif candidate.anos_experiencia >= job.anos_experiencia_min:
        experience_score = 100  # Atende ou supera o requisito
    else:
        # Score proporcional: ex: 2 anos de 4 exigidos = 50%
        experience_score = (candidate.anos_experiencia / job.anos_experiencia_min) * 100

    # --- Score Final Ponderado ---
    final_score = keyword_score * 0.5 + experience_score * 0.3 + hard_skills_score * 0.2

    return {
        "keyword_score": round(keyword_score, 2),
        "experience_score": round(experience_score, 2),
        "hard_skills_score": round(hard_skills_score, 2),
        "final_score": round(final_score, 2),
    }
