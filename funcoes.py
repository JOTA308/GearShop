def exibirSubtitulo(texto):
    print(f"\n--- {texto} ---\n")


def cadastrarVeiculo(veiculos):
    exibirSubtitulo('Cadastro de novos veículos')
    nomeVeiculo = input('Digite o nome do veículo a ser cadastrado: ')
    categoria = input(f'Digite a categoria do veículo {nomeVeiculo}: ')
    dadosVeiculo = {'nome': nomeVeiculo, 'categoria': categoria, 'ativo': False}
    veiculos.append(dadosVeiculo)
    print(f"Veículo {nomeVeiculo} cadastrado com sucesso!")


def listarVeiculo(veiculos):
    exibirSubtitulo('Lista de veículos cadastrados')
    if not veiculos:
        print("Nenhum veículo cadastrado.")
        return
    for i, veiculo in enumerate(veiculos, start=1):
        status = "Ativo" if veiculo['ativo'] else "Inativo"
        print(f"{i}. Nome: {veiculo['nome']}, Categoria: {veiculo['categoria']}, Status: {status}")


def alterarVeiculo(veiculos):
    exibirSubtitulo('Alterar veículo')
    if not veiculos:
        print("Nenhum veículo para alterar.")
        return
    listarVeiculo(veiculos)
    try:
        escolha = int(input("Escolha o número do veículo que deseja alterar: "))
        if escolha < 1 or escolha > len(veiculos):
            print("Número inválido.")
            return
        veiculo = veiculos[escolha - 1]
        novoNome = input(f"Digite o novo nome (ou Enter para manter '{veiculo['nome']}'): ")
        novaCategoria = input(f"Digite a nova categoria (ou Enter para manter '{veiculo['categoria']}'): ")
        novoStatus = input(f"Ativar veículo? (s/n, atual: {'Ativo' if veiculo['ativo'] else 'Inativo'}): ").lower()

        if novoNome:
            veiculo['nome'] = novoNome
        if novaCategoria:
            veiculo['categoria'] = novaCategoria
        if novoStatus == 's':
            veiculo['ativo'] = True
        elif novoStatus == 'n':
            veiculo['ativo'] = False

        print("Veículo alterado com sucesso!")
    except ValueError:
        print("Entrada inválida. Digite um número.")


def opcaoInvalida(_):
    print("Opção inválida! Tente novamente.")