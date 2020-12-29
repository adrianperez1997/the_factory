# The Factory

Este proyecto trata de desarrollar una plataforma ligera de configuración que reduzca el proceso de administración y que permita desplegar recursos 
de computación de forma sencilla, dinámica y eficiente. Para ello se ha desarrollado una interfaz web accesible desde cualquier navegador y desplegada
mediante Docker. Nuestra máxima con esta idea es la simplicidad y sencillez, es decir, evadirnos de complicadas configuraciones que requieren de un
profesional para administrar.


## Instalación

Se proporciona un docker-compose el cual expone el puerto 80 para la interfaz. Además tiene tres volúmenes para guardar los datos

- /data base de datos para la información de las máquinas
- /web información de django
- /keys claves ssh de las máquinas

Para poder desplegarlo con docker-compose:

`docker-compose up -d`
  
Para desplegarlo con docker:

`docker run -d --tag="the_factory" -p 8000:80 -v ./data:/data -v ./web:/web -v ./keys:/keys .`
  
## Funcionamiento

En la página principal podremos ver un resumen de nuestro sistema. Automáticamente detectará el SO y las características de la máquina.

![](https://db3pap003files.storage.live.com/y4mRGTBpOtWDYKr1Hst2GudfqYI1qZwxj6Blss0a6WzJNsm6CJEco1ngc6hlRAwUwGOiqruQsMQvNfcA6TSzCDVbcExmcR4trra21TQC9uys2AjDPX6fLYbQN9ZiVixajoh2ecrfqtRbfW63TFo_m5OQqeXrvY0VPT1aGVuD_dajj_t39LBXSjFwJ3kVDRMROU2?width=602&height=288&cropmode=none)
> Págna principal

Las máquinas se dividen en grupos que podemos crear en la pestaña nuevo grupo. En la pestaña de "nueva máquina" podremos añadir nuevos servidores. 
Deberemos seleccionar una clave ssh creada previamente y asignarlo a un grupo. Si queremos especificar un puerto diferente podremos hacerlo de 
la manera: example.com:2222

Una vez añadido se intentará conectar a la máquina.

![](https://db3pap003files.storage.live.com/y4m9thhWpi0HxwObCLfaLbipIp_9KI8dICJege4qRnpHTdHxjY8FHIPxpHlYegGlLLZqKH0A78IKfzE7_uePrmEkkfdEU_fpQNZlu-YxqthWIQNlsfIQ_K9qcTh9Q6uX7IcMnmpGOCael79jkKjyKL66s7rduFjj4cZGwiGobYOLGrgnDcWtEGs48pJjoS3SfAA?width=602&height=309&cropmode=none)
> Nueva máquina

Si seleccionamos un grupo concreto podremos ejecutar playbooks dentro de él. Seleccionaremos las máquinas donde lanzarlo y lo ejecutaremos.

![](https://db3pap003files.storage.live.com/y4mFgIwKbxrBIG2xkhFTgchJMXCmyaux2tZYE0cNj5NVekEKs0ZV9xLqc-bLGJlstKTdb8qlCu8Q71HNH2UMmkv87ftKRpYt0nbqOewD0EqKXslD-mlSZ4FqYWNxeX7IhyUkgUXun3it5aXksw90Y-YKWv-CMTDufZLXND7MjhwOMU5IelAlR01Ow58RTKHE9fT?width=602&height=307&cropmode=none)
![](https://db3pap003files.storage.live.com/y4mY0fb3rbH8jyCeBSI8_uBnI6b8LL6YSuHSCjtUwFdMjP5XmvlgigjkjtUKzkH3MzufeE-GbZcrCkiXrdq4nZ9HTLYC6nl-9smBGghAC1iqCZBjdBtBDqgNzyRTtk_lp3M348Mj7YD8mU9Ot835V4bcmgOrHCL8pSUTP2zwHJslbwfgmunUYEzCqYYVzfBJ0Oo?width=602&height=305&cropmode=none)
> Ejecución de playbooks

Gracias al dropdown de la interfaz podremos:

- Instalar docker con una red privada entre las máquinas aunque estén en clouds públicas o privadas diferentes
- Lanzar aplicaciones conetenerizadas como Wordpress
- Lanzar archivo docker-compose
- Instalar agente Telegraf para monitorización
- Instalar base de datos InfluxDB + Grafana para monitorización
- Lanzar playbook de Ansible propio
