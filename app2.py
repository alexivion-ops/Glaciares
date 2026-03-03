import csv


def generar_lista_difusion():
    mails = []

    # Abrimos el CSV que generaste antes
    with open('mails_diputados.csv', mode='r', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        next(lector)  # Saltamos el encabezado ("Email Institucional")

        for fila in lector:
            if fila:  # Verificamos que la fila no esté vacía
                mails.append(fila[0])

    # Unimos todos los correos con una coma y un espacio
    lista_comas = ", ".join(mails)

    # Lo guardamos en un archivo .txt para que sea fácil de copiar
    with open('lista_difusion.txt', mode='w', encoding='utf-8') as txt:
        txt.write(lista_comas)

    print("¡Lista generada con éxito!")
    print(f"Total procesados: {len(mails)} correos.")
    print("Revisá el archivo 'lista_difusion.txt', abrite el bloc de notas, copiá todo y pegalo en tu correo.")


if __name__ == "__main__":
    generar_lista_difusion()