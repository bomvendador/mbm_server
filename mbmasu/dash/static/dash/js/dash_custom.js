
$('#dash_logout').on('click', function (e) {
    let token = '{{ csrf_token }}';
    e.preventDefault()
    $.ajax({
        headers: { "X-CSRFToken": token },
        url: "{% url 'dash_logout' %}",
        type: 'POST',

        processData: false,
        contentType: false,
        error: function(data){
            toastr.error('Ошибка', data)
        },
        success:function (data) {
            console.log('logout')
            window.location.href = "{% url 'login_index' %}";
        }
    });

})

function add_hover_menu(selector) {
        $(selector).find('a').css('background-color', 'rgba(255,255,255,.1)').css('color', '#fff')

}

function setTextToHtml(elID, val){
    let html2 = $(elID).text()
    $(elID).html(html2)
    // $(elID).height($(elID).outerHeight(true));

}
