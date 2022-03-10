import csv

csv_header = [
    'UF',
    'cidade',
    'bairro',
    'tipo',
    'area',
    'quartos',
    'banheiros',
    'suites',
    'vagas',
    'aluguel',
    'condominio',
    'iptu'
]


def get_csv_writter(csvfile):
    csvwritter = csv.DictWriter(
        csvfile,
        fieldnames=csv_header,
        extrasaction='ignore',
    )
    return csvwritter
