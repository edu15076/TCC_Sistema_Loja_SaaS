package Entidade;

import java.io.Serializable;
import java.util.Date;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.OneToOne;
import javax.persistence.Table;
import javax.persistence.Temporal;
import javax.persistence.TemporalType;

@Entity
@Table(name = "historico_pagamento")
public class HistoricoPagamento implements Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;
    private double valorASerPago;
    
    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "data_pagamento")
    private Date dataPagamento;
    
    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "data_inicio_prazo")
    private Date dataInicioPrazo;
    
    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "data_fim_prazo")
    private Date dataFimPrazo;
    
    @OneToOne
    @JoinColumn(name = "id_contrato_assinado")
    private ContratoAssinado contratoAssinado;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public double getValorASerPago() {
        return valorASerPago;
    }

    public void setValorASerPago(double valorASerPago) {
        this.valorASerPago = valorASerPago;
    }

    public Date getDataPagamento() {
        return dataPagamento;
    }

    public void setDataPagamento(Date dataPagamento) {
        this.dataPagamento = dataPagamento;
    }

    public Date getDataInicioPrazo() {
        return dataInicioPrazo;
    }

    public void setDataInicioPrazo(Date dataInicioPrazo) {
        this.dataInicioPrazo = dataInicioPrazo;
    }

    public Date getDataFimPrazo() {
        return dataFimPrazo;
    }

    public void setDataFimPrazo(Date dataFimPrazo) {
        this.dataFimPrazo = dataFimPrazo;
    }

    public ContratoAssinado getContratoAssinado() {
        return contratoAssinado;
    }

    public void setContratoAssinado(ContratoAssinado contratoAssinado) {
        this.contratoAssinado = contratoAssinado;
    }
}
