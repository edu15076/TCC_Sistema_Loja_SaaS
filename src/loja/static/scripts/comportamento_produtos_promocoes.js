$('.linha-promocao button').click(function() {
    console.log($(this).attr('data-promocao-id'));
    $('#duplicar-promocao-form').attr('hx-vals', JSON.stringify({'promocao': $(this).attr('data-promocao-id')}));
});

const updatePrecoVendaSpan = (event) => {
    if (event.detail.xhr.status === 200) {
        let response = JSON.parse(event.detail.xhr.response);
        $('#preco-valor').html(formatMoeda(response.preco_de_venda));
    }
}

const updateLimiteDescontoSpan = (event) => {
    if (event.detail.xhr.status === 200) {
        let response = JSON.parse(event.detail.xhr.response);

        $('#limite_porcentagem_desconto_maximo').html(formatPorcentagem(response.limite_porcentagem_desconto_maximo));
    }
}
