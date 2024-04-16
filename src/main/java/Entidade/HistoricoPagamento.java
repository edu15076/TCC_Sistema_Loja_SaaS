package Entidade;

import java.io.Serializable;
import java.util.Date;

import jakarta.persistence.*;

@Entity
@Table(name = "historico_pagamento")
public class HistoricoPagamento implements Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    @Column(name = "valor_a_ser_pago")
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
    
    @ManyToOne
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
