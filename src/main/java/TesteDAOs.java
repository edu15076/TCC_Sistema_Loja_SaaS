
import DAO.ContratanteDAO;
import DAO.DAOException;
import DAO.GerenteDeContratoDAO;
import DAO.LojaDAO;
import Entidade.Contratante;
import Entidade.GerenteDeContrato;
import Entidade.Loja;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Scanner;

public class TesteDAOs {
    private static Scanner in;
    private static ContratanteDAO dao;
    private static final String ERRO_INTERNO;

    static {
        ERRO_INTERNO = "Houve um erro interno.";
        in = new Scanner(System.in);
        try {
            dao = new ContratanteDAO();
        } catch (DAOException e) {
            throw new RuntimeException(ERRO_INTERNO, e);
        }
    }

    private static void criarContratante() {
        Contratante novoContratante = new Contratante();

        System.out.println("Digite o Nome de usuário:");
        novoContratante.setUsername(in.nextLine());

        System.out.println("Digite a senha:");
        novoContratante.setSenha(in.nextLine());

        System.out.println("Digite o CNPJ:");
        novoContratante.setCnpj(in.nextLine());

        System.out.println("Digite o nome:");
        novoContratante.setNome(in.nextLine());

        System.out.println("Digite o sobrenome:");
        novoContratante.setSobrenome(in.nextLine());

        System.out.println("Digite a data de nascimento (formato: yyyy-MM-dd):");
        inputBirthDateUntilCorrectlyFormated(novoContratante);

        System.out.println("Digite o email:");
        novoContratante.setEmail(in.nextLine());

        System.out.println("Digite o telefone:");
        novoContratante.setTelefone(in.nextLine());

        try {
            dao.salvar(novoContratante);
        } catch (DAOException e) {
            System.out.println("Erro ao criar contratante: " + e.getMessage());
            return;
        }
        System.out.println("Contratante criado com sucesso!");
    }

    private static void consultarContratante() {
        System.out.println("Digite o ID do Contratante que deseja resgatar:");
        long idContratante = in.nextLong();
        in.nextLine();

        try {
            Contratante contratanteResgatado = dao.consultar(idContratante);
            if (contratanteResgatado != null) {
                System.out.println("Contratante encontrado:");
                System.out.println(contratanteResgatado);
            } else
                System.out.println("Contratante com o ID " + idContratante + " não encontrado.");
        } catch (DAOException e) {
            System.out.println("Erro ao resgatar contratante: " + e.getMessage());
        }
    }

    private static void atualizarContratante() {
        System.out.println("Digite o ID do Contratante que deseja atualizar:");
        long idContratanteAtualizar = in.nextLong();
        in.nextLine();

        try {
            Contratante contratanteExistente = dao.consultar(idContratanteAtualizar);

            if (contratanteExistente != null)
                atualizarContratanteExistente(contratanteExistente);
            else
                System.out.println("Contratante com o ID " + idContratanteAtualizar + " não encontrado.");
        } catch (DAOException e) {
            System.out.println("Erro ao atualizar contratante: " + e.getMessage());
        }
    }

    private static void deletarContratante() {
        System.out.println("Digite o ID do Contratante que deseja deletar:");
        long idDeletar = in.nextLong();
        in.nextLine();

        try {
            Contratante contratanteDeletar = dao.consultar(idDeletar);

            if (contratanteDeletar != null) {
                dao.deletar(contratanteDeletar);
                System.out.println("Contratante " + contratanteDeletar.getNome() + " deletado com sucesso!");
            } else
                System.out.println("Contratante com o ID " + idDeletar + " não encontrado.");
        } catch (DAOException e) {
            System.out.println("Erro ao deletar contratante: " + e.getMessage());
        }
    }

    private static void listarContratantes() {
        List<Contratante> contratantes;
        try {
            contratantes = dao.consultarTodos();
        } catch (DAOException e) {
            System.out.println("Erro ao listar contratantes: " + e.getMessage());
            return;
        }
        if (contratantes.isEmpty())
            System.out.println("Não há contratantes cadastrados.");
        else {
            System.out.println("Lista de Contratantes:");
            for (Contratante contratante : contratantes) {
                System.out.println(contratante);
                System.out.println("-----------------------------------");
            }
        }
    }

    private static void sair() {
        System.out.println("Encerrando o programa...");
    }

    private static void opcaoInvalida() {
        System.out.println("Opção inválida. Por favor, escolha novamente.");
    }

    public static void main(String[] args) throws DAOException, ParseException {
        while (true) {
            System.out.println("Selecione uma opção:");
            System.out.println("1. Criar Contratante");
            System.out.println("2. Consultar Contratante");
            System.out.println("3. Atualizar Contratante");
            System.out.println("4. Deletar Contratante");
            System.out.println("5. Listar Contratantes");
            System.out.println("0. Sair");

            int opcao = in.nextInt();
            in.nextLine();

            switch (opcao) {
                case 1:
                    criarContratante();
                    break;
                case 2:
                    consultarContratante();
                    break;
                case 3:
                    atualizarContratante();
                    break;
                case 4:
                    deletarContratante();
                    break;
                case 5:
                    listarContratantes();
                    break;
                case 0:
                    sair();
                    return;
                default:
                    opcaoInvalida();
            }
        }
    }

    private static void atualizarContratanteExistente(Contratante contratanteExistente) {
        System.out.println("Digite o novo nome de usuário:");
        contratanteExistente.setUsername(in.nextLine());

        System.out.println("Digite a nova senha:");
        contratanteExistente.setSenha(in.nextLine());

        System.out.println("Digite o novo CNPJ:");
        contratanteExistente.setCnpj(in.nextLine());

        System.out.println("Digite o novo nome:");
        contratanteExistente.setNome(in.nextLine());

        System.out.println("Digite o novo sobrenome:");
        contratanteExistente.setSobrenome(in.nextLine());

        System.out.println("Digite a nova data de nascimento (formato: yyyy-MM-dd):");
        inputBirthDateUntilCorrectlyFormated(contratanteExistente);

        System.out.println("Digite o novo email:");
        contratanteExistente.setEmail(in.nextLine());

        System.out.println("Digite o novo telefone:");
        contratanteExistente.setTelefone(in.nextLine());

        try {
            dao.atualizar(contratanteExistente);
        } catch (DAOException e) {
            System.out.println("Erro ao atualizar contratante: " + e.getMessage());
            return;
        }
        System.out.println("Contratante atualizado com sucesso!");
    }

    private static void inputBirthDateUntilCorrectlyFormated(Contratante contratante) {
        while (true) {
            try {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                Date novaDataNascimento = sdf.parse(in.nextLine());
                contratante.setNascimento(novaDataNascimento);
            } catch (ParseException e) {
                System.out.println("Formato de data inválido. Certifique-se de inserir no formato correto (yyyy-MM-dd).");
                continue;
            }
            break;
        }
    }
}

