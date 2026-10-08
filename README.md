Portfolio personal y blog desarrollados con Django. La portada presenta el portfolio, el blog publica entradas cronologicas con texto y archivos multimedia, y permite que los visitantes dejen comentarios.
La portada está en "http://127.0.0.1:8000/", el blog en "http://127.0.0.1:8000/blog/" y la administración en "http://127.0.0.1:8000/admin/".

## Administración del blog

Iniciá sesión desde el portfolio o el blog para dar like; las cuentas con permisos de administrador también pueden gestionar publicaciones desde el enlace de administración o en `/admin/`. Podés cerrar sesión desde cualquiera de las dos secciones. Las publicaciones aparecen ordenadas de la más reciente a la más antigua. Los visitantes pueden comentar desde la página de cada entrada; los comentarios se moderan y eliminan desde la administración.

Las imágenes se muestran en las tarjetas y en la entrada; los archivos de audio y video se pueden reproducir desde la página. Otros tipos de archivo quedan disponibles como descarga. Los archivos multimedia del blog se guardan en `personal_website/blog/static/img/`; el CSS del blog permanece en `personal_website/blog/static/blog/`.