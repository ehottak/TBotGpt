import os
import openai
import telebot
from keep_alive import keep_alive
import json
import datetime

api_token = os.environ['api_token']
bot_api = os.environ['token_bot']
openai.api_key = api_token

bot = telebot.TeleBot(bot_api)
keep_alive()

def questions_users(message):
  with open("questions_users.txt", "r") as file:
    # Lendo o objeto JSON do arquivo
    data = []
    data = json.load(file)

  # Adicionando a pessoa ao objeto JSON
  data.append({"nome": message.from_user.first_name, "id": message.from_user.id , "msg": message.text})
      

  # Abrindo o arquivo em modo de escrita
  with open("questions_users.txt", "w") as file:
    # Escrevendo o objeto JSON no arquivo
    json.dump(data, file)


def access_atempt(message):
    # Abrindo o arquivo em modo leitura
    with open("access_attempt.txt", "r") as file:
        # Lendo o objeto JSON do arquivo
        data = []
        data = json.load(file)

    # ID da pessoa que queremos adicionar
    id_to_add = message.from_user.id

    # Verificando se já existe uma pessoa com o mesmo ID no objeto JSON
    if any(access["id"] == id_to_add for access in data):
        return


  # Adicionando a pessoa ao objeto JSON
    current_date = datetime.datetime.now()
    data.append({"nome": message.from_user.first_name, "id": id_to_add , "data": str(current_date)})

  # Abrindo o arquivo em modo de escrita
    with open("access_attempt.txt", "w") as file:
    # Escrevendo o objeto JSON no arquivo
     json.dump(data, file)


def validate_number(message):
  with open("permitted_numbers.txt", "r") as file:
    #variavel valida admin
    permitted_numbers_string = file.read()
    # Verificando se a string tem um comprimento maior que zero
  if len(permitted_numbers_string) > 0:
    # Removendo a vírgula do final da string
    permitted_numbers_string = permitted_numbers_string.strip(",")

    # Dividindo a string em uma lista de strings
    permitted_numbers = permitted_numbers_string.split(",")

    # Convertendo cada string da lista em um inteiro
    permitted = [int(id) for id in permitted_numbers]
  if message.from_user.id in permitted:
    return True
  else:
    access_atempt(message)
    bot.send_message(
      message.chat.id,
      "Desculpe, você não tem permissão para utilizar este bot. favor enviar uma mensagem para Eduardo Hotta. Bot em 21/12/2022 as 02:58"
    )
  return False


@bot.message_handler(commands=['adicionar'])
def add_permitted_number(message):
  with open("admin.txt", "r") as file:
    #variavel valida admin
    admin = file.read().split(",")
    admin_id = [int(id) for id in admin]
  if message.from_user.id not in admin_id:
    return
  # Extrair o número a ser adicionado da mensagem
  words = message.text.strip()
  if len(words) >= 2:
    # Acessar a segunda palavra da lista (que deveria ser o número a ser adicionado)
    number_to_add = words[11:]
  # Verificar se o número é um número válido
  if number_to_add.isdigit():
    # Adicionar o número à lista de números permitidos
    with open("permitted_numbers.txt", "a") as file:
      file.write(f"{number_to_add},")
    # Enviar mensagem de sucesso para o usuário
    bot.send_message(chat_id=message.chat.id,
                     text="Adicionado com sucesso ID:" + number_to_add)
  else:
    # Enviar mensagem de erro para o usuário
    bot.send_message(
      chat_id=message.chat.id,
      text=
      "O valor digitado não é um número. Por favor, digite apenas números para adicionar à lista de números permitidos."
    )


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.send_message(
    chat_id=message.chat.id,
    text=
    "Olá, eu sou um bot de inteligência artificial. Envie uma mensagem com o sinal de asterisco (*) no início para fazer uma pergunta, seu ID é:"
    + str(message.from_user.id))


@bot.message_handler(func=validate_number)
def respond_to_questions(message):
  if message.text.startswith('*'):
    questions_users(message)
    response = openai.Completion.create(engine="text-davinci-003",
                                        prompt=message.text[1:],
                                        max_tokens=2000,
                                        temperature=0.5,
                                        top_p=1,
                                        frequency_penalty=0,
                                        presence_penalty=0,
                                        n=1)
    response_text = response["choices"][0].text
    bot.send_message(chat_id=message.chat.id, text=response_text)
    print(message.from_user)


bot.infinity_polling()
