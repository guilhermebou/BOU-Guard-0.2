import nltk
import json
import string
import requests
from bs4 import BeautifulSoup

url = 'https://api.openai.com/v1/chat/completions'
model = 'gpt-3.5-turbo'

# API-KEY GPT
token = 'API KEY GPT'

stopwords = nltk.corpus.stopwords.words("portuguese")
ponctuation = string.punctuation

# URL do site para realizar a analise
link = "URL"

# Acessa a URL fornecida e extrai o texto do site correspondente.
# Retorna o texto extraído.
def soup_func(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.text, "html.parser")
    input = soup.get_text(strip=True)
    return input

soup = soup_func(link)

# Realiza pré-processamento com NLTK: tokenização, converte todo o conteúdo para caixa baixa, remoção de stopwords e pontuações,
# Retorna um vetor de tokens resultante.
def preprocess(soup):
    tokens = []
    for token in nltk.word_tokenize(soup):
        token = token.lower()
        if token not in stopwords and token not in ponctuation:
            tokens.append(token)
    return tokens

tokens = preprocess(soup)

# Acesso ao dicionário LIWC.
def liwc_func():
    liwc = json.load(open('BOU-Guard/liwc_pt.json'))
    return liwc

liwc = liwc_func()

# Realiza análise de sentimento em uma lista de tokens com base no dicionário LIWC,
# calculando a porcentagem de palavras associadas a "emoção negativa", "sexual" e "racista",
# e retorna a soma dessas porcentagens.
def sentiment_analysis(soup, liwc):
    tokens = preprocess(soup)

    negemo = 0
    sexual = 0
    racism = 0

    for token in tokens:
        if token in liwc:
            if "negemo" in liwc [token]:
                negemo +=1
            if "sexual" in liwc [token]:
                sexual +=1
            if "racism" in liwc [token]:
                racism +=1

    negemo = round(negemo / len(tokens),2)
    sexual = round(sexual / len(tokens),2)
    racism = round(racism / len(tokens),2)

    print ("NEG:",negemo, " SEX:", sexual, " RACIS:", racism)
    result = negemo+sexual+racism
    print(result)
    return result

analyst = sentiment_analysis(soup, liwc)

# Divide o texto da raspagem para atender ao limite de 4096 tokens nas solicitações ao GPT.
def div_string(input):
    sizeall = len(input)
    sizepart = sizeall // 2
    parts = [input[i:i + sizepart] for i in range(0, sizeall, sizepart)]
    return parts

parts = div_string(soup)

# Analisa o texto da raspagem com base nos prompts e retorna uma lista de expressões,
# relacionadas a homofobia, racismo e machismo encontradas no site.
def gpt(soup):

    prompt = [

        {'role': 'user', 'content': 'Identifique e enumere apenas expressões presentes nos dados associadas a homofobia, racismo e machismo.'},
        {'role': 'user', 'content': 'caso encontre palavras ou frases relacionadas a solicitação acima, me retorne em uma lista padrão. exemplo: "[1] ..... \n [2] ..... [...]"'},
        {'role': 'user', 'content': 'Se as expressões desejadas não existirem, não crie ou mencione exemplos de conteúdos que não estejam contidos nos dados. Apenas gere uma saída contendo a listagem, sem incluir explicações adicionais.'},
        {'role': 'user', 'content': soup},
    ]

    response = requests.post(
        url,
        headers={'Authorization': f'Bearer {token}'},
        json={
            'model': model,
            'messages': prompt
        }
    )

    data = response.json()
    all_responses = []
    for choice in data['choices']:
        reply = choice['message']['content']
        all_responses.append(reply)
    return all_responses

# Aciona a função GPT se a análise de sentimentos for superior a 5%.
if analyst > 0.05:
    all_output = []
    for part in parts:
         output = gpt(part)
         all_output.extend(output)

# Salva as frases e palavras identificadas pelo GPT em um arquivo de texto.
    with open("BOU-Guard/OutPuts/TEMAS/OUTPUT.txt", "w", encoding="utf-8") as file_txt:
        for response in all_output:
            file_txt.write(json.dumps(response, ensure_ascii=False) + "\n")
