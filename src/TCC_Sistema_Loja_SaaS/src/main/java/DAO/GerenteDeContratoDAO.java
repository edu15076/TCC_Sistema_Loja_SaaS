package DAO;

import Entidade.GerenteDeContrato;

public class GerenteDeContratoDAO extends BaseDAO<GerenteDeContrato> {

    public GerenteDeContratoDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<GerenteDeContrato> getEntityClass() {
        return GerenteDeContrato.class;
    }
}