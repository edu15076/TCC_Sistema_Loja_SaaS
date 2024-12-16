const carregarModalLotes = () => {
    $('#quantidadeLotesModal').modal('show');
    document.querySelector('#produto-form form').reset();
}

let itens = []
let precoTotal = 0;
let descontoTotal = 0;
let precoFinal = 0;

const permitirVenda = () => {
    if (itens.length > 0) {
        $('#finalizar-venda-btn').removeClass('btn-secondary');
        $('#finalizar-venda-btn').addClass('btn-primary');
        $('#finalizar-venda-btn').attr('data-bs-target', '#vendaModal');
    } else {
        $('#finalizar-venda-btn').removeClass('btn-primary');
        $('#finalizar-venda-btn').addClass('btn-secondary');
        $('#finalizar-venda-btn').attr('data-bs-target', '');
    }
}

const setValoresTabela = () => {
    $('.total-venda').text('R$ ' + formatMoeda(precoTotal));
        $('.desconto-venda').text('R$ ' + formatMoeda(descontoTotal));
}

const resetValoresTabela = () => {
    $('.total-venda').text('R$ 0,00');
    $('.desconto-venda').text('R$ 0,00');
}

const removerItemVenda = (produto) => {
    const index = itens.findIndex(item => item.produto === produto);
    itens.splice(index, 1);
    const item = $(`#item-${produto}`);
    const itemForm = $(`#${produto}-form`);
    item.remove();
    itemForm.remove();
    permitirVenda();
}

const carregarItem = (event) => {
    console.log(event.detail.xhr.status)
    if (event.detail.xhr.status === 200) {
        const response = event.detail.xhr.response;
        const data = JSON.parse(response);

        precoTotal += data.preco_total;
        descontoTotal += data.desconto_total;
        precoFinal += data.preco_final;

        setValoresTabela();
    
        let $novaLinha = $(data.linha_tabela_item);
        const existingRow = $('#itens-venda-lista').find(`#${$novaLinha.attr('id')}`);
        if (existingRow.length) {
            existingRow.replaceWith($novaLinha);
        } else {
            $('#itens-venda-lista').prepend($novaLinha);
        }

        let $novaLinhaForm = $(data.linha_tabela_form_item);
        console.log($novaLinhaForm);
        const existingFormRow = $('#itens-venda-form-lista').find(`#${$novaLinhaForm.attr('id')}`);
        if (existingFormRow.length) {
            existingFormRow.replaceWith($novaLinhaForm);
        } else {
            $('#itens-venda-form-lista').prepend($novaLinhaForm);
        }

        data.itens.forEach((novoItem) => {
            const index = itens.findIndex(item => item.lote === novoItem.lote);
            if (index !== -1) {
                itens[index] = novoItem;
            } else {
                itens.push(novoItem);
            }
        });
        
        $('#quantidadeLotesModal').modal('hide').on('hidden.bs.modal', function () {
            $(this).remove();
        });
        
        permitirVenda();
    }
}

const coletarItensVenda = () => {
    return JSON.stringify(itens);
}

$('#id_valor_pago').on('change', function() {
    console.log('mudou');
    const valorPago = parseFloat($(this).val());
    const troco = valorPago - precoFinal;
    if (troco > 0) {
        $('#divida-label').addClass('d-none');
        $('#troco').text('R$ ' + formatMoeda(troco));
        $('#troco-label').removeClass('d-none');
    } else if (troco < 0) {
        $('#troco-label').addClass('d-none');
        $('#divida').text('R$ ' + formatMoeda(-troco));
        $('#divida-label').removeClass('d-none');
    }
});

const vendaEfetuada = () => {
    $('#vendaModal').modal('hide').on('hidden.bs.modal', function () {
        document.querySelector('#venda-form').reset();
        $('#modalResultadoVenda').modal('show');
    });
    itens = [];
    precoTotal = 0;
    descontoTotal = 0;
    precoFinal = 0;
    resetValoresTabela();
    $('#itens-venda-lista').empty();
    permitirVenda();
}