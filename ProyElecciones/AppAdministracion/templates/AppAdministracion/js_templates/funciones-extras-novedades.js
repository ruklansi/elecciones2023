var csrftoken = Cookies.get('csrftoken');
$(function () {
    $.ajaxSetup({
        statusCode: {403:function(xhr,errmsg,err){
            window.location = xhr.responseJSON.redirect_to;
        }},
    });
    function comprobarSesion(){
        $.ajax({
            url: window.location.pathname,
            type: "get",
            dataType: "json",
        });
    }
     $("#id_rol").select2({
       theme: "bootstrap4",
       language: "es",
       placeholder: "Click para seleccionar",
   });
   $("#id_grupo").select2({
       theme: "bootstrap4",
       language: "es",
       placeholder: "Click para seleccionar",
   });

});