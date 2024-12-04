#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash
import time
from datetime import date, timedelta, datetime
import math

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'

                                    ## à ajouter
from flask import session, g
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host="localhost",
            user="constantsuchet",
            password="Password123!",
            database="maraicher_db",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    creators = [
        {
            "name": "SUCHET Constant",
            "title": "Page Accueil et Maraîcher",
            "description": "Developpement des pages accueil/recolte pour le projet de base de donnees SAE 1.04.",
            "profile_url": "/recolte", 
            "created_pages": {
                "Recolte": "/recolte",
            }
        },
        {
            "name": "TOUZI Tahar Amine",
            "title": "Page Produits",
            "description": "Developpement de la page produits pour le projet de base de donnees SAE 1.04.",
            "profile_url": "/produit",
            "created_pages": {
                "Produit": "/produit",
            }
        },
        {
            "name": "SONET Noe",
            "title": "Page Marche", 
            "description": "Developpement de la page marche pour le projet de base de donnees SAE 1.04.",
            "profile_url": "/marche",
            "created_pages": {
                "Marche": "/marche",
            }
        },
        {
            "name": "SPRINGER Theo",
            "title": "Page Vente",
            "description": "Developpement de la page vente pour le projet de base de donnees SAE 1.04.",
            "profile_url": "/vente",
            "created_pages": {
                "Vente": "/vente", 
            }
        }
    ]
    return render_template('home.html', creators=creators)

@app.route('/recolte')
def show_recoltes():
    mycursor = get_db().cursor()
    
    # Requête principale pour les recoltes
    sql_recoltes = """
        SELECT recolte.*, Produit.nom_produit, Maraicher.Nom, Maraicher.Prenom 
        FROM recolte
        JOIN Produit ON recolte.ID_Produit = Produit.ID_Produit
        JOIN Maraicher ON recolte.ID_Maraicher = Maraicher.ID_Maraicher
    """
    
    # Requête pour les statistiques par produit
    sql_stats = """
        SELECT 
            Produit.nom_produit,
            COUNT(*) as nombre_recoltes,
            SUM(recolte.quantite) as quantite_totale,
            AVG(recolte.quantite) as moyenne_quantite
        FROM recolte
        JOIN Produit ON recolte.ID_Produit = Produit.ID_Produit
        GROUP BY Produit.ID_Produit, Produit.nom_produit
    """
    
    mycursor.execute(sql_recoltes)
    recoltes = mycursor.fetchall()
    
    mycursor.execute(sql_stats)
    stats = mycursor.fetchall()
    
    return render_template('recolte/show_recolte.html', 
                         recoltes=recoltes,
                         stats=stats)

@app.route('/recolte/add', methods=['GET'])
def add_recolte_get():
    mycursor = get_db().cursor()
    today_date = datetime.today()
    
    # Get all products and check which ones are in recolte within the date range
    sql_produits = """
        SELECT DISTINCT Produit.*, 
               CASE WHEN EXISTS (
                   SELECT 1 FROM recolte 
                   WHERE recolte.ID_Produit = Produit.ID_Produit
                   AND recolte.Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
                   AND recolte.Date_Debut > DATE_SUB(%s, INTERVAL 7 DAY)
               ) THEN 1 ELSE 0 END as in_recolte,
               (SELECT Date_Debut FROM recolte 
                WHERE recolte.ID_Produit = Produit.ID_Produit
                AND recolte.Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
                AND recolte.Date_Debut > DATE_SUB(%s, INTERVAL 7 DAY)
                LIMIT 1) as Date_Debut
        FROM Produit
    """
    mycursor.execute(sql_produits, (today_date, today_date, today_date, today_date))
    produits = mycursor.fetchall()
    
    # Get all maraichers and check which ones are in recolte within the date range
    sql_maraichers = """
        SELECT DISTINCT Maraicher.*, 
               CASE WHEN EXISTS (
                   SELECT 1 FROM recolte 
                   WHERE recolte.ID_Maraicher = Maraicher.ID_Maraicher
                   AND recolte.Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
                   AND recolte.Date_Debut > DATE_SUB(%s, INTERVAL 7 DAY)
               ) THEN 1 ELSE 0 END as in_recolte,
               (SELECT Date_Debut FROM recolte 
                WHERE recolte.ID_Maraicher = Maraicher.ID_Maraicher
                AND recolte.Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
                AND recolte.Date_Debut > DATE_SUB(%s, INTERVAL 7 DAY)
                LIMIT 1) as Date_Debut
        FROM Maraicher
    """
    mycursor.execute(sql_maraichers, (today_date, today_date, today_date, today_date))
    maraichers = mycursor.fetchall()
    
    # Get all seasons
    mycursor.execute("SELECT * FROM Saison")
    saisons = mycursor.fetchall()
    
    today_date_str = today_date.strftime('%Y-%m-%d')
    next_week_date = (today_date + timedelta(days=7)).strftime('%Y-%m-%d')
    last_week_date = (today_date - timedelta(days=7)).strftime('%Y-%m-%d')

    return render_template('recolte/add_recolte.html', 
                         produits=produits, 
                         maraichers=maraichers,
                         today_date=today_date_str,
                         next_week_date=next_week_date,
                         last_week_date=last_week_date,
                         saisons=saisons)

@app.route('/recolte/add', methods=['POST'])
def add_recolte_post():
    mycursor = get_db().cursor()
    quantite = request.form.get('quantite')
    date_debut = request.form.get('Date_Debut')
    id_produit = request.form.get('ID_Produit')
    id_maraicher = request.form.get('ID_Maraicher')

    # Verification pour le maraîcher
    check_sql = """
        SELECT * FROM recolte 
        WHERE ID_Maraicher = %s 
        AND Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
        AND Date_Debut > DATE_SUB(%s, INTERVAL 7 DAY)
    """
    mycursor.execute(check_sql, (id_maraicher, date_debut, date_debut))
    existing_recolte = mycursor.fetchone()

    if existing_recolte:
        flash('Ce maraicher a déjà une récolte prévue dans la même semaine', 'error')
        return redirect('/recolte/add')

    # Verification pour le produit
    check_sql = """
        SELECT * FROM recolte 
        WHERE ID_Produit = %s 
        AND Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
        AND Date_Debut > DATE_SUB(%s, INTERVAL 7 DAY)
    """
    mycursor.execute(check_sql, (id_produit, date_debut, date_debut))
    existing_recolte = mycursor.fetchone()

    if existing_recolte:
        flash('Ce produit a déjà une récolte prévue dans la même semaine', 'error')
        return redirect('/recolte/add')

    # Si aucun conflit, on ajoute la récolte
    sql = """
        INSERT INTO recolte (quantite, Date_Debut, ID_Produit, ID_Maraicher)
        VALUES (%s, %s, %s, %s)
    """
    mycursor.execute(sql, (quantite, date_debut, id_produit, id_maraicher))
    get_db().commit()
    
    flash('Récolte ajoutée avec succès', 'success')
    return redirect('/recolte')

@app.route('/recolte/edit', methods=['GET'])
def edit_recolte():
    id_recolte = request.args.get('id', type=int)
    
    if not id_recolte:
        flash('ID recolte non specifie', 'error')
        return redirect('/recolte')
    
    mycursor = get_db().cursor()
    
    # Get the basic recolte information
    sql = """
        SELECT recolte.*, Produit.nom_produit, Maraicher.Nom, Maraicher.Prenom 
        FROM recolte 
        JOIN Produit ON recolte.ID_produit = Produit.ID_produit 
        JOIN Maraicher ON recolte.ID_maraicher = Maraicher.ID_maraicher 
        WHERE recolte.ID_recolte = %s
    """
    mycursor.execute(sql, (id_recolte,))
    recolte = mycursor.fetchone()
    
    if not recolte:
        flash('Recolte non trouvee', 'error')
        return redirect('/recolte')

    # Get all products and maraichers
    mycursor.execute("SELECT * FROM Produit")
    produits = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM Maraicher")
    maraichers = mycursor.fetchall()
    
    # Calculate dates
    today_date = datetime.today()
    today_date_str = today_date.strftime('%Y-%m-%d')
    next_week_date = (today_date + timedelta(days=7)).strftime('%Y-%m-%d')
    last_week_date = (today_date - timedelta(days=7)).strftime('%Y-%m-%d')

    return render_template('recolte/edit_recolte.html', 
                         recolte=recolte, 
                         produits=produits, 
                         maraichers=maraichers,
                         today_date=today_date_str,
                         next_week_date=next_week_date,
                         last_week_date=last_week_date)

@app.route('/recolte/edit', methods=['POST'])
def edit_recolte_post():
    mycursor = get_db().cursor()
    id_recolte = request.form.get('ID_recolte', type=int)
    quantite = request.form.get('quantite', type=int)
    date_debut = request.form.get('Date_Debut')
    id_produit = request.form.get('ID_Produit', type=int)
    id_maraicher = request.form.get('ID_Maraicher', type=int)

    check_sql = """
        SELECT * FROM recolte 
        WHERE ID_Maraicher = %s 
        AND ID_recolte != %s 
        AND Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
        AND DATE_ADD(Date_Debut, INTERVAL 7 DAY) > %s
    """
    mycursor.execute(check_sql, (id_maraicher, id_recolte, date_debut, date_debut))    
    existing_recolte = mycursor.fetchone()

    if existing_recolte:
        flash('Ce maraicher a déjà une recolte en cours dans la même semaine', 'error')
        return redirect('/recolte/edit?id=' + str(id_recolte))

    check_sql = """
        SELECT * FROM recolte 
        WHERE ID_Produit = %s 
        AND ID_recolte != %s 
        AND Date_Debut < DATE_ADD(%s, INTERVAL 7 DAY)
        AND DATE_ADD(Date_Debut, INTERVAL 7 DAY) > %s
    """
    mycursor.execute(check_sql, (id_produit, id_recolte, date_debut, date_debut))
    existing_recolte = mycursor.fetchone()

    if existing_recolte:
        flash('Ce produit a déjà une recolte en cours dans la même semaine', 'error')
        return redirect('/recolte/edit?id=' + str(id_recolte))

    sql = """
        UPDATE recolte 
        SET quantite = %s, Date_Debut = %s, ID_Produit = %s, ID_Maraicher = %s
        WHERE ID_recolte = %s
    """
    mycursor.execute(sql, (quantite, date_debut, id_produit, id_maraicher, id_recolte))
    get_db().commit()
    
    flash('Recolte mise à jour avec succès', 'success')
    return redirect('/recolte')

@app.route('/recolte/delete', methods=['POST'])
def delete_recolte():
    id_recolte = request.form.get('ID_recolte', type=int)
    mycursor = get_db().cursor()
    mycursor.execute("DELETE FROM recolte WHERE ID_recolte = %s", (id_recolte,))
    get_db().commit()
    return redirect('/recolte')

@app.route('/conflicts/recolte/<int:recolte_id>')
def show_recolte_conflicts(recolte_id):
    mycursor = get_db().cursor()
    
    sql = """
        SELECT recolte.*, Produit.nom_produit, Maraicher.Nom, Maraicher.Prenom 
        FROM recolte
        LEFT JOIN Produit ON recolte.ID_Produit = Produit.ID_Produit
        LEFT JOIN Maraicher ON recolte.ID_Maraicher = Maraicher.ID_Maraicher
        WHERE recolte.ID_recolte = %s
    """
    mycursor.execute(sql, (recolte_id,))
    recolte = mycursor.fetchone()
    
    if not recolte:
        flash('Recolte non trouvee', 'error')
        return redirect('/recolte')
    
    conflicts = {}
    
    if recolte['ID_Produit']:
        conflicts['produit'] = {
            'ID_Produit': recolte['ID_Produit'],
            'nom_produit': recolte['nom_produit']
        }
    
    if recolte['ID_Maraicher']:
        conflicts['maraicher'] = {
            'ID_Maraicher': recolte['ID_Maraicher'],
            'Nom': recolte['Nom'],
            'Prenom': recolte['Prenom']
        }
    
    return render_template('recolte/conflict_recolte.html', 
                         conflicts=conflicts if conflicts else None,
                         recolte_id=recolte_id)

@app.route('/vente')
def vente():
    return render_template('vente/show_vente.html')

@app.route('/produit')
def produit():
    mycursor = get_db().cursor()
    
    # Requête modifiée pour utiliser est_de_saison au lieu de Produit_Saison
    sql = """
        SELECT p.*, 
               GROUP_CONCAT(s.libelle_saison) as saisons,
               GROUP_CONCAT(s.code_saison) as saisons_id
        FROM Produit p
        LEFT JOIN est_de_saison eds ON p.ID_Produit = eds.ID_Produit
        LEFT JOIN Saison s ON eds.code_saison = s.code_saison
        GROUP BY p.ID_Produit
    """
    mycursor.execute(sql)
    produits = mycursor.fetchall()
    
    return render_template('produit/show_produit.html', produits=produits)

@app.route('/produit/show', methods=['GET'])
def show_produit():
    return render_template('produit/show_produit.html')

@app.route('/produit/add', methods=['GET'])
def add_produit():
    mycursor = get_db().cursor()
    # Récupération des saisons depuis la base de données
    mycursor.execute("SELECT code_saison as ID_Saison, libelle_saison as Nom_Saison FROM Saison")
    saisons = mycursor.fetchall()
    return render_template('produit/add_produit.html', saisons=saisons)

@app.route('/produit/add', methods=['POST'])
def add_produit_post():
    mycursor = get_db().cursor()
    
    nom_produit = request.form.get('nom_produit')
    prix_vente = request.form.get('prix_vente')
    saisons = request.form.getlist('saisons')
    
    try:
        # Insertion du produit (notez que idTypeproduit est requis)
        sql = "INSERT INTO Produit (nom_produit, prix_vente, idTypeproduit) VALUES (%s, %s, %s)"
        mycursor.execute(sql, (nom_produit, prix_vente, 1))  # 1 est l'ID par défaut pour le type
        id_produit = mycursor.lastrowid
        
        # Insertion des saisons pour ce produit
        if saisons:
            sql_saison = "INSERT INTO est_de_saison (ID_Produit, code_saison) VALUES (%s, %s)"
            for saison in saisons:
                mycursor.execute(sql_saison, (id_produit, saison))
        
        get_db().commit()
        flash('Produit ajouté avec succès', 'success')
        return redirect('/produit')
        
    except Exception as e:
        get_db().rollback()
        flash(f'Erreur lors de l\'ajout du produit: {str(e)}', 'error')
        return redirect('/produit/add')

@app.route('/produit/edit', methods=['GET'])
def edit_produit():
    id_produit = request.args.get('id', type=int)
    
    if not id_produit:
        flash('ID produit non spécifié', 'error')
        return redirect('/produit')
    
    mycursor = get_db().cursor()
    
    # Récupération du produit et de ses saisons
    sql = """
        SELECT p.*, 
               GROUP_CONCAT(s.libelle_saison) as saisons,
               GROUP_CONCAT(s.code_saison) as saisons_id
        FROM Produit p
        LEFT JOIN est_de_saison eds ON p.ID_Produit = eds.ID_Produit
        LEFT JOIN Saison s ON eds.code_saison = s.code_saison
        WHERE p.ID_Produit = %s
        GROUP BY p.ID_Produit
    """
    mycursor.execute(sql, (id_produit,))
    produit = mycursor.fetchone()
    
    # Récupération de toutes les saisons
    mycursor.execute("SELECT code_saison as ID_Saison, libelle_saison as Nom_Saison FROM Saison")
    saisons = mycursor.fetchall()
    
    return render_template('produit/edit_produit.html', produit=produit, saisons=saisons)

@app.route('/produit/edit', methods=['POST'])
def edit_produit_post():
    mycursor = get_db().cursor()
    
    id_produit = request.form.get('id_produit', type=int)
    nom_produit = request.form.get('nom_produit')
    prix_vente = request.form.get('prix_vente')
    saisons = request.form.getlist('saisons')
    
    # Vérification qu'au moins une saison est sélectionnée
    if not saisons:
        flash('Veuillez sélectionner au moins une saison pour le produit.', 'error')
        return redirect(f'/produit/edit?id={id_produit}')
    
    try:
        # Mise à jour du produit
        sql = "UPDATE Produit SET nom_produit = %s, prix_vente = %s WHERE ID_Produit = %s"
        mycursor.execute(sql, (nom_produit, prix_vente, id_produit))
        
        # Mise à jour des saisons
        mycursor.execute("DELETE FROM est_de_saison WHERE ID_Produit = %s", (id_produit,))
        sql_saison = "INSERT INTO est_de_saison (ID_Produit, code_saison) VALUES (%s, %s)"
        for saison in saisons:
            mycursor.execute(sql_saison, (id_produit, saison))
        
        get_db().commit()
        flash('Produit mis à jour avec succès', 'success')
        return redirect('/produit')
        
    except Exception as e:
        get_db().rollback()
        flash(f'Erreur lors de la mise à jour du produit: {str(e)}', 'error')
        return redirect(f'/produit/edit?id={id_produit}')

@app.route('/marche')
def show_marches():
    mycursor = get_db().cursor()
    sql = """
        SELECT m.ID_Marche, m.nom_mache as Nom_Marche, l.nom as Adresse,
               CASE DAYOFWEEK(m.date_march)
                   WHEN 1 THEN 'Dimanche'
                   WHEN 2 THEN 'Lundi'
                   WHEN 3 THEN 'Mardi'
                   WHEN 4 THEN 'Mercredi'
                   WHEN 5 THEN 'Jeudi'
                   WHEN 6 THEN 'Vendredi'
                   WHEN 7 THEN 'Samedi'
               END as Jour_Marche,
               m.nombre_standes
        FROM Marche m
        JOIN LieuMarche l ON m.code_lieu = l.code_lieu
        ORDER BY m.nom_mache
    """
    mycursor.execute(sql)
    marches = mycursor.fetchall()
    return render_template('marche/show_marche.html', marches=marches)

@app.route('/marche/add', methods=['GET'])
def add_marche_get():
    mycursor = get_db().cursor()
    
    # Récupérer les valeurs par défaut depuis la requête
    nom_marche = request.args.get('nom_marche', '')
    code_lieu = request.args.get('code_lieu', '')
    nombre_stands = request.args.get('nombre_stands', '')
    
    # Récupérer la liste des lieux de marché
    sql = "SELECT * FROM LieuMarche ORDER BY nom"
    mycursor.execute(sql)
    lieux = mycursor.fetchall()
    
    return render_template('marche/add_marche.html', 
                         lieux=lieux,
                         nom_marche=nom_marche,
                         code_lieu=code_lieu,
                         nombre_stands=nombre_stands)

@app.route('/marche/add', methods=['POST'])
def add_marche_post():
    mycursor = get_db().cursor()
    nom_marche = request.form.get('nom_marche')
    code_lieu = request.form.get('code_lieu')
    nombre_stands = request.form.get('nombre_stands', 0)
    jour_marche = request.form.get('jour_marche')

    try:
        # Vérifier si un marché existe déjà avec le même nom
        sql_check = "SELECT * FROM Marche WHERE nom_mache = %s"
        mycursor.execute(sql_check, (nom_marche,))
        if mycursor.fetchone():
            flash('Un marché avec ce nom existe déjà', 'error')
            return redirect('/marche/add')

        # Vérifier si le lieu existe
        sql_check_lieu = "SELECT * FROM LieuMarche WHERE code_lieu = %s"
        mycursor.execute(sql_check_lieu, (code_lieu,))
        if not mycursor.fetchone():
            flash('Le lieu sélectionné n\'existe pas', 'error')
            return redirect('/marche/add')

        # Générer un nouvel ID_Marche
        sql_max_id = "SELECT MAX(ID_Marche) as max_id FROM Marche"
        mycursor.execute(sql_max_id)
        result = mycursor.fetchone()
        new_id = 1 if result['max_id'] is None else result['max_id'] + 1

        # Calculer la date du marché en fonction du jour sélectionné
        sql = """
            INSERT INTO Marche (ID_Marche, nom_mache, date_march, nombre_standes, code_lieu)
            VALUES (%s, %s, DATE_ADD(CURDATE(), 
                   INTERVAL ((%s - DAYOFWEEK(CURDATE()) + 7) MOD 7) DAY), 
                   %s, %s)
        """
        mycursor.execute(sql, (new_id, nom_marche, jour_marche, nombre_stands, code_lieu))
        get_db().commit()
        flash('Marché ajouté avec succès', 'success')
        return redirect('/marche')
    except Exception as e:
        flash(f'Erreur lors de l\'ajout du marché: {str(e)}', 'error')
        return redirect('/marche/add')

@app.route('/marche/edit/<int:id_marche>', methods=['GET'])
def edit_marche_get(id_marche):
    mycursor = get_db().cursor()
    
    # Récupérer les informations complètes du marché
    sql = """
        SELECT m.*, l.nom as lieu_nom, l.code_lieu
        FROM Marche m
        JOIN LieuMarche l ON m.code_lieu = l.code_lieu
        WHERE m.ID_Marche = %s
    """
    mycursor.execute(sql, (id_marche,))
    marche = mycursor.fetchone()
    
    if not marche:
        flash('Marché non trouvé', 'error')
        return redirect('/marche')

    # Récupérer la liste des lieux de marché
    sql = "SELECT * FROM LieuMarche ORDER BY nom"
    mycursor.execute(sql)
    lieux = mycursor.fetchall()

    return render_template('marche/edit_marche.html', 
                         marche=marche,
                         lieux=lieux)

@app.route('/marche/edit', methods=['POST'])
def edit_marche_post():
    mycursor = get_db().cursor()
    id_marche = request.form.get('id_marche')
    nom_marche = request.form.get('nom_marche')
    code_lieu = request.form.get('code_lieu')
    nombre_stands = request.form.get('nombre_stands', 0)
    jour_marche = request.form.get('jour_marche')

    try:
        # Vérifier si un autre marché existe avec le même nom
        sql_check = "SELECT * FROM Marche WHERE nom_mache = %s AND ID_Marche != %s"
        mycursor.execute(sql_check, (nom_marche, id_marche))
        if mycursor.fetchone():
            flash('Un autre marché avec ce nom existe déjà', 'error')
            return redirect(f'/marche/edit/{id_marche}')

        # Mettre à jour le marché avec le nouveau jour
        sql = """
            UPDATE Marche 
            SET nom_mache = %s, 
                nombre_standes = %s, 
                code_lieu = %s,
                date_march = DATE_ADD(CURDATE(), 
                    INTERVAL ((%s - DAYOFWEEK(CURDATE()) + 7) MOD 7) DAY)
            WHERE ID_Marche = %s
        """
        mycursor.execute(sql, (nom_marche, nombre_stands, code_lieu, jour_marche, id_marche))
        get_db().commit()
        flash('Marché modifié avec succès', 'success')
        return redirect('/marche')
    except Exception as e:
        flash(f'Erreur lors de la modification du marché: {str(e)}', 'error')
        return redirect(f'/marche/edit/{id_marche}')

@app.route('/marche/delete/<int:id_marche>', methods=['GET'])
def delete_marche_get(id_marche):
    mycursor = get_db().cursor()
    # Récupérer les informations du marché
    sql = """
        SELECT m.ID_Marche, m.nom_mache, l.nom as Adresse,
               CASE DAYOFWEEK(m.date_march)
                   WHEN 1 THEN 'Dimanche'
                   WHEN 2 THEN 'Lundi'
                   WHEN 3 THEN 'Mardi'
                   WHEN 4 THEN 'Mercredi'
                   WHEN 5 THEN 'Jeudi'
                   WHEN 6 THEN 'Vendredi'
                   WHEN 7 THEN 'Samedi'
               END as Jour_Marche
        FROM Marche m
        JOIN LieuMarche l ON m.code_lieu = l.code_lieu
        WHERE m.ID_Marche = %s
    """
    mycursor.execute(sql, (id_marche,))
    marche = mycursor.fetchone()
    
    if not marche:
        flash('Marché non trouvé', 'error')
        return redirect('/marche')

    return render_template('marche/delete_marche.html', marche=marche)

@app.route('/marche/delete', methods=['POST'])
def delete_marche_post():
    mycursor = get_db().cursor()
    id_marche = request.form.get('id_marche')
    force_delete = request.form.get('force_delete') == 'on'

    try:
        # Vérifier s'il y a des ventes associées
        sql_check_ventes = "SELECT COUNT(*) as count FROM Vente WHERE ID_Marche = %s"
        mycursor.execute(sql_check_ventes, (id_marche,))
        ventes_count = mycursor.fetchone()['count']

        if ventes_count > 0 and not force_delete:
            flash(f'Ce marché a {ventes_count} vente(s) associée(s). Cochez "Forcer la suppression" pour supprimer le marché et toutes ses ventes.', 'error')
            return redirect(f'/marche/delete/{id_marche}')

        # Si force_delete est activé ou s'il n'y a pas de ventes, procéder à la suppression
        if force_delete:
            # Supprimer d'abord les ventes associées et leurs produits vendus
            sql_get_ventes = "SELECT ID_Vente FROM Vente WHERE ID_Marche = %s"
            mycursor.execute(sql_get_ventes, (id_marche,))
            ventes = mycursor.fetchall()
            
            for vente in ventes:
                # Supprimer les produits vendus pour chaque vente
                sql_delete_est_vendu = "DELETE FROM est_vendu WHERE ID_Vente = %s"
                mycursor.execute(sql_delete_est_vendu, (vente['ID_Vente'],))
            
            # Supprimer les ventes
            sql_delete_ventes = "DELETE FROM Vente WHERE ID_Marche = %s"
            mycursor.execute(sql_delete_ventes, (id_marche,))

        # Supprimer les relations est_dans
        sql_delete_est_dans = "DELETE FROM est_dans WHERE ID_Marche = %s"
        mycursor.execute(sql_delete_est_dans, (id_marche,))

        # Supprimer le marché
        sql = "DELETE FROM Marche WHERE ID_Marche = %s"
        mycursor.execute(sql, (id_marche,))
        
        get_db().commit()
        flash('Marché supprimé avec succès', 'success')
        return redirect('/marche')
    except Exception as e:
        get_db().rollback()
        flash(f'Erreur lors de la suppression du marché: {str(e)}', 'error')
        return redirect(f'/marche/delete/{id_marche}')



@app.route('/etat_recolte', methods=['GET', 'POST'])
def etat_recolte():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        mycursor = get_db().cursor()
        
        sql = """
            SELECT 
                Maraicher.Nom, 
                Maraicher.Prenom, 
                Produit.nom_produit,
                Produit.prix_vente,
                recolte.quantite as quantite,
                (recolte.quantite * Produit.prix_vente) as prix_total
            FROM recolte
            JOIN Maraicher ON recolte.ID_Maraicher = Maraicher.ID_Maraicher
            JOIN Produit ON recolte.ID_Produit = Produit.ID_Produit
            WHERE recolte.Date_Debut BETWEEN %s AND %s
            ORDER BY Maraicher.Nom, Maraicher.Prenom, Produit.nom_produit
        """
        
        sql_participation = """
            SELECT 
                Maraicher.Nom,
                Maraicher.Prenom,
                SUM(recolte.quantite) as total_quantite,
                (SUM(recolte.quantite) * 100.0 / (SELECT SUM(quantite) FROM recolte WHERE Date_Debut BETWEEN %s AND %s)) as participation_percentage
            FROM recolte
            JOIN Maraicher ON recolte.ID_Maraicher = Maraicher.ID_Maraicher
            WHERE recolte.Date_Debut BETWEEN %s AND %s
            GROUP BY Maraicher.ID_Maraicher, Maraicher.Nom, Maraicher.Prenom
            ORDER BY participation_percentage DESC
        """
        
        mycursor.execute(sql, (start_date, end_date))
        results = mycursor.fetchall()
        
        mycursor.execute(sql_participation, (start_date, end_date, start_date, end_date))
        participation_data = mycursor.fetchall()
        
        return render_template('recolte/etat_recolte.html', 
                             results=results,
                             participation_data=participation_data,
                             start_date=start_date,
                             end_date=end_date)
    
    return render_template('recolte/etat_recolte.html')

@app.route('/etat_produit')
def etat_produit():
    mycursor = get_db().cursor()
    
    sql = """
        SELECT 
            Produit.ID_Produit,
            Produit.nom_produit,
            Produit.prix_vente,
            COALESCE(SUM(recolte.quantite), 0) as total_quantite,
            COALESCE(SUM(recolte.quantite) * Produit.prix_vente, 0) as valeur_totale,
            COUNT(DISTINCT recolte.ID_Maraicher) as nombre_maraichers,
            -- Moyenne de quantité par récolte
            COALESCE(AVG(recolte.quantite), 0) as moyenne_quantite_recolte,
            -- Nombre total de récoltes
            COUNT(recolte.ID_recolte) as nombre_recoltes,
            -- Nombre de saisons par produit
            (SELECT COUNT(*) FROM est_de_saison WHERE ID_Produit = Produit.ID_Produit) as nombre_saisons,
            -- Calcul de la part de marché (en pourcentage du total des récoltes)
            CASE 
                WHEN (SELECT SUM(quantite) FROM recolte) > 0 
                THEN COALESCE((SUM(recolte.quantite) * 100.0 / (SELECT SUM(quantite) FROM recolte)), 0)
                ELSE 0 
            END as part_marche,
            -- Ratio valeur/quantité
            CASE 
                WHEN SUM(recolte.quantite) > 0 
                THEN (SUM(recolte.quantite) * Produit.prix_vente) / SUM(recolte.quantite)
                ELSE 0 
            END as ratio_valeur_quantite
        FROM Produit
        LEFT JOIN recolte ON Produit.ID_Produit = recolte.ID_Produit
        GROUP BY Produit.ID_Produit, Produit.nom_produit, Produit.prix_vente
        ORDER BY valeur_totale DESC
    """
    
    mycursor.execute(sql)
    results = mycursor.fetchall()
    
    return render_template('produit/etat_produit.html', results=results)

@app.template_filter('to_datetime')
def to_datetime(date_value):
    if not date_value:
        return None
    if isinstance(date_value, str):
        return datetime.strptime(date_value, '%Y-%m-%d')
    if isinstance(date_value, datetime):
        return date_value
    if isinstance(date_value, date):
        return datetime.combine(date_value, datetime.min.time())
    return None

@app.route('/produit/delete', methods=['GET'])
def delete_produit_get():
    id_produit = request.args.get('id', type=int)
    
    if not id_produit:
        flash('ID produit non spécifié', 'error')
        return redirect('/produit')
    
    mycursor = get_db().cursor()
    
    # Récupération du produit et de ses saisons
    sql = """
        SELECT p.*, 
               GROUP_CONCAT(s.libelle_saison) as saisons,
               GROUP_CONCAT(s.code_saison) as saisons_id
        FROM Produit p
        LEFT JOIN est_de_saison eds ON p.ID_Produit = eds.ID_Produit
        LEFT JOIN Saison s ON eds.code_saison = s.code_saison
        WHERE p.ID_Produit = %s
        GROUP BY p.ID_Produit
    """
    mycursor.execute(sql, (id_produit,))
    produit = mycursor.fetchone()
    
    if not produit:
        flash('Produit non trouvé', 'error')
        return redirect('/produit')
    
    return render_template('produit/delete_produit.html', produit=produit)

@app.route('/produit/delete', methods=['POST'])
def delete_produit_post():
    mycursor = get_db().cursor()
    id_produit = request.form.get('id_produit', type=int)
    force = request.form.get('force') == 'true'
    
    if not id_produit:
        flash('ID produit non spécifié', 'error')
        return redirect('/produit')
    
    try:
        if force:
            # Suppression forcée : supprimer d'abord les dépendances
            mycursor.execute("DELETE FROM recolte WHERE ID_Produit = %s", (id_produit,))
            mycursor.execute("DELETE FROM est_vendu WHERE ID_Produit = %s", (id_produit,))
            
        # Suppression des saisons associées
        mycursor.execute("DELETE FROM est_de_saison WHERE ID_Produit = %s", (id_produit,))
        
        # Vérification des récoltes et ventes associées seulement si ce n'est pas une suppression forcée
        if not force:
            mycursor.execute("SELECT COUNT(*) as count FROM recolte WHERE ID_Produit = %s", (id_produit,))
            recolte_count = mycursor.fetchone()['count']
            
            if recolte_count > 0:
                flash('Impossible de supprimer ce produit car il est associé à des récoltes', 'error')
                return redirect('/produit')
            
            mycursor.execute("SELECT COUNT(*) as count FROM est_vendu WHERE ID_Produit = %s", (id_produit,))
            vente_count = mycursor.fetchone()['count']
            
            if vente_count > 0:
                flash('Impossible de supprimer ce produit car il est associé à des ventes', 'error')
                return redirect('/produit')
        
        # Suppression du produit
        mycursor.execute("DELETE FROM Produit WHERE ID_Produit = %s", (id_produit,))
        get_db().commit()
        
        flash('Produit supprimé avec succès', 'success')
        return redirect('/produit')
        
    except Exception as e:
        get_db().rollback()
        flash(f'Erreur lors de la suppression du produit: {str(e)}', 'error')
        return redirect('/produit')

@app.route('/conflicts/produit/<int:id_produit>')
def produit_conflicts(id_produit):
    mycursor = get_db().cursor()
    conflicts = {}
    
    # Vérification des récoltes
    mycursor.execute("SELECT * FROM recolte WHERE ID_Produit = %s", (id_produit,))
    recoltes = mycursor.fetchall()
    if recoltes:
        conflicts['recoltes'] = recoltes
    
    # Vérification des ventes
    mycursor.execute("SELECT * FROM est_vendu WHERE ID_Produit = %s", (id_produit,))
    ventes = mycursor.fetchall()
    if ventes:
        conflicts['ventes'] = ventes
    
    return render_template('produit/conflict_produit.html', 
                         conflicts=conflicts if conflicts else None,
                         produit_id=id_produit)

@app.route('/etat_marche', methods=['GET', 'POST'])
def etat_marche():
    if request.method == 'POST':
        jours_selectionnes = request.form.getlist('jours[]')
        
        if not jours_selectionnes:
            flash('Veuillez sélectionner au moins un jour', 'error')
            return redirect('/etat_marche')
            
        mycursor = get_db().cursor()
        
        jours_mapping = {
            'Dimanche': 1, 'Lundi': 2, 'Mardi': 3, 'Mercredi': 4,
            'Jeudi': 5, 'Vendredi': 6, 'Samedi': 7
        }
        jours_numeriques = [jours_mapping[jour] for jour in jours_selectionnes]
        jours_clause = "DAYOFWEEK(m.date_march) IN ({})".format(
            ','.join(['%s'] * len(jours_numeriques))
        )
        
        sql = f"""
            SELECT 
                m.nom_mache,
                CASE DAYOFWEEK(m.date_march)
                    WHEN 1 THEN 'Dimanche'
                    WHEN 2 THEN 'Lundi'
                    WHEN 3 THEN 'Mardi'
                    WHEN 4 THEN 'Mercredi'
                    WHEN 5 THEN 'Jeudi'
                    WHEN 6 THEN 'Vendredi'
                    WHEN 7 THEN 'Samedi'
                END as jour_marche,
                m.nombre_standes
            FROM Marche m
            WHERE {jours_clause}
            GROUP BY m.ID_Marche, m.nom_mache, m.date_march
            ORDER BY m.nom_mache
        """
        
        mycursor.execute(sql, jours_numeriques)
        results = mycursor.fetchall()
        
        total_stats = {
            'total_marches': len(results),
            'total_capacite': sum(r['nombre_standes'] for r in results),
            'jours_selectionnes': jours_selectionnes
        }
        
        return render_template('marche/etat_marche.html', 
                             results=results,
                             total_stats=total_stats)
    
    return render_template('marche/etat_marche.html')






if __name__ == '__main__':
    app.run(debug=True)


