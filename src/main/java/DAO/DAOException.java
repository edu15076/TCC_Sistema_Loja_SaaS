package DAO;

public class DAOException extends Exception {
    public DAOException(String mensagem, Exception e) {
        super(mensagem, e);
    }
}