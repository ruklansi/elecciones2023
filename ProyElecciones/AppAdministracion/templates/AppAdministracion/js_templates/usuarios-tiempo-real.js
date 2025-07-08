var csrftoken = Cookies.get('csrftoken');
$(function () {
//           document.body.addEventListener('htmx:wsAfterMessage', (e) => {
//                console.log('entro')
//                let personas = '';
//                personas = JSON.parse(e.detail.message)
//                console.log(personas)
//                if (personas[0]['accion'] === 'inicio_sesion'){
//                    var ul = document.getElementById('miLista')
//                    agregarUsuario(personas[0]['datos_user']);
//                    function agregarUsuario(element) {
//                        var li = document.createElement('li');
//                        li.setAttribute('class','resaltar_usuario');
//                        li.setAttribute('id',personas[0]['id_estado']);
//                        ul.appendChild(li);
//                        li.innerHTML=li.innerHTML + element;
//                    };
//                }
//                 else {
//                    $('#'+personas[0]['id']).remove();
//
//                 }
//            });

});
