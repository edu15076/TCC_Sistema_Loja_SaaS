package DAO;

import java.util.List;
import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;

public abstract class BaseDAO<T> {
    
    protected final EntityManagerFactory entityManagerFactory;
    protected final String nomeEntidade;
    protected final String nomeTabela;

    public BaseDAO(String persistenceUnitName) throws DAOException {
        try {
            this.entityManagerFactory = Persistence.createEntityManagerFactory(persistenceUnitName);
            this.nomeEntidade = this.getEntityClass().getSimpleName();
            this.nomeTabela = this.getEntityClass().getAnnotation(javax.persistence.Table.class).name();
        } catch (Exception e) {
            throw new DAOException("Erro ao criar EntityManagerFactory", e);
        }
    }

    public void salvar(T entity) throws DAOException {
        try {
            EntityManager entityManager = this.entityManagerFactory.createEntityManager();
            entityManager.getTransaction().begin();
            entityManager.persist(entity);
            entityManager.getTransaction().commit();
            entityManager.close();
        } catch (Exception e) {
            throw new DAOException("Erro ao salvar " + nomeEntidade, e);
        }
    }

    public T consultar(Long id) throws DAOException {
        try {
            EntityManager entityManager = this.entityManagerFactory.createEntityManager();
            return entityManager.find(getEntityClass(), id);
        } catch (Exception e) {
            throw new DAOException("Erro ao consultar " + nomeEntidade, e);
        }
    }
    
    public List<T> consultarTodos() throws DAOException {
        try {
            EntityManager entityManager = this.entityManagerFactory.createEntityManager();
            List<T> result = entityManager.createQuery("FROM " + nomeTabela, getEntityClass()).getResultList();
            entityManager.close();
            return result;
        } catch (Exception e) {
            throw new DAOException("Erro ao consultar todos os " + nomeEntidade, e);
        }
    }

    public void atualizar(T entity) throws DAOException {
        try {
            EntityManager entityManager = this.entityManagerFactory.createEntityManager();
            entityManager.getTransaction().begin();
            entityManager.merge(entity);
            entityManager.getTransaction().commit();
            entityManager.close();
        } catch (Exception e) {
            throw new DAOException("Erro ao atualizar " + nomeEntidade, e);
        }
    }

    public void deletar(T entity) throws DAOException {
        try {
            EntityManager entityManager = this.entityManagerFactory.createEntityManager();
            entityManager.getTransaction().begin();
            entityManager.remove(entity);
            entityManager.getTransaction().commit();
            entityManager.close();
        } catch (Exception e) {
            throw new DAOException("Erro ao deletar " + nomeEntidade, e);
        }
    }

    public void fechar() throws DAOException {
        try {
            entityManagerFactory.close();
        } catch (Exception e) {
            throw new DAOException("Erro ao fechar EntityManagerFactory", e);
        }
    }

    protected abstract Class<T> getEntityClass();
}
