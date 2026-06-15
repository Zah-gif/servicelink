# -*- coding: utf-8 -*-
"""
ServiceLink - Script de peuplement
Lancement: python manage.py shell -c "exec(open('populate_db.py', encoding='utf-8').read())"
"""
import random
from datetime import timedelta
from django.utils import timezone
from django.db import connection, transaction

from users.models import Utilisateur, Client, Prestataire
from services.models import Categorie, Metier, Commune, Service
from reservations.models import Reservation, Avis

# Noms par ethnie
NOMS_MANDE  = ['Coulibaly','Traore','Diallo','Konate','Doumbia','Diabate','Fofana','Camara','Keita','Sylla','Kouyate','Cisse','Bamba','Ouattara','Sanogo']
NOMS_AKAN   = ['Kouassi','Konan','Koffi','Yao','Atta','Assi','Brou','Aka','Affi','Amoikon','Kouadio','Kobenan','Amon','Amani','Adou']
NOMS_KROU   = ['Gba','Zoro','Gnaore','Tia','Bi','Gnahore','Zady','Gue','Wahi','Zahoui','Pohi','Ble','Dahi','Grohe','Gnagnon']
NOMS_GUR    = ['Silue','Kone','Soro','Nebie','Tuo','Fane','Coulogo','Drabo','Gbane','Yeo']
NOMS_GOURO  = ['Goli','Zro','Tie','Gnagnou','Loukou','Gbane','Zouhon','Gnagbe','Wahi','Nahounou']

PRENOMS_H   = ['Ibrahima','Moussa','Seydou','Mamadou','Drissa','Bakary','Souleymane','Kouame','Kofi','Kwame','Yao','Amani','Gnagnon','Zro','Goli','Yeo','Tuo','Lassina','Fousseni','Jean-Baptiste','Christian','Theodere','Herve','Patrick','Marcel','Justin','Emmanuel','Rodrigue','Franck','Serge','Wilfried','Didier','Stéphane','Arsene','Gilles']
PRENOMS_F   = ['Fatoumata','Aminata','Mariam','Rokia','Bintou','Awa','Adjoua','Akissi','Affoue','Amenan','Gnagna','Abla','Zata','Gnigba','Bintou','Marie-Claire','Jocelyne','Sandrine','Carine','Nadege','Christelle','Vanessa','Patricia','Laure','Estelle','Audrey','Pulcherie','Rosine','Danielle']

DESCRIPTIONS = {
    1: ["Fabrication et pose de meubles sur mesure. Plus de 8 ans d'experience a Abidjan.","Menuisier qualifie pour tous vos travaux de bois. Devis gratuit."],
    2: ["Travaux de maconnerie generale : construction, renovation, carrelage.","Macon professionnel pour vos projets de construction a Abidjan."],
    3: ["Soudure a l'arc et TIG. Portails, grilles de securite, escaliers metalliques.","Artisan soudeur pour tous vos travaux de metallerie et serrurerie."],
    4: ["Depannage urgent fuite d'eau, installation sanitaire. Disponible 7j/7.","Plombier certifie pour installation et reparation de tous systemes sanitaires."],
    5: ["Installation electrique, depannage, mise aux normes. Certifie et assure.","Electricien professionnel pour particuliers et entreprises. Devis gratuit."],
    6: ["Peinture interieure et exterieure, ravalement de facade. Travail soigne.","Peintre qualifie pour vos projets de renovation. Peintures de qualite."],
    7: ["Coiffeur a domicile : tresses, locks, soins capillaires. Materiel professionnel.","Specialiste en coiffures africaines et modernes. Deplacement a domicile."],
    8: ["Soins du visage, manucure, pedicure et epilation a domicile.","Estheticienne diplomee pour tous vos soins beaute a Abidjan."],
    9: ["Reparation televiseurs, refrigerateurs, climatiseurs et electromenagers.","Technicien qualifie pour depannage de tous appareils electroniques."],
    10:["Entretien et reparation auto, moto. Diagnostic electronique disponible.","Mecanicien experimente pour revision, freins, embrayage et vidange."],
    11:["Nettoyage domicile, repassage, cuisine. Serieuse et discrete.","Aide menagere experimentee pour entretien maison et garde d'enfants."],
    12:["Entretien jardins, taille haies, gazon. Materiel fourni.","Jardinier paysagiste pour creation et entretien d'espaces verts."],
}

BESOINS = [
    "Besoin d'une intervention urgente a mon domicile.",
    "Besoin d'un professionnel pour des travaux dans mon appartement.",
    "Intervention necessaire suite a une panne urgente.",
    "Besoin d'un devis pour des travaux dans ma villa.",
    "Service regulier mensuel souhaite pour l'entretien.",
    "Travaux a realiser avant la fin du mois.",
    "Urgence - besoin d'une intervention rapide.",
    "Renovation de ma cuisine, besoin d'un professionnel.",
    "Probleme recurrent que personne n'a resolu.",
    "Besoin de vos services pour mon bureau.",
]

COMMENTAIRES = [
    "Excellent travail ! Je recommande vivement ce prestataire.",
    "Tres satisfait du service. Travail rapide et propre.",
    "Bon prestataire, prix raisonnable. Je ferai encore appel.",
    "Travail de qualite, prestataire serieux et ponctuel.",
    "Intervention rapide et efficace. Probleme resolu.",
    "Professionnel competent. Explique bien son travail.",
    "Service impeccable, prestataire tres aimable.",
    "Tres bon travail dans les delais. Tarif honnete.",
    "Satisfait du resultat. Prestataire ponctuel.",
    "Excellent rapport qualite-prix. Je rappellerai.",
    "Travail soigne et professionnel. Bonne communication.",
    "Prestataire fiable. Je le recommande a mon entourage.",
    "Rapide, efficace et propre. Exactement ce qu'il fallait.",
    "Super experience ! Prestataire a l'ecoute.",
    "Parfait ! Travail soigne, tarif correct.",
]

COMMUNES = {1:'Cocody',2:'Yopougon',3:'Plateau',4:'Marcory',5:'Treichville',6:'Adjame',7:'Abobo',8:'Koumassi',9:'Port-Bouet',10:'Attecoube'}

def gen_nom(genre='H'):
    groupe = random.choice(['mande','akan','krou','gur','gouro'])
    noms_pool = {'mande':NOMS_MANDE,'akan':NOMS_AKAN,'krou':NOMS_KROU,'gur':NOMS_GUR,'gouro':NOMS_GOURO}
    nom    = random.choice(noms_pool[groupe])
    prenom = random.choice(PRENOMS_H if genre == 'H' else PRENOMS_F)
    return prenom, nom

nb_p=0; nb_c=0; nb_s=0; nb_r=0; nb_a=0

print("Demarrage du peuplement ServiceLink...")

CONFIGS = [
    (1,[1,2,3],15000,50000,120,480,True,True,'H'),
    (4,[1,4,5],8000,25000,60,180,True,False,'H'),
    (5,[1,2,6],10000,35000,60,240,False,False,'H'),
    (7,[1,3,4],5000,15000,60,120,True,True,'F'),
    (6,[2,7,8],20000,80000,240,720,False,False,'H'),
    (2,[2,7,10],25000,100000,480,1440,True,False,'H'),
    (3,[3,4,5],15000,45000,120,360,False,False,'H'),
    (9,[1,3,6],5000,20000,30,120,True,False,'H'),
    (10,[4,5,8],15000,60000,120,480,False,False,'H'),
    (11,[1,2,3,4],3000,8000,120,480,True,False,'F'),
    (12,[1,5,9],10000,30000,120,360,False,False,'H'),
    (1,[6,7,10],20000,70000,180,600,True,True,'H'),
    (5,[2,8,9],12000,40000,60,300,False,False,'H'),
    (4,[3,4,10],10000,30000,60,240,True,False,'H'),
    (6,[1,2,7],15000,50000,180,480,True,True,'H'),
    (8,[1,3,4,5],8000,25000,60,180,False,False,'F'),
    (2,[5,6,7],30000,120000,720,2880,True,False,'H'),
    (3,[8,9,10],12000,40000,90,360,False,False,'H'),
    (9,[2,4,6],3000,12000,30,90,True,False,'H'),
    (10,[1,3,7],20000,80000,180,720,False,False,'H'),
    (7,[5,6,8,9],6000,18000,60,180,True,True,'F'),
    (11,[2,7,10],4000,10000,120,360,False,False,'F'),
    (12,[4,5,6],8000,25000,120,480,True,False,'H'),
    (5,[1,2,3],8000,28000,60,240,False,False,'H'),
    (1,[7,8,9,10],18000,65000,180,720,True,False,'H'),
]

emails_utilises = set()
prestataires_crees = []
clients_crees = []

with transaction.atomic():

    print("\n--- PRESTATAIRES ---")
    for i,(mid,cids,tmin,tmax,dmin,dmax,verif,prem,genre) in enumerate(CONFIGS):
        prenom, nom = gen_nom(genre)
        email = f"prest{i}.{nom.lower()}@sl.ci"
        while email in emails_utilises:
            email = f"prest{i}{random.randint(1,99)}.{nom.lower()}@sl.ci"
        emails_utilises.add(email)
        tel = f"07{random.randint(10000000,99999999)}"
        try:
            with transaction.atomic():
                user = Utilisateur.objects.create_user(email=email,password='ServiceLink2025!',nom=nom,prenoms=prenom,telephone=tel)
                prest = Prestataire.objects.create(
                    id_utilisateur=user,est_verifie=verif,est_premium=prem,
                    est_disponible=random.choice([True,True,True,False]),
                    note_moyenne=round(random.uniform(3.5,5.0),2),
                    nombre_avis=random.randint(2,30),
                    description=random.choice(DESCRIPTIONS.get(mid,["Prestataire professionnel."])),
                )
                with connection.cursor() as cur:
                    for cid in cids:
                        cur.execute("INSERT IGNORE INTO intervient_dans (id_prestataire,id_commune) VALUES (%s,%s)",[prest.id_prestataire,cid])
                metier    = Metier.objects.get(id_metier=mid)
                categorie = Categorie.objects.get(id_categorie=metier.id_categorie.id_categorie)
                svc = Service.objects.create(
                    id_prestataire=prest,id_metier=metier,id_categorie=categorie,
                    titre=f"{metier.nom_metier} - {COMMUNES.get(random.choice(cids),'Abidjan')}",
                    description=random.choice(DESCRIPTIONS.get(mid,["Service professionnel."])),
                    tarif_min=tmin,tarif_max=tmax,duree_min=dmin,duree_max=dmax,est_actif=True,
                )
                prestataires_crees.append((prest,svc))
                nb_p+=1; nb_s+=1
                print(f"OK: {prenom} {nom} - {metier.nom_metier}")
        except Exception as e:
            print(f"SKIP: {prenom} {nom} - {e}")

    print("\n--- CLIENTS ---")
    for i in range(20):
        genre = random.choice(['H','F'])
        prenom, nom = gen_nom(genre)
        email = f"client{i}.{nom.lower()}@sl.ci"
        while email in emails_utilises:
            email = f"client{i}{random.randint(1,99)}.{nom.lower()}@sl.ci"
        emails_utilises.add(email)
        tel = f"05{random.randint(10000000,99999999)}"
        try:
            with transaction.atomic():
                user = Utilisateur.objects.create_user(email=email,password='ServiceLink2025!',nom=nom,prenoms=prenom,telephone=tel)
                client = Client.objects.create(id_utilisateur=user,commune_residence=random.choice(list(COMMUNES.values())))
                clients_crees.append(client)
                nb_c+=1
                print(f"OK: {prenom} {nom}")
        except Exception as e:
            print(f"SKIP: {prenom} {nom} - {e}")

    print("\n--- RESERVATIONS ---")
    if clients_crees and prestataires_crees:
        for i in range(60):
            try:
                with transaction.atomic():
                    client = random.choice(clients_crees)
                    prest, serv = random.choice(prestataires_crees)
                    statut = random.choice(['terminee','terminee','terminee','confirmee','en_attente','annulee'])
                    jours = random.randint(1,120)
                    date_c = timezone.now() - timedelta(days=jours)
                    date_s = (date_c + timedelta(days=random.randint(1,7))).date()
                    montant=None; date_conf=None; sp='non_paye'; mode=None; mc=None; mp=None
                    if statut in ['confirmee','terminee']:
                        date_conf = date_c + timedelta(hours=random.randint(1,48))
                        if serv.tarif_min and serv.tarif_max:
                            montant = round(random.randint(int(serv.tarif_min),int(serv.tarif_max))/1000)*1000
                        if statut == 'terminee':
                            sp = random.choice(['libere','libere','non_paye'])
                            if sp == 'libere' and montant:
                                mode = random.choice(['orange','mtn','wave'])
                                mc   = round(montant*5/100,2)
                                mp   = round(montant-mc,2)
                    Reservation.objects.create(
                        id_client=client,id_prestataire=prest,id_service=serv,
                        type_demande=random.choice(['directe','directe','devis']),
                        statut=statut,description_besoin=random.choice(BESOINS),
                        date_souhaitee=date_s,montant=montant,date_confirmation=date_conf,
                        statut_paiement=sp,mode_paiement=mode,montant_commission=mc,montant_prestataire=mp,
                    )
                    nb_r+=1
                    res = Reservation.objects.filter(id_client=client,id_prestataire=prest).last()
                    if statut=='terminee' and random.random()>0.25 and res:
                        note_a = random.choice([5,5,4,4,3,5])
                        Avis.objects.create(id_reservation=res,note=note_a,commentaire=random.choice(COMMENTAIRES),est_modere=False)
                        tous = Avis.objects.filter(id_reservation__id_prestataire=prest)
                        prest.nombre_avis=tous.count()
                        prest.note_moyenne=round(sum(a.note for a in tous)/tous.count(),2)
                        prest.save()
                        nb_a+=1
            except Exception:
                pass
        print(f"{nb_r} reservations, {nb_a} avis")

print("\n=============================")
print("PEUPLEMENT TERMINE !")
print(f"Prestataires : {nb_p}")
print(f"Clients      : {nb_c}")
print(f"Services     : {nb_s}")
print(f"Reservations : {nb_r}")
print(f"Avis         : {nb_a}")
print("=============================")
print("Mot de passe : ServiceLink2025!")
print("Ethnies : Gouro, Baoulé, Agni, Bété, Sénoufo, Koulango, Dioula...")