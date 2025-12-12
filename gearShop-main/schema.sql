CREATE DATABASE IF NOT EXISTS gearshop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gearshop;

CREATE TABLE IF NOT EXISTS usuarios (
  cpf            VARCHAR(14)  NOT NULL,
  nome           VARCHAR(120) NOT NULL,
  email          VARCHAR(255) NOT NULL,
  telefone       VARCHAR(20)  NOT NULL,
  senha          VARCHAR(255) NOT NULL,
  nascimento     DATE         NOT NULL,
  endereco       VARCHAR(255) NULL,
  created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (cpf),
  UNIQUE KEY uq_usuarios_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS produtos (
  id             INT           NOT NULL AUTO_INCREMENT,
  nome           VARCHAR(120)  NOT NULL,
  categoria      ENUM('motor','suspensao','eletrica','iluminacao','interno','lataria','rodas','acessorios') NOT NULL,
  preco          DECIMAL(10,2) NOT NULL,
  condicao       ENUM('novo','seminovo','usado') NOT NULL,
  descricao      TEXT          NOT NULL,
  localizacao    CHAR(2)       NOT NULL,
  imagem_url     VARCHAR(255)  NOT NULL DEFAULT '/static/uploads/placeholder.png',
  status         ENUM('ativo','vendido') NOT NULL DEFAULT 'ativo',
  usuario_cpf    VARCHAR(14)   NOT NULL,
  created_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_produtos_usuario (usuario_cpf),
  KEY idx_produtos_categoria (categoria),
  KEY idx_produtos_condicao (condicao),
  KEY idx_produtos_status (status),
  CONSTRAINT fk_produtos_usuario FOREIGN KEY (usuario_cpf)
    REFERENCES usuarios(cpf)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS compras (
  id             INT           NOT NULL AUTO_INCREMENT,
  produto_id     INT           NOT NULL,
  comprador_cpf  VARCHAR(14)   NOT NULL,
  preco          DECIMAL(10,2) NOT NULL,
  created_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_compras_comprador (comprador_cpf),
  KEY idx_compras_produto (produto_id),
  CONSTRAINT fk_compras_produto FOREIGN KEY (produto_id)
    REFERENCES produtos(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT fk_compras_comprador FOREIGN KEY (comprador_cpf)
    REFERENCES usuarios(cpf)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB;
