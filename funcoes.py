import os

def cadastrarVeiculo(veiculos):
    exibirSubtitulo('Cadastro de novos veículos')
    nomeVeiculo = input('Digite o nome do veículo a ser cadastrado: ')
    categoria = input(f'Digite a categoria do veículo {nomeVeiculo}: ')
    dadosVeiculo = {'nome':nomeVeiculo, 'categoria':categoria, 'ativo':False}
    veiculos.append(dadosVeiculo)
    print(f'O veículo {nomeVeiculo} foi cadastrado com sucesso!')
    voltarMenuPrincipal()


def listarVeiculo(veiculos):
    exibirSubtitulo('Listagem de veículos')
    print(f'{'Nome do veículo'.ljust(22)} | {'Categoria'.ljust(20)} | Status')
    for veiculo in veiculos:
        nomeVeiculo = veiculo['nome']
        categoria = veiculo['categoria']
        ativo = 'ativado' if veiculo['ativo'] else 'desativado'
        print(f'- {nomeVeiculo.ljust(20)} | {categoria.ljust(20)} | {ativo}')
    voltarMenuPrincipal()


def alterarVeiculo(veiculos):
    exibirSubtitulo('Alterar estado do veículo')
    nomeVeiculo = input('Digite o nome do veículo que deseja alterar o status: ')
    veiculoEncontrado = False
    for veiculo in veiculos:
        if nomeVeiculo == veiculo['nome']:
            veiculoEncontrado = True
            veiculo['ativo'] = not veiculo['ativo']
            mensagem = f'O veiculo {nomeVeiculo} foi ativado com sucesso' if veiculo['ativo'] else f'O veiculo {nomeVeiculo} foi desativado com sucesso'
            print(mensagem)
    if not veiculoEncontrado:
        print('O veiculo não foi encontrado')
    voltarMenuPrincipal()


def exibirSubtitulo(texto):
    os.system('cls')
    linha = '*' * (len(texto))
    print(linha)
    print(texto)
    print(linha)
    print()


def voltarMenuPrincipal():
    input('\nDigite uma tecla para voltar ao menu ')
    from main import main
    main()


def opcaoInvalida(veiculos):
    print('Opção inválida!\n')
    voltarMenuPrincipal()