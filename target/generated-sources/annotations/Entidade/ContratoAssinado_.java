package Entidade;

import Entidade.Periodicidade;
import java.util.Date;
import javax.annotation.processing.Generated;
import javax.persistence.metamodel.SingularAttribute;
import javax.persistence.metamodel.StaticMetamodel;

@Generated(value="org.eclipse.persistence.internal.jpa.modelgen.CanonicalModelProcessor", date="2024-04-14T22:41:58", comments="EclipseLink-2.7.12.v20230209-rNA")
@StaticMetamodel(ContratoAssinado.class)
public class ContratoAssinado_ { 

    public static volatile SingularAttribute<ContratoAssinado, Date> dataContratacao;
    public static volatile SingularAttribute<ContratoAssinado, Boolean> vigente;
    public static volatile SingularAttribute<ContratoAssinado, Periodicidade> periodicidade;
    public static volatile SingularAttribute<ContratoAssinado, Long> id;

}