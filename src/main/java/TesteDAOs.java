
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
    public static void main(String[] args) throws DAOException, ParseException {
        ContratanteDAO dao = new ContratanteDAO();
        //LojaDAO daoLoja = new LojaDAO();
        Scanner in = new Scanner(System.in);
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
                    Contratante novoContratante = new Contratante();
                    /*Loja loja = new Loja();
                    
                    System.out.println("Digite o nome da Loja:");
                    loja.setNome(in.nextLine());*/
                    
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
                    try {
                        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                        Date nascimento = sdf.parse(in.nextLine());
                        novoContratante.setNascimento(nascimento);
                    } catch (ParseException e) {
                        System.out.println("Formato de data inválido. Certifique-se de inserir no formato correto (yyyy-MM-dd).");
                    }

                    System.out.println("Digite o email:");
                    novoContratante.setEmail(in.nextLine());

                    System.out.println("Digite o telefone:");
                    novoContratante.setTelefone(in.nextLine());
                    
                    dao.salvar(novoContratante);
                    //daoLoja.salvar(loja);
                    System.out.println("Contratante criado com sucesso!");
                    break;
                    
                case 2:
                    System.out.println("Digite o ID do Contratante que deseja resgatar:");
                    long idContratante = in.nextLong();
                    in.nextLine(); 
                    try {
                        Contratante contratanteResgatado = dao.consultar(idContratante);
                        if (contratanteResgatado != null) {
                            System.out.println("Contratante encontrado:");
                            System.out.println("ID: " + contratanteResgatado.getId());
                            System.out.println("Username: " + contratanteResgatado.getUsername());
                            System.out.println("CNPJ: " + contratanteResgatado.getCnpj());
                            System.out.println("Nome: " + contratanteResgatado.getNome());
                            System.out.println("Sobrenome: " + contratanteResgatado.getSobrenome());
                            System.out.println("Data de Nascimento: " + contratanteResgatado.getNascimento());
                            System.out.println("Email: " + contratanteResgatado.getEmail());
                            System.out.println("Telefone: " + contratanteResgatado.getTelefone());
                        } else {
                            System.out.println("Contratante com o ID " + idContratante + " não encontrado.");
                        }
                    } catch (DAOException e) {
                        System.out.println("Erro ao resgatar contratante: " + e.getMessage());
                    }
                    break;
                    
                case 3:
                    System.out.println("Digite o ID do Contratante que deseja atualizar:");
                    long idContratanteAtualizar = in.nextLong();
                    in.nextLine();

                    try {
                        Contratante contratanteExistente = dao.consultar(idContratanteAtualizar);

                        if (contratanteExistente != null) {
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
                            try {
                                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                                Date novaDataNascimento = sdf.parse(in.nextLine());
                                contratanteExistente.setNascimento(novaDataNascimento);
                            } catch (ParseException e) {
                                System.out.println("Formato de data inválido. Certifique-se de inserir no formato correto (yyyy-MM-dd).");
                            }

                            System.out.println("Digite o novo email:");
                            contratanteExistente.setEmail(in.nextLine());

                            System.out.println("Digite o novo telefone:");
                            contratanteExistente.setTelefone(in.nextLine());

                            dao.atualizar(contratanteExistente);
                            System.out.println("Contratante atualizado com sucesso!");
                        } else {
                            System.out.println("Contratante com o ID " + idContratanteAtualizar + " não encontrado.");
                        }
                    } catch (DAOException e) {
                        System.out.println("Erro ao atualizar contratante: " + e.getMessage());
                    }
                    break;
                    
                case 4:
                    System.out.println("Digite o ID do Contratante que deseja deletar:");
                    long idDeletar = in.nextLong();
                    in.nextLine(); 
                    try {
                        Contratante contratanteDeletar = dao.consultar(idDeletar);

                        if (contratanteDeletar != null) {
                            dao.deletar(contratanteDeletar);
                            System.out.println("Contratante " + contratanteDeletar.getNome() + " deletado com sucesso!");
                        } else {
                            System.out.println("Contratante com o ID " + idDeletar + " não encontrado.");
                        }
                    } catch (DAOException e) {
                        System.out.println("Erro ao deletar contratante: " + e.getMessage());
                    }
                    break;
                case 5:
                    List<Contratante> contratantes = dao.consultarTodos();
                    if (contratantes.isEmpty()) {
                        System.out.println("Não há contratantes cadastrados.");
                    } else {
                        System.out.println("Lista de Contratantes:");
                        for (Contratante contratante : contratantes) {
                            System.out.println("ID: " + contratante.getId());
                            System.out.println("Username: " + contratante.getUsername());
                            System.out.println("CNPJ: " + contratante.getCnpj());
                            System.out.println("Nome: " + contratante.getNome());
                            System.out.println("Sobrenome: " + contratante.getSobrenome());
                            System.out.println("Data de Nascimento: " + contratante.getNascimento());
                            System.out.println("Email: " + contratante.getEmail());
                            System.out.println("Telefone: " + contratante.getTelefone());
                            System.out.println("-----------------------------------");
                        }
                    }
                break;
                case 0:
                    System.out.println("Encerrando o programa...");
                    return;
                default:
                    System.out.println("Opção inválida. Por favor, escolha novamente.");
            }
        }
    }
}

