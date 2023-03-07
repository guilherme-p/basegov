CREATE INDEX IF NOT EXISTS contracts_price_index ON contracts(initialContractualPrice);
CREATE INDEX IF NOT EXISTS contracting_description_index ON contracting_entities(contracting_description); 
CREATE INDEX IF NOT EXISTS contracted_description_index ON contracted_entities(contracted_description);
CREATE INDEX IF NOT EXISTS cpvs_index ON cpvs(cpv);

-- Contratos com um custo inicial acima de 100,000, atribuidos por um Municipio/Freguesia/Camara a uma entidade que nunca tinha recebido um contrato publico antes. 
-- (Na verdade, pode ser um dos primeiros contratos dessa entidade em vez de O primeiro, visto que pode ter feito um contrato com uma signingDate anterior mas publicado depois, 
-- mas como muita das vezes contratos nao incluem uma signingDate, ao contrario da publicationDate que é sempre presente, tive de filtrar por publicationDate)

SELECT c.id, c.signingDate, c.publicationDate, c.initialContractualPrice, c.description, c.contractingProcedureType, c.contracting_description, c.contracted_description FROM
(
    contracts
    INNER JOIN
    contracting_entities ON contracts.id = contracting_entities.contract_id 
    INNER JOIN
    contracted_entities ON contracts.id = contracted_entities.contract_id
) AS c
WHERE
(
    c.initialContractualPrice > 100000 
    AND
    (
        c.contracting_description LIKE 'Município%' OR  
        c.contracting_description LIKE 'Freguesia%' OR  
        c.contracting_description LIKE 'Câmara Municipal%'
    )
    AND
    c.id IN (
        SELECT temp.id FROM (contracts INNER JOIN contracted_entities ON contracts.id = contracted_entities.contract_id) AS temp
        WHERE temp.contracted_description = c.contracted_description ORDER BY temp.publicationDate ASC LIMIT 1
    )
);

-- Contratos com um custo inicial acima de 100,000, atribuidos por um Municipio/Freguesia/Camara a uma pessoa individual (sem NIPC) 
-- (Ha alguns falsos positivos porque as vezes contratos nao sao preenchidos/submetidos corretamente, e entao empresas aparecem sem NIPC, mas é facil de distinguir pelo nome)
SELECT c.id, c.signingDate, c.publicationDate, c.initialContractualPrice, c.description, c.contractingProcedureType, c.contracting_description, c.contracted_description FROM
(
    contracts
    INNER JOIN
    contracting_entities ON contracts.id = contracting_entities.contract_id 
    INNER JOIN
    contracted_entities ON contracts.id = contracted_entities.contract_id
    INNER JOIN
    entities ON contracted_entities.contracted_description = entities.description
) AS c
WHERE
(
    c.initialContractualPrice > 100000 
    AND
    (
        c.contracting_description LIKE 'Município%' OR  
        c.contracting_description LIKE 'Freguesia%' OR  
        c.contracting_description LIKE 'Câmara Municipal%'
    )
    AND entities.nif IS NULL AND entities.id IS NOT NULL 
);

-- Entidades a quem foram atribuidos mais de 50% dos contratos de um determinado CPV adjudicados por um Municipio/Freguesia/Camara,
-- com um total minimo de 10 contratos adjudicados com esse CPV por esse Municipio/Freguesia/Camara 
SELECT DISTINCT c.contracting_description, c.contracted_description, c.cpv FROM
(
    contracts
    INNER JOIN
    contracting_entities ON contracts.id = contracting_entities.contract_id 
    INNER JOIN
    contracted_entities ON contracts.id = contracted_entities.contract_id
    INNER JOIN
    cpvs ON contracts.id = cpvs.contract_id
) AS c
WHERE
(
    (
        c.contracting_description LIKE 'Município%' OR  
        c.contracting_description LIKE 'Freguesia%' OR  
        c.contracting_description LIKE 'Câmara Municipal%'
    ) 

    AND
    EXISTS
    (
        SELECT CAST(contracted as FLOAT) / MAX(total, 1) AS ratio FROM
        (
            (
                SELECT COUNT(*) AS contracted FROM
                (
                    SELECT temp.id FROM
                    (     
                        contracts
                        INNER JOIN
                        contracting_entities ON contracts.id = contracting_entities.contract_id 
                        INNER JOIN
                        contracted_entities ON contracts.id = contracted_entities.contract_id
                        INNER JOIN
                        cpvs ON contracts.id = cpvs.contract_id
                    ) AS temp
                    WHERE temp.contracting_description = c.contracting_description AND temp.contracted_description = c.contracted_description AND temp.cpv = c.cpv 
                )  
            )

            FULL OUTER JOIN 
            (
                SELECT COUNT(*) AS total FROM
                (
                    SELECT temp.id FROM
                    (     
                        contracts
                        INNER JOIN
                        contracting_entities ON contracts.id = contracting_entities.contract_id 
                        INNER JOIN
                        contracted_entities ON contracts.id = contracted_entities.contract_id
                        INNER JOIN
                        cpvs ON contracts.id = cpvs.contract_id
                    ) AS temp
                    WHERE temp.contracting_description = c.contracting_description AND temp.cpv = c.cpv 
                )  
            )

            ON 1 = 1
        ) WHERE total >= 10 AND ratio >= 0.50
    )
);

-- Mesmo que o de cima mas com um CPV especifico
SELECT DISTINCT c.contracting_description, c.contracted_description, c.cpv FROM
(
    contracts
    INNER JOIN
    contracting_entities ON contracts.id = contracting_entities.contract_id 
    INNER JOIN
    contracted_entities ON contracts.id = contracted_entities.contract_id
    INNER JOIN
    cpvs ON contracts.id = cpvs.contract_id
) AS c
WHERE
(
    c.cpv = '50000000-5'
    AND
    (
        c.contracting_description LIKE 'Município%' OR  
        c.contracting_description LIKE 'Freguesia%' OR  
        c.contracting_description LIKE 'Câmara Municipal%'
    )
    AND
    EXISTS
    (
        SELECT CAST(contracted as FLOAT) / MAX(total, 1) AS ratio FROM
        (
            (
                SELECT COUNT(*) AS contracted FROM
                (
                    SELECT temp.id FROM
                    (     
                        contracts
                        INNER JOIN
                        contracting_entities ON contracts.id = contracting_entities.contract_id 
                        INNER JOIN
                        contracted_entities ON contracts.id = contracted_entities.contract_id
                        INNER JOIN
                        cpvs ON contracts.id = cpvs.contract_id
                    ) AS temp
                    WHERE temp.contracting_description = c.contracting_description AND temp.contracted_description = c.contracted_description AND temp.cpv = c.cpv 
                )  
            )

            FULL OUTER JOIN 
            (
                SELECT COUNT(*) AS total FROM
                (
                    SELECT temp.id FROM
                    (     
                        contracts
                        INNER JOIN
                        contracting_entities ON contracts.id = contracting_entities.contract_id 
                        INNER JOIN
                        contracted_entities ON contracts.id = contracted_entities.contract_id
                        INNER JOIN
                        cpvs ON contracts.id = cpvs.contract_id
                    ) AS temp
                    WHERE temp.contracting_description = c.contracting_description AND temp.cpv = c.cpv 
                )  
            )

            ON 1 = 1
        ) WHERE total >= 10 AND ratio >= 0.50
    )
);


-- SELECT c.id, c.signingDate, c.publicationDate, c.initialContractualPrice, c.description, c.contractingProcedureType, c.contracting_description, c.contracted_description, c.cpv FROM
-- (
--     contracts
--     INNER JOIN
--     contracting_entities ON contracts.id = contracting_entities.contract_id 
--     INNER JOIN
--     contracted_entities ON contracts.id = contracted_entities.contract_id
--     INNER JOIN
--     cpvs ON contracts.id = cpvs.contract_id
-- ) AS c WHERE c.contracting_description = "Câmara Municipal da Amadora" AND c.cpv = "50700000-2"; 
--
-- select e.nif, e.id, c.contracted_description from entities e inner join contracted_entities c where e.nif = 500280908;
