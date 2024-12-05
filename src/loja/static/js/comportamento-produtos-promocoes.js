$('.linha-promocao button').click(function() {
    $('#duplicar-promocao-form').attr('hx-vals', JSON.stringify({'promocao': $(this).attr('data-promocao-id')}));
});