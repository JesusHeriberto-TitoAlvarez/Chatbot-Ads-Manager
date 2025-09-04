# Usar la imagen oficial de Python 3.9 como base
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Dar permisos de ejecución al script
RUN chmod +x /app/start_monitors.sh

# Definir el comando de inicio para ejecutar todos los monitores
CMD ["/bin/bash", "/app/start_monitors.sh"]
