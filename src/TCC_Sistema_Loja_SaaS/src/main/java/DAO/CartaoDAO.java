package DAO;

import Entidade.Cartao;

public class CartaoDAO extends BaseDAO<Cartao> {

    public CartaoDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<Cartao> getEntityClass() {
        return Cartao.class;
    }
}