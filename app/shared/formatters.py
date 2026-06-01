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
        "journey_stage": _stage_label(avaliacao.etapa_jornada),
        "exam_result": _exam_result_label(avaliacao.resultado_exame),
        "result_type": _result_type_label(avaliacao.tipo_resultado),
        "post_diagnosis_plan": avaliacao.plano_pos_diagnostico,
        "post_diagnosis_support": avaliacao.suporte_pos_diagnostico,
    }


def _stage_label(value):
    labels = {
        "pre_avaliacao": "Pré-avaliação",
        "recepcao_tecnica": "Recepção técnica",
        "triagem": "Triagem clínica e socioeconômica",
        "exame": "Encaminhamento para exame",
        "resultado": "Recebimento do resultado",
        "pos_diagnostico": "Suporte pós-diagnóstico",
    }
    return labels.get(value or "pre_avaliacao", "Pré-avaliação")


def _exam_result_label(value):
    labels = {
        "aguardando": "Aguardando",
        "positivo": "Positivo",
        "negativo": "Negativo",
        "inconclusivo": "Inconclusivo",
    }
    return labels.get(value or "aguardando", "Aguardando")


def _result_type_label(value):
    labels = {
        "intermediario": "Intermediário",
        "pre_mutacao": "Pré-mutação",
        "mutacao_completa": "Mutação completa",
        "normal": "Normal",
    }
    return labels.get(value or "", "")
