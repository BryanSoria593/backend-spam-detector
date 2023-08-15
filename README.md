# backend-spam-detector
Este proyecto ha sido desarrollado en Python junto al framework Flask para la creación de las APIs REST.
El backend representa uno de los componentes que he desarrollado para el sistema de detección de spam en su conjunto, a través de el, se puede obtener los diferentes datos que serán visualizados en el dashboard web, que lo puedes encontrar en https://github.com/BryanSoria593/dashboard-spam-detector.

Para poder ejecutar el backend, es necesario utilizar la versión 3 de Python e instalar las siguientes librerías:

```bash
pip3 install bcrypt==4.0.1
pip3 install Flask==2.0.3
pip3 install Flask-Cors==3.0.10
pip3 install yagmail==0.15.293
pip3 install setuptools_rust
pip3 install cryptography==40.0.2
pip3 install mail-parser==3.15.0
pip3 install PyJWT==1.4.2
pip3 install pymongo==4.1.1
pip3 install secure-smtplib==0.1.1
```
Cabe recalcar que las versiones instaladas pueden variar dependiendo el sistema operativo, en este caso, el backend desarrollado estaba en el SO Centos 7, por lo que las últimas versiones disponibles son las mencionadas previamente.

Para poder ejecutar el proyecto, deberás modificar el archivo [`config.py`](config.py), asegurandote de seguir las instrucciones dentro del archivo para poder crear las claves correctamente.

