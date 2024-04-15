package Entidade;

import Entidade.Contratante;
import javax.annotation.processing.Generated;
import javax.persistence.metamodel.SingularAttribute;
import javax.persistence.metamodel.StaticMetamodel;

@Generated(value="org.eclipse.persistence.internal.jpa.modelgen.CanonicalModelProcessor", date="2024-04-14T22:41:58", comments="EclipseLink-2.7.12.v20230209-rNA")
@StaticMetamodel(Cartao.class)
public class Cartao_ { 

    public static volatile SingularAttribute<Cartao, Integer> numeroEndereco;
    public static volatile SingularAttribute<Cartao, Integer> codigo;
    public static volatile SingularAttribute<Cartao, Long> numero;
    public static volatile SingularAttribute<Cartao, Contratante> contratante;
    public static volatile SingularAttribute<Cartao, Long> id;
    public static volatile SingularAttribute<Cartao, Integer> bandeira;
    public static volatile SingularAttribute<Cartao, String> cep;

}