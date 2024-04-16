package Entidade;

import java.io.Serializable;
import java.util.Date;
import java.util.List;

import jakarta.persistence.*;

@Entity
@Table(name = "contrato_assinado")
public class ContratoAssinado implements Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;
    private boolean vigente;
    private Date dataContratacao;
    
    @ManyToOne
    @JoinColumn(name = "id_contrato")
    private Periodicidade periodicidade;

    @ManyToOne
    @JoinColumn(name = "id_contratante")
    private Contratante contratante;

    @OneToMany(fetch = FetchType.LAZY, cascade = CascadeType.ALL, mappedBy = "contratoAssinado")
    private List<HistoricoPagamento> historicoPagamento;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public boolean isVigente() {
        return vigente;
    }

    public void setVigente(boolean vigente) {
        this.vigente = vigente;
    }

    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "data_contratacao")
    public Date getDataContratacao() {
        return dataContratacao;
    }

    public void setDataContratacao(Date dataContratacao) {
        this.dataContratacao = dataContratacao;
    }

    public Periodicidade getPeriodicidade() {
        return periodicidade;
    }

    public void setPeriodicidade(Periodicidade periodicidade) {
        this.periodicidade = periodicidade;
    }

    public Contratante getContratante() {
        return contratante;
    }

    public void setContratante(Contratante contratante) {
        this.contratante = contratante;
    }

    public List<HistoricoPagamento> getHistoricoPagamento() {
        return historicoPagamento;
    }

    public void setHistoricoPagamento(List<HistoricoPagamento> historicoPagamento) {
        this.historicoPagamento = historicoPagamento;
    }
}
