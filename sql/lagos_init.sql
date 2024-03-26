# Cria usuário do subsistema de contratos
insert into pessoa (nome, sobrenome, nascimento, email, telefone)
values ('José', 'Judeu', '2006-07-15', 'eduardbh2014@gmail.com', 32999781209);
insert into usuario (tipo, username, senha, pk)
values (1, 'jew', 'dfssadfouihfrfq$9efwhqsaf', (select last_insert_id()));
set @usuario_contratante := (select last_insert_id());

# Adiciona cartão ao usuário
insert into endereco (cep, numero)
values (12345678, 1234);
set @endereco := (select last_insert_id());
insert into cartao (numero, bandeira, endereco__fk, usuario__fk)
values (1243525235432324, 1, (select @endereco), (select @usuario_contratante));

# Cria contrato
insert into periodicidade (periodo, quantidade_dias_por_periodo)
values (2, 365);
insert into contrato (ativo, preco, numero_de_lojas, data_de_criacao, periodicidade__fk)
values (true, 2500, 10, '2022-10-18', (select last_insert_id()));

# Assina contrato
insert into contrato_assinado (data_de_contratacao, cancelado, usuario__fk, contrato__fk)
values ('2023-08-18', false, (select @usuario_contratante), (select last_insert_id()));

# Configura interface
insert into configuracoes_de_interface (nome_da_empresa, cor_base, pk)
values ('LOSH', '#000000', (select @usuario_contratante));

# Cria uma loja, e gera, automaticamente, uma configuração de venda padrão
insert into loja (endereco__fk, usuario__fk)
values ((select @endereco), (select @usuario_contratante));
insert into configuracoes_de_venda (limite_de_desconto, taxa_de_juros_ao_mes, porcentagem_comissao, pk)
values (0.10, 0.10, 0.05, 1);

# Contratante cria chefe para uma loja
insert into pessoa (nome, sobrenome, nascimento, email, telefone)
values ('Chefe', 'Mau', '1968-09-12', 'che@yahoo.com', 32999781234);
insert into funcionario (salario, ativo, tipo_funcionario, pk, loja__fk)
values (8000, true, 0, (select last_insert_id()), 1);
insert into usuario_loja (username, senha, pk)
values ('che', 'pohuf8ygwefq7rgo8723r', (select last_insert_id()));

# Chefe cria um vendedor
insert into pessoa (nome, sobrenome, nascimento, email, telefone)
values ('Wr', 'Sz', '1900-04-13', 'abril@gmail.com', 32999781209);
insert into funcionario (salario, ativo, tipo_funcionario, pk, loja__fk)
values (1200, true, 1, (select last_insert_id()), 1);
set @vendedor := (select last_insert_id());

# Chefe cria um caixeiro
insert into pessoa (nome, sobrenome, nascimento, email, telefone)
values ('Cai', 'Xa', '2000-08-09', 'caixa@hotmail.com', 32999781209);
insert into funcionario (salario, ativo, tipo_funcionario, pk, loja__fk)
values (1300, true, 2, (select last_insert_id()), 1);
insert into usuario_loja (username, senha, pk)
values ('caixaa', '4302-598dfsqg0', (select last_insert_id()));

# Gerente cria um caixa
insert into caixa (aberto, dinheiro_em_caixa, usuario_loja__fk, loja__fk)
values (false, 26.5, (select last_insert_id()), 1);
set @caixa := (select last_insert_id());
insert into fluxo_de_caixa (dinheiro_em_caixa, tipo, hora, caixa__fk)
values (26.5, 0, '2023-09-19 09:07:48', (select @caixa));

# Chefe tira 0.50 centavos do caixa
update caixa set dinheiro_em_caixa = 26 where pk = (select @caixa);
insert into fluxo_de_caixa (dinheiro_em_caixa, tipo, hora, caixa__fk)
values (26, 1, '2023-09-19 09:08:57', (select @caixa));

# Gerente altera configurações de venda
update configuracoes_de_venda set limite_de_desconto = 0.5 where pk = 1;

# Gerente cria compra e insere produtos comprados
insert into compra (data_de_compra, loja__fk)
values ('2023-09-29', 1);
set @compra1 := (select last_insert_id());

insert into produto (codigo, nome, quantidade, preco, loja__fk)
values ('qg4352df', 'Luminaria de cavalo', 0, 199.99, 1);
set @luminaria := (select last_insert_id());
insert into produto_compra (quantidade, preco_unitario, compra__fk, produto__fk)
values (10, 100, (select @compra1), (select last_insert_id()));

insert into produto (codigo, nome, quantidade, preco, loja__fk)
values ('jf34990', 'Limpa tudo', 0, 7.99, 1);
set @limpa := (select last_insert_id());
insert into produto_compra (quantidade, preco_unitario, compra__fk, produto__fk)
values (100, 3, (select @compra1), (select last_insert_id()));

# Outra compra é realizada, primeiro inserem-se os produtos e depois se realiza a compra daqueles
insert into compra (data_de_compra, loja__fk)
values ('2023-10-05', 1);
set @compra2 := (select last_insert_id());

insert into produto_compra (quantidade, preco_unitario, compra__fk, produto__fk)
values (14, 110, (select @compra2), (select @luminaria));

# Compra chega e altera todo produto relacionado àquela compra
update compra set data_de_chegada = '2023-10-15' where pk = (select @compra1);
# update produto
update produto
    inner join produto_compra on produto.pk = produto_compra.produto__fk
set produto.quantidade = produto.quantidade + produto_compra.quantidade
where produto_compra.compra__fk = (select @compra1);

# Cria promoção para luminaria, a promoção começara a ser aplicada a partir da data de inicio
insert into periodicidade (periodo, quantidade_dias_por_periodo)
values (4, 1);
insert into promocao (porcentagem, ativa, data_inicio, periodicidade__fk, loja__fk)
values (.1, true, '2023-10-30', (select last_insert_id()), 1);
insert into promocoes__produtos (produto__fk, promocao__fk)
values ((select last_insert_id()), (select @luminaria));

# Cria promoção de fidelidade para a luminaria
insert into periodicidade (periodo, quantidade_dias_por_periodo)
values (4, 1);
insert into promocao_de_fidelidade (min_vendas, porcentagem, ativa, data_inicio, periodicidade__fk, loja__fk)
values (1, .2, true, '2023-10-30', (select last_insert_id()), 1);
insert into promocoes_de_fidelidade__produtos (produto__fk, promocao_de_fidelidade__fk)
values ((select last_insert_id()), (select @luminaria));

# Cria cliente
insert into pessoa (nome, sobrenome, nascimento, email, telefone)
values ('Cl', 'iente', '1987-05-19', 'eugostodepagarcaro@gmail.com', 23451542365);
insert into cliente (instagram, cadastro, pk, loja__fk)
values ('semOArroba', '2023-10-16', (select last_insert_id()), 1);
set @cliente := (select last_insert_id());

# Cliente compra pela primeira vez no dia 2023-10-16
insert into historico_vet (tipo, data, loja__fk)
values (1, '2023-10-16 13:53:00', 1);
set @hv1 := (select last_insert_id());

insert into item (preco, quantidade, historico_vet__fk, produto__fk)
values ((select (preco) from produto where pk = (select @luminaria)), 3, (select @hv1), (select @luminaria));
insert into item (preco, quantidade, historico_vet__fk, produto__fk)
values ((select (preco) from produto where pk = (select @limpa)), 10, (select @hv1), (select @limpa));

insert into venda (desconto, numero_de_parcelas, pk, caixa__fk, funcionario__fk, cliente__fk)
values (0.05, 2, (select @hv1), (select @caixa), (select @vendedor), (select @cliente));

update produto
    inner join item on item.produto__fk = produto.pk
set produto.quantidade = produto.quantidade - item.quantidade
where item.historico_vet__fk = (@hv1);

insert into promocoes__vendas (promocao__fk, venda__fk)
select pk, (select @hv1)
from promocao
where '2023-10-16' between data_inicio
          and adddate(data_inicio, (select (periodo * periodicidade.quantidade_dias_por_periodo)
                                    from periodicidade
                                    where pk = periodicidade__fk));

insert into promocoes_de_fidelidade__vendas (promocao_de_fidelidade__fk, venda__fk)
select promocao_de_fidelidade.pk, (select @hv1)
from promocao_de_fidelidade
where '2023-10-16' between data_inicio
    and adddate(data_inicio, (select (periodo * periodicidade.quantidade_dias_por_periodo)
                              from periodicidade
                              where pk = periodicidade__fk))
  and (select count(*) from venda where cliente__fk = (select @cliente)) >= min_vendas;

# Compra chega
update compra set data_de_chegada = '2023-10-20' where pk = (select @compra2);
# update produto
update produto
    inner join produto_compra on produto.pk = produto_compra.produto__fk
set produto.quantidade = produto.quantidade + produto_compra.quantidade
where produto_compra.compra__fk = (select @compra2);

# Altera preço da luminária
update produto set preco = 249.99 where pk = (select @luminaria);

# Cliente compra pela segunda vez
insert into historico_vet (tipo, data, loja__fk)
values (1, '2023-10-30 13:53:00', 1);
set @hv2 := (select last_insert_id());

insert into item (preco, quantidade, historico_vet__fk, produto__fk)
values ((select (preco) from produto where pk = (select @luminaria)), 1, (select @hv2), (select @luminaria));

insert into venda (numero_de_parcelas, pk, caixa__fk, funcionario__fk, cliente__fk)
values (2, (select @hv2), (select @caixa), (select @vendedor), (select @cliente));

update produto
    inner join item on item.produto__fk = produto.pk
set produto.quantidade = produto.quantidade - item.quantidade
where item.historico_vet__fk = (@hv2);

insert into promocoes__vendas (promocao__fk, venda__fk)
select pk, (select @hv2)
from promocao
where '2023-10-30' between data_inicio
          and adddate(data_inicio, (select (periodo * periodicidade.quantidade_dias_por_periodo)
                                    from periodicidade
                                    where pk = periodicidade__fk));

insert into promocoes_de_fidelidade__vendas (promocao_de_fidelidade__fk, venda__fk)
select promocao_de_fidelidade.pk, (select @hv2)
from promocao_de_fidelidade
where '2023-10-30' between data_inicio
    and adddate(data_inicio, (select (periodo * periodicidade.quantidade_dias_por_periodo)
                              from periodicidade
                              where pk = periodicidade__fk))
  and (select count(*) from venda where cliente__fk = (select @cliente)) >= min_vendas;
