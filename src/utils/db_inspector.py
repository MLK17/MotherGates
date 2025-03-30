from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
import os

def inspect_database():
    """
    Récupère et affiche la structure de toutes les tables de la base de données
    """
    load_dotenv()
    
    # Récupération de l'URL de la base de données depuis les variables d'environnement
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("Erreur: DATABASE_URL non trouvée dans les variables d'environnement")
        return
    
    # Création du moteur SQLAlchemy
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    # Récupération de toutes les tables
    tables = inspector.get_table_names()
    
    print("\nStructure de la base de données:")
    print("=" * 50)
    
    for table in tables:
        print(f"\nTable: {table}")
        print("-" * 30)
        
        # Récupération des colonnes
        columns = inspector.get_columns(table)
        for column in columns:
            nullable = "NULL" if column['nullable'] else "NOT NULL"
            print(f"- {column['name']}: {column['type']} {nullable}")
        
        # Récupération des clés primaires
        pks = inspector.get_pk_constraint(table)
        if pks['constrained_columns']:
            print(f"\nClé(s) primaire(s): {', '.join(pks['constrained_columns'])}")
        
        # Récupération des clés étrangères
        fks = inspector.get_foreign_keys(table)
        if fks:
            print("\nClés étrangères:")
            for fk in fks:
                print(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

if __name__ == "__main__":
    inspect_database()
