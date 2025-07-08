var csrftoken = Cookies.get('csrftoken');
$(function () {
    {% load static %}
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
            };
    var GenerarReporte = function () {
            let url = $(this).attr('url');
            var control = '';
            var nombre_archivo = 'listado.xls'; // por las dudas si no viene
            $.LoadingOverlay("show",
                    {
                        image           : "{% static 'coffaa/logo.png' %}",
                        background      : "rgba(0, 0, 0, 0.5)",
                        imageAnimation  : "1.5s fadein",
                        imageColor      : "#ffcc00",
//                        text                    : "Descargando archivo...",                                // String/Boolean
//                        textAnimation           : "True",                                // String/Boolean
//                        textAutoResize          : "true",                              // Boolean
//                        textResizeFactor        : 0.3,                               // Float
//                        textColor               : "#ffcc00",                         // String/Boolean
//                        textClass               : "",                                // String/Boolean
//                        textOrder               : 5,                                 // Integer
                    });
            fetch(url)
              .then(function(response) {
                if (response.ok) {
                     control = response.headers.get('X-control');
                     nombre_archivo = response.headers.get('X-nombre-archivo');
                  return response.blob();
                } else {
                  throw new Error('Error al descargar el archivo');
                }
              })
              .then(function(blob) {
                if (control == 1) {
                    // Crear un enlace temporal para descargar el archivo
                    var url1 = window.URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url1;
//                    a.download = 'locales.xls';
                    a.download = nombre_archivo;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    $.LoadingOverlay("hide");
                } else {
                        $.LoadingOverlay("hide");
                         Swal.fire({
                         position: 'center',
                         text: 'No hay registros para exportar',
                         showConfirmButton: false,
                         timer: 2500
                     });
                }

              })
              .catch(function(error) {
                console.log(error);
              });
    };
    $('#reporte-locales').on('click', GenerarReporte)
    $('#exportar-nov-en-locales-excel').on('click', GenerarReporte)
    $('#exportar-veh-propios-excel').on('click', GenerarReporte)
    $('#exportar-veh-propios-empleo-excel').on('click', GenerarReporte)
    $('#exportar-movimientos-excel').on('click', GenerarReporte)
//    $('#exportar-resumen-pers-jerarquia-tipo-excel').on('click', GenerarReporte)
    $('#exportar-resumen-general').on('click', GenerarReporte)
    $('#exportar-lugar-interes').on('click', GenerarReporte)
    $('#exportar-guia').on('click', GenerarReporte)
    $('#exportar-nov-grl-excel').on('click', GenerarReporte)
    $('#exportar-personal-excel').on('click', GenerarReporte)
    $('#exportar-veh-contratados-excel').on('click', GenerarReporte)
    $('#exportar-veh-contratados-empleo-excel').on('click', GenerarReporte)
    $('#exportar-led-excel').on('click', GenerarReporte)
    $('#exportar-sed-excel').on('click', GenerarReporte)





});
