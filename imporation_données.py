import os
import re
import pandas as pd
import s3fs

def charger_tous_les_fichiers(chemin_dossier, bucket=None, mettre_dans_globals=False):
    if bucket is None:
        bucket = os.getenv("AWS_STORAGE_USER") or os.getenv("USER") or "etiennealpy"
    
    chemin_dossier = chemin_dossier.strip("/")
    dossier_s3 = f"{bucket}/{chemin_dossier}"
    
    
    endpoint_url = os.getenv("AWS_S3_ENDPOINT", "https://minio.lab.sspcloud.fr")
    if not endpoint_url.startswith("http"):
        endpoint_url = f"https://{endpoint_url}"
    
    fs = s3fs.S3FileSystem(
        client_kwargs={'endpoint_url': endpoint_url}
    )
    
    fichiers_s3 = fs.ls(dossier_s3)
    dataframes = {}
    
    print(f"--- Recherche dans : s3://{dossier_s3} ---")
    
    for fichier_path in fichiers_s3:
        nom_fichier = os.path.basename(fichier_path)
        
        if fs.isdir(fichier_path) or nom_fichier.startswith("."):
            continue
            
        nom_cle = re.sub(r'\.(csv|gz|parquet)$', '', nom_fichier, flags=re.IGNORECASE)
        nom_cle = re.sub(r'\.(csv|gz)$', '', nom_cle, flags=re.IGNORECASE)
        nom_cle = re.sub(r'[^a-zA-Z0-9_]', '_', nom_cle)
        
        s3_url = f"s3://{fichier_path}"
        
        try:
          
            with fs.open(s3_url, 'rb') as f:
                if nom_fichier.endswith('.parquet'):
                    df = pd.read_parquet(f)
                else:
                    df = pd.read_csv(f)
                
            dataframes[nom_cle] = df
            print(f"Chargé : {nom_fichier} -> Variable : '{nom_cle}'")
            
            if mettre_dans_globals:
                globals()[nom_cle] = df
                
        except Exception as e:
            print(f"Erreur sur {nom_fichier}: {e}")
            
    return dataframes


données=charger_tous_les_fichiers("données paris","etiennealpy")
print(données