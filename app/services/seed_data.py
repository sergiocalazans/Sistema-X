from __future__ import annotations

from datetime import date

from werkzeug.security import generate_password_hash

from app.database import SessionLocal
from app.models import DocumentoPaciente, FamiliarPaciente, LimiarDecisao, Paciente, PesoSintoma, Profissional, Sexo, Sintoma


SINTOMAS_MVP = [
    ("Deficiencia intelectual", "Cognitivo", 0.14, 0.13),
    ("Atraso na fala", "Comunicação", 0.09, 0.08),
    ("Dificuldades de aprendizagem", "Cognitivo", 0.08, 0.09),
    ("Déficit de atenção", "Comportamental", 0.07, 0.07),
    ("Hiperatividade", "Comportamental", 0.07, 0.06),
    ("Movimentos repetitivos", "Comportamental", 0.06, 0.06),
    ("Evitação de contato visual", "Comportamental", 0.06, 0.06),
    ("Dificuldade de interacao social", "Comportamental", 0.06, 0.07),
    ("Face alongada", "Físico", 0.07, 0.06),
    ("Orelhas proeminentes", "Físico", 0.06, 0.05),
    ("Macroorquidismo", "Físico", 0.09, 0.00),
]

SINTOMA_ALIASES = {
    "Comunicação": ["Comunicacao"],
    "Déficit de atenção": ["Deficit de atencao"],
    "Evitação de contato visual": ["Evitacao de contato visual"],
}

PACIENTES_DEMO = [
    {
        "nome": "Ana Silva Santos",
        "sexo": Sexo.FEMININO,
        "nascimento": date(2018, 5, 1),
        "email": "familia.ana@example.com",
        "telefone": "(11) 90000-0001",
        "status_jornada": "triagem",
        "origem_encaminhamento": "Pediatria",
        "requisicao_medica": "Requisição para investigação molecular de SXF após atraso de fala e dificuldades escolares.",
        "triagem_clinica": "Atraso de linguagem, dificuldade de atenção e contato visual reduzido.",
        "triagem_socioeconomica": "Família com disponibilidade para comparecimento em dias úteis e necessidade de orientação sobre rede de apoio.",
        "caracteristicas_fisicas": "Face alongada discreta e orelhas proeminentes.",
        "familiares": [("Carla Silva", "Mãe", "(11) 98888-0001", "carla.silva@example.com", "pre_avaliacao")],
        "documentos": [("Relatório escolar anterior", "avaliacao_anterior", "Escola municipal")],
    },
    {
        "nome": "Pedro Oliveira Costa",
        "sexo": Sexo.MASCULINO,
        "nascimento": date(2014, 4, 30),
        "email": "familia.pedro@example.com",
        "telefone": "(11) 90000-0002",
        "status_jornada": "exame",
        "origem_encaminhamento": "Neuropediatria",
        "requisicao_medica": "Solicitação de teste genético confirmatório para SXF.",
        "triagem_clinica": "Deficiência intelectual, hiperatividade e movimentos repetitivos.",
        "triagem_socioeconomica": "Responsável relata dificuldade de deslocamento e necessidade de agendamento assistido.",
        "caracteristicas_fisicas": "Orelhas proeminentes, face alongada e macroorquidismo relatado.",
        "familiares": [
            ("Marcos Costa", "Pai", "(11) 97777-0002", "marcos.costa@example.com", "pre_avaliacao"),
            ("Juliana Oliveira", "Mãe", "(11) 96666-0002", "juliana.oliveira@example.com", "pos_avaliacao"),
        ],
        "documentos": [("Avaliação neuropsicológica", "avaliacao_anterior", "Clínica externa")],
    },
    {
        "nome": "Maria Souza Lima",
        "sexo": Sexo.FEMININO,
        "nascimento": date(2020, 4, 29),
        "email": "familia.maria@example.com",
        "telefone": "(11) 90000-0003",
        "status_jornada": "cadastro",
        "origem_encaminhamento": "Atenção básica",
        "requisicao_medica": "Investigação inicial por histórico familiar e atraso de desenvolvimento.",
        "triagem_clinica": "Atraso global leve e dificuldade de interação social.",
        "triagem_socioeconomica": "Família solicita orientações sobre possibilidades diagnósticas e grupos de apoio.",
        "caracteristicas_fisicas": "Sem alterações físicas relevantes registradas na visita inicial.",
        "familiares": [("Renata Lima", "Mãe", "(11) 95555-0003", "renata.lima@example.com", "pre_avaliacao")],
        "documentos": [("Encaminhamento UBS", "requisicao_medica", "Unidade básica de saúde")],
    },
]


def sync_profissional_demo(db):
    profissional = db.query(Profissional).filter_by(email="contato@sxf.com").first()
    if profissional:
        profissional.nome = "Dr. Admin"
        profissional.senha_hash = generate_password_hash("123456")
        profissional.especialidade = "Genética Médica"
        profissional.tipo_usuario = "admin"
        return profissional, False

    profissional = Profissional(
        nome="Dr. Admin",
        email="contato@sxf.com",
        senha_hash=generate_password_hash("123456"),
        especialidade="Genética Médica",
        tipo_usuario="admin",
    )
    db.add(profissional)
    db.flush()
    return profissional, True


def sync_limiares(db):
    for sexo, valor in ((Sexo.MASCULINO, 0.56), (Sexo.FEMININO, 0.55)):
        limiar = db.query(LimiarDecisao).filter_by(sexo=sexo).first()
        if limiar:
            limiar.valor = valor
        else:
            db.add(LimiarDecisao(sexo=sexo, valor=valor))


def sync_sintomas(db):
    for descricao, categoria, peso_m, peso_f in SINTOMAS_MVP:
        descricoes_possiveis = [descricao, *SINTOMA_ALIASES.get(descricao, [])]
        sintoma = db.query(Sintoma).filter(Sintoma.descricao.in_(descricoes_possiveis)).first()
        if not sintoma:
            sintoma = Sintoma(descricao=descricao, categoria=categoria)
            db.add(sintoma)
            db.flush()
        else:
            sintoma.descricao = descricao
            sintoma.categoria = categoria

        for sexo, valor in ((Sexo.MASCULINO, peso_m), (Sexo.FEMININO, peso_f)):
            peso = db.query(PesoSintoma).filter_by(
                sintoma_id=sintoma.id,
                sexo_referencia=sexo,
            ).first()
            if peso:
                peso.peso = valor
            else:
                db.add(PesoSintoma(sintoma_id=sintoma.id, sexo_referencia=sexo, peso=valor))


def sync_pacientes_demo(db, profissional):
    for demo in PACIENTES_DEMO:
        paciente = (
            db.query(Paciente)
            .join(Paciente.profissionais)
            .filter(Paciente.nome == demo["nome"], Profissional.id == profissional.id)
            .first()
        )
        if paciente:
            paciente.data_nascimento = demo["nascimento"]
            paciente.sexo = demo["sexo"]
        else:
            paciente = Paciente(
                nome=demo["nome"],
                data_nascimento=demo["nascimento"],
                sexo=demo["sexo"],
            )
            paciente.profissionais.append(profissional)
            db.add(paciente)
            db.flush()

        paciente.email = demo["email"]
        paciente.telefone = demo["telefone"]
        paciente.status_jornada = demo["status_jornada"]
        paciente.origem_encaminhamento = demo["origem_encaminhamento"]
        paciente.requisicao_medica = demo["requisicao_medica"]
        paciente.triagem_clinica = demo["triagem_clinica"]
        paciente.triagem_socioeconomica = demo["triagem_socioeconomica"]
        paciente.caracteristicas_fisicas = demo["caracteristicas_fisicas"]
        paciente.consentimento_lgpd = True
        paciente.observacoes_lgpd = "Dados sensíveis registrados para finalidade assistencial e extensionista do Sistema-X."
        _sync_demo_relatives(paciente, demo["familiares"])
        _sync_demo_documents(paciente, demo["documentos"])


def _sync_demo_relatives(paciente, familiares):
    paciente.familiares.clear()
    for nome, parentesco, telefone, email, momento in familiares:
        paciente.familiares.append(FamiliarPaciente(
            nome=nome,
            parentesco=parentesco,
            telefone=telefone,
            email=email,
            momento_cadastro=momento,
        ))


def _sync_demo_documents(paciente, documentos):
    paciente.documentos.clear()
    for descricao, tipo, origem in documentos:
        paciente.documentos.append(DocumentoPaciente(
            descricao=descricao,
            tipo_documento=tipo,
            origem=origem,
        ))


def sync_mvp_defaults(include_demo_patients=False):
    db = SessionLocal()
    try:
        profissional, created = sync_profissional_demo(db)
        sync_limiares(db)
        sync_sintomas(db)
        if include_demo_patients:
            sync_pacientes_demo(db, profissional)

        db.commit()
        return {"profissional_created": created}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
