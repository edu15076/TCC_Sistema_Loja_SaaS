function colectItensVenda() {
    itens = [];

    $(".item-venda").each(function() {
        let item = {
            'codigo_de_barras':$(this).data().produtoCodigoDeBarras,
            'quantidade':$(this).data().itemQuantidade
        };

        itens.push(item);
    });

    // $('#venda-form form').attr('hx-vals', '{itens:' + JSON.stringify(itens) + '}');
    // console.log('{"itens":' + JSON.stringify(itens) + '}')
    return JSON.stringify(itens)
}