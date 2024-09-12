import psycopg2
from config import USER_WALLET_DB, DB_WALLET, IP_WALLET_DB

def connection_to_db(logger):
    try:
        # Modifier la connexion pour inclure les certificats SSL
        connection = psycopg2.connect(
                host=IP_WALLET_DB,   # l'adresse IP de ton Raspberry Pi maître
                database=DB_WALLET,    # nom de la base de données
                user=USER_WALLET_DB,          # mot de passe de l'utilisateur
                password=""
            )
        
        cursor = connection.cursor()
        if connection:
            logger.info("Wallet database connected with SSL")
            return connection, cursor
    except Exception as e:
        logger.error(f"Unable to connect to the wallet db: {e}")
        raise ValueError()

# Connexion à la base de données PostgreSQL
def toDatabase(logger, connection, cursor, address, gross_profit, win_rate, total_roi, volume, total_traded, total_token_traded):
    try:
        upsert_query = """
        INSERT INTO wallet_stats (address, gross_profit, win_rate, total_roi, volume, total_traded, total_token_traded)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (address)
        DO UPDATE SET
            gross_profit = EXCLUDED.gross_profit,
            win_rate = EXCLUDED.win_rate,
            total_roi = EXCLUDED.total_roi,
            volume = EXCLUDED.volume,
            total_traded = EXCLUDED.total_traded,
            total_token_traded = EXCLUDED.total_token_traded;
        """
        
        values_to_insert = (
            address,  # address
            gross_profit,        # gross_profit
            win_rate,          # win_rate
            total_roi,          # total_roi
            volume,       # volume
            total_traded,        # total_traded
            total_token_traded   # total_token_traded
        )
        
        cursor.execute(upsert_query, values_to_insert)
        connection.commit()
        logger.info("Wallet stats saved to wallet db")

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error at saving stats to db : {error}")

def close_sql_connection(logger, connection, cursor):
    try:
        cursor.close()
        connection.close()
        logger.info("PostgreSQL connection closed.")
    except Exception as e:
        logger.warn(f"Error while closing connection: {e}")
