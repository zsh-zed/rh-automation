# =============================================================
#  models.py
#  Define a "forma" dos dados usando Pydantic.
#  Pydantic garante que os dados retornados pelo LLM estejam
#  no formato correto (tipagem, validação automática).
# =============================================================

from typing import List, Optional

from pydantic import BaseModel


# Representa os dados extraídos de um currículo
class CandidateAnalysis(BaseModel):
    nome: str
    nivel: str  # "Júnior", "Pleno" ou "Sênior"
    anos_experiencia: int
    skills_tecnicas: List[str]  # ex: ["Python", "FastAPI", "Docker"]
    soft_skills: List[str]  # ex: ["Comunicação", "Trabalho em equipe"]
    educacao: Optional[str] = None  # Opcional: nem todo currículo tem formação
    resumo_profissional: str


# Representa os dados extraídos da descrição de uma vaga
class JobDescription(BaseModel):
    titulo: str
    nivel_esperado: str
    anos_experiencia_min: int
    skills_obrigatorias: List[str]  # O candidato PRECISA ter
    skills_desejaveis: List[str]  # Seria bom ter, mas não é obrigatório
    formacao_minima: str


# Representa o score calculado (não vem do LLM, é calculado por código)
class CandidateScore(BaseModel):
    keyword_score: float  # % de skills obrigatórias que o candidato tem
    experience_score: float  # Pontuação baseada nos anos de experiência
    hard_skills_score: float  # % de skills desejáveis que o candidato tem
    final_score: float  # Score final ponderado
