# PrivacifyDoc

PrivacifyDoc is an open-source tool designed to automatically anonymize sensitive data in documents. Our goal is to provide a tool that helps protect privacy by hiding or removing personal and confidential information from text documents and images.

## Features

- **Automatic Detection and Anonymization of Sensitive Data**: PrivacifyDoc identifies and anonymizes data such as names, addresses, phone numbers, email addresses, and identifiers like PESEL, NIP, etc.
- **Support for Various Document Formats**: The project supports multiple document formats, including PDF, DOCX, TXT, and images.
- **Planned Integration with TERYT Database (Central Statistical Office of Poland)**: For more accurate recognition and validation of addresses in Poland.
- **Planned Integration with the Database of Names and Surnames from the Government Data Warehouse**: For more accurate recognition of names and surnames.
- **Configurable Anonymization Rules**: Allows defining custom patterns of sensitive data to be anonymized.
- **Easy Integration**: With the provided API, PrivacifyDoc can be easily integrated with other systems.

## Architecture and Technologies

The project leverages modern solutions and technologies to ensure performance, scalability, and ease of extension:

- **CQRS (Command Query Responsibility Segregation)**: Separation of responsibilities between commands (write) and queries (read) to improve performance, scalability, and security.
- **Event Sourcing**: Storing application state changes as a sequence of events, which facilitates history playback, debugging, and analysis.
- **RabbitMQ**: Use of RabbitMQ message broker for inter-service communication, supporting asynchronicity and system resilience.
- **MongoDB**: Use of the non-relational MongoDB database for flexible data storage and easy scalability.
- **API Backend**: A backend module based on technologies supporting CQRS and Event Sourcing, utilizing RabbitMQ for communication and MongoDB as the database.
- **Frontend**: User interface created with React and TypeScript, providing a dynamic and responsive web application experience.

## Requirements

- Docker
- Python 3.8+
- Python libraries: see `requirements.txt`

## Installation

To install PrivacifyDoc, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/yourusername/PrivacifyDoc.git
cd PrivacifyDoc
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Running with Docker

You can also run PrivacifyDoc using Docker:

1. Build the Docker image:

```bash
docker build -t privacifydoc .
```

2. Run the Docker container:

```bash
docker run -d -p 8000:8000 privacifydoc
```

## Contribution and Support

PrivacifyDoc is an open-source project, and we encourage contributions by:

- Reporting bugs and suggesting features.
- Improving documentation.
- Creating pull requests with new features and fixes.

## License

The project is available under the MIT License. For more details, see the LICENSE file.

## Contact

If you have any questions or want to join the project, please contact us.

---

# PrivacifyDoc

PrivacifyDoc to narzędzie open-source stworzone do automatycznej anonimizacji danych wrażliwych na dokumentach. Naszym celem jest zapewnienie narzędzia, które pomoże chronić prywatność poprzez ukrywanie lub usuwanie informacji osobistych i poufnych z dokumentów tekstowych i obrazów.

## Funkcje

- **Automatyczne wykrywanie i anonimizacja danych wrażliwych**: PrivacifyDoc identyfikuje i anonimizuje dane takie jak imiona, nazwiska, adresy, numery telefonów, adresy e-mail, a także identyfikatory takie jak PESEL, NIP itd.
- **Wsparcie dla różnych formatów dokumentów**: Projekt obsługuje wiele formatów dokumentów, w tym PDF, DOCX, TXT, oraz obrazy.
- **Planowana integracja z bazą TERYT (Główny Urząd Statystyczny)**: Dla dokładniejszego rozpoznawania i walidacji adresów w Polsce.
- **Planowana integracja z bazą imion i nazwisk w Polsce z rządowej hurtowni danych**: Dla dokładniejszego rozpoznawania imion i nazwisk.
- **Konfigurowalne reguły anonimizacji**: Możliwość definiowania własnych wzorców danych wrażliwych, które mają być anonimizowane.
- **Łatwa integracja**: Dzięki dostarczonemu API, PrivacifyDoc może być łatwo zintegrowane z innymi systemami.

## Architektura i Technologie

Projekt wykorzystuje nowoczesne rozwiązania i technologie, aby zapewnić wydajność, skalowalność i łatwość rozszerzania:

- **CQRS (Command Query Responsibility Segregation)**: Rozdzielenie odpowiedzialności pomiędzy komendami (zapis) a zapytaniami (odczyt) w celu zwiększenia wydajności, skalowalności i bezpieczeństwa.
- **Event Sourcing**: Zapisywanie zmian w stanie aplikacji jako sekwencję zdarzeń, co ułatwia odtwarzanie historii zmian, debugowanie i analizę.
- **RabbitMQ**: Zastosowanie brokera wiadomości RabbitMQ do zarządzania komunikacją międzyserwisową, co wspiera asynchroniczność i odporność systemu.
- **MongoDB**: Użycie nierelacyjnej bazy danych MongoDB dla elastycznego przechowywania danych i łatwej skalowalności.
- **API Backend**: Moduł backendowy oparty na technologiach wspierających CQRS i Event Sourcing, wykorzystujący RabbitMQ do komunikacji oraz MongoDB jako bazy danych.
- **Frontend**: Interfejs użytkownika stworzony z użyciem React i TypeScript, zapewniający dynamiczną i responsywną obsługę aplikacji webowej.

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

### Uruchamianie z Dockerem

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
