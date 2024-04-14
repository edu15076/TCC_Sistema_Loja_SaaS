package Entidade;

import java.io.Serializable;
import javax.persistence.*;

@Entity
@Table(name = "periodicidade")
public class Periodicidade implements Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;
    private int qtdPeriodos;
    private int qtdDiasPorPeriodo;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public int getQtdPeriodos() {
        return qtdPeriodos;
    }

    public void setQtdPeriodos(int qtdPeriodos) {
        this.qtdPeriodos = qtdPeriodos;
    }

    public int getQtdDiasPorPeriodo() {
        return qtdDiasPorPeriodo;
    }

    public void setQtdDiasPorPeriodo(int qtdDiasPorPeriodo) {
        this.qtdDiasPorPeriodo = qtdDiasPorPeriodo;
    }
}
