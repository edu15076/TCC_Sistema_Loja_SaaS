package DAO;

import Entidade.Contratante;

public class ContratanteDAO extends BaseDAO<Contratante> {

    public ContratanteDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<Contratante> getEntityClass() {
        return Contratante.class;
    }
}