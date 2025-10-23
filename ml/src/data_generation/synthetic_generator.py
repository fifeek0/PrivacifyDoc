"""
Synthetic Data Generator for Polish NER

Generates training examples with Polish names, addresses, PESEL, NIP, etc.
"""

import random
import json
from typing import List, Dict, Tuple
from faker import Faker


class SyntheticDataGenerator:
    """Generates synthetic data for Polish NER tasks."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.fake = Faker('pl_PL')
        Faker.seed(seed)

        self.templates = self._load_templates()

    def _load_templates(self) -> List[str]:
        return [
            # Medical record
            """Dane pacjenta:
Imię i nazwisko: {PERSON}
Adres: {ADDRESS}
PESEL: {PESEL}
Kontakt: {EMAIL}, tel. {PHONE}
Rozpoznanie: {DIAGNOSIS}""",

            # Job application
            """Szanowni Państwo,

Nazywam się {PERSON} i aplikuję na stanowisko {JOB}.
Mieszkam w {CITY} przy {STREET}.
Mój numer PESEL: {PESEL}.
Proszę o kontakt: {EMAIL}, {PHONE}

Pozdrawiam,
{PERSON}""",

            # Invoice
            """FAKTURA VAT {NUMBER}

Sprzedawca:
{COMPANY}
NIP: {NIP}
{ADDRESS}

Nabywca:
{PERSON}
{ADDRESS}
PESEL: {PESEL}

Do zapłaty: {AMOUNT} PLN""",

            # Contract
            """UMOWA {TYPE}

Strona pierwsza:
{PERSON}
zamieszkały: {ADDRESS}
PESEL: {PESEL}

Strona druga:
{COMPANY}
NIP: {NIP}
REGON: {REGON}
{ADDRESS}

Kontakt: {EMAIL}, {PHONE}""",
        ]

    def generate_batch(self,
                       num_examples: int = 100,
                       show_progress: bool = True) -> List[Dict]:
        """"Generates a batch of synthetic data examples."""
        examples = []

        iterator = range(num_examples)
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(iterator, desc="Generating synthetic data")

        for _ in iterator:
            example = self._generate_single_example()
            if example:
                examples.append(example)

        return examples

    def _generate_single_example(self) -> Dict:
        """"Generate single training example."""
        template = random.choice(self.templates)

        person_name = self.fake.name()
        company_name = self.fake.company()
        street = f"{self.fake.street_name()} {random.randint(1, 150)}"
        city = self.fake.city()
        postal_code = self.fake.postcode()
        address = f"{street}, {postal_code} {city}"

        pesel = self._generate_valid_pesel()
        nip = self._generate_valid_nip()
        regon = self._generate_regon()

        email = self.fake.email()
        phone = f"+48 {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"

        text = template.format(
            PERSON=person_name,
            COMPANY=company_name,
            STREET=street,
            CITY=city,
            ADDRESS=address,
            PESEL=pesel,
            NIP=nip,
            REGON=regon,
            EMAIL=email,
            PHONE=phone,
            NUMBER=f"{random.randint(1, 999)}/{random.randint(2020, 2025)}",
            AMOUNT=f"{random.randint(100, 100000):.2f}",
            TYPE=random.choice(["NAJMU", "SPRZEDAŻY", "ZLECENIA"]),
            JOB=random.choice(["Programista", "Manager", "Specjalista"]),
            DIAGNOSIS=random.choice(["Kontrola", "Grypa", "Badanie"])
        )

        entities = self._extract_entities(text, {
            "PERSON": person_name,
            "COMPANY": company_name,
            "ADDRESS": address,
            "PESEL": pesel,
            "NIP": nip,
            "REGON": regon,
            "EMAIL": email,
            "PHONE": phone
        })

        return {
            "text": text,
            "entities": entities
        }

    def _extract_entities(
            self,
            text: str,
            values: Dict[str, str]
    ) -> List[Tuple[int, int, str]]:

        entities = []

        for entity_type, value in values.items():
            start = 0
            while True:
                pos = text.find(value, start)
                if pos == -1:
                    break

                entities.append((pos, pos + len(value), entity_type))
                start = pos + len(value)

        return sorted(entities, key=lambda x: x[0])

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
            control = random.randint(0, 9)

        return ''.join(map(str, digits + [control]))

    def _generate_regon(self) -> str:
        """Generate REGON (9 digits, no checksum, for simplicity)."""
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])

    def save_dataset(self,
                     examples: List[Dict],
                     output_path: str):
        """Save dataset in JSONL format.

        Args:
            examples: List of generated examples.
            output_path: Path to save the JSONL file.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')

        print(f"Saved {len(examples)} examples to {output_path}")


def split_dataset(
        examples: List[Dict],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
        Split dataset into train/val/test.

        Args:
            examples: Full dataset
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio

        Returns:
            (train, val, test) tuples
        """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    # Shuffle
    random.shuffle(examples)

    # Split
    n = len(examples)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train = examples[:train_end]
    val = examples[train_end:val_end]
    test = examples[val_end:]

    return train, val, test
