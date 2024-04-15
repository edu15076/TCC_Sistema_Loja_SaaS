package DAO;

import Entidade.Contrato;

public class ContratoDAO extends BaseDAO<Contrato> {

    public ContratoDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<Contrato> getEntityClass() {
        return Contrato.class;
    }
}