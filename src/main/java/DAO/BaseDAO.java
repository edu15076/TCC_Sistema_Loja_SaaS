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
        EntityManager entityManager = this.entityManagerFactory.createEntityManager();
        try {
            entityManager.getTransaction().begin();
            entityManager.persist(entity);
            entityManager.getTransaction().commit();
        } catch (Exception e) {
            throw new DAOException("Erro ao salvar " + nomeEntidade, e);
        } finally {
            entityManager.close();
        }
    }

    public T consultar(Long id) throws DAOException {
        T result;
        EntityManager entityManager = this.entityManagerFactory.createEntityManager();
        try {
            result = entityManager.find(getEntityClass(), id);
        } catch (Exception e) {
            throw new DAOException("Erro ao consultar " + nomeEntidade, e);
        } finally {
            entityManager.close();
        }
        return result;
    }
    
    public List<T> consultarTodos() throws DAOException {
        List<T> result;
        EntityManager entityManager = this.entityManagerFactory.createEntityManager();
        try {
          result = entityManager.createQuery("FROM " + nomeEntidade + " t", getEntityClass()).getResultList();
        } catch (Exception e) {
            throw new DAOException("Erro ao consultar todos os " + nomeEntidade, e);
        } finally {
            entityManager.close();
        }
        return result;
    }

    public void atualizar(T entity) throws DAOException {
        EntityManager entityManager = this.entityManagerFactory.createEntityManager();
        try {
            entityManager.getTransaction().begin();
            entityManager.merge(entity);
            entityManager.getTransaction().commit();
        } catch (Exception e) {
            throw new DAOException("Erro ao atualizar " + nomeEntidade, e);
        } finally {
            entityManager.close();
        }
    }

    public void deletar(T entity) throws DAOException {
        EntityManager entityManager = this.entityManagerFactory.createEntityManager();
        try {
            entityManager.getTransaction().begin();
            if (!entityManager.contains(entity)) {
          
                entity = entityManager.merge(entity);
            }
            entityManager.remove(entity);

            entityManager.getTransaction().commit();
        } catch (Exception e) {
            throw new DAOException("Erro ao deletar " + nomeEntidade, e);
        } finally {
            entityManager.close();
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