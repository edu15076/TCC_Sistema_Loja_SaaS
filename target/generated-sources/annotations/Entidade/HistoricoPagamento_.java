package Entidade;

import Entidade.ContratoAssinado;
import java.util.Date;
import javax.annotation.processing.Generated;
import javax.persistence.metamodel.SingularAttribute;
import javax.persistence.metamodel.StaticMetamodel;

@Generated(value="org.eclipse.persistence.internal.jpa.modelgen.CanonicalModelProcessor", date="2024-04-14T22:41:58", comments="EclipseLink-2.7.12.v20230209-rNA")
@StaticMetamodel(HistoricoPagamento.class)
public class HistoricoPagamento_ { 

    public static volatile SingularAttribute<HistoricoPagamento, Date> dataPagamento;
    public static volatile SingularAttribute<HistoricoPagamento, Double> valorASerPago;
    public static volatile SingularAttribute<HistoricoPagamento, Date> dataInicioPrazo;
    public static volatile SingularAttribute<HistoricoPagamento, Long> id;
    public static volatile SingularAttribute<HistoricoPagamento, Date> dataFimPrazo;
    public static volatile SingularAttribute<HistoricoPagamento, ContratoAssinado> contratoAssinado;

}