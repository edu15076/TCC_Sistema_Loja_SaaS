package DAO;

import Entidade.ContratoAssinado;

public class ContratoAssinadoDAO extends BaseDAO<ContratoAssinado> {

    public ContratoAssinadoDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<ContratoAssinado> getEntityClass() {
        return ContratoAssinado.class;
    }
}