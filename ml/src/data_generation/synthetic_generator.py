"""
Enhanced Synthetic Data Generator for Polish NER

Generates realistic training examples with Polish names, addresses, PESEL, NIP, etc.
"""

import random
import json
import re
from typing import List, Dict, Tuple, Optional, Union, Callable, Any
from faker import Faker
from datetime import datetime, timedelta
import string


class EnhancedSyntheticDataGenerator:
    """Generates realistic synthetic data for Polish NER tasks."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.fake = Faker('pl_PL')
        Faker.seed(seed)

        # Extended entity patterns
        self.polish_cities = [
            "Warszawa", "Kraków", "Łódź", "Wrocław", "Poznań", "Gdańsk",
            "Szczecin", "Bydgoszcz", "Lublin", "Katowice", "Białystok",
            "Gdynia", "Częstochowa", "Radom", "Sosnowiec", "Toruń"
        ]

        self.street_types = [
            "ul.", "al.", "pl.", "os.", "rondo", "skwer", "bulwar"
        ]

        self.company_suffixes = [
            "Sp. z o.o.", "S.A.", "Sp.j.", "Sp.p.", "Sp.c.",
            "Spółdzielnia", "Fundacja", "Stowarzyszenie"
        ]

        self.job_titles = [
            "Programista", "Analityk", "Manager", "Specjalista ds. IT",
            "Konsultant", "Dyrektor", "Kierownik", "Asystent", "Sekretarka",
            "Księgowy", "Prawnik", "Lekarz", "Inżynier", "Architekt"
        ]

        self.document_types = [
            "UMOWA NAJMU", "UMOWA SPRZEDAŻY", "UMOWA ZLECENIA",
            "UMOWA O PRACĘ", "PROTOKÓŁ", "WNIOSEK", "ZAŚWIADCZENIE",
            "ODPIS AKTU URODZENIA", "KARTA PACJENTA", "FAKTURA VAT"
        ]

        self.templates = self._load_enhanced_templates()
        self.noise_patterns = self._load_noise_patterns()

    def _load_enhanced_templates(self) -> List[str]:
        return [
            # Medical records with more detail
            """KARTA PACJENTA
            
Data wizyty: {DATE}
Lekarz prowadzący: dr {DOCTOR_NAME}

DANE PACJENTA:
Imię i nazwisko: {PERSON}
Data urodzenia: {BIRTH_DATE}
PESEL: {PESEL}
Adres zamieszkania: {ADDRESS}
Telefon kontaktowy: {PHONE}
E-mail: {EMAIL}

DANE KONTAKTOWE W NAGŁYCH WYPADKACH:
Osoba kontaktowa: {EMERGENCY_CONTACT}
Telefon: {EMERGENCY_PHONE}

WYWIAD:
{MEDICAL_HISTORY}

ROZPOZNANIE: {DIAGNOSIS}
ZALECENIA: {RECOMMENDATIONS}""",

            # Employment contract
            """UMOWA O PRACĘ Nr {CONTRACT_NUMBER}

zawarta w dniu {DATE} między:

PRACODAWCĄ:
{COMPANY}
z siedzibą w {COMPANY_ADDRESS}
NIP: {NIP}
REGON: {REGON}
reprezentowaną przez: {REPRESENTATIVE}

a

PRACOWNIKIEM:
{PERSON}
zamieszkałym w {ADDRESS}
PESEL: {PESEL}
nr dowodu osobistego: {ID_NUMBER}

§ 1. Przedmiot umowy
Pracodawca zatrudnia Pracownika na stanowisku: {JOB_TITLE}
w pełnym wymiarze czasu pracy.

§ 2. Wynagrodzenie
Miesięczne wynagrodzenie brutto: {SALARY} PLN

Kontakt: {EMAIL}, {PHONE}

Podpisy stron:
Pracodawca: ________________  Pracownik: ________________""",

            # Invoice with VAT
            """FAKTURA VAT Nr {INVOICE_NUMBER}

Data wystawienia: {DATE}
Data sprzedaży: {SALE_DATE}
Termin płatności: {PAYMENT_DATE}

SPRZEDAWCA:
{COMPANY}
{COMPANY_ADDRESS}
NIP: {NIP}
REGON: {REGON}
Tel.: {COMPANY_PHONE}
E-mail: {COMPANY_EMAIL}

NABYWCA:
{BUYER_COMPANY}
{BUYER_ADDRESS}
NIP: {BUYER_NIP}

OSOBA FIZYCZNA (jeśli dotyczy):
{PERSON}
{ADDRESS}
PESEL: {PESEL}

Opis towaru/usługi: {SERVICE_DESCRIPTION}
Wartość netto: {NET_AMOUNT} PLN
VAT 23%: {VAT_AMOUNT} PLN
Wartość brutto: {GROSS_AMOUNT} PLN

Sposób płatności: przelew
Nr konta: {BANK_ACCOUNT}""",

            # Personal data processing consent
            """ZGODA NA PRZETWARZANIE DANYCH OSOBOWYCH

Ja, niżej podpisany/a {PERSON}
zamieszkały/a w {ADDRESS}
PESEL: {PESEL}
nr dowodu osobistego: {ID_NUMBER}
telefon: {PHONE}
e-mail: {EMAIL}

wyrażam zgodę na przetwarzanie moich danych osobowych przez {COMPANY}
z siedzibą w {COMPANY_ADDRESS}
NIP: {NIP}

w celu: {PROCESSING_PURPOSE}

Data: {DATE}
Podpis: ________________""",

            # Bank account opening
            """WNIOSEK O OTWARCIE RACHUNKU BANKOWEGO

Data złożenia wniosku: {DATE}

DANE WNIOSKODAWCY:
Imię i nazwisko: {PERSON}
Data urodzenia: {BIRTH_DATE}
PESEL: {PESEL}
Nr dowodu osobistego: {ID_NUMBER}
Adres zamieszkania: {ADDRESS}
Adres korespondencyjny: {CORRESPONDENCE_ADDRESS}
Telefon: {PHONE}
E-mail: {EMAIL}

DANE ZAWODOWE:
Miejsce pracy: {COMPANY}
Adres pracodawcy: {COMPANY_ADDRESS}
NIP pracodawcy: {COMPANY_NIP}
Miesięczne dochody: {INCOME} PLN

OSOBA UPOWAŻNIONA (jeśli dotyczy):
{AUTHORIZED_PERSON}
PESEL: {AUTHORIZED_PESEL}""",

            # Real estate rental agreement
            """UMOWA NAJMU LOKALU MIESZKALNEGO

zawarta w dniu {DATE} między:

WYNAJMUJĄCYM:
{LANDLORD}
zamieszkałym w {LANDLORD_ADDRESS}
PESEL: {LANDLORD_PESEL}
nr dowodu: {LANDLORD_ID}
telefon: {LANDLORD_PHONE}

NAJEMCĄ:
{PERSON}
zamieszkałym w {ADDRESS}
PESEL: {PESEL}
nr dowodu: {ID_NUMBER}
telefon: {PHONE}
e-mail: {EMAIL}

PRZEDMIOT NAJMU:
Lokal mieszkalny o powierzchni {AREA} m²
położony w {PROPERTY_ADDRESS}

CZYNSZ: {RENT} PLN miesięcznie
KAUCJA: {DEPOSIT} PLN

Okres najmu: od {START_DATE} do {END_DATE}""",
        ]

    def _load_noise_patterns(self) -> list[
        Union[Callable[[Any], Any], Callable[[Any], str], Callable[[Any], Any], Callable[[Any], Any]]]:
        """Patterns to add realistic noise and variations to text."""
        return [
            lambda text: text.replace('l', '1').replace('I', '1').replace('O', '0'),
            lambda text: re.sub(r'(\d+)-(\d+)-(\d+)', r'\1 - \2 - \3', text),
            lambda text: text.replace('PESEL:', 'Pesel:').replace('NIP:', 'Nip:'),
            lambda text: text.replace(':', ' :').replace(',', ' ,'),
        ]

    def generate_batch(self,
                       num_examples: int = 100,
                       apply_noise: bool = True,
                       show_progress: bool = True) -> List[Dict]:
        """Generates a batch of synthetic data examples."""
        examples = []

        iterator = range(num_examples)
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(iterator, desc="Generating realistic synthetic data")

        for _ in iterator:
            example = self._generate_single_example(apply_noise=apply_noise)
            if example:
                examples.append(example)

        return examples

    def _generate_single_example(self, apply_noise: bool = True) -> Dict:
        """Generate single realistic training example."""
        template = random.choice(self.templates)

        person_name = self._generate_realistic_person()
        company_name = self._generate_realistic_company()
        address = self._generate_realistic_address()
        pesel = self._generate_valid_pesel()
        nip = self._generate_valid_nip()
        regon = self._generate_valid_regon()
        email = self._generate_realistic_email(person_name)
        phone = self._generate_realistic_phone()
        dates = self._generate_realistic_dates()
        amounts = self._generate_realistic_amounts()

        variables = {
            'PERSON': person_name,
            'COMPANY': company_name,
            'ADDRESS': address,
            'PESEL': pesel,
            'NIP': nip,
            'REGON': regon,
            'EMAIL': email,
            'PHONE': phone,
            'DATE': dates['current'],
            'BIRTH_DATE': dates['birth'],
            'START_DATE': dates['start'],
            'END_DATE': dates['end'],
            'SALE_DATE': dates['sale'],
            'PAYMENT_DATE': dates['payment'],
            # Additional realistic variables
            'DOCTOR_NAME': self.fake.name(),
            'EMERGENCY_CONTACT': self.fake.name(),
            'EMERGENCY_PHONE': self._generate_realistic_phone(),
            'CONTRACT_NUMBER': f"UOP/{random.randint(1, 999)}/{random.randint(2020, 2025)}",
            'INVOICE_NUMBER': f"FV/{random.randint(1, 9999)}/{random.randint(2020, 2025)}",
            'JOB_TITLE': random.choice(self.job_titles),
            'SALARY': f"{random.randint(3000, 15000):,}".replace(',', ' '),
            'ID_NUMBER': self._generate_id_number(),
            'BANK_ACCOUNT': self._generate_bank_account(),
            'COMPANY_ADDRESS': self._generate_realistic_address(),
            'COMPANY_PHONE': self._generate_realistic_phone(),
            'COMPANY_EMAIL': self._generate_realistic_email(company_name),
            'BUYER_COMPANY': self._generate_realistic_company(),
            'BUYER_ADDRESS': self._generate_realistic_address(),
            'BUYER_NIP': self._generate_valid_nip(),
            'SERVICE_DESCRIPTION': random.choice([
                "Usługi informatyczne", "Konsultacje prawne", "Usługi księgowe",
                "Projektowanie graficzne", "Szkolenia", "Audyt"
            ]),
            'NET_AMOUNT': amounts['net'],
            'VAT_AMOUNT': amounts['vat'],
            'GROSS_AMOUNT': amounts['gross'],
            'PROCESSING_PURPOSE': random.choice([
                "rekrutacji", "prowadzenia działalności", "realizacji umowy",
                "marketingu", "obsługi klienta"
            ]),
            'INCOME': f"{random.randint(3000, 12000):,}".replace(',', ' '),
            'AUTHORIZED_PERSON': self.fake.name(),
            'AUTHORIZED_PESEL': self._generate_valid_pesel(),
            'LANDLORD': self.fake.name(),
            'LANDLORD_ADDRESS': self._generate_realistic_address(),
            'LANDLORD_PESEL': self._generate_valid_pesel(),
            'LANDLORD_ID': self._generate_id_number(),
            'LANDLORD_PHONE': self._generate_realistic_phone(),
            'PROPERTY_ADDRESS': self._generate_realistic_address(),
            'AREA': random.randint(25, 120),
            'RENT': f"{random.randint(1500, 5000):,}".replace(',', ' '),
            'DEPOSIT': f"{random.randint(1500, 5000):,}".replace(',', ' '),
            'CORRESPONDENCE_ADDRESS': self._generate_realistic_address(),
            'REPRESENTATIVE': self.fake.name(),
            'MEDICAL_HISTORY': random.choice([
                "Bez obciążeń", "Nadciśnienie tętnicze", "Cukrzyca typu 2",
                "Alergia na penicylinę", "Choroba wieńcowa"
            ]),
            'DIAGNOSIS': random.choice([
                "Kontrola profilaktyczna", "Infekcja górnych dróg oddechowych",
                "Nadciśnienie tętnicze", "Zapalenie gardła", "Migrena"
            ]),
            'RECOMMENDATIONS': random.choice([
                "Kontrola za 6 miesięcy", "Przyjmować leki zgodnie z zaleceniem",
                "Dieta niskosodowa", "Regularny pomiar ciśnienia", "Odpoczynek"
            ])
        }

        try:
            text = template.format(**variables)
        except KeyError as e:
            missing_var = str(e).strip("'")
            variables[missing_var] = f"[{missing_var}]"
            text = template.format(**variables)

        if apply_noise and random.random() < 0.3:  # 30% chance of noise
            noise_func = random.choice(self.noise_patterns)
            text = noise_func(text)

        # Extract entities
        entities = self._extract_entities_advanced(text, variables)

        return {
            "text": text,
            "entities": entities
        }

    def _generate_realistic_person(self) -> str:
        """Generate realistic Polish person name."""
        if random.random() < 0.1:
            title = random.choice(["dr", "prof.", "mgr", "inż."])
            return f"{title} {self.fake.name()}"
        return self.fake.name()

    def _generate_realistic_company(self) -> str:
        """Generate realistic company name."""
        base_name = random.choice([
            self.fake.company().replace(' Sp. z o.o.', ''),
            f"{self.fake.last_name()} {random.choice(['Group', 'Solutions', 'Consulting', 'Services'])}",
            f"{random.choice(['Euro', 'Polish', 'Modern', 'Smart'])} {random.choice(['Tech', 'Systems', 'Logistics', 'Finance'])}"
        ])
        suffix = random.choice(self.company_suffixes)
        return f"{base_name} {suffix}"

    def _generate_realistic_address(self) -> str:
        """Generate realistic Polish address."""
        street_type = random.choice(self.street_types)
        street_name = self.fake.street_name()
        building_number = random.randint(1, 150)

        # Sometimes add apartment number
        apartment = ""
        if random.random() < 0.4:
            apartment = f"/{random.randint(1, 50)}"

        postal_code = self.fake.postcode()
        city = random.choice(self.polish_cities)

        return f"{street_type} {street_name} {building_number}{apartment}, {postal_code} {city}"

    def _generate_realistic_email(self, name: str) -> str:
        """Generate realistic email based on name."""
        if not name or name.startswith('['):
            return self.fake.email()

        clean_name = re.sub(r'[^a-zA-ZąćęłńóśżźĄĆĘŁŃÓŚŻŹ\s]', '', name.lower())
        parts = clean_name.split()

        if len(parts) >= 2:
            patterns = [
                f"{parts[0]}.{parts[-1]}",
                f"{parts[0][0]}.{parts[-1]}",
                f"{parts[0]}{parts[-1]}",
                f"{parts[0]}{random.randint(1, 99)}"
            ]
            username = random.choice(patterns)
        else:
            username = clean_name if clean_name else "user"

        domain = random.choice([
            "gmail.com", "wp.pl", "onet.pl", "interia.pl",
            "o2.pl", "poczta.fm", "gazeta.pl"
        ])

        return f"{username}@{domain}"

    def _generate_realistic_phone(self) -> str:
        """Generate realistic Polish phone number."""
        formats = [
            "+48 {} {} {}",
            "+48-{}-{}-{}",
            "{} {} {}",
            "{}-{}-{}",
            "({}) {} {}"
        ]

        area_code = random.choice([
            "501", "502", "503", "504", "505", "506", "507", "508", "509",
            "600", "601", "602", "603", "604", "605", "606", "607", "608", "609",
            "660", "661", "662", "663", "664", "665", "666", "667", "668", "669",
            "780", "781", "782", "783", "784", "785", "786", "787", "788", "789"
        ])

        number1 = f"{random.randint(100, 999)}"
        number2 = f"{random.randint(100, 999)}"

        format_str = random.choice(formats)
        return format_str.format(area_code, number1, number2)

    def _generate_realistic_dates(self) -> Dict[str, str]:
        """Generate realistic date combinations."""
        current = datetime.now()

        return {
            'current': current.strftime("%d.%m.%Y"),
            'birth': (current - timedelta(days=random.randint(6570, 25550))).strftime("%d.%m.%Y"),  # 18-70 years
            'start': (current + timedelta(days=random.randint(1, 90))).strftime("%d.%m.%Y"),
            'end': (current + timedelta(days=random.randint(365, 1095))).strftime("%d.%m.%Y"),  # 1-3 years
            'sale': (current - timedelta(days=random.randint(1, 30))).strftime("%d.%m.%Y"),
            'payment': (current + timedelta(days=random.randint(14, 30))).strftime("%d.%m.%Y")
        }

    def _generate_realistic_amounts(self) -> Dict[str, str]:
        """Generate realistic financial amounts."""
        net = random.randint(500, 50000)
        vat = int(net * 0.23)
        gross = net + vat

        return {
            'net': f"{net:,}".replace(',', ' '),
            'vat': f"{vat:,}".replace(',', ' '),
            'gross': f"{gross:,}".replace(',', ' ')
        }

    def _generate_id_number(self) -> str:
        """Generate realistic Polish ID number."""
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=6))
        return f"{letters} {numbers}"

    def _generate_bank_account(self) -> str:
        """Generate realistic Polish bank account number."""
        numbers = ''.join(random.choices(string.digits, k=26))
        formatted = ' '.join([numbers[i:i+4] for i in range(0, len(numbers), 4)])
        return f"PL {formatted}"

    def _generate_valid_regon(self) -> str:
        """Generate valid 9-digit REGON with proper checksum."""
        digits = [random.randint(0, 9) for _ in range(8)]

        weights = [8, 9, 2, 3, 4, 5, 6, 7]
        checksum = sum(d * w for d, w in zip(digits, weights)) % 11

        if checksum == 10:
            checksum = 0

        return ''.join(map(str, digits + [checksum]))

    def _extract_entities_advanced(self, text: str, variables: Dict[str, str]) -> List[Tuple[int, int, str]]:
        """Advanced entity extraction with better pattern matching."""
        entities = []

        entity_mappings = {
            'PERSON': ['PERSON', 'DOCTOR_NAME', 'EMERGENCY_CONTACT', 'AUTHORIZED_PERSON', 'LANDLORD', 'REPRESENTATIVE'],
            'COMPANY': ['COMPANY', 'BUYER_COMPANY'],
            'ADDRESS': ['ADDRESS', 'COMPANY_ADDRESS', 'BUYER_ADDRESS', 'LANDLORD_ADDRESS', 'PROPERTY_ADDRESS', 'CORRESPONDENCE_ADDRESS'],
            'PESEL': ['PESEL', 'LANDLORD_PESEL', 'AUTHORIZED_PESEL'],
            'NIP': ['NIP', 'BUYER_NIP', 'COMPANY_NIP'],
            'REGON': ['REGON'],
            'EMAIL': ['EMAIL', 'COMPANY_EMAIL'],
            'PHONE': ['PHONE', 'EMERGENCY_PHONE', 'COMPANY_PHONE', 'LANDLORD_PHONE'],
            'DATE': ['DATE', 'BIRTH_DATE', 'START_DATE', 'END_DATE', 'SALE_DATE', 'PAYMENT_DATE'],
            'AMOUNT': ['SALARY', 'NET_AMOUNT', 'VAT_AMOUNT', 'GROSS_AMOUNT', 'INCOME', 'RENT', 'DEPOSIT'],
            'ID_NUMBER': ['ID_NUMBER', 'LANDLORD_ID'],
            'BANK_ACCOUNT': ['BANK_ACCOUNT'],
            'CONTRACT_NUMBER': ['CONTRACT_NUMBER', 'INVOICE_NUMBER']
        }

        for entity_type, var_names in entity_mappings.items():
            for var_name in var_names:
                if var_name in variables:
                    value = variables[var_name]
                    if value and not value.startswith('['):
                        start = 0
                        while True:
                            pos = text.find(value, start)
                            if pos == -1:
                                break
                            entities.append((pos, pos + len(value), entity_type))
                            start = pos + len(value)

        entities = self._remove_overlapping_entities(entities)

        return sorted(entities, key=lambda x: x[0])

    def _remove_overlapping_entities(self, entities: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
        """Remove overlapping entities, keeping the longer ones."""
        if not entities:
            return entities

        entities.sort(key=lambda x: (x[0], -(x[1] - x[0])))

        result = []
        for entity in entities:
            start, end, label = entity

            overlaps = False
            for existing_start, existing_end, _ in result:
                if not (end <= existing_start or start >= existing_end):
                    overlaps = True
                    break

            if not overlaps:
                result.append(entity)

        return result

    def _generate_valid_pesel(self) -> str:
        """Generate valid PESEL with checksum."""
        digits = [random.randint(0, 9) for _ in range(10)]

        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        checksum = sum(d * w for d, w in zip(digits, weights))
        control = (10 - (checksum % 10)) % 10

        return ''.join(map(str, digits + [control]))

    def _generate_valid_nip(self) -> str:
        """Generate valid NIP with checksum."""
        digits = [random.randint(0, 9) for _ in range(9)]

        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(d * w for d, w in zip(digits, weights))
        control = checksum % 11

        if control == 10:
            # Regenerate if control digit would be 10
            return self._generate_valid_nip()

        formatted = ''.join(map(str, digits + [control]))
        # Sometimes format with dashes
        if random.random() < 0.5:
            return f"{formatted[:3]}-{formatted[3:6]}-{formatted[6:8]}-{formatted[8:]}"
        return formatted

    def save_dataset(self, examples: List[Dict], output_path: str):
        """Save dataset in JSONL format with metadata."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')

        # Save metadata
        metadata = {
            'num_examples': len(examples),
            'entity_types': list(set(
                entity[2] for example in examples
                for entity in example['entities']
            )),
            'generation_date': datetime.now().isoformat(),
            'generator_version': '2.0'
        }

        metadata_path = output_path.replace('.jsonl', '_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(examples)} examples to {output_path}")
        print(f"Metadata saved to {metadata_path}")
