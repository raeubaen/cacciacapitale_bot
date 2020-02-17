...
TUTTO IL NECESSARIO PER IL DEPLOYMENT NON E' QUI, VA PRESO DALLE ALTRE CARTELLE
Versione di Python:
3.6.9 o comunque >= 3.6 - salvata in runtime.txt

Dipendenze:
  - pacchetti python in requirements.txt

Seguendo queste istruzioni si installa il development server,
che consente di modificare e di debuggare il codice,
ma non di fare il deploy su heroku.

E' necessario installare le librerie ed eseguire il tutto
all'interno di un virtual environment Python

Per fare ciò basta porsi nella cartella EMME ed eseguire:
virtualenv -p python3 emme_env
source $HOME/emme_env/bin/activate
pip install -r requirements.txt

Per inizializzare il tutto:
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser #per creare l'account per entrare

Per eseguire il development server:
./manage.py runserver --noreload

e ctrl-click sul link a 127.ecc...


I file nella root directory sono quelli originali della prima 
implementazione di EMME, aggiunti ai files essenziali per django

I file nella cartella emme_site/ sono relativi al funzionamento della back-end
che gestisce il sito vero e proprio

I file nella cartella M/ sono relativi al funzionamento della back-end che
gestisce il bot e i campi dei database

I file nella cartella templates/ sono relativi al funzionamento della
front-end e contengono i template delle pagine html.

I parametri di M_State (il path) si modificano da M/apps.py
# cacciacapitale_bot
