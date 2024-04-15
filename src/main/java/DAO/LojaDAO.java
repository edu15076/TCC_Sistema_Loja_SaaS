package DAO;

import Entidade.Loja;

public class LojaDAO extends BaseDAO<Loja> {

    public LojaDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<Loja> getEntityClass() {
        return Loja.class;
    }
}