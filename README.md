Portfolio personal y blog desarrollados con Django. La portada presenta el portfolio, el blog publica entradas cronologicas con texto y archivos multimedia, y permite que los visitantes dejen comentarios.
La portada está en "http://127.0.0.1:8000/", el blog en "http://127.0.0.1:8000/blog/" y la administración en "http://127.0.0.1:8000/admin/".

## Administración del blog

Iniciá sesión como administrador en `/admin/` para crear entradas y cargar su archivo multimedia. Las publicaciones aparecen ordenadas de la más reciente a la más antigua. Los visitantes pueden comentar desde la página de cada entrada; los comentarios se moderan y eliminan desde la administración.

Las imágenes se muestran en las tarjetas y en la entrada; los archivos de audio y video se pueden reproducir desde la página. Otros tipos de archivo quedan disponibles como descarga. En desarrollo, Django sirve las cargas desde `personal_website/media/`.