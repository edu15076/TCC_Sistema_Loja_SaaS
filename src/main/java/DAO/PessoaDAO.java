package DAO;

import Entidade.Pessoa;

public class PessoaDAO extends BaseDAO<Pessoa> {

    public PessoaDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<Pessoa> getEntityClass() {
        return Pessoa.class;
    }
}