package Entidade;

import Entidade.Periodicidade;
import javax.annotation.processing.Generated;
import javax.persistence.metamodel.SingularAttribute;
import javax.persistence.metamodel.StaticMetamodel;

@Generated(value="org.eclipse.persistence.internal.jpa.modelgen.CanonicalModelProcessor", date="2024-04-14T22:41:58", comments="EclipseLink-2.7.12.v20230209-rNA")
@StaticMetamodel(Contrato.class)
public class Contrato_ { 

    public static volatile SingularAttribute<Contrato, Double> preco;
    public static volatile SingularAttribute<Contrato, Boolean> ativo;
    public static volatile SingularAttribute<Contrato, Integer> memoria;
    public static volatile SingularAttribute<Contrato, Double> taxaDeMulta;
    public static volatile SingularAttribute<Contrato, Integer> armazenamento;
    public static volatile SingularAttribute<Contrato, Integer> processamento;
    public static volatile SingularAttribute<Contrato, byte[]> documento;
    public static volatile SingularAttribute<Contrato, Integer> tolerancia;
    public static volatile SingularAttribute<Contrato, Periodicidade> periodicidade;
    public static volatile SingularAttribute<Contrato, Long> id;
    public static volatile SingularAttribute<Contrato, String> descricao;

}