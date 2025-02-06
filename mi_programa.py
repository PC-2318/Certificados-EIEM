print("¡Hola, Python en VS Code!")
numero = 10
decimal = 3.14
saludo = "Hola Mundo"
es_verdadero = True
bella = "calro"
print(numero)      # Imprime 10
print(decimal)     # Imprime 3.14
print(saludo)      # Imprime Hola Mundo
print(es_verdadero) # Imprime True
print(bella)
a = 5
b = 3

# Suma
suma = a + b
print(suma)  # 8

# Resta
resta = a - b
print(resta)  # 2

# Multiplicación
multiplicacion = a * b
print(multiplicacion)  # 15

# División
division = a / b
print(division)  # 1.6666666666666667

# Potencia
potencia = a ** b
print(potencia)  # 125
edad = 24

# Verificar si la persona es mayor de edad
if edad >= 18:
    print("Eres mayor de edad.")
else:
    print("Eres menor de edad.")
# Imprimir los números del 1 al 5
for i in range(1, 9):
    print(i)
contador = 6
while contador <= 10:
    print(contador)
    contador += 1  # Esto aumenta contador en 1 cada vez
# Crea un programa que te pida al usuario su edad, y luego le diga si es mayor o menor de edad usando condicionales.
if edad >= 21:
    print("Puede entrar")
else:
    print("debe salir")
#Crea un programa que calcule la suma de todos los números del 1 al 100 usando un bucle
suma=0
for i in range(1,101):
       suma += i
print("la suma de los numeros del 1 al 100", suma)
edad = int(input("Ingresa tu edad: "))  

if edad >= 18:  
    print("Eres mayor de edad.")  
else:  
    print("Eres menor de edad.")  
while True:
    entrada = input("Ingresa tu edad: ")
    if entrada.isdigit():  # Verifica si solo contiene números
        edad = int(entrada)
        break  # Sale del bucle si es un número válido
    else:
        print("Por favor, ingresa un número válido.")
#Escribe un programa que le pida al usuario ingresar una temperatura en grados Celsius y 
# le diga si hace frío (≤15°C), calor (≥30°C) o un clima agradable (entre 16°C y 29°C).
temperatura= float(input ("ingresa la tempreratura en grados celcius:"))
if temperatura <= 15:
    print("hace frio")
elif temperatura >=30:
    print("hace calor")
else:
    print("temperatura agradable")  
    # Creación de una lista
frutas = ["manzana", "banana", "naranja", "uva"]

# Acceder a elementos de la lista
print(frutas[0])  # Imprime 'manzana'
print(frutas[1])  # Imprime 'banana'

# Agregar elementos a la lista
frutas.append("mango")
print(frutas)  # Imprime ['manzana', 'banana', 'naranja', 'uva', 'mango']

# Eliminar un elemento de la lista
frutas.remove("banana")
print(frutas)  # Imprime ['manzana', 'naranja', 'uva', 'mango']

# Recorrer una lista
for fruta in frutas:
    print(fruta)
 # Lista de números
numeros = [1, 2, 3, 4, 5]

# Sumar todos los números de la lista
suma = 0
for numero in numeros:
    suma += numero

print("La suma es:", suma)
#Crea una lista que contenga los siguientes números: 5, 12, 8, 21, 18.
#Añade el número 30 al final de la lista.
#Elimina el número 8 de la lista.
#Añade el número 17 al principio de la lista.
#Imprime la longitud (cantidad de elementos) de la lista.
#Imprime la lista final después de todas las modificaciones.
valores = [5,12,8,21,18]
print (valores)
#Añade el número 30 al final de la lista.
valores.append(30)
print (valores)
#Elimina el número 8 de la lista.
valores . remove (8)
print (valores)
#Añade el número 17 al principio de la lista.
valores .insert (0, 17)
print (valores)
#Imprime la longitud (cantidad de elementos) de la lista.
Longitud= len(valores)
print (valores)


