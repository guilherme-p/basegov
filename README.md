# Basegov
O objetivo deste repo é disponibilizar a informação do [portal BASE](https://www.base.gov.pt/Base4/pt/pesquisa/) em formato Python e SQL (sqlite3), para fazer queries mais complexas.
Alguns exemplos interessantes estão documentados em [queries.sql](queries.sql), mas tenho a certeza que alguem terá ideias melhores.

Abaixo estão instrucoes sobre como fazer scrape e compilar esta informacao, mas para simplificar o processo dei upload no dataset que já fiz scrape.
Contém 1,692,197 contratos e vai de 2008-08-05 até 2023-03-13 (acho que faltam cerca de 400 onde o servidor deu timeout consistentemente).

[contracts_info.json](https://drive.google.com/file/d/1K1YGfKQcFJV3huQ52hzYm6DO8--pDkpn/view?usp=sharing) (478M compressed, 3.2G uncompressed)

[contracts_info.pickle](https://drive.google.com/file/d/1b7NGzzzzikb9J47OgtQh1ineLboQsXcD/view?usp=sharing) (162M compressed, 573M uncompressed)

[basegov.db](https://drive.google.com/file/d/1G0jT50wulmi46OZLFW3mX0jEa-9Qpuuo/view?usp=sharing) (515M compressed, 1.3G uncompressed, inclui indices)

<details>
<summary>Exemplo do formato de contracts_info.json</summary>

` head -n 2 contracts_info.json `

`{"contractFundamentationType":"Artigo 19.º, alínea c) do Código dos Contratos Públicos","increments":false,"invitees":[],"closeDate":"03-12-2019","causesDeadlineChange":"CONDIÇÕES METEOROLOGICAS","causesPriceChange":"NÃO APLICÁVEL","frameworkAgreementProcedureId":"Não aplicável.","frameworkAgreementProcedureDescription":"Não aplicável.","announcementId":-1,"contractingProcedureUrl":null,"documents":[],"observations":"NÃO APLICÁVEL","totalEffectivePrice":"519.999,00 €","ambientCriteria":false,"directAwardFundamentationType":"Não aplicável","publicationDate":"03-04-2019","endOfContractType":"Cumprimento integral do contrato","ccp":false,"contestants":[{"nif":"508018030","id":152494,"description":"2007COM, LDA"},{"nif":"510874169","id":528496,"description":"Gonksys, S.A"}],"cocontratantes":false,"aquisitionStateMemberUE":false,"infoAquisitionStateMemberUE":null,"groupMembers":null,"cpvsDesignation":"Obras de construção total ou parcial e de engenharia civil","cpvsValue":"51999.0 € ","contracted":[{"nif":"508018030","id":152494,"description":"2007 COM, Lda"}],"contracting":[{"nif":"508331471","id":79250,"description":"Centro Hospitalar do Porto, E.P.E. (CHP)"}],"contractingProcedureType":"Consulta Prévia","objectBriefDescription":"CRIAÇÃO DE CAMINHOS DE CABOS PARA INTERLIGAÇÃO DE DATACENTERS","cpvs":"45200000-9","executionDeadline":"30 dias","contractTypes":"Empreitadas de obras públicas","contractTypeCS":false,"income":false,"centralizedProcedure":false,"executionPlace":"Portugal, Porto, Porto<BR/>Portugal","nonWrittenContractJustificationTypes":"Artigo 95.º, n.º 1, c), locação ou aquisição de bens móveis ou de serviços nos termos das alíneas i),ii),iii),cumulativamente","initialContractualPrice":"51.999,00 €","contractStatus":null,"materialCriteria":false,"normal":true,"specialMeasures":null,"regime":"Código dos Contratos Públicos ( DL 111-B/2017 )","cpvsType":"Principal","signingDate":"13-02-2019","id":5458627,"description":"PV/125/2018"} `

`{"contractFundamentationType":"Artigo 20.º, n.º 1, alínea d) do Código dos Contratos Públicos","increments":false,"invitees":[],"closeDate":"01-02-2021","causesDeadlineChange":"Devido aos constrangimentos ocorridos pela situação pandémica foi necessário prorrogar a data de términus do contrato por mais dois meses.","causesPriceChange":"Ao valor inicial acresce 1100,00€ referente aos dois meses de aditamento do prazo  inicial.","frameworkAgreementProcedureId":"Não aplicável.","frameworkAgreementProcedureDescription":"Não aplicável.","announcementId":-1,"contractingProcedureUrl":null,"documents":[{"id":1430858,"description":"ICA - 2018 - RGPD..pdf"}],"observations":"Na","totalEffectivePrice":"11.550,00 €","ambientCriteria":false,"directAwardFundamentationType":"ausência de recursos próprios","publicationDate":"23-01-2019","endOfContractType":"Cumprimento integral do contrato","ccp":false,"contestants":[],"cocontratantes":false,"aquisitionStateMemberUE":false,"infoAquisitionStateMemberUE":null,"groupMembers":null,"cpvsDesignation":"Fornos, fornalhas e incineradores industriais ou de laboratório","cpvsValue":"11550.0 € ","contracted":[{"nif":"508625688","id":2690065,"description":"ICA - Incluir Cooperativa Artesanal CRL"}],"contracting":[{"nif":"504650939","id":19484,"description":"Centro Social de Santa Maria de Sardoura"}],"contractingProcedureType":"Ajuste Direto Regime Geral","objectBriefDescription":"Arrendamento de espaço e aluguer de equipamento de olaria (rodas de pé e forno) para desenvolvimento do curso “Oleiro/a” desenvolver ao abrigo da tipologia 3.01 - Formação de Pessoas com deficiência e/ou Incapacidade, da tutela do POISE.","cpvs":"42300000-9","executionDeadline":"550 dias","contractTypes":"Locação de bens móveis","contractTypeCS":false,"income":false,"centralizedProcedure":false,"executionPlace":"Portugal, Aveiro, Castelo de Paiva","nonWrittenContractJustificationTypes":"","initialContractualPrice":"11.550,00 €","contractStatus":null,"materialCriteria":false,"normal":true,"specialMeasures":null,"regime":"Código dos Contratos Públicos ( DL 111-B/2017 )","cpvsType":"Principal","signingDate":"28-09-2018","id":5175906,"description":"Arrendamento de espaço e aluguer de equipamento de olaria (rodas de pé e forno) para desenvolvimento do curso “Oleiro/a” desenvolver ao abrigo da tipologia 3.01 - Formação de Pessoas com deficiência e/ou Incapacidade, da tutela do POISE."} `

</details>

<details>
<summary>Exemplo do formato de contracts_info.pickle</summary>

```
from parse import *

with open("contracts_info.pickle", "rb") as f:
    ci = pickle.load(f)

print(len(ci), list(ci.items())[:2])
```

`1692197`

`[(5458627, Contract(id=5458627, initialContractualPrice=51999.0, totalEffectivePrice=519999.0, invitees=[], contestants=[Entity(description='2007com, Lda', id=152494, nif=508018030), Entity(description='GONKSYS, S.A.', id=528496, nif=510874169)], contracting=[Entity(description='Centro Hospitalar Universitário do Porto, E. P. E.', id=79250, nif=508331471)], contracted=[Entity(description='2007com, Lda', id=152494, nif=508018030)], groupMembers=[], announcementId=None, frameworkAgreementProcedureId=None, frameworkAgreementProcedureDescription='Não aplicável.', publicationDate='2019-04-03', objectBriefDescription='CRIAÇÃO DE CAMINHOS DE CABOS PARA INTERLIGAÇÃO DE DATACENTERS', cpvs=[('45200000-9', True)], ccp=False, ambientCriteria=False, materialCriteria=False, cocontratantes=False, aquisitionStateMemberUE=False, income=False, increments=False, normal=True, contractTypeCS=False, centralizedProcedure=False, infoAquisitionStateMemberUE=None, signingDate='2019-02-13', closeDate='2019-12-03', description=None, observations=None, executionDeadline=None, contractingProcedureType=None, contractFundamentationType=None, directAwardFundamentationType=None, nonWrittenContractJustificationTypes=None, regime=None, specialMeasures=None, executionPlace=None, causesDeadlineChange=None, causesPriceChange=None, endOfContractType=None, contractStatus=None, contractTypes=None)),`

`(5175906, Contract(id=5175906, initialContractualPrice=11550.0, totalEffectivePrice=11550.0, invitees=[], contestants=[], contracting=[Entity(description='Centro Social de Santa Maria de Sardoura', id=19484, nif=504650939)], contracted=[Entity(description='ICA - Incluir Cooperativa Artesanal CRL', id=2690065, nif=508625688)], groupMembers=[], announcementId=None, frameworkAgreementProcedureId=None, frameworkAgreementProcedureDescription='Não aplicável.', publicationDate='2019-01-23', objectBriefDescription='Arrendamento de espaço e aluguer de equipamento de olaria (rodas de pé e forno) para desenvolvimento do curso “Oleiro/a” desenvolver ao abrigo da tipologia 3.01 - Formação de Pessoas com deficiência e/ou Incapacidade, da tutela do POISE.', cpvs=[('42300000-9', True)], ccp=False, ambientCriteria=False, materialCriteria=False, cocontratantes=False, aquisitionStateMemberUE=False, income=False, increments=False, normal=True, contractTypeCS=False, centralizedProcedure=False, infoAquisitionStateMemberUE=None, signingDate='2018-09-28', closeDate='2021-02-01', description=None, observations=None, executionDeadline=None, contractingProcedureType=None, contractFundamentationType=None, directAwardFundamentationType=None, nonWrittenContractJustificationTypes=None, regime=None, specialMeasures=None, executionPlace=None, causesDeadlineChange=None, causesPriceChange=None, endOfContractType=None, contractStatus=None, contractTypes=None))] `

</details>

## Exemplo de como fazer scrape
```
from parse import *
from scrape import *

page_range = list(range(70000)) # Scrape paginas [0, 70000), formato no url é 0-indexed mas no portal é 1-indexed, ultimo elemento da range é exclusivo
multi_thread(get_contract_page, page_range)

# Concatenar todas as paginas num ficheiro
$ cat contract_pages/*.json > contract_pages.json

# Provavelmente precisam de usar o find com a opcao exec porque a shell nao vai conseguir fazer wildcard expansion a todos os argumentos
$ find contract_pages/ -type f -exec cat {} + > contract_pages.json 

# Extrair os ids para fazer scrape individualmente
parse_ids_from_contract_pages("contract_pages.json", "ids.pickle")

with open("ids.pickle", "rb") as f:
    ids = pickle.load(f)

# Isto demorou-me ~50 horas com 500 workers
# Podem ter que aumentar o limite de open file descriptors com $ ulimit -S -n 2048
multi_thread(get_contract_info, ids, max_workers = 500)

# Concatenar todos os contratos num ficheiro
$ cat contracts/contract_*.json > contracts_info.json

# Provavelmente precisam de usar o find com a opcao exec porque a shell nao vai conseguir fazer wildcard expansion a todos os argumentos
$ find contracts/ -type f -exec cat {} + > contracts_info.json

parse_contracts("contracts_info.json", "contracts_info.pickle")
parse_contract_map("contracts_info.pickle", "basegov.db")
```
## Requirements
- Python >= 3.9
- sqlite3

## Keywords

<details>
<summary>Keywords para motores de pesquisa</summary>

base.gov.pt sql dataset python 

contratos publicos online 

contratos publicos sql 

contratos publicos python 

contratos publicos dataset 

base de dados portal base

base de dados contratos publicos 

portal base dataset

portal base sql

portal base python

base gov pt

dados gov pt

transparencia
</details>
