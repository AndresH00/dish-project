import os
import mysql.connector
import boto3
import json


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
    Función principal de la lambda para hacer el delete en la tabla suscriptores de la bd.

    Args:
        event (dict): Evento que contiene los datos del suscriptor.
        context (object): Objeto de contexto de la lambda.

    Returns:
        dict: Respuesta de la lambda.
    """
    print(event)
    body = json.loads(event['body'])
    suscriptor = body['suscriptor'] if 'suscriptor' in body else None
    telefono_celular = suscriptor['telefono_celular'] if 'telefono_celular' in suscriptor else None

    if suscriptor == None:
        return {
            'statusCode': 400,
            'body': 'La informacion del suscriptor es obligatoria.'
        }
    if telefono_celular == None:
        return {
            'statusCode': 400,
            'body': 'El telefono celular es obligatorio.'
        }
    secret_arn = os.environ['SECRET_ARN']

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

        # Execute the SQL query to delete the record
        sql = "DELETE FROM suscriptores WHERE telefono_celular = %s"
        values = (telefono_celular,)
        cursor.execute(sql, values)

        # Confirm the changes in the database
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': 'Registro eliminado exitosamente.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
