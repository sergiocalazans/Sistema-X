from __future__ import annotations

from datetime import date, datetime

from werkzeug.security import generate_password_hash

from app.database import SessionLocal
from app.models import (
    Avaliacao,
    AvaliacaoSintoma,
    DocumentoPaciente,
    FamiliarPaciente,
    LimiarDecisao,
    Paciente,
    PesoSintoma,
    Profissional,
    Sexo,
    Sintoma,
)


SINTOMAS_MVP = [
    ("Deficiência intelectual", "Cognitivo", 0.14, 0.13),
    ("Atraso na fala", "Comunicação", 0.09, 0.08),
    ("Dificuldades de aprendizagem", "Cognitivo", 0.08, 0.09),
    ("Déficit de atenção", "Comportamental", 0.07, 0.07),
    ("Hiperatividade", "Comportamental", 0.07, 0.06),
    ("Movimentos repetitivos", "Comportamental", 0.06, 0.06),
    ("Evitação de contato visual", "Comportamental", 0.06, 0.06),
    ("Dificuldade de interação social", "Comportamental", 0.06, 0.07),
    ("Face alongada", "Físico", 0.07, 0.06),
    ("Orelhas proeminentes", "Físico", 0.06, 0.05),
    ("Macroorquidismo", "Físico", 0.09, 0.00),
]

SINTOMA_ALIASES = {
    "Deficiência intelectual": ["Deficiencia intelectual"],
    "Comunicação": ["Comunicacao"],
    "Déficit de atenção": ["Deficit de atencao"],
    "Evitação de contato visual": ["Evitacao de contato visual"],
    "Dificuldade de interação social": ["Dificuldade de interacao social"],
}

USUARIOS_DEMO = [
    ("Dr. Admin", "contato@sxf.com", "Genética Médica", "admin"),
    ("Dra. Helena Ramos", "triagem@sxf.com", "Neuropediatria", "profissional"),
    ("Coordenação IBK", "relatorios@sxf.com", "Gestão de Projetos", "visualizador"),
]

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
        "avaliacao": {
            "sintomas": ["Atraso na fala", "Dificuldades de aprendizagem", "Déficit de atenção", "Evitação de contato visual"],
            "observacao": "Acompanhar evolução escolar e repertório comunicativo.",
            "etapa_jornada": "triagem",
            "resultado_exame": "aguardando",
            "realizado_em": datetime(2026, 2, 18, 9, 30),
        },
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
        "avaliacao": {
            "sintomas": [
                "Deficiência intelectual",
                "Hiperatividade",
                "Movimentos repetitivos",
                "Face alongada",
                "Orelhas proeminentes",
                "Macroorquidismo",
            ],
            "observacao": "Encaminhamento prioritário por score elevado e características físicas associadas.",
            "etapa_jornada": "exame",
            "encaminhamento_exame": "Teste molecular FMR1 solicitado ao laboratório parceiro.",
            "resultado_exame": "positivo",
            "tipo_resultado": "mutacao_completa",
            "plano_pos_diagnostico": "Aconselhamento genético e orientação de seguimento multiprofissional.",
            "suporte_pos_diagnostico": "Contato com programa de acolhimento familiar.",
            "realizado_em": datetime(2026, 3, 8, 14, 15),
        },
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
        "avaliacao": {
            "sintomas": ["Atraso na fala", "Dificuldade de interação social"],
            "observacao": "Manter acompanhamento e reavaliar após coleta de documentos escolares.",
            "etapa_jornada": "pre_avaliacao",
            "resultado_exame": "aguardando",
            "realizado_em": datetime(2026, 4, 4, 10, 0),
        },
    },
    {
        "nome": "Lucas Ferreira Alves",
        "sexo": Sexo.MASCULINO,
        "nascimento": date(2012, 9, 12),
        "email": "familia.lucas@example.com",
        "telefone": "(41) 90000-0004",
        "status_jornada": "resultado",
        "origem_encaminhamento": "Genética clínica",
        "requisicao_medica": "Requisição médica com suspeita de síndrome do X frágil por histórico familiar.",
        "triagem_clinica": "Déficit de atenção, dificuldade de aprendizagem e hiperatividade persistente.",
        "triagem_socioeconomica": "Família com boa adesão às consultas e acesso a transporte.",
        "caracteristicas_fisicas": "Orelhas proeminentes sem macroorquidismo relatado.",
        "familiares": [("Patrícia Alves", "Mãe", "(41) 98888-0004", "patricia.alves@example.com", "pre_avaliacao")],
        "documentos": [("Laudo pediátrico", "requisicao_medica", "Hospital universitário")],
        "avaliacao": {
            "sintomas": ["Dificuldades de aprendizagem", "Déficit de atenção", "Hiperatividade", "Orelhas proeminentes"],
            "observacao": "Score intermediário, mas histórico familiar justifica encaminhamento assistido.",
            "etapa_jornada": "resultado",
            "encaminhamento_exame": "Exame realizado em laboratório conveniado.",
            "resultado_exame": "negativo",
            "tipo_resultado": "normal",
            "plano_pos_diagnostico": "Investigar outras causas neurodesenvolvimentais.",
            "suporte_pos_diagnostico": "Encaminhado para grupo de apoio e reavaliação neuropediátrica.",
            "realizado_em": datetime(2026, 4, 19, 16, 45),
        },
    },
    {
        "nome": "Beatriz Martins Rocha",
        "sexo": Sexo.FEMININO,
        "nascimento": date(2016, 11, 3),
        "email": "familia.beatriz@example.com",
        "telefone": "(31) 90000-0005",
        "status_jornada": "exame",
        "origem_encaminhamento": "Psicologia escolar",
        "requisicao_medica": "Solicitação para triagem por atraso de fala e dificuldade de socialização.",
        "triagem_clinica": "Atraso na fala, evitação de contato visual e movimentos repetitivos.",
        "triagem_socioeconomica": "Responsável precisa de apoio para conciliar consultas com horário de trabalho.",
        "caracteristicas_fisicas": "Face alongada discreta.",
        "familiares": [("Daniel Rocha", "Pai", "(31) 97777-0005", "daniel.rocha@example.com", "pre_avaliacao")],
        "documentos": [("Relatório psicopedagógico", "avaliacao_anterior", "Escola estadual")],
        "avaliacao": {
            "sintomas": [
                "Atraso na fala",
                "Movimentos repetitivos",
                "Evitação de contato visual",
                "Dificuldade de interação social",
                "Face alongada",
            ],
            "observacao": "Encaminhar para exame por somatório clínico e impacto funcional.",
            "etapa_jornada": "exame",
            "encaminhamento_exame": "Agendamento de coleta orientado para a família.",
            "resultado_exame": "inconclusivo",
            "realizado_em": datetime(2026, 5, 7, 11, 20),
        },
    },
    {
        "nome": "Rafael Nogueira Paes",
        "sexo": Sexo.MASCULINO,
        "nascimento": date(2019, 1, 22),
        "email": "familia.rafael@example.com",
        "telefone": "(51) 90000-0006",
        "status_jornada": "triagem",
        "origem_encaminhamento": "Fonoaudiologia",
        "requisicao_medica": "Investigação por atraso expressivo de fala e comportamento repetitivo.",
        "triagem_clinica": "Atraso na fala, movimentos repetitivos e contato visual reduzido.",
        "triagem_socioeconomica": "Família relata boa rede de apoio local.",
        "caracteristicas_fisicas": "Sem achados físicos marcantes no cadastro inicial.",
        "familiares": [("Aline Paes", "Mãe", "(51) 96666-0006", "aline.paes@example.com", "pre_avaliacao")],
        "documentos": [("Encaminhamento fonoaudiológico", "requisicao_medica", "Clínica de fonoaudiologia")],
        "avaliacao": {
            "sintomas": ["Atraso na fala", "Movimentos repetitivos", "Evitação de contato visual"],
            "observacao": "Score abaixo do limiar, com recomendação de acompanhamento clínico.",
            "etapa_jornada": "triagem",
            "resultado_exame": "aguardando",
            "realizado_em": datetime(2026, 5, 24, 8, 50),
        },
    },
    {
        "nome": "Gabriel Cardoso Melo",
        "sexo": Sexo.MASCULINO,
        "nascimento": date(2009, 7, 18),
        "email": "familia.gabriel@example.com",
        "telefone": "(21) 90000-0007",
        "status_jornada": "pos_diagnostico",
        "origem_encaminhamento": "Neurologia",
        "requisicao_medica": "Avaliação para confirmação diagnóstica após triagem externa.",
        "triagem_clinica": "Deficiência intelectual, hiperatividade e dificuldades de aprendizagem.",
        "triagem_socioeconomica": "Família solicita orientação sobre direitos e rede de cuidado.",
        "caracteristicas_fisicas": "Face alongada e orelhas proeminentes.",
        "familiares": [("Cláudia Melo", "Mãe", "(21) 98888-0007", "claudia.melo@example.com", "pos_avaliacao")],
        "documentos": [("Resultado de exame externo", "resultado_exame", "Laboratório externo")],
        "avaliacao": {
            "sintomas": [
                "Deficiência intelectual",
                "Dificuldades de aprendizagem",
                "Déficit de atenção",
                "Hiperatividade",
                "Face alongada",
                "Orelhas proeminentes",
            ],
            "observacao": "Caso positivo em acompanhamento pós-diagnóstico.",
            "etapa_jornada": "pos_diagnostico",
            "encaminhamento_exame": "Resultado externo anexado e validado na jornada.",
            "resultado_exame": "positivo",
            "tipo_resultado": "pre_mutacao",
            "plano_pos_diagnostico": "Acompanhamento genético familiar e plano educacional individualizado.",
            "suporte_pos_diagnostico": "Orientação para benefícios sociais e rede de apoio.",
            "realizado_em": datetime(2026, 6, 1, 13, 10),
        },
    },
    {
        "nome": "Lívia Carvalho Dias",
        "sexo": Sexo.FEMININO,
        "nascimento": date(2021, 3, 6),
        "email": "familia.livia@example.com",
        "telefone": "(47) 90000-0008",
        "status_jornada": "recepcao_tecnica",
        "origem_encaminhamento": "Atenção básica",
        "requisicao_medica": "Encaminhamento inicial para avaliação de desenvolvimento.",
        "triagem_clinica": "Atraso leve na fala, sem outros sinais fortes no momento.",
        "triagem_socioeconomica": "Família em fase de organização documental.",
        "caracteristicas_fisicas": "Sem alterações físicas registradas.",
        "familiares": [("João Dias", "Pai", "(47) 97777-0008", "joao.dias@example.com", "pre_avaliacao")],
        "documentos": [("Ficha de encaminhamento", "requisicao_medica", "UBS local")],
        "avaliacao": {
            "sintomas": ["Atraso na fala"],
            "observacao": "Baixa prioridade para investigação molecular imediata.",
            "etapa_jornada": "pre_avaliacao",
            "resultado_exame": "aguardando",
            "realizado_em": datetime(2026, 6, 5, 15, 0),
        },
    },
]


def sync_profissional_demo(db):
    profissionais = {}
    created = False

    for nome, email, especialidade, tipo_usuario in USUARIOS_DEMO:
        profissional = db.query(Profissional).filter_by(email=email).first()
        if profissional:
            profissional.nome = nome
            profissional.senha_hash = generate_password_hash("123456")
            profissional.especialidade = especialidade
            profissional.tipo_usuario = tipo_usuario
        else:
            profissional = Profissional(
                nome=nome,
                email=email,
                senha_hash=generate_password_hash("123456"),
                especialidade=especialidade,
                tipo_usuario=tipo_usuario,
            )
            db.add(profissional)
            db.flush()
            created = True
        profissionais[email] = profissional

    return profissionais["contato@sxf.com"], created


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
    sintomas = {sintoma.descricao: sintoma for sintoma in db.query(Sintoma).all()}

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
            db.add(paciente)
            db.flush()

        if profissional not in paciente.profissionais:
            paciente.profissionais.append(profissional)

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
        _sync_demo_assessment(db, paciente, profissional, demo["avaliacao"], sintomas)


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


def _sync_demo_assessment(db, paciente, profissional, demo, sintomas):
    selected_symptoms = [sintomas[name] for name in demo["sintomas"] if name in sintomas]
    limiar = db.query(LimiarDecisao).filter_by(sexo=paciente.sexo).first()
    pesos = {
        peso.sintoma_id: peso.peso
        for peso in db.query(PesoSintoma).filter_by(sexo_referencia=paciente.sexo).all()
    }
    # Usa a mesma regra da triagem para que os relatórios de demonstração reflitam o comportamento real do sistema.
    score = sum(pesos.get(sintoma.id, 0) for sintoma in selected_symptoms)
    avaliacao = (
        db.query(Avaliacao)
        .filter(
            Avaliacao.paciente_id == paciente.id,
            Avaliacao.profissional_id == profissional.id,
            Avaliacao.observacao == demo["observacao"],
        )
        .first()
    )

    if not avaliacao:
        avaliacao = Avaliacao(paciente_id=paciente.id, profissional_id=profissional.id)
        db.add(avaliacao)

    avaliacao.limiar_decisao_id = limiar.id
    avaliacao.score_calculado = score
    avaliacao.encaminhar = score >= limiar.valor
    avaliacao.observacao = demo["observacao"]
    avaliacao.etapa_jornada = demo.get("etapa_jornada", "pre_avaliacao")
    avaliacao.requisicao_medica = paciente.requisicao_medica
    avaliacao.triagem_clinica = paciente.triagem_clinica
    avaliacao.triagem_socioeconomica = paciente.triagem_socioeconomica
    avaliacao.encaminhamento_exame = demo.get("encaminhamento_exame")
    avaliacao.resultado_exame = demo.get("resultado_exame", "aguardando")
    avaliacao.tipo_resultado = demo.get("tipo_resultado")
    avaliacao.plano_pos_diagnostico = demo.get("plano_pos_diagnostico")
    avaliacao.suporte_pos_diagnostico = demo.get("suporte_pos_diagnostico")
    avaliacao.realizado_em = demo["realizado_em"]

    avaliacao.sintomas.clear()
    selected_ids = {sintoma.id for sintoma in selected_symptoms}
    for sintoma in sintomas.values():
        avaliacao.sintomas.append(AvaliacaoSintoma(
            sintoma_id=sintoma.id,
            presente=sintoma.id in selected_ids,
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
