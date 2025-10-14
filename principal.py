
from funcoes import adicionar

def main():
  numeros = []
  for i in range(5):
    entrada = int(input(f"Digite o número: "))
    adicionar(numeros, entrada)

  print(f"Lista final de números: {numeros}")

if __name__ == "__main__":
  main()


