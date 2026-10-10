# football-value-predictor

Projekt uczący się przewidywać, czy wartość rynkowa piłkarza **wzrośnie, spadnie czy zostanie mniej więcej taka sama** w ciągu najbliższych 180 dni. Robiony samodzielnie jako projekt do portfolio, w trakcie rozwijania.

## Co to robi

1. Pobiera z Transfermarkt (przez lokalnie uruchomione `transfermarkt-api`) składy klubów Premier League, profile zawodników i historię ich wartości rynkowej.
2. Zapisuje dane do SQLite (SQLAlchemy).
3. Z historii wartości buduje przykłady treningowe: cechy liczone z danych **sprzed** punktu `t`, etykieta z tego, co stało się 180 dni **po** `t`.
4. Trenuje klasyfikator XGBoost z podziałem czasowym (nie losowym) na train/test.
5. Dociąga statystyki formy (gole, asysty, minuty, rating) z API-Football i dopasowuje zawodników między źródłami.

## Stack

- **Język:** Python
- **Dane i baza:** SQLite, SQLAlchemy 2.0, pandas, NumPy
- **API:** requests, `transfermarkt-api` (Docker), API-Football
- **ML:** XGBoost, scikit-learn
- **Dopasowanie nazw:** rapidfuzz
- **Wizualizacja:** matplotlib
- **Narzędzia:** Docker, Git/GitHub, python-dotenv
- **W planach:** SHAP, Streamlit

## Dane

- **Transfermarkt** (nieoficjalne `transfermarkt-api` w Dockerze): wartość rynkowa w czasie, profile, składy. Aktualnie Premier League, 544 zawodników.
- **API-Football** (darmowy plan): statystyki ligowe z sezonu 2023. Limit 100 zapytań dziennie, do tego limit na minutę, dostępne tylko sezony 2022-2024.

## Cechy i etykieta

Cechy (tylko z przeszłości względem `t`): zmiana wartości w ostatnich 180 dniach, nachylenie trendu z 4 ostatnich punktów, wiek, zmiana klubu, dni od poprzedniej wyceny, liczba dotychczasowych wycen.

Etykieta: `increase` / `stable` / `loss` po 180 dniach, próg stabilności ±15%.

## Wyniki na ten moment

Podział czasowy 80/20, próg 15%:

- accuracy ≈ 0.48, macro F1 ≈ 0.47
- naiwny baseline (zawsze zgaduj najczęstszą klasę) ≈ 43% accuracy

Model niewiele przebija baseline. Ważność cech jest rozłożona dość równo (żadna nie dominuje), więc samo to, co wiadomo z historii cen, to za mało.

## Co próbowałem

- **Interpolacja Czebyszewa** jako metoda prognozy: odrzucona. Wielomiany świetnie interpolują wewnątrz przedziału, ale ekstrapolacja w przyszłość jest niestabilna, a historia wartości jest zaszumiona i nieregularna.
- **Wagi klas** (`sample_weight`): lepszy recall dla klas rzadszych, ale niższa accuracy.
- **Różne progi stabilności** (5%, 10%, 15%, 20%): macro F1 zmienia się tylko z 0.44 do 0.46. Próg nie jest wąskim gardłem.
- **Nachylenie trendu** (regresja liniowa z 4 ostatnich punktów): drobna poprawa, macro F1 z 0.46 do 0.47.

## Ograniczenia

- Dane tylko z Premier League i raczej z topowych klubów, więc klasa `increase` dominuje (młodzi zawodnicy zwykle drożeją).
- Ekstremalne zmiany procentowe u bardzo młodych zawodników (start od bardzo niskich wycen). Do rozważenia przycinanie lub log.
- Statystyki z API-Football dotyczą jednego sezonu (2023/24), więc to cecha statyczna. Dołączanie ich do starszych przykładów byłoby wyciekiem danych z przyszłości, więc można je użyć tylko dla przykładów po zakończeniu sezonu.
- Dopasowanie zawodników między źródłami (rapidfuzz, `partial_ratio`, próg 85) pomija część osób, np. gdy nazwiska zapisano inaczej ("Vitor Reis" i "Vitor Nunes"). Wolę brak danych niż błędne dopasowanie.
- Darmowy limit API-Football sprawia, że zbieranie statystyk dla całej ligi trwa kilka dni.

## Struktura

```
src/
  config.py               # konfiguracja, mapowanie klubów
  data/
    db.py                 # modele SQLAlchemy (Player, MarketValueSnapshot, PlayerStats)
    transfermarkt_client.py
    api_football_client.py
    matching.py           # dopasowanie zawodników między API
    collect.py            # zbieranie z Transfermarkt
    collect_stats.py      # zbieranie statystyk z API-Football
  features/
    build_dataset.py      # cechy + etykieta
  analysis/
    explore.py            # wykresy
  models/
    train.py              # baseline + XGBoost
data/                     # baza SQLite, dataset CSV (poza gitem)
```

## Uruchomienie

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

1. Uruchom `transfermarkt-api` (Docker, port 8000), instrukcja w repo felipeall/transfermarkt-api.
2. W `.env` ustaw `API_FOOTBALL_KEY`.
3. Dane z Transfermarkt: `python -m src.data.collect`
4. Statystyki formy: `python -m src.data.collect_stats`
5. Dataset: `build_examples()` z `src/features/build_dataset.py` zapisuje `data/training_examples.csv`
6. Trening: `python -m src.models.train`

## Plan

- [ ] Zebrać statystyki formy dla kolejnych klubów i dołączyć je do cech
- [ ] Porównać model z formą i bez niej
- [ ] SHAP / feature importance
- [ ] Wykrywanie niedowartościowanych zawodników
- [ ] Dashboard w Streamlit
- [ ] Więcej lig
