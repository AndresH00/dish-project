### Prerrequisitos
Se requiere una base de datos MySQL.
Se necesita un secreto aws para la base de datos con la contraseña en la cuenta.
El framework Serverless este instalado.
AWS CLI este instalado.
Python este instalado.
venv (entorno virtual de Python) este instalado.
npm este instalado.
Las credenciales de AWS esten correctamente configuradas.


### Comandos a ejecutar
Crear un entorno virtual: python -m venv venv --python=python3

Activar el entorno virtual:
    Windows: venv\Scripts\activate.bat
    Linux/Mac: source venv/bin/activate

Instalar el conector de MySQL: pip install mysql-connector-python

Inicializar el proyecto npm: 
    npm install
    --Se instalara lo siguiente (no se requieren ejecutar):
        -npm install serverless-plugin-include-dependencies
        -npm install --save serverless-python-requirements

Hacer deploy a la arquitectura serverless:
    sls deploy

### Nota importante
Asegúrate de que el grupo de seguridad de las Lambdas tenga acceso a la base de datos MySQL.

Para destruir la arquitectura:
    sls remove

Para probar lambdas en especifico:
    sls invoke -f <FunctionName> --data {el json de la informacion}

# Endpoints de dev funcionales de 06/06/2023 seran terminados el dia 07/06/2023
POST - https://7bqlaxos1d.execute-api.us-east-1.amazonaws.com/dev/create-suscriptor
GET - https://7bqlaxos1d.execute-api.us-east-1.amazonaws.com/dev/read-suscriptores
PUT - https://7bqlaxos1d.execute-api.us-east-1.amazonaws.com/dev/update-suscriptor
DELETE - https://7bqlaxos1d.execute-api.us-east-1.amazonaws.com/dev/delete-suscriptor