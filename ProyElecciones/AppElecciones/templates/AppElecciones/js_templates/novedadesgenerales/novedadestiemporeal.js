var csrftoken = Cookies.get('csrftoken');

$(function () {
     $(window).on('map:init', function (e) {
//          var audio = document.createElement("AUDIO")
//          document.body.appendChild(audio);
//          audio.src = '/media/misil.mp3'
          var detail = e.detail;

          document.body.addEventListener('htmx:wsAfterMessage', (datos) => {
//          audio.play();
            



            let  mensaje = JSON.parse(datos.detail.message)

            let cant_criticas = mensaje.contadores.cant_criticas
            let cant_altas =mensaje.contadores.cant_medias
            let cant_medias = mensaje.contadores.cant_altas
            $('#cant_criticas').html('Críticas: '+ cant_criticas)
            $('#cant_altas').html('Altas: '+ cant_altas)
            $('#cant_medias').html('Medias: '+ cant_medias)

            let longitud = parseFloat(mensaje.mapa.longitud)
            let latitud = parseFloat(mensaje.mapa.latitud)

            if (mensaje.mapa.subsanada == 'No'){
                if (mensaje.mapa.nivel == '1'){
                              L.circleMarker([latitud, longitud],{
                                  radius: 4.0,
                                  fillColor: '#ffff73',
                                  color: '#000000',
                                  weight: 1,
                                  opacity: 1.0,
                                  fillOpacity: 1.0
                                  }).bindPopup('Subsanada: '+ '<span class="estilo_en_mapa_no_subsanada">'+mensaje.mapa.subsanada+ '</span>'+ '<br> Distrito: ' + mensaje.mapa.distrito + '<br> Fecha/hora: ' + mensaje.mapa.fecha_novedad +' <br> Tipo: '+mensaje.mapa.tipo + '<br> Detalle: ' + mensaje.mapa.detalle + '<br> Medidas adoptadas: ' + mensaje.mapa.medidas_adoptadas).addTo(detail.map)
                }
                if (mensaje.mapa.nivel == '2'){
                            L.circleMarker([latitud, longitud],{
                                radius: 4.0,
                                fillColor: '#ffaa00',
                                color: '#000000',
                                weight: 1,
                                opacity: 1.0,
                                fillOpacity: 1.0
                                }).bindPopup('Subsanada: '+ '<span class="estilo_en_mapa_no_subsanada">'+mensaje.mapa.subsanada+ '</span>'+ '<br> Distrito: ' + mensaje.mapa.distrito + '<br> Fecha/hora: ' + mensaje.message.mapa.fecha_novedad +' <br> Tipo: '+mensaje.mapa.tipo + '<br> Detalle: ' + mensaje.mapa.detalle + '<br> Medidas adoptadas: ' + mensaje.mapa. medidas_adoptadas).addTo(detail.map)
                }
                if (mensaje.mapa.nivel == '3'){
                          L.circleMarker([latitud, longitud],{
                              radius: 4.0,
                              fillColor: 'red',
                              color: '#000000',
                              weight: 1,
                              opacity: 1.0,
                              fillOpacity: 1.0
                              }).bindPopup('Subsanada: '+ '<span class="estilo_en_mapa_no_subsanada">'+mensaje.mapa.subsanada+ '</span>'+ '<br> Distrito: ' + mensaje.mapa.distrito + '<br> Fecha/hora: ' + mensaje.mapa.fecha_novedad +' <br> Tipo: '+mensaje.mapa.tipo + '<br> Detalle: ' + mensaje.mapa.detalle + '<br> Medidas adoptadas: ' + mensaje.mapa.medidas_adoptadas).addTo(detail.map)
                }
            }

            const search = new GeoSearch.GeoSearchControl({
              //provider: new GeoSearch.OpenStreetMapProvider(),
              provider: new GeoSearch.EsriProvider(),
              searchLabel: 'Ingrese la dirección...',
              notFoundMessage: 'No hay resultados',
              retainZoomLevel: true,
              showMarker: true,
              selected: 0,
              autoClose: true,
              keepResult: true
            });
            detail.map.addControl(search);
            detail.map.setView([-40,-59],3)
//            detail.map.spin(true, {lines: 15, length: 20});
         });
          $.ajax({
                url: "{% url 'novedades-tiempo-real' %}",
                type: "POST",
                headers: { 'X-CSRFToken': csrftoken },
                dataType: "json",
                data: { 'accion': 'cargar-nov-tiempo-real' },
                success: function (data) {
//                     detail.map.spin(false);
//                     console.log(data)
                      //Borro las novedades que estaban en el mapa
                      detail.map.eachLayer(function (layer) {
                        if (layer instanceof L.CircleMarker) {
                            detail.map.removeLayer(layer);
                        }
                      });
                      //Mustro los resumenes de novedades
                       let cant_criticas = 0
                       let cant_altas = 0
                       let cant_medias = 0
                       if (data.cant_criticas !== 0){
                        cant_criticas = data.cant_criticas
                       }
                       if (data.cant_altas !== 0){
                        cant_altas = data.cant_altas
                       }
                       if (data.cant_medias !== 0){
                        cant_medias = data.cant_medias
                       }
                       $('#cant_criticas').html('Críticas: '+ cant_criticas)
                       $('#cant_altas').html('Altas: '+ cant_altas)
                       $('#cant_medias').html('Medias: '+ cant_medias)
                       var grupo_marcadores = new L.featureGroup;

                        $.each(data.datos, function( clave, valor ) {
                            let longitud = parseFloat(valor.longitud)
                            let latitud = parseFloat(valor.latitud)
                            if (valor.nivel == '1'){
                                marcador =   L.circleMarker([latitud, longitud],{
                                      radius: 4.0,
                                      fillColor: '#ffff73',
                                      color: '#000000',
                                      weight: 1,
                                      opacity: 1.0,
                                      fillOpacity: 1.0
                                      }).bindPopup('Subsanada: '+ '<span class="estilo_en_mapa_no_subsanada">'+valor.subsanada+ '</span>'+ '<br> Distrito: ' + valor.distrito + '<br> Fecha/hora: ' + valor.fecha_novedad +' <br> Tipo: '+valor.tipo + '<br> Detalle: ' + valor.detalle + '<br> Medidas adoptadas: ' + valor.medidas_adoptadas).addTo(detail.map)
                                      grupo_marcadores.addLayer(marcador);
                                }
                            if (valor.nivel == '2'){
                               marcador = L.circleMarker([latitud, longitud],{
                                    radius: 4.0,
                                    fillColor: '#ffaa00',
                                    color: '#000000',
                                    weight: 1,
                                    opacity: 1.0,
                                    fillOpacity: 1.0
                                    }).bindPopup('Subsanada: '+ '<span class="estilo_en_mapa_no_subsanada">'+valor.subsanada+ '</span>'+ '<br> Distrito: ' + valor.distrito + '<br> Fecha/hora: ' + valor.fecha_novedad +' <br> Tipo: '+valor.tipo + '<br> Detalle: ' + valor.detalle + '<br> Medidas adoptadas: ' + valor.medidas_adoptadas).addTo(detail.map)
                                    grupo_marcadores.addLayer(marcador);
                              }
                            if (valor.nivel == '3'){
                               marcador = L.circleMarker([latitud, longitud],{
                                  radius: 4.0,
                                  fillColor: 'red',
                                  color: '#000000',
                                  weight: 1,
                                  opacity: 1.0,
                                  fillOpacity: 1.0
                                  }).bindPopup('Subsanada: '+ '<span class="estilo_en_mapa_no_subsanada">'+valor.subsanada+ '</span>'+ '<br> Distrito: ' + valor.distrito + '<br> Fecha/hora: ' + valor.fecha_novedad +' <br> Tipo: '+valor.tipo + '<br> Detalle: ' + valor.detalle + '<br> Medidas adoptadas: ' + valor.medidas_adoptadas).addTo(detail.map)
                                  grupo_marcadores.addLayer(marcador);
                            }
                       });
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    alert('Error:' + textStatus);
                }
            });
     });
});