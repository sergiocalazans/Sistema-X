from io import BytesIO

import pandas as pd

from app.models import Avaliacao, Paciente, Profissional


def patients_workbook(db, profissional_id):
    rows = (
        db.query(Paciente)
        .join(Paciente.profissionais)
        .filter(Profissional.id == profissional_id)
        .order_by(Paciente.criado_em.desc())
        .all()
    )

    data = []
    for paciente in rows:
        ultima = max(paciente.avaliacoes, key=lambda avaliacao: avaliacao.realizado_em, default=None)
        data.append({
            "ID": paciente.id,
            "Nome": paciente.nome,
            "Nome social": paciente.nome_social,
            "CPF": paciente.cpf,
            "E-mail": paciente.email,
            "Telefone": paciente.telefone,
            "Sexo": "Feminino" if paciente.sexo.value == "feminino" else "Masculino",
            "Etapa da jornada": _stage(paciente.status_jornada),
            "Origem do encaminhamento": paciente.origem_encaminhamento,
            "Características físicas": paciente.caracteristicas_fisicas,
            "Familiares": _family_summary(paciente),
            "Documentos anteriores": _documents_summary(paciente),
            "LGPD": "Consentimento documentado" if paciente.consentimento_lgpd else "Conformidade registrada no prontuário",
            "Data de nascimento": paciente.data_nascimento,
            "Idade": paciente.idade,
            "Data de cadastro": paciente.criado_em,
            "Último score": round(ultima.score_calculado, 2) if ultima else None,
            "Última recomendação": _recommendation(ultima.encaminhar) if ultima else None,
        })

    columns = [
        "ID",
        "Nome",
        "Nome social",
        "CPF",
        "E-mail",
        "Telefone",
        "Sexo",
        "Etapa da jornada",
        "Origem do encaminhamento",
        "Características físicas",
        "Familiares",
        "Documentos anteriores",
        "LGPD",
        "Data de nascimento",
        "Idade",
        "Data de cadastro",
        "Último score",
        "Última recomendação",
    ]
    return _xlsx_response(pd.DataFrame(data, columns=columns), "Pacientes")


def assessments_workbook(db, profissional_id):
    rows = (
        db.query(Avaliacao)
        .filter(Avaliacao.profissional_id == profissional_id)
        .order_by(Avaliacao.realizado_em.desc())
        .all()
    )

    data = []
    for avaliacao in rows:
        paciente = avaliacao.paciente
        sintomas_presentes = [
            item.sintoma.descricao
            for item in avaliacao.sintomas
            if item.presente
        ]
        data.append({
            "ID": avaliacao.id,
            "Paciente": paciente.nome,
            "Sexo": "Feminino" if paciente.sexo.value == "feminino" else "Masculino",
            "Score": round(avaliacao.score_calculado, 2),
            "Limiar": round(avaliacao.limiar_decisao.valor, 2),
            "Recomendação": _recommendation(avaliacao.encaminhar),
            "Etapa da jornada": _assessment_stage(avaliacao.etapa_jornada),
            "Resultado do exame": _exam_result(avaliacao.resultado_exame),
            "Tipo do resultado": _result_type(avaliacao.tipo_resultado),
            "Plano pós-diagnóstico": avaliacao.plano_pos_diagnostico,
            "Suporte pós-diagnóstico": avaliacao.suporte_pos_diagnostico,
            "Sintomas presentes": ", ".join(sintomas_presentes),
            "Observação": avaliacao.observacao,
            "Data da avaliação": avaliacao.realizado_em,
        })

    columns = [
        "ID",
        "Paciente",
        "Sexo",
        "Score",
        "Limiar",
        "Recomendação",
        "Etapa da jornada",
        "Resultado do exame",
        "Tipo do resultado",
        "Plano pós-diagnóstico",
        "Suporte pós-diagnóstico",
        "Sintomas presentes",
        "Observação",
        "Data da avaliação",
    ]
    return _xlsx_response(pd.DataFrame(data, columns=columns), "Histórico de Avaliações")


def _xlsx_response(frame, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]
        worksheet.freeze_panes = "A2"

        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            column_letter = column_cells[0].column_letter
            worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 48)

    output.seek(0)
    return output


def _recommendation(should_refer):
    return "Encaminhar" if should_refer else "Não prioritário"


def _family_summary(paciente):
    return "; ".join(
        f"{familiar.nome} ({familiar.parentesco or 'parentesco não informado'}, {familiar.momento_cadastro.replace('_', ' ')})"
        for familiar in paciente.familiares
    )


def _documents_summary(paciente):
    return "; ".join(
        f"{documento.descricao} ({documento.tipo_documento.replace('_', ' ')})"
        for documento in paciente.documentos
    )


def _stage(value):
    return {
        "cadastro": "Cadastro",
        "recepcao_tecnica": "Recepção técnica",
        "requisicao_medica": "Requisição médica",
        "triagem": "Triagem",
        "exame": "Exame",
        "resultado": "Resultado",
        "pos_diagnostico": "Pós-diagnóstico",
    }.get(value or "cadastro", "Cadastro")


def _assessment_stage(value):
    return {
        "pre_avaliacao": "Pré-avaliação",
        "recepcao_tecnica": "Recepção técnica",
        "triagem": "Triagem clínica e socioeconômica",
        "exame": "Encaminhamento para exame",
        "resultado": "Recebimento do resultado",
        "pos_diagnostico": "Suporte pós-diagnóstico",
    }.get(value or "pre_avaliacao", "Pré-avaliação")


def _exam_result(value):
    return {
        "aguardando": "Aguardando",
        "positivo": "Positivo",
        "negativo": "Negativo",
        "inconclusivo": "Inconclusivo",
    }.get(value or "aguardando", "Aguardando")


def _result_type(value):
    return {
        "intermediario": "Intermediário",
        "pre_mutacao": "Pré-mutação",
        "mutacao_completa": "Mutação completa",
        "normal": "Normal",
    }.get(value or "", "")
