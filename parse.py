from dataclasses import dataclass, fields
import json
import pickle
import sqlite3
from typing import Optional

@dataclass
class Entity:
    description: str
    id: Optional[int] = None
    nif: Optional[int] = None

@dataclass
class Contract:
    id: int
    initialContractualPrice: Optional[float] # initialContractualPrice so deve estar nulo se ocorrer um erro no parsing do valor (deve estar sempre presente no contrato) 
    totalEffectivePrice: Optional[float]
    invitees: list[Entity]
    contestants: list[Entity]
    contracting: list[Entity]
    contracted: list[Entity]
    groupMembers: list[Entity]  # Relacionado com cocontratantes, nao sei
    announcementId: Optional[int]
    frameworkAgreementProcedureId: Optional[int] # Nº do acordo quadro
    frameworkAgreementProcedureDescription: str # Descrição do acordo quadro
    publicationDate: Optional[str] # publicationDate so deve estar nulo se ocorrer um erro na normalizacao da data (deve estar sempre presente no contrato) 
    objectBriefDescription: str
    cpvs: list[tuple[str, bool]] 
    ccp: bool = False 
    ambientCriteria: bool = False  # Contrato sustentável
    materialCriteria: bool = False  # Critérios materiais
    cocontratantes: bool = False 
    aquisitionStateMemberUE: bool = False 
    income: bool = False  # Preço contratual (a receber) de um contrato de concessão
    increments: bool = False
    normal: bool = False 
    contractTypeCS: bool = False  # Contrato de concessão
    centralizedProcedure: bool = False
    infoAquisitionStateMemberUE: Optional[str] = None
    signingDate: Optional[str] = None
    closeDate: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    executionDeadline: Optional[str] = None
    contractingProcedureType: Optional[str] = None
    contractFundamentationType: Optional[str] = None
    directAwardFundamentationType: Optional[str] = None
    nonWrittenContractJustificationTypes: Optional[str] = None
    regime: Optional[str] = None
    specialMeasures: Optional[str] = None
    executionPlace: Optional[str] = None
    causesDeadlineChange: Optional[str] = None
    causesPriceChange: Optional[str] = None
    endOfContractType: Optional[str] = None
    contractStatus: Optional[str] = None
    contractTypes: Optional[str] = None
    
def parse_entities(entity_list: list[dict], entity_map: dict) -> list[Entity]:
    if not entity_list: 
        return []

    out = []

    for entity_json in entity_list:
        entity = Entity(description=entity_json["description"].strip())
       
        if entity_json["nif"].isnumeric() and len(entity_json["nif"]) == 9:
            entity.nif = int(entity_json["nif"])

        if entity_json["id"] > 0:
            entity.id = entity_json["id"]

        if entity.id:            
            if entity.id in entity_map:
                mapped_entity, entity_description_freqs = entity_map[entity.id]

                if entity.description in entity_description_freqs:
                    entity_description_freqs[entity.description] += 1
                else:
                    entity_description_freqs[entity.description] = 1

                # Sort by frequency of description, break ties by longest length
                mapped_entity.description = sorted([d for d in entity_description_freqs.keys()], key = lambda d: (entity_description_freqs.get(d), len(d)))[-1]

                if mapped_entity.nif is None and entity.nif:
                    mapped_entity.nif = entity.nif

                entity = mapped_entity

            else:
                entity_map[entity.id] = [entity, {entity.description: 1}]
        
        out.append(entity)

    return out

def parse_euro(s: str) -> Optional[float]:
    if not s:
        return None 

    return float(
        s.replace(".", "").replace(",", ".").replace("€", "").strip()
    )

def date_to_iso8601(d: str) -> Optional[str]:
    if not d:
        return None 

    return "-".join(reversed(d.strip().split("-"))) # 01-02-2021 -> 2021-02-01

def parse_ids_from_contract_pages(input_file_path: str, output_file_path: str):
    contract_ids = [] 

    with open(input_file_path, "r") as f:
        for page in f.readlines():
            try:
                page_json = json.loads(page)
            except Exception as e:
                print(e, page)
                return
            
            for contract in page_json["items"]:
                contract_ids.append(int(contract["id"]))

    with open(output_file_path, "wb") as f:
        pickle.dump(contract_ids, f)

def parse_contracts(input_file_path: str, output_file_path: str):
    contract_map = {}
    entity_map = {}

    with open(input_file_path, "rb") as f:
        for contract in f.readlines():
            try:
               contract_json = json.loads(contract)
            except Exception as e:
                print(e, contract)
                return
            
            cpvs = [cpv.strip() for cpv in contract_json["cpvs"].split("|")]
            cpvsType = [cpvT.strip() for cpvT in contract_json["cpvsType"].split("|")]
            
            c = Contract(
                    id = int(contract_json["id"]),
                    objectBriefDescription = contract_json["objectBriefDescription"].strip(),
                    frameworkAgreementProcedureDescription = contract_json["frameworkAgreementProcedureDescription"].strip(),
                    initialContractualPrice = parse_euro(contract_json["initialContractualPrice"]),
                    totalEffectivePrice = parse_euro(contract_json["totalEffectivePrice"]),
                    signingDate = date_to_iso8601(contract_json["signingDate"]),
                    publicationDate = date_to_iso8601(contract_json["publicationDate"]),
                    closeDate = date_to_iso8601(contract_json["closeDate"]),
                    invitees = parse_entities(contract_json["invitees"], entity_map),
                    contestants = parse_entities(contract_json["contestants"], entity_map),
                    contracting = parse_entities(contract_json["contracting"], entity_map),
                    contracted = parse_entities(contract_json["contracted"], entity_map),
                    groupMembers = parse_entities(contract_json["groupMembers"], entity_map),
                    announcementId = aid if (aid := int(contract_json["announcementId"])) != -1 else None,
                    frameworkAgreementProcedureId = int(faid) if (faid := contract_json["frameworkAgreementProcedureId"]).isnumeric() else None,
                    cpvs = [(cpv, cpvT == "Principal") for cpv, cpvT in zip(cpvs, cpvsType)]
                )

            for field in fields(c):
                if field.type == str and contract_json[field.name] is not None:                                     # Some strings might be null
                    setattr(c, field.name, contract_json[field.name].strip())
                elif field.type == bool and contract_json[field.name] is not None:                                  # Some bools might be null
                    setattr(c, field.name, contract_json[field.name])

            contract_map[c.id] = c

    with open(output_file_path, "wb") as f:
        pickle.dump(contract_map, f)


def parse_contract_map(input_file_path, database_path):
    with open(input_file_path, "rb") as f:
        contract_map = pickle.load(f)
    
    conversion_sqlite_types = {int: "INT", Optional[int]: "INT", str: "TEXT", Optional[str]: "TEXT", float: "REAL", Optional[float]: "REAL", bool: "INT"}
    excluded_fields = {"contracting", "contracted", "contestants", "invitees", "groupMembers", "cpvs"} 

    create_contract_table_statement = "CREATE TABLE contracts ({},\nPRIMARY KEY (id))".format(
        ",\n".join([field.name + " " + conversion_sqlite_types[field.type] for field in fields(Contract) if field.name not in excluded_fields])
    ) 

    con = sqlite3.connect(database_path)
    cur = con.cursor()

    cur.execute(create_contract_table_statement)

    cur.execute(
        """
        CREATE TABLE entities ( 
            description TEXT, id INT, nif INT,
            PRIMARY KEY (description, nif, id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE contracting_entities (
            contract_id INT, contracting_description TEXT,
            PRIMARY KEY (contract_id, contracting_description),
            FOREIGN KEY (contract_id) REFERENCES contracts(id),
            FOREIGN KEY (contracting_description) REFERENCES entities(description)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE contracted_entities (
            contract_id INT, contracted_description TEXT,
            PRIMARY KEY (contract_id, contracted_description),
            FOREIGN KEY (contract_id) REFERENCES contracts(id),
            FOREIGN KEY (contracted_description) REFERENCES entities(description)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE invited_entities (
            contract_id INT, invited_description TEXT,
            PRIMARY KEY (contract_id, invited_description),
            FOREIGN KEY (contract_id) REFERENCES contracts(id),
            FOREIGN KEY (invited_description) REFERENCES entities(description)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE contesting_entities (
            contract_id INT, contesting_description TEXT,
            PRIMARY KEY (contract_id, contesting_description),
            FOREIGN KEY (contract_id) REFERENCES contracts(id),
            FOREIGN KEY (contesting_description) REFERENCES entities(description)
        )
        """
    )


    cur.execute(
        """
        CREATE TABLE grouped_entities (
            contract_id INT, grouped_description TEXT,
            PRIMARY KEY (contract_id, grouped_description),
            FOREIGN KEY (contract_id) REFERENCES contracts(id),
            FOREIGN KEY (grouped_description) REFERENCES entities(description)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE cpvs (
            contract_id INT, cpv TEXT, cpvPrincipal INT,
            PRIMARY KEY (contract_id, cpv, cpvPrincipal),
            FOREIGN KEY (contract_id) REFERENCES contracts(id)
        )
        """
    )

    for contract_id, contract in contract_map.items():
        data = [getattr(contract, field.name) if field.type != bool else int(getattr(contract, field.name)) for field in fields(Contract) if field.name not in excluded_fields]
        cur.execute("INSERT INTO contracts VALUES ({})".format(", ".join(
                                                                        ["?"] * (len(fields(Contract)) - len(excluded_fields))
                                                                    )
                                                               ),
                    tuple(data)
        )
        
        try:
            for entity in contract.contracting:
                data = (entity.description, entity.id, entity.nif)
                cur.execute("INSERT OR IGNORE INTO entities VALUES (?, ?, ?)", data)
            
                data = (contract_id, entity.description)
                cur.execute("INSERT OR IGNORE INTO contracting_entities VALUES (?, ?)", data)

            for entity in contract.contracted:
                data = (entity.description, entity.id, entity.nif)
                cur.execute("INSERT OR IGNORE INTO entities VALUES (?, ?, ?)", data)
            
                data = (contract_id, entity.description)
                cur.execute("INSERT OR IGNORE INTO contracted_entities VALUES (?, ?)", data)

            for entity in contract.invitees:
                data = (entity.description, entity.id, entity.nif)
                cur.execute("INSERT OR IGNORE INTO entities VALUES (?, ?, ?)", data)
            
                data = (contract_id, entity.description)
                cur.execute("INSERT OR IGNORE INTO invited_entities VALUES (?, ?)", data)

            for entity in contract.contestants:
                data = (entity.description, entity.id, entity.nif)
                cur.execute("INSERT OR IGNORE INTO entities VALUES (?, ?, ?)", data)
            
                data = (contract_id, entity.description)
                cur.execute("INSERT OR IGNORE INTO contesting_entities VALUES (?, ?)", data)

            for entity in contract.groupMembers:
                data = (entity.description, entity.id, entity.nif)
                cur.execute("INSERT OR IGNORE INTO entities VALUES (?, ?, ?)", data)
            
                data = (contract_id, entity.description)
                cur.execute("INSERT OR IGNORE INTO grouped_entities VALUES (?, ?)", data)
            
            for cpv, cpvType in contract.cpvs:
                data = (contract_id, cpv, int(cpvType))
                cur.execute("INSERT OR IGNORE INTO cpvs VALUES (?, ?, ?)", data)

        except Exception as e:
            print(e, contract)
            return

    con.commit()
    con.close()
