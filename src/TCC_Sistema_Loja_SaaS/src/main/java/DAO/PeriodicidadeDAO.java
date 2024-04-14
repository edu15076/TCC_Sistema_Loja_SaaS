package DAO;

import Entidade.Periodicidade;

public class PeriodicidadeDAO extends BaseDAO<Periodicidade> {

    public PeriodicidadeDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<Periodicidade> getEntityClass() {
        return Periodicidade.class;
    }
}