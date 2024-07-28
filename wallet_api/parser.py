import pandas as pd

# Charger les données CSV
file_path = './wallet_api/toProcess/A5TYS17zBnd8TUEr2GyHzysBqisBUnG8seRZrMxaK4Ku.csv'  # Remplacer par le chemin de votre fichier CSV
df = pd.read_csv(file_path)

# Filtrer les transactions impliquant le token So11111111111111111111111111111111111111112
Sola = 'So11111111111111111111111111111111111111112'
df_token = df[(df['token1'] == Sola) | (df['token2'] == Sola)]

# Convertir les montants en fonction des décimales
df_token['amount1'] = df_token['amount1'] / (10 ** df_token['decimal1'])
df_token['amount2'] = df_token['amount2'] / (10 ** df_token['decimal2'])

# Inverser l'ordre des lignes
df_token = df_token[::-1]

# Afficher le nombre de lignes et le contenu du DataFrame filtré pour diagnostic
print(f"Nombre de lignes dans df_token: {len(df_token)}")
print(df_token)

# Initialiser les compteurs pour le realized et unrealized PNL pour chaque token
pnl_tracker = {}

# Parcourir chaque transaction
for index, row in df_token.iterrows():
    token1 = row['token1']  # vendre
    token2 = row['token2']  # achat
    amount1 = row['amount1']  # vendre
    amount2 = row['amount2']  # achat
    
    if token1 == Sola: 
        print(f"Transaction achat: token2={token2}, amount1={amount1}, amount2={amount2}")
        
        if token2 not in pnl_tracker:  # Premier achat
            pnl_tracker[token2] = {'realized': 0, 'unrealized': 0, 'Sol_invest': 0, 'balance': 0}
            pnl_tracker[token2]['Sol_invest'] = amount1
            pnl_tracker[token2]['balance'] = amount2
        else:
            pnl_tracker[token2]['Sol_invest'] += amount1
            pnl_tracker[token2]['balance'] += amount2
    else:
        print(f"Transaction vente: token1={token1}, amount1={amount1}, amount2={amount2}")
        
        if token1 not in pnl_tracker:
            pnl_tracker[token1] = {'realized': 0, 'unrealized': 0, 'Sol_invest': 0, 'balance': 0}
            pnl_tracker[token1]['realized'] += amount2
        else :
            pnl_tracker[token1]['realized'] += (amount2 - pnl_tracker[token1]['Sol_invest'])
            pnl_tracker[token1]['balance'] -= amount1

# Afficher les résultats pour chaque token
for token, pnl in pnl_tracker.items():
    print(f"Token: {token}")
    print(f"  PNL réalisé : {pnl['realized']}")
    print(f"  Sol investi : {pnl['Sol_invest']}")
    print(f"  PNL total : {pnl['realized'] + pnl['unrealized']}")
    print(f"  Solde restant : {pnl['balance']}\n")
