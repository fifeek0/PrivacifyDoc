
---

# PrivacifyDoc

PrivacifyDoc to narzędzie open-source stworzone do automatycznej anonimizacji danych wrażliwych na dokumentach. Naszym celem jest zapewnienie narzędzia, które pomoże chronić prywatność poprzez ukrywanie lub usuwanie informacji osobistych i poufnych z dokumentów tekstowych i obrazów.

## Funkcje

- **Automatyczne wykrywanie i anonimizacja danych wrażliwych**: PrivacifyDoc identyfikuje i anonimizuje dane takie jak imiona, nazwiska, adresy, numery telefonów, adresy e-mail, a także identyfikatory takie jak PESEL, NIP itd.
- **Wsparcie dla różnych formatów dokumentów**: Projekt obsługuje wiele formatów dokumentów, w tym PDF, DOCX, TXT, oraz obrazy.
- **Planowana integracja z bazą TERYT (Główny Urząd Statystyczny)**: Dla dokładniejszego rozpoznawania i walidacji adresów w Polsce.
- **Planowana intergracja z bazą imion i nazwisk w Polsce z rządowej hurtowni danych**  Dla dokładniejszego rozpoznawania imion i nazwisk.
- **Konfigurowalne reguły anonimizacji**: Możliwość definiowania własnych wzorców danych wrażliwych, które mają być anonimizowane.
- **Łatwa integracja**: Dzięki dostarczonemu API, PrivacifyDoc może być łatwo zintegrowane z innymi systemami.

## Wymagania

- Docker
- Python 3.8+
- Biblioteki Python: zobacz `requirements.txt`

## Instalacja

Aby zainstalować PrivacifyDoc, wykonaj następujące kroki:

1. Sklonuj repozytorium:

```bash
git clone https://github.com/yourusername/PrivacifyDoc.git
cd PrivacifyDoc
```

2. Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

## Szybki start

## Uruchamianie z Dockerem

Możesz również uruchomić PrivacifyDoc za pomocą Dockera:

1. Zbuduj obraz Dockera:

```bash
docker build -t privacifydoc .
```

2. Uruchom kontener Dockera:

```bash
docker run -d -p 8000:8000 privacifydoc
```

## Współpraca i wsparcie

PrivacifyDoc to projekt open-source'owy i zachęcamy do wspierania go poprzez:

- Zgłaszanie błędów i propozycji funkcji.
- Ulepszanie dokumentacji.
- Tworzenie pull requestów z nowymi funkcjami i poprawkami.

## Licencja

Projekt jest dostępny na licencji MIT. Szczegółowe informacje znajdziesz w pliku LICENSE.

## Kontakt

Jeśli masz pytania lub chcesz się przyłączyć do projektu, skontaktuj się z nami.

---
