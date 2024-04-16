package Entidade;

import Entidade.Cartao;
import Entidade.Loja;
import java.util.Date;
import javax.annotation.processing.Generated;
import javax.persistence.metamodel.ListAttribute;
import javax.persistence.metamodel.SingularAttribute;
import javax.persistence.metamodel.StaticMetamodel;

@Generated(value="org.eclipse.persistence.internal.jpa.modelgen.CanonicalModelProcessor", date="2024-04-15T22:10:45", comments="EclipseLink-2.7.12.v20230209-rNA")
@StaticMetamodel(Contratante.class)
public class Contratante_ { 

    public static volatile SingularAttribute<Contratante, String> senha;
    public static volatile SingularAttribute<Contratante, Date> nascimento;
    public static volatile SingularAttribute<Contratante, String> telefone;
    public static volatile ListAttribute<Contratante, Cartao> cartoes;
    public static volatile SingularAttribute<Contratante, Loja> loja;
    public static volatile SingularAttribute<Contratante, String> nome;
    public static volatile SingularAttribute<Contratante, Long> id;
    public static volatile SingularAttribute<Contratante, String> cnpj;
    public static volatile SingularAttribute<Contratante, String> sobrenome;
    public static volatile SingularAttribute<Contratante, String> email;
    public static volatile SingularAttribute<Contratante, String> username;

}