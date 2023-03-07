CREATE TABLE contracts (
    id INT,
    initialContractualPrice REAL,
    totalEffectivePrice REAL,
    announcementId INT,
    frameworkAgreementProcedureId INT,
    frameworkAgreementProcedureDescription TEXT,
    publicationDate TEXT,
    objectBriefDescription TEXT,
    ccp INT,
    ambientCriteria INT,
    materialCriteria INT,
    cocontratantes INT,
    aquisitionStateMemberUE INT,
    income INT,
    increments INT,
    normal INT,
    contractTypeCS INT,
    centralizedProcedure INT,
    infoAquisitionStateMemberUE TEXT,
    signingDate TEXT,
    closeDate TEXT,
    description TEXT,
    observations TEXT,
    executionDeadline TEXT,
    contractingProcedureType TEXT,
    contractFundamentationType TEXT,
    directAwardFundamentationType TEXT,
    nonWrittenContractJustificationTypes TEXT,
    regime TEXT,
    specialMeasures TEXT,
    executionPlace TEXT,
    causesDeadlineChange TEXT,
    causesPriceChange TEXT,
    endOfContractType TEXT,
    contractStatus TEXT,
    contractTypes TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE entities (
    description TEXT, id INT, nif INT,
    PRIMARY KEY (description, nif, id)
);

CREATE TABLE contracting_entities (
    contract_id INT, contracting_description TEXT,
    PRIMARY KEY (contract_id, contracting_description),
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (contracting_description) REFERENCES entities(description)
);

CREATE TABLE contracted_entities (
    contract_id INT, contracted_description TEXT,
    PRIMARY KEY (contract_id, contracted_description),
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (contracted_description) REFERENCES entities(description)
);

CREATE TABLE invited_entities (
    contract_id INT, invited_description TEXT,
    PRIMARY KEY (contract_id, invited_description),
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (invited_description) REFERENCES entities(description)
);

CREATE TABLE contesting_entities (
    contract_id INT, contesting_description TEXT,
    PRIMARY KEY (contract_id, contesting_description),
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (contesting_description) REFERENCES entities(description)
);

CREATE TABLE grouped_entities (
    contract_id INT, grouped_description TEXT,
    PRIMARY KEY (contract_id, grouped_description),
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (grouped_description) REFERENCES entities(description)
);

CREATE TABLE cpvs (
    contract_id INT, cpv TEXT, cpvPrincipal INT,
    PRIMARY KEY (contract_id, cpv, cpvPrincipal),
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
);

CREATE INDEX contracts_price_index ON contracts(initialContractualPrice);

CREATE INDEX contracting_description_index ON contracting_entities(contracting_description);

CREATE INDEX contracted_description_index ON contracted_entities(contracted_description);

CREATE INDEX cpvs_index ON cpvs(cpv);
