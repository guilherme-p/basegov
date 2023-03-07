import subprocess
import concurrent.futures
from collections.abc import Callable

# Processos distintos sao criados ao chamar subprocess. I/O tasks nao bloqueiam a Global Interpreter Lock (GIL), por isso podemos escrever em varios ficheiros em simultaneo
# visto que a latencia de um write é varias vezes superior a de um context switch.

# Usei curl em vez de uma biblioteca async para simplificar o paralelismo e porque nao consegui construir o POST request com a raw data de outra forma.

def check_request(request):
    output = subprocess.check_output(request, shell=True, encoding='utf-8')

    while output.split()[0] == "null" or len(output) < 800:
        output = subprocess.check_output(request, shell=True, encoding='utf-8')
    
    return output

def get_contract_page(page: int):
    request = "curl 'https://www.base.gov.pt/Base4/pt/resultados/' \
    -H 'Accept: text/plain, */*; q=0.01' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
    -H 'DNT: 1' \
    -H 'Origin: https://www.base.gov.pt' \
    -H 'Sec-Fetch-Dest: empty' \
    -H 'Sec-Fetch-Mode: cors' \
    -H 'Sec-Fetch-Site: same-origin' \
    -H 'X-Requested-With: XMLHttpRequest' \
    --retry 10 \
    --retry-all-errors \
    --fail \
    --data-raw 'type=search_contratos&version=110.0&query=tipo%3D0%26tipocontrato%3D0%26pais%3D0%26distrito%3D0%26concelho%3D0&sort=-publicationDate&page={}&size=25' \
    --compressed 2> /dev/null".format(page)

    output = check_request(request)
    
    with open("contract_pages/contract_{}_page.json".format(page), "w", encoding='utf-8') as f:
        f.write(output)

def get_contract_info(contract_id: int):
    request = "curl -s 'https://www.base.gov.pt/Base4/pt/resultados/' \
    -H 'Accept: text/plain, */*; q=0.01' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
    -H 'DNT: 1' \
    -H 'Origin: https://www.base.gov.pt' \
    -H 'Sec-Fetch-Dest: empty' \
    -H 'Sec-Fetch-Mode: cors' \
    -H 'Sec-Fetch-Site: same-origin' \
    --retry 10 \
    --retry-all-errors \
    --fail \
    --data-raw 'type=detail_contratos&version=79.0&id={}' \
    --compressed 2> /dev/null".format(contract_id)

    output = check_request(request)
    
    with open("contracts/contract_{}.json".format(contract_id), "w", encoding='utf-8') as f:
        f.write(output)

def get_entity_page(page: int):
    request = "curl 'https://www.base.gov.pt/Base4/pt/resultados/' \
    -H 'Accept: text/plain, */*; q=0.01' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
    -H 'DNT: 1' \
    -H 'Origin: https://www.base.gov.pt' \
    -H 'Referer: https://www.base.gov.pt/Base4/pt/pesquisa/?type=entidades&texto=' \
    -H 'Sec-Fetch-Dest: empty' \
    -H 'Sec-Fetch-Mode: cors' \
    -H 'Sec-Fetch-Site: same-origin' \
    -H 'X-Requested-With: XMLHttpRequest' \
    --retry 10 \
    --retry-all-errors \
    --fail \
    --data-raw 'type=search_entidades&version=110.0&query=&sort=%2Bdescription&page={}&size=25' \
    --compressed 2> /dev/null".format(page)

    output = check_request(request)

    with open("entity_pages/entity_{}_page.json".format(page), "w", encoding='utf-8') as f:
        f.write(output)


def multi_thread(func: Callable, args: list[int], max_threads: int = 250):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_arg = {executor.submit(func, arg): arg for arg in args}

        for future in concurrent.futures.as_completed(future_to_arg):
            arg = future_to_arg[future]

            try:
                future.result()
            except Exception as e:
                print("{} generated an exception: {}".format(arg, e))
            else:
                print("{} is done".format(arg))
