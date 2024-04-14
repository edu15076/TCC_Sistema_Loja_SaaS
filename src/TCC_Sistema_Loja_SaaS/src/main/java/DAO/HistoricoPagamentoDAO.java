package DAO;

import Entidade.HistoricoPagamento;

public class HistoricoPagamentoDAO extends BaseDAO<HistoricoPagamento> {

    public HistoricoPagamentoDAO() throws DAOException {
        super("persistence");
    }

    @Override
    protected Class<HistoricoPagamento> getEntityClass() {
        return HistoricoPagamento.class;
    }
}