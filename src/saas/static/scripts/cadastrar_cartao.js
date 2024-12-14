const publicKey = $("#payment-form").data("public-key");
console.info('Public Key', publicKey);
const stripe = Stripe(publicKey);
const elements = stripe.elements();

let card = elements.create("card", {
    style: {
        base: {
            fontSize: '1rem',
            fontWeight: '400',
            lineHeight: '25px',
            color: '#dee2e6',
            '::placeholder': {
                color: '#aab7c4',
                "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
            },
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545',
        },
    },
    classes: {
        base: "textinput payment-method form-control"
    },
});
card.mount("#card-element");

const $cadastroCartaoBtn = $("#payment-form button");
$cadastroCartaoBtn.click(function () {
    stripe.createToken(card).then(function (result) {
        if (result.error) {
            console.error(result.error.message);
        } else {
            const csrfToken = $("#payment-form input[name=csrfmiddlewaretoken]").val()
            //Extrair informações da resposta do Stripe
            const cardData = {
                'csrfmiddlewaretoken': csrfToken,
                'token': result.token.id,
                'cep': $("#id_cep").val(),
                'numero_residencial': $("#id_numero_residencial").val(),
                'complemento': $("#id_complemento").val(),
                'nome_titular': $("#id_nome_titular").val(),
                [$cadastroCartaoBtn.attr('name')]: $cadastroCartaoBtn.attr('value')
            };

            fetch("/metodos_pagamento/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(cardData),
            })
            .then((response) => {
                if (response.status !== 200) {
                    throw new Error(`Erro na requisição: ${response.status}`);
                }
                
                return response.text(); 
            })
            .then((html) => {
                let $html = $(html);

                if ($html.is('#metodos-de-pagamento-conteudo')) {
                        $('#conteudo').prepend($html);
                } else {
                    $("#lista-metodos-pagamento > div").prepend($html);
                } 
                
                $('#addCartaoModal').modal('hide');
                $("#payment-form")[0].reset();
                $("input[name=csrfmiddlewaretoken]").val(csrfToken);
            
                card.unmount(); 
                card.mount('#card-element');
            
                let $avisoSemCartoesDiv = $('#aviso-sem-cartoes');
                if ($avisoSemCartoesDiv.length > 0) {
                    $avisoSemCartoesDiv.remove();
                }
                let $avisoUnicoCartao = $('#aviso-unico-cartao')
                if ($avisoUnicoCartao.length > 0) {
                    $avisoUnicoCartao.remove();
                }
                $('#conteudo').removeClass('d-none');
            })
            .catch((error) => {
                console.error(error);
            });
        }
    });
});
