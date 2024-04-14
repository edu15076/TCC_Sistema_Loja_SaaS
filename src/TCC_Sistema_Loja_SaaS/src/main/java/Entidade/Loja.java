package Entidade;

import java.io.Serializable;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.MapsId;
import javax.persistence.OneToOne;
import javax.persistence.Table;

@Entity
@Table(name = "loja")
public class Loja implements Serializable {
    @Id
    private long idContratante;
    private String nome;
    private byte[] logo;
    
    @OneToOne
    @MapsId 
    @JoinColumn(name = "id_contratante")
    private Contratante contratante;

    public long getIdContratante() {
        return idContratante;
    }

    public void setIdContratante(long idContratante) {
        this.idContratante = idContratante;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public byte[] getLogo() {
        return logo;
    }

    public void setLogo(byte[] logo) {
        this.logo = logo;
    }

    public Contratante getContratante() {
        return contratante;
    }

    public void setContratante(Contratante contratante) {
        this.contratante = contratante;
    }
}
