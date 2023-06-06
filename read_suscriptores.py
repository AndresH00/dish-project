import os
import json
import mysql.connector
import boto3


def get_secret(secret_arn):
    """
    Obtiene el valor del secreto almacenado en AWS Secrets Manager.

    Args:
        secret_arn (str): ARN del secreto.

    Returns:
        dict: Diccionario con el valor del secreto.
    """

    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_arn)
    if 'SecretString' in response:
        secret = json.loads(response['SecretString'])
        return secret
    else:
        # Handle binary secrets if necessary
        secret = response['SecretBinary']
        return secret


def lambda_handler(event, context):
    """
    Función principal de la lambda para hacer la lectura de la tabla suscriptores en la bd.

    Args:
        event (dict): Evento que contiene los datos del suscriptor.
        context (object): Objeto de contexto de la lambda.

    Returns:
        dict: Respuesta de la lambda.
    """
    print(event)
    secret_arn = os.environ['SECRET_ARN']
    body = event['queryStringParameters'] if event['queryStringParameters'] is not None else None
    print(body)
    print(type(body))
    telefono_celular = body['telefono_celular'] if isinstance(body, dict) and 'telefono_celular' in body else None

    try:
        # Retrieve the password from the secret
        secret = get_secret(secret_arn)
        conn = mysql.connector.connect(
            host=secret['host'],
            user=secret['username'],
            password=secret['password'],
            database=os.environ['DB_DATABASE']
        )
        cursor = conn.cursor()

        # Execute the SQL query to retrieve all suscriptor records
        if telefono_celular == None:
            sql = "SELECT * FROM suscriptores"
            cursor.execute(sql)
        else:
            sql = "SELECT * FROM suscriptores WHERE telefono_celular = %s"
            values = (telefono_celular,)
            cursor.execute(sql, values)
        # Fetch all rows from the result set
        rows = cursor.fetchall()
        # Format the result as a list of dictionaries
        suscriptores = []
        for row in rows:
            suscriptor = {
                'nombre': row[1],
                'apellido_materno': row[2],
                'apellido_paterno': row[3],
                'edad': row[4],
                'telefono_celular': row[0]
            }
            suscriptores.append(suscriptor)

        # Close the database connection
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps(suscriptores)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
