$(document).on('blur', '.check-on-blur', function(e) {
    if (!this.checkValidity())
        this.reportValidity();
});