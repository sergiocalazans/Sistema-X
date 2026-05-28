from datetime import datetime

from app.models import Avaliacao, Paciente, Sexo


def sex_label(value):
    return "Feminino" if value in (Sexo.FEMININO, "F", "feminino") else "Masculino"


def recommendation_label(should_refer):
    return "Encaminhar" if should_refer else "Não prioritário"


def recommendation_key(should_refer):
    return "encaminhar" if should_refer else "nao-prio"


def date_time(value: datetime):
    return value.strftime("%d/%m/%Y %H:%M") if value else ""


def patient_last_assessment(paciente: Paciente):
    return max(paciente.avaliacoes, key=lambda avaliacao: avaliacao.realizado_em, default=None)


def patient_last_score(paciente: Paciente):
    ultima = patient_last_assessment(paciente)
    return round(ultima.score_calculado, 2) if ultima else 0


def assessment_view(avaliacao: Avaliacao):
    paciente = avaliacao.paciente
    return {
        "id": avaliacao.id,
        "patient": paciente.nome,
        "sex": sex_label(paciente.sexo),
        "score": round(avaliacao.score_calculado, 2),
        "threshold": round(avaliacao.limiar_decisao.valor, 2),
        "recommendation": recommendation_label(avaliacao.encaminhar),
        "recommendation_key": recommendation_key(avaliacao.encaminhar),
        "date": date_time(avaliacao.realizado_em),
    }

