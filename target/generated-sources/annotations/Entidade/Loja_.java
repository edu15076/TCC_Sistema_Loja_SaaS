package Entidade;

import Entidade.Contratante;
import javax.annotation.processing.Generated;
import javax.persistence.metamodel.SingularAttribute;
import javax.persistence.metamodel.StaticMetamodel;

@Generated(value="org.eclipse.persistence.internal.jpa.modelgen.CanonicalModelProcessor", date="2024-04-15T22:10:45", comments="EclipseLink-2.7.12.v20230209-rNA")
@StaticMetamodel(Loja.class)
public class Loja_ { 

    public static volatile SingularAttribute<Loja, Long> idContratante;
    public static volatile SingularAttribute<Loja, Contratante> contratante;
    public static volatile SingularAttribute<Loja, byte[]> logo;
    public static volatile SingularAttribute<Loja, String> nome_da_empresa;

}