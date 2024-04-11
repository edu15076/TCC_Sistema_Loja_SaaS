CREATE TABLE contratante (
    username varchar(63) NOT NULL,
    senha varchar(255) NOT NULL,
    cnpj varchar(14) NOT NULL UNIQUE,
    id bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    -- Dados de pessoa
    nome varchar(31) NOT NULL,
    sobrenome varchar(63),
    nascimento date,
    email varchar(127) NOT NULL,
    telefone varchar(13)
);

-- Decidi criar uma tabela loja no caso de, futuramente, ser necessario poder adicionar varias loja a um contratante, em uma especie de franquia
CREATE TABLE loja (
    nome_da_empresa varchar(63),
    logo bytea,

    -- Relacao com contratante
    id_contratante bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    CONSTRAINT fk_contratante FOREIGN KEY (id_contratante)
                  REFERENCES contratante(id)
);

CREATE TABLE cartao (
    numero bigint NOT NULL,
    bandeira int NOT NULL,
    codigo int NOT NULL,
    id bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    -- Dados do endereco
    cep varchar(14) NOT NULL,
    numero_endereco int NOT NULL,

    -- Relacao com contratante
    id_contratante bigint NOT NULL,

    CONSTRAINT fk_contratante FOREIGN KEY (id_contratante)
                    REFERENCES contratante(id)
);

CREATE TABLE gerente_de_contrato (
    email varchar(127) NOT NULL UNIQUE,
    senha varchar(255) NOT NULL,
    id bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY
);

CREATE TABLE periodicidade (
    qtd_periodos int NOT NULL,
    qtd_dias_por_periodo int NOT NULL,
    id bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    CONSTRAINT unique_together_qtds UNIQUE (qtd_periodos, qtd_dias_por_periodo)
);

CREATE TABLE contrato (
    ativo boolean NOT NULL DEFAULT true,
    descricao varchar(1023),
    preco float NOT NULL,
    documento bytea,
    taxa_de_multa float,
    tolerancia int, -- Em dias
    processamento int, -- Tempo de processamento em ms diarios
    memoria int, -- memoria maxima utilizada em um momento em MB
    armazenamento int, -- armazenamento em GB
    id bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    -- Relacao com periodicidade
    id_periodicidade bigint NOT NULL,

    CONSTRAINT fk_periodicidade FOREIGN KEY (id_periodicidade)
                      REFERENCES periodicidade(id)
);

CREATE TABLE contrato_assinado (
    vigente boolean NOT NULL DEFAULT true,
    data_contratacao date NOT NULL,
    id bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    -- Relacao com contrato
    id_contrato bigint NOT NULL,

    CONSTRAINT fk_contrato FOREIGN KEY (id_contrato)
                               REFERENCES contrato(id),

    -- Relacao com contratante
    id_contratante bigint NOT NULL,

    CONSTRAINT fk_contratante FOREIGN KEY (id_contratante)
                               REFERENCES contratante(id)
);

CREATE TABLE historico_pagamento (
    valor_a_ser_pago float NOT NULL,
    data_pagamento date, -- Se NULL nao foi pago ainda
    data_inicio_prazo date NOT NULL,
    data_fim_prazo date NOT NULL,
    id bigint NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    -- Relacao com contrato_assinado
    id_contrato_assinado bigint NOT NULL,

    CONSTRAINT fk_contrato_assinado FOREIGN KEY (id_contrato_assinado)
                                 REFERENCES contrato_assinado(id)
);
