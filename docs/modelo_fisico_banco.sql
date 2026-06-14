CREATE DATABASE IF NOT EXISTS `sistema-x`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `sistema-x`;

CREATE TABLE IF NOT EXISTS `profissional` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(120) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `senha_hash` VARCHAR(255) NOT NULL,
  `especialidade` VARCHAR(120) NOT NULL,
  `tipo_usuario` VARCHAR(40) NOT NULL DEFAULT 'profissional',
  `deve_atualizar_senha` BOOLEAN NOT NULL DEFAULT FALSE,
  `criado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_profissional_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `paciente` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(120) NOT NULL,
  `cpf` VARCHAR(14) NULL,
  `email` VARCHAR(120) NULL,
  `telefone` VARCHAR(20) NULL,
  `data_nascimento` DATE NOT NULL,
  `sexo` ENUM('masculino', 'feminino') NOT NULL,
  `nome_social` VARCHAR(120) NULL,
  `endereco` VARCHAR(255) NULL,
  `origem_encaminhamento` VARCHAR(160) NULL,
  `requisicao_medica` TEXT NULL,
  `status_jornada` VARCHAR(80) NOT NULL DEFAULT 'cadastro',
  `triagem_clinica` TEXT NULL,
  `triagem_socioeconomica` TEXT NULL,
  `caracteristicas_fisicas` TEXT NULL,
  `foto_rosto` VARCHAR(255) NULL,
  `foto_perfil` VARCHAR(255) NULL,
  `foto_lado` VARCHAR(255) NULL,
  `consentimento_lgpd` BOOLEAN NOT NULL DEFAULT FALSE,
  `observacoes_lgpd` TEXT NULL,
  `criado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `paciente_profissional` (
  `paciente_id` INT NOT NULL,
  `profissional_id` INT NOT NULL,
  `criado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`paciente_id`, `profissional_id`),
  CONSTRAINT `fk_paciente_profissional_paciente`
    FOREIGN KEY (`paciente_id`) REFERENCES `paciente` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_paciente_profissional_profissional`
    FOREIGN KEY (`profissional_id`) REFERENCES `profissional` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sintoma` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `descricao` VARCHAR(255) NOT NULL,
  `categoria` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `peso_sintoma` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sintoma_id` INT NOT NULL,
  `sexo_referencia` ENUM('masculino', 'feminino') NOT NULL,
  `peso` FLOAT NOT NULL,
  `atualizado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_peso_sintoma_sintoma` (`sintoma_id`),
  CONSTRAINT `fk_peso_sintoma_sintoma`
    FOREIGN KEY (`sintoma_id`) REFERENCES `sintoma` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `limiar_decisao` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sexo` ENUM('masculino', 'feminino') NOT NULL,
  `valor` FLOAT NOT NULL,
  `atualizado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `avaliacao` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `paciente_id` INT NOT NULL,
  `profissional_id` INT NOT NULL,
  `limiar_decisao_id` INT NOT NULL,
  `score_calculado` FLOAT NOT NULL,
  `encaminhar` BOOLEAN NOT NULL DEFAULT FALSE,
  `observacao` VARCHAR(500) NULL,
  `etapa_jornada` VARCHAR(80) NOT NULL DEFAULT 'pre_avaliacao',
  `requisicao_medica` TEXT NULL,
  `triagem_clinica` TEXT NULL,
  `triagem_socioeconomica` TEXT NULL,
  `encaminhamento_exame` TEXT NULL,
  `resultado_exame` VARCHAR(40) NOT NULL DEFAULT 'aguardando',
  `tipo_resultado` VARCHAR(40) NULL,
  `plano_pos_diagnostico` TEXT NULL,
  `suporte_pos_diagnostico` TEXT NULL,
  `realizado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_avaliacao_paciente` (`paciente_id`),
  KEY `idx_avaliacao_profissional` (`profissional_id`),
  KEY `idx_avaliacao_limiar` (`limiar_decisao_id`),
  CONSTRAINT `fk_avaliacao_paciente`
    FOREIGN KEY (`paciente_id`) REFERENCES `paciente` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_avaliacao_profissional`
    FOREIGN KEY (`profissional_id`) REFERENCES `profissional` (`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_avaliacao_limiar`
    FOREIGN KEY (`limiar_decisao_id`) REFERENCES `limiar_decisao` (`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `avaliacao_sintoma` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `avaliacao_id` INT NOT NULL,
  `sintoma_id` INT NOT NULL,
  `presente` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`id`),
  KEY `idx_avaliacao_sintoma_avaliacao` (`avaliacao_id`),
  KEY `idx_avaliacao_sintoma_sintoma` (`sintoma_id`),
  CONSTRAINT `fk_avaliacao_sintoma_avaliacao`
    FOREIGN KEY (`avaliacao_id`) REFERENCES `avaliacao` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_avaliacao_sintoma_sintoma`
    FOREIGN KEY (`sintoma_id`) REFERENCES `sintoma` (`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `familiar_paciente` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `paciente_id` INT NOT NULL,
  `nome` VARCHAR(120) NOT NULL,
  `parentesco` VARCHAR(80) NULL,
  `telefone` VARCHAR(20) NULL,
  `email` VARCHAR(120) NULL,
  `momento_cadastro` VARCHAR(30) NOT NULL DEFAULT 'pre_avaliacao',
  `observacao` VARCHAR(500) NULL,
  `criado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_familiar_paciente` (`paciente_id`),
  CONSTRAINT `fk_familiar_paciente`
    FOREIGN KEY (`paciente_id`) REFERENCES `paciente` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `documento_paciente` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `paciente_id` INT NOT NULL,
  `descricao` VARCHAR(160) NOT NULL,
  `tipo_documento` VARCHAR(80) NOT NULL DEFAULT 'avaliacao_anterior',
  `origem` VARCHAR(160) NULL,
  `nome_arquivo` VARCHAR(255) NULL,
  `caminho_arquivo` VARCHAR(255) NULL,
  `criado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_documento_paciente` (`paciente_id`),
  CONSTRAINT `fk_documento_paciente`
    FOREIGN KEY (`paciente_id`) REFERENCES `paciente` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
