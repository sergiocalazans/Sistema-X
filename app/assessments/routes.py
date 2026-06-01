from io import BytesIO
import smtplib
from urllib.parse import quote
from email.message import EmailMessage

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for

from app.models import Avaliacao, AvaliacaoSintoma, LimiarDecisao, PesoSintoma, Sintoma
from app.services.exports import assessments_workbook
from app.shared.auth import current_professional_id, login_required
from app.shared.db import db_session
from app.shared.formatters import assessment_view
from app.shared.patients import professional_patient_query

assessments_bp = Blueprint("assessments", __name__, url_prefix="/avaliacoes")


@assessments_bp.get("")
@login_required
def index():
    profissional_id = current_professional_id()
    with db_session() as db:
        avaliacoes = (
            db.query(Avaliacao)
            .filter(Avaliacao.profissional_id == profissional_id)
            .order_by(Avaliacao.realizado_em.desc())
            .all()
        )
        rows = [assessment_view(item) for item in avaliacoes]
        return render_template("pages/assessments.html", active_page="assessments", assessments=rows)


@assessments_bp.route("/nova", methods=["GET", "POST"])
@login_required
def create():
    profissional_id = current_professional_id()
    with db_session() as db:
        pacientes = professional_patient_query(db, profissional_id).order_by("nome").all()
        sintomas = db.query(Sintoma).order_by(Sintoma.categoria, Sintoma.descricao).all()

        if request.method == "POST":
            paciente_id = request.form.get("paciente_id", type=int)
            paciente = professional_patient_query(db, profissional_id).filter_by(id=paciente_id).first()
            if not paciente:
                flash("Paciente não encontrado.", "error")
                return redirect(url_for("assessments.create"))

            selected_symptoms = {int(item) for item in request.form.getlist("sintomas")}
            limiar = db.query(LimiarDecisao).filter(LimiarDecisao.sexo == paciente.sexo).first()
            if not limiar:
                flash("Limiar de decisão não cadastrado para o sexo do paciente.", "error")
                return redirect(url_for("assessments.create"))

            pesos = {
                peso.sintoma_id: peso.peso
                for peso in db.query(PesoSintoma).filter(PesoSintoma.sexo_referencia == paciente.sexo).all()
            }
            score = sum(pesos.get(sintoma.id, 0) for sintoma in sintomas if sintoma.id in selected_symptoms)
            avaliacao = Avaliacao(
                paciente_id=paciente.id,
                profissional_id=profissional_id,
                limiar_decisao_id=limiar.id,
                score_calculado=score,
                encaminhar=score >= limiar.valor,
                observacao=(request.form.get("observacao") or "").strip() or None,
                etapa_jornada=request.form.get("etapa_jornada") or "pre_avaliacao",
                requisicao_medica=_optional(request.form.get("requisicao_medica")) or paciente.requisicao_medica,
                triagem_clinica=_optional(request.form.get("triagem_clinica")) or paciente.triagem_clinica,
                triagem_socioeconomica=_optional(request.form.get("triagem_socioeconomica")) or paciente.triagem_socioeconomica,
                encaminhamento_exame=_optional(request.form.get("encaminhamento_exame")),
                resultado_exame=request.form.get("resultado_exame") or "aguardando",
                tipo_resultado=_optional(request.form.get("tipo_resultado")),
                plano_pos_diagnostico=_optional(request.form.get("plano_pos_diagnostico")),
                suporte_pos_diagnostico=_optional(request.form.get("suporte_pos_diagnostico")),
            )
            paciente.status_jornada = _patient_stage_from_assessment(avaliacao)
            db.add(avaliacao)
            db.flush()

            for sintoma in sintomas:
                db.add(AvaliacaoSintoma(
                    avaliacao_id=avaliacao.id,
                    sintoma_id=sintoma.id,
                    presente=sintoma.id in selected_symptoms,
                ))

            db.commit()
            return redirect(url_for("assessments.result", assessment_id=avaliacao.id))

        return render_template(
            "pages/triage.html",
            active_page="triage",
            patients=pacientes,
            symptoms=sintomas,
        )


@assessments_bp.get("/<int:assessment_id>/resultado")
@login_required
def result(assessment_id):
    profissional_id = current_professional_id()
    with db_session() as db:
        avaliacao = (
            db.query(Avaliacao)
            .filter(Avaliacao.id == assessment_id, Avaliacao.profissional_id == profissional_id)
            .first()
        )
        if not avaliacao:
            flash("Avaliação não encontrada.", "error")
            return redirect(url_for("assessments.index"))

        return render_template(
            "pages/result.html",
            active_page="assessments",
            assessment=assessment_view(avaliacao),
            should_refer=avaliacao.encaminhar,
            bar_width=min(avaliacao.score_calculado * 100, 100),
            mailto_link=_mailto_link(avaliacao),
        )


@assessments_bp.get("/<int:assessment_id>/documento")
@login_required
def document(assessment_id):
    profissional_id = current_professional_id()
    with db_session() as db:
        avaliacao = (
            db.query(Avaliacao)
            .filter(Avaliacao.id == assessment_id, Avaliacao.profissional_id == profissional_id)
            .first()
        )
        if not avaliacao:
            flash("Avaliação não encontrada.", "error")
            return redirect(url_for("assessments.index"))

        content = _assessment_document(avaliacao)
        output = BytesIO(content.encode("utf-8"))
        return send_file(
            output,
            as_attachment=True,
            download_name=f"jornada-paciente-{avaliacao.id}.txt",
            mimetype="text/plain; charset=utf-8",
        )


@assessments_bp.post("/<int:assessment_id>/email")
@login_required
def send_email(assessment_id):
    profissional_id = current_professional_id()
    with db_session() as db:
        avaliacao = (
            db.query(Avaliacao)
            .filter(Avaliacao.id == assessment_id, Avaliacao.profissional_id == profissional_id)
            .first()
        )
        if not avaliacao:
            flash("Avaliação não encontrada.", "error")
            return redirect(url_for("assessments.index"))
        if not avaliacao.paciente.email or not avaliacao.paciente.consentimento_email:
            flash("E-mail não autorizado ou não cadastrado para este paciente.", "error")
            return redirect(url_for("assessments.result", assessment_id=assessment_id))

        sent = _send_assessment_email(avaliacao)
        if sent:
            flash("E-mail enviado com sucesso.", "success")
        else:
            flash("Configure SMTP_HOST, SMTP_USER e SMTP_PASSWORD para envio direto de e-mails.", "error")
        return redirect(url_for("assessments.result", assessment_id=assessment_id))


@assessments_bp.get("/export")
@login_required
def export():
    profissional_id = current_professional_id()
    with db_session() as db:
        workbook = assessments_workbook(db, profissional_id)
        return send_file(
            workbook,
            as_attachment=True,
            download_name="historico-avaliacoes.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _optional(value):
    return (value or "").strip() or None


def _patient_stage_from_assessment(avaliacao):
    if avaliacao.resultado_exame in ("positivo", "negativo"):
        return "pos_diagnostico"
    if avaliacao.encaminhamento_exame:
        return "exame"
    return "triagem"


def _mailto_link(avaliacao):
    paciente = avaliacao.paciente
    if not paciente.email or not paciente.consentimento_email:
        return None

    subject = quote(f"Resumo da jornada - {paciente.nome}")
    lines = [
        f"Paciente: {paciente.nome}",
        f"Resultado da triagem: {assessment_view(avaliacao)['recommendation']}",
        f"Score: {avaliacao.score_calculado:.2f}",
        f"Resultado do exame: {avaliacao.resultado_exame}",
    ]
    if avaliacao.tipo_resultado:
        lines.append(f"Tipo: {avaliacao.tipo_resultado.replace('_', ' ')}")
    if avaliacao.plano_pos_diagnostico:
        lines.append(f"Plano pós-diagnóstico: {avaliacao.plano_pos_diagnostico}")
    body = quote("\r\n".join(lines))
    return f"mailto:{paciente.email}?subject={subject}&body={body}"


def _assessment_document(avaliacao):
    paciente = avaliacao.paciente
    view = assessment_view(avaliacao)
    sintomas = [item.sintoma.descricao for item in avaliacao.sintomas if item.presente]
    familiares = [
        f"- {familiar.nome} ({familiar.parentesco or 'parentesco não informado'}) - {familiar.momento_cadastro.replace('_', ' ')}"
        for familiar in paciente.familiares
    ]
    documentos = [
        f"- {documento.descricao} ({documento.tipo_documento.replace('_', ' ')})"
        for documento in paciente.documentos
    ]

    return "\n".join([
        "Sistema-X - Documento da Jornada do Paciente IBK",
        "",
        f"Paciente: {paciente.nome}",
        f"CPF: {paciente.cpf or 'Não informado'}",
        f"E-mail: {paciente.email or 'Não informado'}",
        f"Telefone: {paciente.telefone or 'Não informado'}",
        f"LGPD: {'Consentimento documentado' if paciente.consentimento_lgpd else 'Conformidade registrada no prontuário'}",
        "",
        "Jornada",
        f"Etapa: {view['journey_stage']}",
        f"Requisição médica: {avaliacao.requisicao_medica or paciente.requisicao_medica or 'Não informado'}",
        f"Triagem clínica: {avaliacao.triagem_clinica or paciente.triagem_clinica or 'Não informado'}",
        f"Triagem socioeconômica: {avaliacao.triagem_socioeconomica or paciente.triagem_socioeconomica or 'Não informado'}",
        f"Características físicas: {paciente.caracteristicas_fisicas or 'Não informado'}",
        "",
        "Triagem SXF",
        f"Score: {view['score']}",
        f"Limiar: {view['threshold']}",
        f"Recomendação: {view['recommendation']}",
        f"Sintomas presentes: {', '.join(sintomas) if sintomas else 'Nenhum'}",
        "",
        "Exame e pós-diagnóstico",
        f"Encaminhamento: {avaliacao.encaminhamento_exame or 'Não informado'}",
        f"Resultado: {view['exam_result']}",
        f"Tipo: {view['result_type'] or 'Não informado'}",
        f"Plano: {avaliacao.plano_pos_diagnostico or 'Não informado'}",
        f"Suporte: {avaliacao.suporte_pos_diagnostico or 'Não informado'}",
        "",
        "Familiares",
        "\n".join(familiares) if familiares else "Nenhum familiar cadastrado",
        "",
        "Documentos anteriores",
        "\n".join(documentos) if documentos else "Nenhum documento cadastrado",
    ])


def _send_assessment_email(avaliacao):
    host = current_app.config.get("SMTP_HOST")
    if not host:
        return False

    paciente = avaliacao.paciente
    message = EmailMessage()
    message["Subject"] = f"Resumo da jornada - {paciente.nome}"
    message["From"] = current_app.config["SMTP_FROM"]
    message["To"] = paciente.email
    message.set_content(_assessment_document(avaliacao))

    try:
        with smtplib.SMTP(host, current_app.config["SMTP_PORT"]) as smtp:
            smtp.starttls()
            if current_app.config.get("SMTP_USER"):
                smtp.login(current_app.config["SMTP_USER"], current_app.config.get("SMTP_PASSWORD") or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        return False
    return True

